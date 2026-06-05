"""
Interactive Leo constellation editor (v3).

Controls:
  Left-click empty        -> place a star
  Drag star -> star       -> draw a straight line (snaps to nearest)
  Cmd+click star          -> toggle BLUE (Regulus)
  Shift+click star        -> delete star
  C                       -> enter curve trace mode (move mouse to draw)
  C or Enter (in curve)   -> commit curve (snaps bright pixels + smooths)
  Esc (in curve)          -> cancel trace without committing
  Esc (normal)            -> quit
  U                       -> undo last action
  E / Export button       -> write two SVGs (dark bg + transparent)
  Q                       -> quit
"""

import math
import tkinter as tk
from tkinter import messagebox

import numpy as np
from PIL import Image, ImageTk

LOGO_PATH   = "src/guidestar/static/guidestar-logo.png"
SVG_OUT_BG  = "docs/_static/favicon.svg"
SVG_OUT_CLR = "docs/_static/favicon-transparent.svg"

DISPLAY_SIZE       = 800
SNAP_RADIUS        = 24
STAR_RADIUS        = 7
TRACE_MIN_INTERVAL  = 6
TRACE_BAND_HALF     = 5    # canvas px either side of path to search (cross-section half-width)
TRACE_BAND_SAMPLES  = 21   # sample points across the cross-section
TRACE_MIN_BRIGHTNESS = 20  # ignore pixels darker than this (0-255)

COL_STAR     = "#FFD060"
COL_STAR_BLU = "#7DD8FF"
COL_LINE     = "#B88800"
COL_PATH     = "#C89000"
COL_HOVER    = "#FFFFFF"
COL_OUTLINE  = "#000000"
COL_GHOST    = "#FFFF80"
COL_TRACE    = "#00FFCC"

class ConstellationEditor:
    def __init__(self, root):
        self.root = root

        logo_img = Image.open(LOGO_PATH).convert("RGBA")
        lw, lh = logo_img.size
        scale = DISPLAY_SIZE / max(lw, lh)
        self.disp_w = int(lw * scale)
        self.disp_h = int(lh * scale)
        logo_resized = logo_img.resize((self.disp_w, self.disp_h), Image.LANCZOS)
        self._logo_tk = ImageTk.PhotoImage(logo_resized)
        self._logo_gray = np.array(logo_img.convert("L"), dtype=np.float32)

        self.stars    = []
        self.lines    = []
        self.paths    = []
        self.blue_idx = None
        self._history = []

        self._drag_start   = None
        self._drag_line_id = None
        self._hover_idx    = None

        self._curve_mode = False
        self._trace_raw  = []
        self._trace_last = None

        self._hint_text = tk.StringVar(value=self._normal_hint())
        hint = tk.Label(root, textvariable=self._hint_text,
                        font=("Helvetica", 11), anchor="w")
        hint.pack(side=tk.TOP, fill=tk.X, padx=6, pady=3)

        btns = tk.Frame(root)
        btns.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=4)
        tk.Button(btns, text="Undo (U)",        command=self.undo,       width=10).pack(side=tk.LEFT, padx=3)
        tk.Button(btns, text="Clear All",       command=self.clear_all,  width=10).pack(side=tk.LEFT, padx=3)
        tk.Button(btns, text="Export SVGs (E)", command=self.export_svg,
                  width=15, bg="#2a6", fg="white").pack(side=tk.RIGHT, padx=4)
        self.status = tk.Label(btns, text="Stars: 0  Lines: 0  Paths: 0", anchor="w")
        self.status.pack(side=tk.LEFT, padx=8)

        self.canvas = tk.Canvas(root, width=self.disp_w, height=self.disp_h,
                                bg="black", cursor="crosshair")
        self.canvas.pack(padx=6, pady=2)

        # Mouse
        self.canvas.bind("<Button-1>",         self._on_press)
        self.canvas.bind("<B1-Motion>",        self._on_drag)
        self.canvas.bind("<ButtonRelease-1>",  self._on_release)
        self.canvas.bind("<Shift-Button-1>",   self._on_shift_click)
        self.canvas.bind("<Command-Button-1>", self._on_cmd_click)
        self.canvas.bind("<Motion>",           self._on_hover)

        # Keys — bind_all ensures they fire regardless of which widget has focus
        root.bind_all("<c>",      lambda e: self._toggle_curve())
        root.bind_all("<C>",      lambda e: self._toggle_curve())
        root.bind_all("<Return>", lambda e: self._commit_curve())
        root.bind_all("<Escape>", self._on_escape)
        root.bind_all("<u>",      lambda e: self.undo())
        root.bind_all("<U>",      lambda e: self.undo())
        root.bind_all("<e>",      lambda e: self.export_svg())
        root.bind_all("<E>",      lambda e: self.export_svg())
        root.bind_all("<q>",      lambda e: root.destroy())

        root.title("Constellation Editor  [C=curve  U=undo  E=export  Q=quit]")
        self._redraw()

    # ── Hint / status ─────────────────────────────────────────────────────

    def _normal_hint(self):
        return ("Click: star  |  Drag star->star: line  |  Cmd+click star: blue  |  "
                "Shift+click star: delete  |  C: trace curve  |  U: undo  |  E: export  |  Q: quit")

    def _curve_hint(self):
        return "*** CURVE MODE ***  Move mouse to trace  |  C / Enter: commit  |  Esc: cancel"

    def _update_hint(self):
        self._hint_text.set(self._curve_hint() if self._curve_mode else self._normal_hint())

    def _nearest_star(self, x, y, exclude=None):
        best, best_d = None, float("inf")
        for i, (sx, sy) in enumerate(self.stars):
            if i == exclude:
                continue
            d = math.hypot(x - sx, y - sy)
            if d < best_d:
                best, best_d = i, d
        return (best, best_d) if best is not None else (None, float("inf"))

    # keep old name as alias so any leftover calls don't break
    def nearest_star(self, x, y, exclude=None):
        return self._nearest_star(x, y, exclude)

    def update_status(self):
        self._update_status()

    def _update_status(self):
        self.status.config(
            text=f"Stars: {len(self.stars)}  Lines: {len(self.lines)}  Paths: {len(self.paths)}"
        )

    # ── Mouse event handlers ─────────────────────────────────────────────

    def _on_press(self, event):
        if self._curve_mode:
            return
        idx, d = self._nearest_star(event.x, event.y)
        if idx is not None and d < SNAP_RADIUS:
            self._drag_start = idx
            sx, sy = self.stars[idx]
            self._drag_line_id = self.canvas.create_line(
                sx, sy, event.x, event.y,
                fill=COL_GHOST, width=2, dash=(6, 3))
        else:
            self._drag_start = None

    # keep old names so event bindings still work if Tkinter cached them
    def on_left_press(self, event):
        self._on_press(event)

    def _on_drag(self, event):
        if self._curve_mode or self._drag_start is None or not self._drag_line_id:
            return
        sx, sy = self.stars[self._drag_start]
        idx, d = self._nearest_star(event.x, event.y, exclude=self._drag_start)
        tx, ty = (self.stars[idx] if idx is not None and d < SNAP_RADIUS
                  else (event.x, event.y))
        self.canvas.coords(self._drag_line_id, sx, sy, tx, ty)

    def on_drag_motion(self, event):
        self._on_drag(event)

    def _on_release(self, event):
        if self._curve_mode:
            return
        if self._drag_line_id:
            self.canvas.delete(self._drag_line_id)
            self._drag_line_id = None

        if self._drag_start is not None:
            idx, d = self._nearest_star(event.x, event.y, exclude=self._drag_start)
            if idx is not None and d < SNAP_RADIUS:
                a, b = min(self._drag_start, idx), max(self._drag_start, idx)
                if (a, b) not in self.lines:
                    self.lines.append((a, b))
                    self._history.append(('line', a, b))
                    self._update_status()
            self._drag_start = None
        else:
            idx, d = self._nearest_star(event.x, event.y)
            if idx is None or d >= SNAP_RADIUS:
                self.stars.append((event.x, event.y))
                self._history.append(('star', len(self.stars) - 1))
                self._update_status()
        self._redraw()

    def on_left_release(self, event):
        self._on_release(event)

    def _on_shift_click(self, event):
        if self._curve_mode:
            return
        idx, d = self._nearest_star(event.x, event.y)
        if idx is not None and d < SNAP_RADIUS:
            self._delete_star(idx)

    def on_shift_click(self, event):
        self._on_shift_click(event)

    def _on_cmd_click(self, event):
        if self._curve_mode:
            return
        idx, d = self._nearest_star(event.x, event.y)
        if idx is not None and d < SNAP_RADIUS:
            old = self.blue_idx
            self.blue_idx = idx if self.blue_idx != idx else None
            self._history.append(('blue', old))
            self._redraw()

    def on_right_click(self, event):
        self._on_cmd_click(event)

    def on_middle_click(self, event):
        self._on_shift_click(event)

    def _on_hover(self, event):
        idx, d = self._nearest_star(event.x, event.y)
        new_hover = idx if (idx is not None and d < SNAP_RADIUS) else None
        if new_hover != self._hover_idx:
            self._hover_idx = new_hover

        if self._curve_mode:
            lx, ly = self._trace_last if self._trace_last else (event.x - 9999, 0)
            if math.hypot(event.x - lx, event.y - ly) >= TRACE_MIN_INTERVAL:
                self._trace_raw.append((event.x, event.y))
                self._trace_last = (event.x, event.y)

        self._redraw()

    def on_motion(self, event):
        self._on_hover(event)

    # ── Curve mode ───────────────────────────────────────────────────────

    def _toggle_curve(self):
        if self._curve_mode:
            self._commit_curve()
        else:
            self._curve_mode = True
            self._trace_raw  = []
            self._trace_last = None
            self.canvas.config(cursor="pencil")
            self._update_hint()
            self._redraw()

    def _commit_curve(self):
        if not self._curve_mode:
            return
        self._curve_mode = False
        self.canvas.config(cursor="crosshair")
        self._update_hint()
        if len(self._trace_raw) >= 4:
            path = self._snap_bright_path(self._trace_raw)
            if path:
                self.paths.append(path)
                self._history.append(("path", len(self.paths) - 1))
                self._update_status()
        self._trace_raw  = []
        self._trace_last = None
        self._redraw()

    def _cancel_curve(self):
        self._curve_mode = False
        self._trace_raw  = []
        self._trace_last = None
        self.canvas.config(cursor="crosshair")
        self._update_hint()
        self._redraw()

    def _on_escape(self, event):
        if self._curve_mode:
            self._cancel_curve()
        else:
            self.root.destroy()

    # ── Bright-pixel snap + smooth ───────────────────────────────────────

    # ── Bright-pixel band tracing ────────────────────────────────────────

    def _snap_bright_path(self, canvas_pts):
        """
        For each uniformly-resampled point on the traced path, cast a
        cross-section perpendicular to the local tangent (±TRACE_BAND_HALF
        canvas pixels) and find the brightness-weighted centroid.  This
        locks onto the actual centre of the bright feature without jumping
        to distant pixels, and the centroid averaging already produces a
        smooth result — no post-smoothing step needed.
        """
        gray   = self._logo_gray
        ih, iw = gray.shape
        sx_s   = iw / self.disp_w   # canvas-px → image-px scale
        sy_s   = ih / self.disp_h

        # 1. Resample to uniform ~4 canvas-px spacing so band density is even
        pts = self._resample_uniform(canvas_pts, spacing=4)
        if len(pts) < 2:
            return canvas_pts

        n = len(pts)
        result = []

        offsets = np.linspace(-TRACE_BAND_HALF, TRACE_BAND_HALF, TRACE_BAND_SAMPLES)

        for i, (cx, cy) in enumerate(pts):
            # Local tangent from neighbours
            if i == 0:
                tx, ty = pts[1][0] - cx, pts[1][1] - cy
            elif i == n - 1:
                tx, ty = cx - pts[-2][0], cy - pts[-2][1]
            else:
                tx = pts[i+1][0] - pts[i-1][0]
                ty = pts[i+1][1] - pts[i-1][1]

            tlen = math.sqrt(tx*tx + ty*ty)
            if tlen < 1e-9:
                result.append((cx, cy))
                continue

            # Normal (perpendicular) unit vector
            nx_d = -ty / tlen
            ny_d =  tx / tlen

            # Brightness-weighted centroid along cross-section
            tw = 0.0
            wx = 0.0
            wy = 0.0
            for off in offsets:
                scx = cx + off * nx_d
                scy = cy + off * ny_d
                six = int(round(scx * sx_s))
                siy = int(round(scy * sy_s))
                if 0 <= six < iw and 0 <= siy < ih:
                    w = max(0.0, float(gray[siy, six]) - TRACE_MIN_BRIGHTNESS)
                    tw += w
                    wx += scx * w
                    wy += scy * w

            result.append((wx / tw, wy / tw) if tw > 0 else (cx, cy))

        # 2. Decimate to ~40 points for a compact SVG path
        target = 40
        step = max(1, len(result) // target)
        return result[::step] + [result[-1]]

    def _resample_uniform(self, pts, spacing=4):
        """Resample a polyline so consecutive points are ~`spacing` canvas px apart."""
        if len(pts) < 2:
            return list(pts)
        out = [pts[0]]
        buf = 0.0
        for i in range(1, len(pts)):
            dx = pts[i][0] - pts[i-1][0]
            dy = pts[i][1] - pts[i-1][1]
            seg = math.sqrt(dx*dx + dy*dy)
            if seg < 1e-9:
                continue
            t = (spacing - buf) / seg
            while t <= 1.0:
                out.append((pts[i-1][0] + t*dx, pts[i-1][1] + t*dy))
                t += spacing / seg
            buf = (t - 1.0) * seg
        if math.hypot(out[-1][0] - pts[-1][0], out[-1][1] - pts[-1][1]) > spacing / 2:
            out.append(pts[-1])
        return out

    def _delete_star(self, idx):
        removed_lines = [(a, b) for a, b in self.lines if a == idx or b == idx]
        self.lines = [(a, b) for a, b in self.lines if a != idx and b != idx]
        self.lines = [(a - (a > idx), b - (b > idx)) for a, b in self.lines]
        old_blue = self.blue_idx
        if self.blue_idx == idx:
            self.blue_idx = None
        elif self.blue_idx is not None and self.blue_idx > idx:
            self.blue_idx -= 1
        self._history.append(('delete', idx, self.stars[idx], removed_lines, old_blue))
        self.stars.pop(idx)
        self._update_status()
        self._redraw()

    def undo(self):
        if not self._history:
            return
        action = self._history.pop()
        if action[0] == 'star':
            idx = action[1]
            self.lines = [(a, b) for a, b in self.lines if a != idx and b != idx]
            if self.blue_idx == idx:
                self.blue_idx = None
            self.stars.pop(idx)
        elif action[0] == 'line':
            a, b = action[1], action[2]
            if (a, b) in self.lines:
                self.lines.remove((a, b))
        elif action[0] == 'blue':
            self.blue_idx = action[1]
        elif action[0] == 'path':
            pidx = action[1]
            if pidx < len(self.paths):
                self.paths.pop(pidx)
        elif action[0] == 'delete':
            _, idx, pos, removed_lines, old_blue = action
            self.stars.insert(idx, pos)
            self.lines = [(a + (a >= idx), b + (b >= idx)) for a, b in self.lines]
            for a, b in removed_lines:
                self.lines.append((a, b))
            if old_blue is not None:
                self.blue_idx = old_blue + (old_blue >= idx)
        self._update_status()
        self._redraw()

    def clear_all(self):
        if messagebox.askyesno("Clear", "Remove all stars, lines, and paths?"):
            self.stars.clear()
            self.lines.clear()
            self.paths.clear()
            self.blue_idx = None
            self._history.clear()
            self._cancel_curve()
            self._update_status()
            self._redraw()

    # ── Drawing ───────────────────────────────────────────────────────────

    def _redraw(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._logo_tk)

        # Committed smooth paths
        for path in self.paths:
            if len(path) >= 2:
                flat = [coord for p in path for coord in p]
                self.canvas.create_line(*flat, fill=COL_PATH, width=2,
                                        smooth=True, splinesteps=32)

        # Straight lines
        for a, b in self.lines:
            ax, ay = self.stars[a]
            bx, by = self.stars[b]
            self.canvas.create_line(ax, ay, bx, by, fill=COL_LINE, width=2)

        # Live trace preview
        if self._curve_mode and len(self._trace_raw) >= 2:
            flat = [coord for p in self._trace_raw for coord in p]
            self.canvas.create_line(*flat, fill=COL_TRACE, width=2,
                                    smooth=True, splinesteps=16)

        # Curve mode border indicator
        if self._curve_mode:
            self.canvas.create_rectangle(
                2, 2, self.disp_w - 2, self.disp_h - 2,
                outline=COL_TRACE, width=3, dash=(8, 4))

        # Stars
        for i, (sx, sy) in enumerate(self.stars):
            is_blue  = (i == self.blue_idx)
            is_hover = (i == self._hover_idx)
            col = COL_STAR_BLU if is_blue else COL_STAR
            outline = COL_HOVER if is_hover else COL_OUTLINE
            r = STAR_RADIUS + (2 if is_hover else 0)
            self.canvas.create_oval(sx-r, sy-r, sx+r, sy+r,
                                    fill=col, outline=outline, width=1.5)

    def redraw(self):
        self._redraw()

    # ── SVG Export ────────────────────────────────────────────────────────

    def export_svg(self):
        if not self.stars and not self.paths:
            messagebox.showwarning("Export", "Nothing placed yet.")
            return

        PAD = 6
        scx = (100 - 2*PAD) / self.disp_w
        scy = (100 - 2*PAD) / self.disp_h

        def nx(cx): return round(cx * scx + PAD, 2)
        def ny(cy): return round(cy * scy + PAD, 2)

        norm_stars = [(nx(cx), ny(cy)) for cx, cy in self.stars]
        norm_paths = [[(nx(cx), ny(cy)) for cx, cy in p] for p in self.paths]

        lines_svg = "\n".join(
            f'    <line x1="{norm_stars[a][0]}" y1="{norm_stars[a][1]}" '
            f'x2="{norm_stars[b][0]}" y2="{norm_stars[b][1]}"/>'
            for a, b in self.lines
        )
        paths_svg = "\n".join(
            (f'    <line x1="{p[0][0]}" y1="{p[0][1]}" x2="{p[-1][0]}" y2="{p[-1][1]}"/>'
             if self._max_chord_dev(p) < 1.5 else
             f'    <path d="{self._svg_catmull_rom(p)}" fill="none"/>')
            for p in norm_paths if len(p) >= 2
        )
        gold_glows = "\n".join(
            f'    <circle cx="{x}" cy="{y}" r="2.6"/>'
            for i, (x, y) in enumerate(norm_stars) if i != self.blue_idx
        )
        gold_dots = "\n".join(
            f'    <circle cx="{x}" cy="{y}" r="1.8"/>'
            for i, (x, y) in enumerate(norm_stars) if i != self.blue_idx
        )

        if self.blue_idx is not None:
            bx, by = norm_stars[self.blue_idx]
            regulus = (
                f'  <circle cx="{bx}" cy="{by}" r="5" fill="#3AACEE" filter="url(#rg)"/>\n'
                f'  <circle cx="{bx}" cy="{by}" r="3.2" fill="#7DD8FF"/>\n'
                f'  <circle cx="{bx}" cy="{by}" r="1.5" fill="#E8F8FF"/>'
            )
        else:
            regulus = "  <!-- no blue star designated -->"

        defs = """  <defs>
    <radialGradient id="bg" cx="60%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#0e0920"/>
      <stop offset="100%" stop-color="#020108"/>
    </radialGradient>
    <filter id="gg" x="-300%" y="-300%" width="700%" height="700%">
      <feGaussianBlur stdDeviation="2.2"/>
    </filter>
    <filter id="rg" x="-400%" y="-400%" width="900%" height="900%">
      <feGaussianBlur stdDeviation="3.5"/>
    </filter>
    <filter id="spf" x="-600%" y="-600%" width="1300%" height="1300%">
      <feGaussianBlur stdDeviation="1.0"/>
    </filter>
  </defs>"""

        spikes = self._spikes_svg(norm_stars, self.blue_idx)

        body = f"""{spikes}
  <g stroke="#B88800" stroke-width="0.75" stroke-linecap="round" opacity="0.75">
{lines_svg}
{paths_svg}
  </g>
  <g fill="#C89000" filter="url(#gg)">
{gold_glows}
  </g>
{regulus}
  <g fill="#FFD060">
{gold_dots}
  </g>"""

        def make_svg(with_bg):
            bg = ('  <rect width="100" height="100" rx="11" fill="url(#bg)"/>'
                  if with_bg else '  <!-- transparent background -->')
            return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">\n'
                    f'{defs}\n{bg}\n{body}\n</svg>')

        with open(SVG_OUT_BG,  "w") as f:
            f.write(make_svg(with_bg=True))
        with open(SVG_OUT_CLR, "w") as f:
            f.write(make_svg(with_bg=False))

        messagebox.showinfo("Exported",
            f"Written:\n  {SVG_OUT_BG}  (dark rounded bg)\n"
            f"  {SVG_OUT_CLR}  (transparent)\n\n"
            f"{len(self.stars)} stars  {len(self.lines)} lines  {len(self.paths)} paths")

    # ── Post-processing helpers (also used by _postprocess_svgs.py) ────────

    def _max_chord_dev(self, pts):
        """Max perpendicular deviation of point list from its start-to-end chord."""
        if len(pts) < 2:
            return 0.0
        x0, y0 = pts[0]
        x1, y1 = pts[-1]
        dx, dy = x1 - x0, y1 - y0
        L = math.sqrt(dx*dx + dy*dy)
        if L < 1e-9:
            return max(math.sqrt((x-x0)**2 + (y-y0)**2) for x, y in pts[1:])
        return max(abs(dy*(x-x0) - dx*(y-y0)) / L for x, y in pts)

    def _spikes_svg(self, norm_stars, blue_idx,
                    spike_hv=4.5, spike_diag=2.5,
                    spike_hv_reg=7.0, spike_diag_reg=4.0):
        """Return SVG fragment: H/V cardinal spikes + shorter 45° diagonals."""
        dg  = spike_diag     * math.sqrt(0.5)
        bdg = spike_diag_reg * math.sqrt(0.5)
        out = ['  <!-- diffraction spikes -->', '  <g filter="url(#spf)" stroke-linecap="round">']
        gold = [(x, y) for i, (x, y) in enumerate(norm_stars) if i != blue_idx]
        if gold:
            out.append('    <g stroke="#FFD060" stroke-width="0.5" opacity="0.9">')
            for cx, cy in gold:
                out.append(f'      <line x1="{cx-spike_hv:.2f}" y1="{cy:.2f}" x2="{cx+spike_hv:.2f}" y2="{cy:.2f}"/>')
                out.append(f'      <line x1="{cx:.2f}" y1="{cy-spike_hv:.2f}" x2="{cx:.2f}" y2="{cy+spike_hv:.2f}"/>')
                out.append(f'      <line x1="{cx-dg:.2f}" y1="{cy-dg:.2f}" x2="{cx+dg:.2f}" y2="{cy+dg:.2f}"/>')
                out.append(f'      <line x1="{cx+dg:.2f}" y1="{cy-dg:.2f}" x2="{cx-dg:.2f}" y2="{cy+dg:.2f}"/>')
            out.append('    </g>')
        if blue_idx is not None and blue_idx < len(norm_stars):
            bx, by = norm_stars[blue_idx]
            out.append('    <g stroke="#7DD8FF" stroke-width="0.7" opacity="0.95">')
            out.append(f'      <line x1="{bx-spike_hv_reg:.2f}" y1="{by:.2f}" x2="{bx+spike_hv_reg:.2f}" y2="{by:.2f}"/>')
            out.append(f'      <line x1="{bx:.2f}" y1="{by-spike_hv_reg:.2f}" x2="{bx:.2f}" y2="{by+spike_hv_reg:.2f}"/>')
            out.append(f'      <line x1="{bx-bdg:.2f}" y1="{by-bdg:.2f}" x2="{bx+bdg:.2f}" y2="{by+bdg:.2f}"/>')
            out.append(f'      <line x1="{bx+bdg:.2f}" y1="{by-bdg:.2f}" x2="{bx-bdg:.2f}" y2="{by+bdg:.2f}"/>')
            out.append('    </g>')
        out.append('  </g>')
        return '\n'.join(out)

    def _svg_catmull_rom(self, pts):
        if len(pts) < 2:
            return ""
        if len(pts) == 2:
            return f"M {pts[0][0]} {pts[0][1]} L {pts[1][0]} {pts[1][1]}"
        d = [f"M {pts[0][0]} {pts[0][1]}"]
        for i in range(len(pts) - 1):
            p0 = pts[max(0, i - 1)]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[min(len(pts) - 1, i + 2)]
            cp1x = round(p1[0] + (p2[0] - p0[0]) / 6, 2)
            cp1y = round(p1[1] + (p2[1] - p0[1]) / 6, 2)
            cp2x = round(p2[0] - (p3[0] - p1[0]) / 6, 2)
            cp2y = round(p2[1] - (p3[1] - p1[1]) / 6, 2)
            d.append(f"C {cp1x} {cp1y} {cp2x} {cp2y} {p2[0]} {p2[1]}")
        return " ".join(d)


def main():
    root = tk.Tk()
    root.resizable(False, False)
    app = ConstellationEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()

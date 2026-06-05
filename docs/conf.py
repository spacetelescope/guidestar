project = 'guidestar'
copyright = '2026, guidestar contributors'
author = 'Kyle Conroy and guidestar contributors'
release = '0.1.0'

extensions = [
    'guidestar',
]

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

html_logo = '_static/favicon-transparent.svg'
html_favicon = '_static/favicon.svg'

html_theme_options = {
    'github_url': 'https://github.com/spacetelescope/guidestar',
    'logo': {
        'image_light': '_static/favicon-transparent.svg',
        'image_dark': '_static/favicon-transparent.svg',
    },
}

# Suppress "toctree contains reference to nonexisting document" for demo pages
suppress_warnings = ['toc.excluded']

project = 'guidestar'
copyright = '2026, guidestar contributors'
author = 'Kyle Conroy and guidestar contributors'
release = '0.1.0'

extensions = [
    'guidestar',
]

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

html_logo = '_static/guidestar-logo.png'

html_theme_options = {
    'github_url': 'https://github.com/spacetelescope/guidestar',
    'logo': {
        'image_light': '_static/guidestar-logo.png',
        'image_dark': '_static/guidestar-logo.png',
    },
}

# Suppress "toctree contains reference to nonexisting document" for demo pages
suppress_warnings = ['toc.excluded']

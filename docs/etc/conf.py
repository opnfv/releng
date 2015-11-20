import datetime

needs_sphinx = '1.3'

numfig = True

source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'sphinx'
html_use_index = False
html_logo = 'opnfv-logo.png'

pdf_fit_mode = "shrink"
pdf_stylesheets = ['sphinx','kerning','a4']

latex_elements = {
    'printindex': '',
}
latex_logo = 'opnfv-logo.png'

copyright = u'%s, OPNFV' % datetime.date.today().year
version = u'1.0.0'
release = u'1.0.0'

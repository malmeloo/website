import glob
import os.path

from compressor.filters import CompilerFilter
from django.template.loaders.app_directories import get_app_template_dirs


def get_all_templates():
    templates = []

    dirs = get_app_template_dirs('jinja2')
    for d in dirs:
        for file in glob.glob(os.path.join(d, '**/*.html')):
            templates.append(file)

    return templates


class PurgeCSSFilter(CompilerFilter):
    command = 'purgecss --css {infile} -o {outfile} --content {content}'

    options = (
        ('content', ' '.join(get_all_templates())),
    )

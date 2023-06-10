import glob
import os.path

from compressor.filters import CompilerFilter  # type: ignore
from django.conf import settings
from django.template.loaders.app_directories import get_app_template_dirs  # type: ignore


def get_all_templates() -> list[str]:
    templates = []

    dirs = get_app_template_dirs('templates')
    for d in dirs:
        for file in glob.glob(os.path.join(d, '**/*.html')):
            templates.append(file)

    return templates


class PurgeCSSFilter(CompilerFilter):  # type: ignore
    command = 'purgecss --css {infile} -o {outfile} --safelist {safelist} --content {content}'

    options = (
        ('content', ' '.join(get_all_templates())),
        ('safelist', ' '.join(settings.PURGECSS_SAFELIST))
    )

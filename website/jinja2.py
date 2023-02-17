import random

from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def _pick(*options):
    return random.choice(options)


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,

        'pick': _pick
    })
    return env

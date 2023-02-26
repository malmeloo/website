import random

from django import template

register = template.Library()


@register.simple_tag
def choice(*options):
    return random.choice(options)

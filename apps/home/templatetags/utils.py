import random
from typing import TypeVar

from django import template

register = template.Library()

T = TypeVar('T')


@register.simple_tag
def choice(*options: T) -> T:
    return random.choice(options)

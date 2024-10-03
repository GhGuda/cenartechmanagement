from django import template
from django.conf import settings

register = template.Library()

@register.filter
def absolute_static(path):
    return f"{settings.STATIC_URL}{path}"

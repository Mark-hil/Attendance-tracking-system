import base64
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='b64encode')
def b64encode(value):
    """
    Custom template filter to encode a string in base64.
    Usage: {{ some_string|b64encode }}
    """
    if not value:
        return ''
    # Convert to bytes if not already
    if isinstance(value, str):
        value = value.encode('utf-8')
    # Encode to base64 and return as string
    return base64.b64encode(value).decode('utf-8')

from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Returns the value for a given key in a dictionary."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

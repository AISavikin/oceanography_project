
from django import template

register = template.Library()

@register.filter
def split(value, key):
    """Разделяет строку по разделителю"""
    return value.split(key)

@register.filter
def get_item(value, index):
    """Получает элемент по индексу из списка"""
    try:
        return value[index]
    except (IndexError, TypeError):
        return ""
from django import template

register = template.Library()

@register.filter
def rpl(value):
    return value.replace(" ","+")
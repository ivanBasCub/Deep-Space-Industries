from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter()
def format_number(value):
    try:
        return f"{value:,.2f}".replace(",", " ").replace(".", ".")
    except (ValueError, TypeError):
        return value
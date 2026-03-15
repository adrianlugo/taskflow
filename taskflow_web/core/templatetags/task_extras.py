from django import template

register = template.Library()

@register.filter
def status_color(status):
    colors = {
        'por_hacer': 'secondary',
        'en_progreso': 'primary',
        'revision': 'warning',
        'completado': 'success',
    }
    return colors.get(status, 'secondary')

@register.filter
def priority_color(priority):
    colors = {
        'baja': 'info',
        'media': 'primary',
        'alta': 'warning',
        'urgente': 'danger',
    }
    return colors.get(priority, 'secondary')

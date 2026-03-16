from django import template
from django.utils import timezone
from datetime import datetime

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

@register.filter
def natural_date(value):
    """
    Devuelve una cadena representativa del tiempo relativo (Ej: "hace 2h" o "vence en 3d").
    """
    if not value:
        return ""
    
    if isinstance(value, str):
        try:
            # Intentar parsear ISO format de la API
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return value

    now = timezone.now()
    if timezone.is_aware(value):
        now = now.replace(tzinfo=value.tzinfo)
    else:
        now = timezone.make_naive(now)

    diff = value - now
    
    if diff.days > 0:
        if diff.days == 1:
            return "vence mañana"
        return f"vence en {diff.days}d"
    
    if diff.days == 0 and diff.total_seconds() > 0:
        hours = int(diff.total_seconds() // 3600)
        if hours > 0:
            return f"vence en {hours}h"
        return "vence pronto"

    # Fechas pasadas (hace X tiempo)
    abs_diff = abs(diff)
    if abs_diff.days > 0:
        if abs_diff.days == 1:
            return "ayer"
        return f"hace {abs_diff.days}d"
    
    seconds = abs_diff.total_seconds()
    if seconds < 60:
        return "ahora mismo"
    if seconds < 3600:
        return f"hace {int(seconds // 60)}min"
    return f"hace {int(seconds // 3600)}h"

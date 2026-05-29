from django import template

register = template.Library()


@register.filter
def filesize(value):
    """
    Convert bytes to human readable size.
    """
    if value is None:
        return ""

    for unit in ["B", "KB", "MB", "GB"]:
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024

    return f"{value:.1f} TB"

from django import template
import re

register = template.Library()

@register.filter
def youtube_id(url):
    """Extract YouTube video ID from URL"""
    if not url:
        return ''
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([^&]+)',
        r'(?:youtu\.be\/)([^?]+)',
        r'(?:youtube\.com\/embed\/)([^?]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ''

@register.filter
def vimeo_id(url):
    """Extract Vimeo video ID from URL"""
    if not url:
        return ''
    match = re.search(r'vimeo\.com\/(\d+)', url)
    return match.group(1) if match else ''

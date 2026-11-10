from django import template
from portfolio.course_guides import guide_for

register = template.Library()


@register.filter
def course_guide(curso):
    return guide_for(curso)

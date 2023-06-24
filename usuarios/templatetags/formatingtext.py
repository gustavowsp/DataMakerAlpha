from django import template

register = template.Library()

@register.filter(name='active_inative')
def active_inative(value):
    
    if value:
        status = ' Ativa '
    else:
        status = ' Inativa '
    return status

@register.filter(name='filha_pai')
def pai_ou_filha(active):

    if active:
        status = ' Principal '
    else:
        status = ' Secundária '
    return status
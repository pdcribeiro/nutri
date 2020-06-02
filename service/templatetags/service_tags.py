from django import template

register = template.Library()

@register.filter
def get_last_measurement(client, measure):
    return client.measurement_set.filter(measure__exact=measure.id).first()
    #TODO try without exact


# @register.filter
# def endswith(str, substr):
#     return str.endswith(substr)

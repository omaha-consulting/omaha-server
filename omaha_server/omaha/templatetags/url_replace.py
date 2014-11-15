from django import template


register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """
    <a href="?{% url_replace request 'param' value %}">
    """

    dict_ = request.GET.copy()

    dict_[field] = value

    return dict_.urlencode()

from django.conf        import settings
from django.shortcuts   import render

def round_up(value):
    return int(value) if settings.ROUND_UPTO == 0 else round(value, settings.ROUND_UPTO)

def get_template(template_path, is_htmx):
    if not is_htmx:
        return template_path
    
    *parent_path, template_name = template_path.split("/")

    template_name = template_name.split(".")[0] + "_component.html"
    template_modified_path = parent_path + ["components", template_name]
    return "/".join(template_modified_path)

def custom_render(request, template_path, context):
    is_htmx = request.META.get("HTTP_HX_REQUEST", 'false') == 'true'

    return render(request, get_template(template_path, is_htmx), context)
from django.conf import settings

def round_up(value):
    return int(value) if settings.ROUND_UPTO == 0 else round(value, settings.ROUND_UPTO)
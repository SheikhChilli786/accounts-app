from atexit import register
from django import template
from cryptography.fernet import Fernet
from django.conf import settings

register = template.Library()

@register.filter
def replaceBlank(value,stringVal=""):
    value = str(value).replace(stringVal,'')
    return value

@register.filter
def encryptdata(value):
    fernet = Fernet(settings.ID_ENCRYPTION_KEY)
    value  = fernet.encrypt(str(value).encode())
    return value


@register.filter(name='abs')
def absolute_value(value):
    return abs(value)

@register.filter(name='credit_or_debit')
def credit_or_debit(value):
    if value < 0:
        return f"بنام {abs(value)}"
    elif value > 0:
        return f"جمع {abs(value)}"
    else:
        return abs(value)
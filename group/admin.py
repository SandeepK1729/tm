from django.contrib import admin

from .models import Group, Transaction

admin.site.register(Group)
admin.site.register(Transaction)
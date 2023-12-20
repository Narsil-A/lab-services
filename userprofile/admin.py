# userprofile/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Notification

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'is_labstaff', 'is_client',]

admin.site.register(User, CustomUserAdmin)
admin.site.register(Notification)


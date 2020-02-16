from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Subscription


# USERS
class SubscriptionInline(admin.StackedInline):
    model = Subscription
    can_delete = False
    verbose_name_plural = 'Options'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (SubscriptionInline, )


# REGISTERING and DISPLAY
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

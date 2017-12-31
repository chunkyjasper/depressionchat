from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.apps import apps
from .models import *
# Register your models here.

app = apps.get_app_config('apiauth')

for model_name, model in app.models.items():
    admin.site.register(model)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
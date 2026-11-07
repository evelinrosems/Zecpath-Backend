from django.contrib import admin
from .models import User, Job, Application, Candidate, Employer


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'phone',
        'role',
        'is_active',
        'is_verified',
    )

    list_filter = ('role', 'is_active', 'is_verified')

    search_fields = ('name', 'email', 'phone')


admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Candidate)
admin.site.register(Employer)
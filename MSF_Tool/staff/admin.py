from django.contrib import admin
from .models import *

# Show doctors on the admin dashboard
@admin.register(Doctor)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('public_id',)

# Show nurses on the admin dashboard
@admin.register(Nurse)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('public_id',)

# Show therapists on the admin dashboard
@admin.register(Therapist)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('public_id',)
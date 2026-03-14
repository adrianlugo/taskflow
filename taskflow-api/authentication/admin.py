from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'phone', 'created_at')
    list_filter = ('location',)
    search_fields = ('user__username', 'location', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Usuario', {'fields': ('user',)}),
        ('Datos de perfil', {'fields': ('bio', 'avatar', 'phone', 'location')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

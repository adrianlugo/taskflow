from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'owner')
    search_fields = ('name', 'description', 'owner__username')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('owner',)
    filter_horizontal = ('members',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description')}),
        ('Propietario y miembros', {'fields': ('owner', 'members')}),
        ('Estado y fechas', {'fields': ('status', 'start_date', 'end_date')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

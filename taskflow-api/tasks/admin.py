from django.contrib import admin

from .models import Task, TaskComment


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    readonly_fields = ('author', 'created_at', 'updated_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'priority', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'project')
    search_fields = ('title', 'description', 'project__name', 'assigned_to__username')
    raw_id_fields = ('project', 'assigned_to', 'created_by')
    inlines = [TaskCommentInline]
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fieldsets = (
        (None, {'fields': ('title', 'description')}),
        ('Relaciones', {'fields': ('project', 'assigned_to', 'created_by')}),
        ('Estado y prioridad', {'fields': ('status', 'priority', 'due_date', 'completed_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    search_fields = ('task__title', 'author__username', 'content')
    raw_id_fields = ('task', 'author')
    readonly_fields = ('created_at', 'updated_at')

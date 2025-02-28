from django.contrib import admin
from tasks.models import Task, Epic, Sprint

class TaskAdmin(admin.ModelAdmin):

    # special configuration for the admin Interface behaves for a Task model
    list_display = ('id', 'title', 'description', 'status', 'priority', 'owner', 'created_at', 'updated_at', 'due_date')
    list_filter = ("status", "created_at", 'priority')

    # actions for admin to perform on selected tasks
    actions = ['mark_as_in_progress', 'mark_as_done', 'mark_as_archived']

    def mark_as_archived(self, request, queryset):
        queryset.update(status='ARCHIVED')
    
    mark_as_archived.short_description = "Mark selected tasks as Archived"

    def mark_as_done(self, request, queryset):
        queryset.update(status='DONE')
    
    mark_as_done.short_description = "Mark selected tasks as Done"

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='IN_PROGRESS')
    
    mark_as_in_progress.short_description = "Mark selected tasks as In Progress"


    # add methods that check for the permissions of the user

    def has_add_permission(self, request):
        if request.user.has_perm('tasks.add_task'):
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('tasks.change_task'):
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('tasks.delete_task'):
            return True
        return False


class EpicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at', 'updated_at')
    

class SprintAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'start_date', 'end_date', 'created_at', 'updated_at')


# Register your models here.
admin.site.register(Task, TaskAdmin)
admin.site.register(Epic, EpicAdmin)
admin.site.register(Sprint, SprintAdmin)



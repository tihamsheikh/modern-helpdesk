from django.contrib import admin

from .models import Department, Student, Ticket


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "roll", "username", "is_agent", "department", "is_manager")
    list_filter = ("is_agent", "department")
    search_fields = ("name", "roll", "user__username")
    actions = ["make_agent", "remove_agent"]

    @admin.display(ordering="user__username", description="Username")
    def username(self, obj):
        return obj.user.username

    @admin.display(boolean=True, description="Manager")
    def is_manager(self, obj):
        return obj.user.is_superuser

    def save_model(self, request, obj, form, change):
        if not obj.is_agent:
            obj.department = None
        super().save_model(request, obj, form, change)

    @admin.action(description="Promote selected students to agents")
    def make_agent(self, request, queryset):
        queryset.update(is_agent=True)

    @admin.action(description="Remove agent role from selected students")
    def remove_agent(self, request, queryset):
        queryset.update(is_agent=False, department=None)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_id", "title", "created_by", "assiged_agent", "department", "mode", "status", "created_at")
    list_filter = ("status", "department", "mode", "assiged_agent")
    search_fields = ("title", "description", "created_by__username")
    readonly_fields = ("ticket_id", "created_at")
    

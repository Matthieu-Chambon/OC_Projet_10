from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Contributor, Project, Issue, Comment
from .forms import CustomUserCreationForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = User
    list_display = ('username', 'age', 'can_be_contacted', 'can_data_be_shared')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('age', 'can_be_contacted', 'can_data_be_shared'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'age', 'can_be_contacted', 'can_data_be_shared', 'password1', 'password2'),
        }),
    )
    
@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('user', 'project')
    ordering = ('user',)
    fieldsets = (
        (None, {
            'fields': ('user', 'project')
        }),
    )
    

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'created_time')
    ordering = ('created_time',)
    fieldsets = (
        (None, {
            'fields': ('author', 'contributors', 'title', 'description')
        }),
    )
    

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('author', 'project', 'title', 'created_time')
    ordering = ('created_time',)
    fieldsets = (
        (None, {
            'fields': ('author', 'project', 'title', 'description', 'priority', 'type', 'status')
        }),
    )
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'issue', 'uuid', 'created_time')
    ordering = ('created_time',)
    fieldsets = (
        (None, {
            'fields': ('author', 'issue', 'description')
        }),
    )
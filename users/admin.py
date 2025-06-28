from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    """
    Defines an inline admin descriptor for the Profile model, which allows it
    to be edited directly within the User admin page.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    """
    Extends the default User admin to include the Profile inline.
    This allows for managing user profiles (like blocking) directly from the
    user admin page. It also adds custom actions to the user list view.
    """
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_blocked')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'profile__is_blocked')
    actions = ['block_users', 'unblock_users']

    def get_is_blocked(self, instance):
        """Returns the blocked status from the related profile."""
        return instance.profile.is_blocked
    get_is_blocked.short_description = 'Blocked'
    get_is_blocked.boolean = True # Displays a nice icon

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

    def block_users(self, request, queryset):
        """Admin action to block selected users."""
        for user in queryset:
            user.profile.is_blocked = True
            user.profile.save()
        self.message_user(request, "Selected users have been blocked.")
    block_users.short_description = "Block selected users"

    def unblock_users(self, request, queryset):
        """Admin action to unblock selected users."""
        for user in queryset:
            user.profile.is_blocked = False
            user.profile.save()
        self.message_user(request, "Selected users have been unblocked.")
    unblock_users.short_description = "Unblock selected users"

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
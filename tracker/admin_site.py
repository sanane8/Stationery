from django.contrib.admin import AdminSite
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class RestrictedAdminSite(AdminSite):
    """Custom admin site that restricts access based on user roles"""
    
    site_header = _('SP Msabila Stationery Administration')
    site_title = _('SP Msabila Admin')
    index_title = _('Administration Panel')
    
    def has_permission(self, request):
        """
        Only allow admin users to access the admin panel
        """
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = request.user.profile
            is_admin = profile.is_admin()
            # Debug info
            print(f"User: {request.user.username}, Role: {profile.role}, Is Admin: {is_admin}")
            return is_admin
        except Exception as e:
            print(f"Permission check error: {e}")
            # If profile doesn't exist, deny access
            return False
    
    def has_module_permission(self, request, app_label):
        """
        Override to allow admin users to access all modules
        """
        return self.has_permission(request)
    
    def has_view_permission(self, request, obj=None):
        """
        Override to allow admin users to view all objects
        """
        return self.has_permission(request)
    
    def has_change_permission(self, request, obj=None):
        """
        Override to allow admin users to change all objects
        """
        return self.has_permission(request)
    
    def has_add_permission(self, request):
        """
        Override to allow admin users to add objects
        """
        return self.has_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """
        Override to allow admin users to delete objects
        """
        return self.has_permission(request)
    
    def get_model_admin(self, model):
        """
        Override to ensure model admins are properly registered
        """
        return super().get_model_admin(model)
    
    def index(self, request, extra_context=None):
        """
        Override index to ensure proper permission handling
        """
        if not self.has_permission(request):
            return self.login(request)
        
        return super().index(request, extra_context)


# Create custom admin site
restricted_admin_site = RestrictedAdminSite(name='restricted_admin')

# Register all models with the restricted admin site
from .admin import register_with_restricted_admin
register_with_restricted_admin(restricted_admin_site)

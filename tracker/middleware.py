import logging
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.core.exceptions import MiddlewareNotUsed
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from .models import UserProfile

logger = logging.getLogger(__name__)


class UserProfileMiddleware(MiddlewareMixin):
    """Middleware to ensure user profiles exist and add role info to requests"""
    
    def process_request(self, request):
        # Check if user is authenticated and has user attribute
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                profile = request.user.profile
            except UserProfile.DoesNotExist:
                # Create profile for existing users without one
                UserProfile.objects.create(
                    user=request.user,
                    role='shop_seller'  # Default role for existing users
                )
                profile = request.user.profile
            
            # Add role info to request for easy access
            request.user_role = profile.role
            request.is_admin = profile.is_admin()
            request.is_shop_seller = profile.is_shop_seller()
        
        return None


class SessionManagementMiddleware:
    """
    Middleware to handle session management and prevent 500 errors
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Add session headers for debugging
        if hasattr(request, 'session') and request.session:
            response['X-Session-Age'] = str(request.session.get_expiry_age()) if hasattr(request.session, 'get_expiry_age') else 'unknown'
            response['X-Session-Exists'] = 'true'
        else:
            response['X-Session-Exists'] = 'false'
        
        return response


class SessionSecurityMiddleware:
    """
    Enhanced security middleware for session management
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip session checks for static files and admin
        if self.should_skip_session_check(request):
            return self.get_response(request)
        
        # Check if session has expired
        if hasattr(request, 'user') and request.user.is_authenticated:
            if self.is_session_expired(request):
                logger.warning(f"Session expired for user {request.user.username}")
                logout(request)
                
                # For AJAX requests, return JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'error': 'Session expired',
                        'redirect_url': '/login/?message=Your session has expired due to inactivity'
                    }, status=401)
                
                # For regular requests, redirect to login
                return redirect('/login/?message=Your session has expired due to inactivity')
        
        return self.get_response(request)
    
    def should_skip_session_check(self, request):
        """Skip session checks for certain paths"""
        skip_paths = [
            '/static/',
            '/media/',
            '/favicon.ico',
            '/login/',
            '/logout/',
            '/password-reset/',
            '/admin/login/',
        ]
        
        return any(request.path.startswith(path) for path in skip_paths)
    
    def is_session_expired(self, request):
        """Check if the session has expired"""
        try:
            if not hasattr(request, 'session') or not request.session:
                return True
            
            # Check session expiry age
            if hasattr(request.session, 'get_expiry_age'):
                expiry_age = request.session.get_expiry_age()
                if expiry_age <= 0:
                    return True
            
            # Check session modification time
            if hasattr(request.session, 'get_last_activity_time'):
                last_activity = request.session.get_last_activity_time()
                if last_activity:
                    now = timezone.now()
                    time_diff = (now - last_activity).total_seconds()
                    if time_diff > settings.SESSION_COOKIE_AGE:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking session expiration: {e}")
            # If we can't determine session status, assume it's valid to prevent false logouts
            return False


class ErrorHandlingMiddleware:
    """
    Middleware to handle errors gracefully and prevent 500 errors
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error in request {request.path}: {e}")
            
            # For AJAX requests, return JSON error response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': 'An unexpected error occurred',
                    'message': 'The system encountered an error but your data is safe'
                }, status=500)
            
            # For regular requests, show error page
            return self.render_error_page(request, e)
    
    def render_error_page(self, request, exception):
        """Render a user-friendly error page"""
        try:
            from django.shortcuts import render
            return render(request, 'error.html', {
                'error_message': 'An unexpected error occurred. Please try again.',
                'error_details': str(exception) if settings.DEBUG else None
            }, status=500)
        except Exception:
            # If even the error page fails, return a simple response
            from django.http import HttpResponse
            return HttpResponse(
                'An error occurred. Please refresh the page or contact support.',
                status=500,
                content_type='text/html'
            )


class ShopSelectionMiddleware:
    """
    Middleware to handle shop selection and filtering
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        from django.core.cache import cache
        from .models import Shop
        
        # Get selected shop from session or default
        shop_id = request.session.get('selected_shop_id', 1)
        
        try:
            # Get selected shop
            selected_shop = Shop.objects.get(id=shop_id, is_active=True)
            request.selected_shop = selected_shop
            
            # Add shop filtering helper to request
            def filter_by_shop(queryset):
                """Filter queryset by selected shop"""
                if hasattr(queryset.model, 'shop'):
                    return queryset.filter(shop=selected_shop)
                return queryset
            
            request.filter_by_shop = filter_by_shop
            
        except Shop.DoesNotExist:
            # Fallback to first available shop
            default_shop = Shop.objects.filter(is_active=True).first()
            request.selected_shop = default_shop or None
            request.filter_by_shop = lambda queryset: queryset
        
        response = self.get_response(request)
        
        return response

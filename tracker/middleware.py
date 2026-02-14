import logging
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.core.exceptions import MiddlewareNotUsed

logger = logging.getLogger(__name__)


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

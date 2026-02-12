"""
Custom middleware for session timeout and user logout
"""
import time
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone


class SessionTimeoutMiddleware:
    """
    Middleware to handle session timeout and automatic logout
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Get last activity time from session
            last_activity = request.session.get('last_activity')
            current_time = timezone.now().timestamp()
            
            if last_activity:
                # Calculate inactive time in seconds
                inactive_time = current_time - last_activity
                
                # If inactive for more than 10 minutes (600 seconds)
                if inactive_time > 600:
                    # Add warning message
                    messages.warning(
                        request, 
                        'You have been logged out due to 10 minutes of inactivity. Please log in again.',
                        extra_tags='session_timeout'
                    )
                    
                    # Logout user
                    from django.contrib.auth import logout
                    logout(request)
                    
                    # Clear session
                    request.session.flush()
                    
                    # Redirect to login page with timeout message
                    return redirect('login')
            
            # Update last activity time
            request.session['last_activity'] = current_time
            request.session.modified = True
        
        response = self.get_response(request)
        return response

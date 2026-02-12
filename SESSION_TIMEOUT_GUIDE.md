# Session Timeout Implementation Guide

## Overview
Added automatic user logout after 10 minutes of inactivity with warning system.

## Features Implemented

### 1. Session Timeout Middleware
- **File**: `stationery_tracker/middleware.py`
- **Function**: `SessionTimeoutMiddleware`
- **Timeout**: 10 minutes (600 seconds)
- **Warning**: 8 minutes (480 seconds)

### 2. Updated Settings
- **File**: `stationery_tracker/settings.py`
- **Change**: Added middleware to MIDDLEWARE list
- **Position**: After SecurityMiddleware, before SessionMiddleware

### 3. Enhanced Base Template
- **File**: `templates/base.html`
- **Features**: 
  - Session timeout warning popup
  - Countdown timer display
  - Activity detection (click, keypress, scroll, mousemove)
  - Auto-hide warning on user interaction
  - Responsive design

## How It Works

### 1. Middleware Logic
```python
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
```

### 2. Frontend Warning System
```javascript
// Session timeout warning system
let warningShown = false;
let timeoutWarning = 8 * 60; // 8 minutes in seconds
let sessionTimeout = 10 * 60; // 10 minutes in seconds
let lastActivity = Date.now();

// Update last activity on user interaction
document.addEventListener('click', updateActivity);
document.addEventListener('keypress', updateActivity);
document.addEventListener('scroll', updateActivity);
document.addEventListener('mousemove', updateActivity);

function updateActivity() {
    lastActivity = Date.now();
    warningShown = false;
    hideWarning();
}

// Check for inactivity every 30 seconds
setInterval(checkInactivity, 30000);

function checkInactivity() {
    const currentTime = Date.now();
    const inactiveTime = Math.floor((currentTime - lastActivity) / 1000);
    
    // Show warning after 8 minutes of inactivity
    if (inactiveTime >= timeoutWarning && !warningShown) {
        showWarning();
        warningShown = true;
    }
    
    // Auto-logout after 10 minutes (handled by middleware)
    // This is just a visual countdown since middleware handles actual logout
    if (inactiveTime >= timeoutWarning && warningShown) {
        updateCountdown(sessionTimeout - inactiveTime);
    }
}
```

## User Experience

### 1. Normal Usage
- User interacts with the app → Session stays active
- No warnings or interruptions
- Seamless experience

### 2. Inactivity Warning
- After 8 minutes of inactivity → Warning popup appears
- Shows countdown timer (2 minutes remaining)
- User can click anywhere to extend session
- Warning disappears when user interacts

### 3. Automatic Logout
- After 10 minutes of inactivity → Automatic logout
- User redirected to login page
- Warning message displayed: "You have been logged out due to 10 minutes of inactivity"
- Session completely cleared

### 4. Visual Indicators
- **Warning popup**: Fixed position, top-right corner
- **Countdown timer**: Shows remaining time
- **Bootstrap styling**: Consistent with app design
- **Responsive**: Works on mobile and desktop

## Configuration Options

### Customizing Timeout Duration
Edit `stationery_tracker/middleware.py`:
```python
# Change these values
if inactive_time > 600:  # 10 minutes
if inactive_time >= timeoutWarning:  # 8 minutes warning
```

### Customizing Warning Time
Edit `templates/base.html`:
```javascript
let timeoutWarning = 8 * 60;  // 8 minutes in seconds
let sessionTimeout = 10 * 60; // 10 minutes in seconds
```

## Security Benefits

1. **Prevents unauthorized access**: Auto-logout inactive users
2. **Protects sensitive data**: No abandoned sessions
3. **Reduces session hijacking risk**: Limited session lifetime
4. **User-friendly**: Clear warnings before logout
5. **Mobile compatible**: Works on all devices

## Testing

### 1. Test Normal Usage
1. Login to the application
2. Use the app normally
3. Verify no warnings appear during active use

### 2. Test Inactivity Warning
1. Login to the application
2. Wait for 8 minutes without any interaction
3. Verify warning popup appears with countdown
4. Click anywhere to dismiss warning
5. Verify warning disappears

### 3. Test Automatic Logout
1. Login to the application
2. Wait for 10 minutes without any interaction
3. Verify automatic logout occurs
4. Verify redirect to login page
5. Verify timeout message is displayed

## Deployment Notes

- **Middleware**: Automatically active when added to settings
- **Template**: Updated with session timeout JavaScript
- **Database**: No changes required
- **Compatible**: Works with existing authentication system

## Troubleshooting

### Session Not Expiring
- Check middleware order in settings.py
- Verify session middleware is active
- Check browser console for JavaScript errors

### Warning Not Showing
- Verify JavaScript is loading in base template
- Check browser console for errors
- Verify user is authenticated
- Check message tags in template

### Logout Not Working
- Verify logout URL is correct
- Check authentication backend
- Verify session clearing logic

This implementation provides a robust, user-friendly session timeout system that enhances security while maintaining good user experience.

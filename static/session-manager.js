// Session Manager - Automatic logout after 10 minutes of inactivity
class SessionManager {
    constructor() {
        this.timeoutMinutes = 10; // 10 minutes
        this.warningSeconds = 60; // Show warning 60 seconds before logout
        this.timeoutId = null;
        this.warningId = null;
        this.logoutUrl = '/logout/';
        this.extendUrl = '/extend-session/';
        
        this.init();
    }

    init() {
        // Reset timeout on user activity
        this.resetTimeout();
        
        // Listen for user activity events
        this.setupActivityListeners();
        
        // Check if user is logged in
        if (this.isLoggedIn()) {
            this.startSessionManager();
        }
    }

    isLoggedIn() {
        // Check if user is logged in by looking for user-related elements
        return document.querySelector('body').classList.contains('logged-in') || 
               document.querySelector('[data-user-logged-in="true"]') ||
               window.location.pathname !== '/login/' && 
               !window.location.pathname.includes('/admin/login/');
    }

    setupActivityListeners() {
        const events = [
            'mousedown', 'mousemove', 'keypress', 'scroll', 
            'touchstart', 'click', 'keydown', 'keyup'
        ];

        events.forEach(event => {
            document.addEventListener(event, () => {
                this.resetTimeout();
            }, true);
        });

        // Also listen for storage events (for multi-tab support)
        window.addEventListener('storage', (e) => {
            if (e.key === 'sessionActivity') {
                this.resetTimeout();
            }
        });
    }

    resetTimeout() {
        // Clear existing timeouts
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
        if (this.warningId) {
            clearTimeout(this.warningId);
        }

        // Set new warning timeout
        this.warningId = setTimeout(() => {
            this.showWarning();
        }, (this.timeoutMinutes * 60 * 1000) - (this.warningSeconds * 1000));

        // Set new logout timeout
        this.timeoutId = setTimeout(() => {
            this.logout();
        }, this.timeoutMinutes * 60 * 1000);

        // Notify other tabs of activity
        localStorage.setItem('sessionActivity', Date.now());
    }

    showWarning() {
        // Create warning modal
        const modal = this.createWarningModal();
        document.body.appendChild(modal);

        // Show modal with animation
        setTimeout(() => {
            modal.classList.add('show');
        }, 100);

        // Start countdown
        this.startCountdown(modal);

        // Auto-remove modal after warning period
        setTimeout(() => {
            this.removeModal(modal);
        }, this.warningSeconds * 1000);
    }

    createWarningModal() {
        const modal = document.createElement('div');
        modal.id = 'session-warning-modal';
        modal.className = 'session-warning-modal';
        modal.innerHTML = `
            <div class="session-warning-content">
                <div class="session-warning-header">
                    <h3>⚠️ Session Timeout Warning</h3>
                </div>
                <div class="session-warning-body">
                    <p>Your session will expire in <span id="countdown">60</span> seconds due to inactivity.</p>
                    <p>You will be automatically logged out for security reasons.</p>
                </div>
                <div class="session-warning-footer">
                    <button id="extend-session-btn" class="btn btn-primary btn-lg">
                        <i class="fas fa-clock"></i> Stay Logged In
                    </button>
                    <button id="logout-now-btn" class="btn btn-secondary">
                        <i class="fas fa-sign-out-alt"></i> Logout
                    </button>
                </div>
            </div>
            <div class="session-warning-backdrop"></div>
        `;

        // Add event listeners
        modal.querySelector('#extend-session-btn').addEventListener('click', () => {
            this.extendSession();
            this.removeModal(modal);
        });

        modal.querySelector('#logout-now-btn').addEventListener('click', () => {
            this.logout();
        });

        // Close on backdrop click
        modal.querySelector('.session-warning-backdrop').addEventListener('click', () => {
            this.extendSession();
            this.removeModal(modal);
        });

        return modal;
    }

    startCountdown(modal) {
        let seconds = this.warningSeconds;
        const countdownElement = modal.querySelector('#countdown');
        
        const countdownInterval = setInterval(() => {
            seconds--;
            countdownElement.textContent = seconds;
            
            if (seconds <= 0) {
                clearInterval(countdownInterval);
            }
        }, 1000);

        // Store interval ID for cleanup
        modal.dataset.countdownInterval = countdownInterval;
    }

    removeModal(modal) {
        // Clear countdown interval
        if (modal.dataset.countdownInterval) {
            clearInterval(modal.dataset.countdownInterval);
        }

        // Remove modal with animation
        modal.classList.remove('show');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }

    async extendSession() {
        try {
            // Call server to extend session
            const response = await fetch(this.extendUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action: 'extend' })
            });

            if (response.ok) {
                this.resetTimeout();
                this.showNotification('Session extended successfully', 'success');
            } else {
                // If server fails, still reset timeout on client side
                this.resetTimeout();
                this.showNotification('Session extended (offline mode)', 'info');
            }
        } catch (error) {
            // Network error - still extend session locally
            this.resetTimeout();
            this.showNotification('Session extended (offline mode)', 'info');
        }
    }

    async logout() {
        try {
            // Call server logout
            const response = await fetch(this.logoutUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                }
            });

            // Redirect to login page regardless of response
            window.location.href = '/login/?message=Your session has expired due to inactivity';
        } catch (error) {
            // Network error - still redirect to login
            window.location.href = '/login/?message=Your session has expired due to inactivity';
        }
    }

    getCSRFToken() {
        // Get CSRF token from cookie or meta tag
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                         document.querySelector('meta[name="csrf-token"]')?.content ||
                         this.getCookie('csrftoken');
        return csrfToken || '';
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `session-notification session-notification-${type}`;
        notification.innerHTML = `
            <div class="session-notification-content">
                <span>${message}</span>
                <button class="session-notification-close">&times;</button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Show with animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);

        // Close button
        notification.querySelector('.session-notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        });
    }

    startSessionManager() {
        // Add CSS styles
        this.addStyles();
        
        // Mark body as having session manager
        document.body.classList.add('session-manager-active');
        
        // Initial timeout setup
        this.resetTimeout();
    }

    addStyles() {
        if (document.getElementById('session-manager-styles')) {
            return; // Styles already added
        }

        const styles = document.createElement('style');
        styles.id = 'session-manager-styles';
        styles.textContent = `
            .session-warning-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .session-warning-modal.show {
                opacity: 1;
            }

            .session-warning-backdrop {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(2px);
            }

            .session-warning-content {
                position: relative;
                background: white;
                border-radius: 8px;
                padding: 0;
                max-width: 400px;
                width: 90%;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                transform: scale(0.9);
                transition: transform 0.3s ease;
            }

            .session-warning-modal.show .session-warning-content {
                transform: scale(1);
            }

            .session-warning-header {
                background: #dc3545;
                color: white;
                padding: 20px;
                border-radius: 8px 8px 0 0;
                text-align: center;
            }

            .session-warning-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
            }

            .session-warning-body {
                padding: 20px;
                text-align: center;
            }

            .session-warning-body p {
                margin: 10px 0;
                color: #333;
                line-height: 1.5;
            }

            .session-warning-body #countdown {
                font-weight: bold;
                color: #dc3545;
                font-size: 18px;
            }

            .session-warning-footer {
                padding: 25px;
                background: #f8f9fa;
                border-radius: 0 0 8px 8px;
                display: flex;
                gap: 15px;
                justify-content: center;
                align-items: center;
            }

            .session-warning-footer .btn {
                padding: 15px 30px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                min-width: 160px;
                justify-content: center;
            }

            .session-warning-footer .btn-primary {
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
                border: 2px solid transparent;
            }

            .session-warning-footer .btn-primary:hover {
                background: linear-gradient(135deg, #0056b3, #004085);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
            }

            .session-warning-footer .btn-secondary {
                background: #6c757d;
                color: white;
                border: 2px solid #6c757d;
            }

            .session-warning-footer .btn-secondary:hover {
                background: #545b62;
                border-color: #545b62;
                transform: translateY(-1px);
            }

            .session-warning-footer .btn i {
                font-size: 18px;
            }

            .session-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                min-width: 250px;
                max-width: 400px;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
            }

            .session-notification.show {
                opacity: 1;
                transform: translateX(0);
            }

            .session-notification-content {
                background: white;
                border-radius: 4px;
                padding: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
            }

            .session-notification-success .session-notification-content {
                border-left: 4px solid #28a745;
            }

            .session-notification-info .session-notification-content {
                border-left: 4px solid #17a2b8;
            }

            .session-notification-warning .session-notification-content {
                border-left: 4px solid #ffc107;
            }

            .session-notification-error .session-notification-content {
                border-left: 4px solid #dc3545;
            }

            .session-notification-close {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                color: #6c757d;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .session-notification-close:hover {
                color: #333;
            }

            /* Mobile responsive */
            @media (max-width: 480px) {
                .session-warning-content {
                    margin: 20px;
                    width: calc(100% - 40px);
                }

                .session-warning-footer {
                    flex-direction: column;
                    gap: 12px;
                    padding: 20px;
                }

                .session-warning-footer .btn {
                    width: 100%;
                    margin: 0;
                    padding: 18px 25px;
                    font-size: 16px;
                    min-width: auto;
                }

                .session-warning-footer .btn i {
                    font-size: 20px;
                }

                .session-notification {
                    left: 20px;
                    right: 20px;
                    max-width: none;
                }
            }
        `;

        document.head.appendChild(styles);
    }
}

// Initialize session manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.sessionManager = new SessionManager();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading
} else {
    // DOM is already loaded
    if (!window.sessionManager) {
        window.sessionManager = new SessionManager();
    }
}

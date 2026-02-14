// Django Admin Theme JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add dark mode toggle
    const darkModeToggle = document.createElement('button');
    darkModeToggle.textContent = '🌙';
    darkModeToggle.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: #79aec8;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        cursor: pointer;
        z-index: 9999;
        font-size: 16px;
    `;
    
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        darkModeToggle.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
        localStorage.setItem('admin-dark-mode', document.body.classList.contains('dark-mode'));
    });
    
    // Check for saved dark mode preference
    if (localStorage.getItem('admin-dark-mode') === 'true') {
        document.body.classList.add('dark-mode');
        darkModeToggle.textContent = '☀️';
    }
    
    document.body.appendChild(darkModeToggle);
    
    // Add responsive sidebar toggle for mobile
    const sidebarToggle = document.createElement('button');
    sidebarToggle.textContent = '☰';
    sidebarToggle.style.cssText = `
        display: none;
        position: fixed;
        top: 10px;
        left: 10px;
        background: #79aec8;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        cursor: pointer;
        z-index: 9999;
        font-size: 16px;
    `;
    
    sidebarToggle.addEventListener('click', function() {
        const sidebar = document.getElementById('nav-sidebar');
        if (sidebar) {
            sidebar.style.display = sidebar.style.display === 'none' ? 'block' : 'none';
        }
    });
    
    // Show sidebar toggle on mobile
    if (window.innerWidth <= 768) {
        document.body.appendChild(sidebarToggle);
        
        // Hide sidebar by default on mobile
        const sidebar = document.getElementById('nav-sidebar');
        if (sidebar) {
            sidebar.style.display = 'none';
        }
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        const sidebar = document.getElementById('nav-sidebar');
        if (window.innerWidth <= 768) {
            if (sidebarToggle.parentNode === null) {
                document.body.appendChild(sidebarToggle);
            }
            if (sidebar && sidebar.style.display !== 'none') {
                sidebar.style.display = 'none';
            }
        } else {
            if (sidebarToggle.parentNode) {
                sidebarToggle.parentNode.removeChild(sidebarToggle);
            }
            if (sidebar) {
                sidebar.style.display = 'block';
            }
        }
    });
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add table row highlighting on hover
    document.querySelectorAll('.results tbody tr').forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f5f5f5';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
    
    // Add loading states for forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('input[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.value = 'Loading...';
            }
        });
    });
    
    // Add confirmation for destructive actions
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        if (checkbox.name && checkbox.name.includes('DELETE') || checkbox.name.includes('delete')) {
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                        this.checked = false;
                    }
                }
            });
        }
    });
    
    // Add copy functionality for IDs
    document.querySelectorAll('.field-readonly input').forEach(input => {
        const copyBtn = document.createElement('button');
        copyBtn.textContent = '📋';
        copyBtn.style.cssText = `
            margin-left: 5px;
            background: #6c757d;
            color: white;
            border: none;
            padding: 2px 6px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        `;
        
        copyBtn.addEventListener('click', function() {
            navigator.clipboard.writeText(input.value).then(() => {
                copyBtn.textContent = '✓';
                setTimeout(() => {
                    copyBtn.textContent = '📋';
                }, 1000);
            });
        });
        
        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(copyBtn);
    });
});

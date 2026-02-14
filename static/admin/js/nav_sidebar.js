// Django Admin Navigation Sidebar JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('nav-sidebar');
    const mainContent = document.querySelector('.content-main');
    
    if (!sidebar || !mainContent) return;
    
    // Create toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.innerHTML = '☰';
    toggleBtn.className = 'sidebar-toggle';
    toggleBtn.style.cssText = `
        display: none;
        position: fixed;
        top: 15px;
        left: 15px;
        background: #79aec8;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        cursor: pointer;
        z-index: 1000;
        font-size: 16px;
    `;
    
    // Toggle sidebar function
    function toggleSidebar() {
        const isHidden = sidebar.style.display === 'none';
        sidebar.style.display = isHidden ? 'block' : 'none';
        
        if (mainContent) {
            if (isHidden) {
                mainContent.style.marginLeft = '250px';
            } else {
                mainContent.style.marginLeft = '0';
            }
        }
        
        toggleBtn.innerHTML = isHidden ? '☰' : '✕';
        localStorage.setItem('sidebar-collapsed', !isHidden);
    }
    
    toggleBtn.addEventListener('click', toggleSidebar);
    
    // Check for saved state
    const savedState = localStorage.getItem('sidebar-collapsed');
    if (savedState === 'true') {
        sidebar.style.display = 'none';
        if (mainContent) {
            mainContent.style.marginLeft = '0';
        }
        toggleBtn.innerHTML = '✕';
    }
    
    // Show toggle on mobile
    function checkMobile() {
        if (window.innerWidth <= 768) {
            document.body.appendChild(toggleBtn);
            toggleBtn.style.display = 'block';
            
            // Auto-hide sidebar on mobile
            if (savedState !== 'false') {
                sidebar.style.display = 'none';
                if (mainContent) {
                    mainContent.style.marginLeft = '0';
                }
                toggleBtn.innerHTML = '✕';
            }
        } else {
            if (toggleBtn.parentNode) {
                toggleBtn.parentNode.removeChild(toggleBtn);
            }
            sidebar.style.display = 'block';
            if (mainContent) {
                mainContent.style.marginLeft = '250px';
            }
            toggleBtn.innerHTML = '☰';
        }
    }
    
    // Initial check
    checkMobile();
    
    // Handle resize
    window.addEventListener('resize', checkMobile);
    
    // Add keyboard shortcut
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'b') {
            e.preventDefault();
            toggleSidebar();
        }
    });
    
    // Highlight current section
    function highlightCurrentSection() {
        const currentPath = window.location.pathname;
        const links = sidebar.querySelectorAll('a');
        
        links.forEach(link => {
            link.classList.remove('current-model');
            if (link.getAttribute('href') && currentPath.startsWith(link.getAttribute('href'))) {
                link.classList.add('current-model');
            }
        });
    }
    
    highlightCurrentSection();
    
    // Add search functionality
    const searchBox = document.createElement('input');
    searchBox.type = 'text';
    searchBox.placeholder = 'Search admin...';
    searchBox.style.cssText = `
        width: 100%;
        padding: 8px;
        margin: 10px 0;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    `;
    
    searchBox.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const modules = sidebar.querySelectorAll('.module');
        
        modules.forEach(module => {
            const text = module.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                module.style.display = 'block';
            } else {
                module.style.display = searchTerm ? 'none' : 'block';
            }
        });
    });
    
    // Add search box to sidebar
    const firstModule = sidebar.querySelector('.module');
    if (firstModule) {
        firstModule.parentNode.insertBefore(searchBox, firstModule);
    }
    
    // Add collapse functionality
    const modules = sidebar.querySelectorAll('.module');
    modules.forEach(module => {
        const header = module.querySelector('h2');
        if (header) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const list = module.querySelector('ul');
                if (list) {
                    const isHidden = list.style.display === 'none';
                    list.style.display = isHidden ? 'block' : 'none';
                    header.textContent = header.textContent.replace('▶', '▼').replace('▼', '▶');
                }
            });
        }
    });
});

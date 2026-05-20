// Main Application Controller
const App = {
    currentPage: 'dashboard',
    
    async init() {
        console.log('Initializing App...');
        await Auth.init();
        this.setupNavigation();
        this.setupUserMenu();
        
        // Load initial page based on URL hash or default to dashboard
        const hash = window.location.hash.slice(1);
        if (hash && ['dashboard', 'students', 'teachers', 'classes', 'attendance'].includes(hash)) {
            await this.navigateTo(hash);
        } else {
            await this.navigateTo('dashboard');
        }
    },
    
    setupNavigation() {
        // Setup main navigation links
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                await this.navigateTo(page);
                window.location.hash = page;
            });
        });
    },
    
    setupUserMenu() {
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');
        
        if (userMenuBtn) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('hidden');
            });
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            if (userDropdown) userDropdown.classList.add('hidden');
        });
        
        // Setup logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => Auth.logout());
        }
    },
    
    async navigateTo(page) {
        this.currentPage = page;
        
        // Update active nav link
        document.querySelectorAll('[data-page]').forEach(link => {
            if (link.dataset.page === page) {
                link.classList.add('text-purple-400');
                link.classList.remove('text-gray-300');
            } else {
                link.classList.remove('text-purple-400');
                link.classList.add('text-gray-300');
            }
        });
        
        // Show loading overlay
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) loadingOverlay.classList.remove('hidden');
        
        try {
            switch (page) {
                case 'dashboard':
                    if (typeof Dashboard !== 'undefined') {
                        await Dashboard.load();
                    } else {
                        console.error('Dashboard module not loaded');
                        this.showPlaceholder('Dashboard');
                    }
                    break;
                case 'students':
                    if (typeof Students !== 'undefined') {
                        await Students.load();
                    } else {
                        console.error('Students module not loaded');
                        this.showPlaceholder('Students Management');
                    }
                    break;
                case 'teachers':
                    if (typeof Teachers !== 'undefined') {
                        await Teachers.load();
                    } else {
                        console.error('Teachers module not loaded');
                        this.showPlaceholder('Teachers Management');
                    }
                    break;
                case 'classes':
                    if (typeof Classes !== 'undefined') {
                        await Classes.load();
                    } else {
                        console.error('Classes module not loaded');
                        this.showPlaceholder('Classes Management');
                    }
                    break;
                case 'attendance':
                    if (typeof Attendance !== 'undefined') {
                        await Attendance.load();
                    } else {
                        console.error('Attendance module not loaded');
                        this.showPlaceholder('Attendance Tracking');
                    }
                    break;
                default:
                    if (typeof Dashboard !== 'undefined') {
                        await Dashboard.load();
                    } else {
                        this.showPlaceholder('Dashboard');
                    }
            }
        } catch (error) {
            console.error('Error loading page:', error);
            Auth.showToast('Error loading page', 'error');
            this.showPlaceholder(page);
        } finally {
            // Hide loading overlay
            if (loadingOverlay) loadingOverlay.classList.add('hidden');
        }
    },
    
    showPlaceholder(page) {
        const content = document.getElementById('content');
        if (content) {
            content.innerHTML = `
                <div class="text-center py-20 animate-fade-up">
                    <i class="fas fa-school text-6xl text-purple-400 mb-4"></i>
                    <h2 class="text-3xl font-bold mb-2">${page.charAt(0).toUpperCase() + page.slice(1)}</h2>
                    <p class="text-gray-400">Content for ${page} will be displayed here.</p>
                    <p class="text-gray-500 text-sm mt-4">Please ensure all modules are properly loaded.</p>
                </div>
            `;
        }
    }
};

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM ready, initializing App...');
    App.init();
});

// Make App available globally
window.App = App;
// Main Application
const App = {
    currentUser: null,
    
    async init() {
        await this.checkAuth();
        this.setupEventListeners();
        if (window.UploadHandler) {
            UploadHandler.init();
        }
    },
    
    async checkAuth() {
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        
        console.log('Checking auth - token:', !!token, 'userStr:', !!userStr);
        
        if (token && userStr) {
            try {
                this.currentUser = JSON.parse(userStr);
                this.showUserMenu();
                
                // Load images only after confirming token works
                if (window.UploadHandler) {
                    try {
                        await UploadHandler.loadImages();
                        const myImagesSection = document.getElementById('myImagesSection');
                        if (myImagesSection) myImagesSection.classList.remove('hidden');
                    } catch (error) {
                        console.error('Error loading images:', error);
                        // If token is invalid, logout
                        if (error.message.includes('401')) {
                            this.logout();
                        }
                    }
                }
            } catch (e) {
                console.error('Error parsing user data:', e);
                this.logout();
            }
        } else {
            this.showAuthButtons();
        }
    },
    
    setupEventListeners() {
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const closeModal = document.getElementById('closeModal');
        const authModal = document.getElementById('authModal');
        
        if (loginBtn) loginBtn.addEventListener('click', () => this.showModal('login'));
        if (registerBtn) registerBtn.addEventListener('click', () => this.showModal('register'));
        if (logoutBtn) logoutBtn.addEventListener('click', () => this.logout());
        if (closeModal) closeModal.addEventListener('click', () => this.hideModal());
        
        if (authModal) {
            authModal.addEventListener('click', (e) => {
                if (e.target === authModal) this.hideModal();
            });
        }
    },
    
    showModal(type) {
        const modal = document.getElementById('authModal');
        const formsContainer = document.getElementById('authForms');
        
        if (!modal || !formsContainer) return;
        
        if (type === 'login') {
            formsContainer.innerHTML = `
                <h2 class="text-2xl font-bold mb-6 text-center">Welcome Back</h2>
                <form id="loginForm" class="space-y-4">
                    <div>
                        <input type="text" id="loginUsername" placeholder="Username" class="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-purple-500">
                    </div>
                    <div>
                        <input type="password" id="loginPassword" placeholder="Password" class="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-purple-500">
                    </div>
                    <button type="submit" class="w-full py-2 rounded-lg bg-purple-600 hover:bg-purple-700 transition">Login</button>
                </form>
                <p class="text-center mt-4 text-gray-400">
                    Don't have an account? 
                    <button onclick="App.showModal('register')" class="text-purple-400 hover:underline">Register</button>
                </p>
            `;
            
            const loginForm = document.getElementById('loginForm');
            if (loginForm) {
                loginForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const username = document.getElementById('loginUsername').value;
                    const password = document.getElementById('loginPassword').value;
                    await this.login(username, password);
                });
            }
        } else {
            formsContainer.innerHTML = `
                <h2 class="text-2xl font-bold mb-6 text-center">Create Account</h2>
                <form id="registerForm" class="space-y-4">
                    <div>
                        <input type="text" id="regUsername" placeholder="Username" class="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-purple-500">
                    </div>
                    <div>
                        <input type="email" id="regEmail" placeholder="Email" class="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-purple-500">
                    </div>
                    <div>
                        <input type="password" id="regPassword" placeholder="Password" class="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-purple-500">
                    </div>
                    <div>
                        <input type="password" id="regPassword2" placeholder="Confirm Password" class="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-purple-500">
                    </div>
                    <button type="submit" class="w-full py-2 rounded-lg bg-purple-600 hover:bg-purple-700 transition">Register</button>
                </form>
                <p class="text-center mt-4 text-gray-400">
                    Already have an account? 
                    <button onclick="App.showModal('login')" class="text-purple-400 hover:underline">Login</button>
                </p>
            `;
            
            const registerForm = document.getElementById('registerForm');
            if (registerForm) {
                registerForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const userData = {
                        username: document.getElementById('regUsername').value,
                        email: document.getElementById('regEmail').value,
                        password: document.getElementById('regPassword').value,
                        password2: document.getElementById('regPassword2').value
                    };
                    await this.register(userData);
                });
            }
        }
        
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    },
    
    hideModal() {
        const modal = document.getElementById('authModal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    },
    
    async login(username, password) {
        try {
            console.log('Attempting login...');
            const data = await api.login({ username, password });
            console.log('Login response:', data);
            
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify({ id: data.user_id, username: data.username }));
            this.currentUser = { id: data.user_id, username: data.username };
            this.showUserMenu();
            this.hideModal();
            
            if (window.UploadHandler) {
                window.UploadHandler.showToast('Login successful!', 'success');
                await UploadHandler.loadImages();
                const myImagesSection = document.getElementById('myImagesSection');
                if (myImagesSection) myImagesSection.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Login error:', error);
            if (window.UploadHandler) {
                window.UploadHandler.showToast(error.message, 'error');
            }
        }
    },
    
    async register(userData) {
        try {
            console.log('Attempting registration...');
            const data = await api.register(userData);
            console.log('Registration response:', data);
            
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            this.currentUser = data.user;
            this.showUserMenu();
            this.hideModal();
            
            if (window.UploadHandler) {
                window.UploadHandler.showToast('Registration successful!', 'success');
            }
        } catch (error) {
            console.error('Registration error:', error);
            if (window.UploadHandler) {
                window.UploadHandler.showToast(error.message, 'error');
            }
        }
    },
    
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.currentUser = null;
        this.showAuthButtons();
        
        if (window.UploadHandler) {
            window.UploadHandler.showToast('Logged out successfully', 'info');
        }
        
        const processingOptions = document.getElementById('processingOptions');
        const myImagesSection = document.getElementById('myImagesSection');
        const originalPreview = document.getElementById('originalPreview');
        const processedPreview = document.getElementById('processedPreview');
        
        if (processingOptions) processingOptions.classList.add('hidden');
        if (myImagesSection) myImagesSection.classList.add('hidden');
        if (originalPreview) originalPreview.src = '';
        if (processedPreview) processedPreview.src = '';
    },
    
    showUserMenu() {
        const authButtons = document.getElementById('authButtons');
        const userMenu = document.getElementById('userMenu');
        const usernameSpan = document.getElementById('username');
        
        if (authButtons) authButtons.classList.add('hidden');
        if (userMenu) userMenu.classList.remove('hidden');
        if (usernameSpan && this.currentUser) usernameSpan.textContent = this.currentUser.username;
    },
    
    showAuthButtons() {
        const authButtons = document.getElementById('authButtons');
        const userMenu = document.getElementById('userMenu');
        
        if (authButtons) authButtons.classList.remove('hidden');
        if (userMenu) userMenu.classList.add('hidden');
    }
};

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

window.App = App;
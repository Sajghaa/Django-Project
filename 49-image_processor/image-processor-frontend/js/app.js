const App = {
    currentUser: null,
    
    async init() {
        await this.checkAuth();
        this.setupEventListeners();
        UploadHandler.init();
    },
    
    async checkAuth() {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');
        
        if (token && user) {
            this.currentUser = JSON.parse(user);
            this.showUserMenu();
            await UploadHandler.loadImages();
            document.getElementById('myImagesSection').classList.remove('hidden');
        }
    },
    
    setupEventListeners() {
        document.getElementById('loginBtn').addEventListener('click', () => this.showModal('login'));
        document.getElementById('registerBtn').addEventListener('click', () => this.showModal('register'));
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
        document.getElementById('closeModal').addEventListener('click', () => this.hideModal());
        
        const modal = document.getElementById('authModal');
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.hideModal();
        });
    },
    
    showModal(type) {
        const modal = document.getElementById('authModal');
        const formsContainer = document.getElementById('authForms');
        
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
            
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('loginUsername').value;
                const password = document.getElementById('loginPassword').value;
                await this.login(username, password);
            });
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
            
            document.getElementById('registerForm').addEventListener('submit', async (e) => {
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
        
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    },
    
    hideModal() {
        const modal = document.getElementById('authModal');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    },
    
    async login(username, password) {
        try {
            const data = await api.login({ username, password });
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify({ id: data.user_id, username: data.username }));
            this.currentUser = { id: data.user_id, username: data.username };
            this.showUserMenu();
            this.hideModal();
            UploadHandler.showToast('Login successful!', 'success');
            await UploadHandler.loadImages();
            document.getElementById('myImagesSection').classList.remove('hidden');
        } catch (error) {
            UploadHandler.showToast(error.message, 'error');
        }
    },
    
    async register(userData) {
        try {
            const data = await api.register(userData);
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            this.currentUser = data.user;
            this.showUserMenu();
            this.hideModal();
            UploadHandler.showToast('Registration successful!', 'success');
        } catch (error) {
            UploadHandler.showToast(error.message, 'error');
        }
    },
    
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.currentUser = null;
        this.showAuthButtons();
        UploadHandler.showToast('Logged out successfully', 'info');
        document.getElementById('processingOptions').classList.add('hidden');
        document.getElementById('myImagesSection').classList.add('hidden');
        document.getElementById('originalPreview').src = '';
        document.getElementById('processedPreview').src = '';
    },
    
    showUserMenu() {
        document.getElementById('authButtons').classList.add('hidden');
        document.getElementById('userMenu').classList.remove('hidden');
        document.getElementById('username').textContent = this.currentUser?.username;
    },
    
    showAuthButtons() {
        document.getElementById('authButtons').classList.remove('hidden');
        document.getElementById('userMenu').classList.add('hidden');
    }
};

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

window.App = App;
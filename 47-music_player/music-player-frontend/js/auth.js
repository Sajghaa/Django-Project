// Auth Module
const Auth = {
    currentUser: null,
    
    init() {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');
        
        if (token && user) {
            this.currentUser = JSON.parse(user);
            this.updateUI();
            return true;
        }
        return false;
    },
    
    async login(username, password) {
        console.log('Attempting login...');
        try {
            const data = await api.login({ username, password });
            console.log('Login response:', data);
            
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify({ id: data.user_id, username: data.username }));
            this.currentUser = { id: data.user_id, username: data.username };
            this.updateUI();
            this.hideModal();
            showToast('Login successful! Welcome back!', 'success');
            
            // Reload the page content
            if (typeof loadHomePage === 'function') {
                await loadHomePage();
            } else if (window.Components) {
                await Components.renderHome();
            }
            return true;
        } catch (error) {
            console.error('Login error details:', error);
            let errorMsg = 'Login failed. Please check your credentials.';
            if (error.message) errorMsg = error.message;
            showToast(errorMsg, 'error');
            return false;
        }
    },
    
    async register(userData) {
        console.log('Attempting registration...');
        try {
            const data = await api.register(userData);
            console.log('Registration response:', data);
            
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            this.currentUser = data.user;
            this.updateUI();
            this.hideModal();
            showToast('Registration successful! Welcome!', 'success');
            
            if (window.Components) {
                await Components.renderHome();
            }
            return true;
        } catch (error) {
            console.error('Registration error details:', error);
            let errorMsg = 'Registration failed. Please try again.';
            if (error.message) errorMsg = error.message;
            showToast(errorMsg, 'error');
            return false;
        }
    },
    
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.currentUser = null;
        this.updateUI();
        showToast('Logged out successfully', 'info');
        if (window.Components) {
            Components.renderHome();
        }
    },
    
    updateUI() {
        const authButtons = document.getElementById('authButtons');
        const userMenu = document.getElementById('userMenu');
        const usernameSpan = document.getElementById('username');
        
        if (this.currentUser) {
            if (authButtons) authButtons.classList.add('hidden');
            if (userMenu) userMenu.classList.remove('hidden');
            if (usernameSpan) usernameSpan.textContent = this.currentUser.username;
        } else {
            if (authButtons) authButtons.classList.remove('hidden');
            if (userMenu) userMenu.classList.add('hidden');
        }
    },
    
    showModal(type = 'login') {
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
                    <button onclick="Auth.showModal('register')" class="text-purple-400 hover:underline">Register</button>
                </p>
            `;
            
            const loginForm = document.getElementById('loginForm');
            if (loginForm) {
                loginForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const username = document.getElementById('loginUsername').value;
                    const password = document.getElementById('loginPassword').value;
                    await Auth.login(username, password);
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
                    <button onclick="Auth.showModal('login')" class="text-purple-400 hover:underline">Login</button>
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
                    await Auth.register(userData);
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
    }
};

// Helper function for toast notifications
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    if (!toast || !toastMessage) return;
    
    const colors = {
        success: 'bg-green-600',
        error: 'bg-red-600',
        info: 'bg-blue-600'
    };
    
    toast.classList.remove('bg-green-600', 'bg-red-600', 'bg-blue-600');
    toast.classList.add(colors[type] || colors.info);
    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

window.Auth = Auth;
window.showToast = showToast;
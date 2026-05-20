const Auth = {
    currentUser: null,
    userType: null,
    
    async init() {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');
        const userType = localStorage.getItem('userType');
        
        if (token && user) {
            this.currentUser = JSON.parse(user);
            this.userType = userType;
            this.updateUI();
            await Dashboard.load();
            return true;
        }
        return false;
    },
    
    async login(username, password) {
        try {
            const data = await api.login({ username, password });
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify({ id: data.user_id, username: data.username }));
            localStorage.setItem('userType', data.user_type);
            
            this.currentUser = { id: data.user_id, username: data.username };
            this.userType = data.user_type;
            this.updateUI();
            this.hideModal();
            this.showToast('Login successful! Welcome back!', 'success');
            await Dashboard.load();
            return true;
        } catch (error) {
            this.showToast(error.message, 'error');
            return false;
        }
    },
    
    async register(userData) {
        try {
            const data = await api.register(userData);
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('userType', data.user_type);
            
            this.currentUser = data.user;
            this.userType = data.user_type;
            this.updateUI();
            this.hideModal();
            this.showToast('Registration successful!', 'success');
            return true;
        } catch (error) {
            this.showToast(error.message, 'error');
            return false;
        }
    },
    
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('userType');
        this.currentUser = null;
        this.userType = null;
        this.updateUI();
        this.showToast('Logged out successfully', 'info');
        document.getElementById('content').innerHTML = '<div class="text-center py-20"><i class="fas fa-school text-6xl text-purple-400 mb-4"></i><h2 class="text-3xl font-bold mb-2">Welcome to EduManager</h2><p class="text-gray-400">Please login to access the dashboard</p></div>';
    },
    
    updateUI() {
        const authButtons = document.getElementById('authButtons');
        const userMenu = document.getElementById('userMenu');
        const usernameSpan = document.getElementById('username');
        const navMenu = document.getElementById('navMenu');
        
        if (this.currentUser) {
            authButtons.classList.add('hidden');
            userMenu.classList.remove('hidden');
            navMenu.classList.remove('hidden');
            usernameSpan.textContent = this.currentUser.username;
            
            // Show/hide admin-only menu items based on user type
            const adminOnlyItems = document.querySelectorAll('.admin-only');
            if (this.userType === 'admin') {
                adminOnlyItems.forEach(el => el.classList.remove('hidden'));
            } else {
                adminOnlyItems.forEach(el => el.classList.add('hidden'));
            }
        } else {
            authButtons.classList.remove('hidden');
            userMenu.classList.add('hidden');
            navMenu.classList.add('hidden');
        }
    },
    
    showModal(type) {
        const modal = document.getElementById('authModal');
        const formsContainer = document.getElementById('authForms');
        
        if (type === 'login') {
            formsContainer.innerHTML = `
                <h2 class="text-2xl font-bold mb-6 text-center">Welcome Back</h2>
                <form id="loginForm" class="space-y-4">
                    <div>
                        <input type="text" id="loginUsername" placeholder="Username" class="w-full px-4 py-3 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                    </div>
                    <div>
                        <input type="password" id="loginPassword" placeholder="Password" class="w-full px-4 py-3 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                    </div>
                    <button type="submit" class="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition font-semibold">
                        Login
                    </button>
                </form>
                <p class="text-center mt-4 text-gray-400">
                    Don't have an account? 
                    <button onclick="Auth.showModal('register')" class="text-purple-400 hover:underline">Register</button>
                </p>
            `;
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('loginUsername').value;
                const password = document.getElementById('loginPassword').value;
                await Auth.login(username, password);
            });
        } else {
            formsContainer.innerHTML = `
                <h2 class="text-2xl font-bold mb-6 text-center">Create Account</h2>
                <form id="registerForm" class="space-y-4">
                    <div>
                        <input type="text" id="regUsername" placeholder="Username" class="w-full px-4 py-3 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                    </div>
                    <div>
                        <input type="email" id="regEmail" placeholder="Email" class="w-full px-4 py-3 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                    </div>
                    <div>
                        <input type="password" id="regPassword" placeholder="Password" class="w-full px-4 py-3 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                    </div>
                    <div>
                        <input type="password" id="regPassword2" placeholder="Confirm Password" class="w-full px-4 py-3 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                    </div>
                    <div>
                        <select id="regUserType" class="w-full px-4 py-3 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                            <option value="admin">Admin</option>
                            <option value="teacher">Teacher</option>
                            <option value="parent">Parent</option>
                        </select>
                    </div>
                    <button type="submit" class="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition font-semibold">
                        Register
                    </button>
                </form>
                <p class="text-center mt-4 text-gray-400">
                    Already have an account? 
                    <button onclick="Auth.showModal('login')" class="text-purple-400 hover:underline">Login</button>
                </p>
            `;
            document.getElementById('registerForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const userData = {
                    username: document.getElementById('regUsername').value,
                    email: document.getElementById('regEmail').value,
                    password: document.getElementById('regPassword').value,
                    password2: document.getElementById('regPassword2').value,
                    user_type: document.getElementById('regUserType').value
                };
                await Auth.register(userData);
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
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        const colors = {
            success: 'bg-green-600',
            error: 'bg-red-600',
            info: 'bg-blue-600'
        };
        toast.className = `fixed bottom-6 right-6 ${colors[type]} rounded-xl shadow-2xl px-5 py-3 z-50 animate-fade-up`;
        toastMessage.textContent = message;
        toast.classList.remove('hidden');
        setTimeout(() => toast.classList.add('hidden'), 3000);
    }
};

window.Auth = Auth;
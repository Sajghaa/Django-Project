const Dashboard = {
    async load() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6 animate-fade-up">
                <div>
                    <h1 class="text-3xl font-bold mb-2">Dashboard</h1>
                    <p class="text-gray-400">Welcome back, ${Auth.currentUser?.username}!</p>
                </div>
                
                <!-- Stats Cards -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" id="statsCards">
                    <div class="loader mx-auto col-span-full"></div>
                </div>
                
                <!-- Charts Row -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="bg-gray-800/50 rounded-2xl p-6">
                        <h3 class="text-lg font-semibold mb-4">Student Enrollment</h3>
                        <canvas id="enrollmentChart" height="200"></canvas>
                    </div>
                    <div class="bg-gray-800/50 rounded-2xl p-6">
                        <h3 class="text-lg font-semibold mb-4">Attendance Overview</h3>
                        <canvas id="attendanceChart" height="200"></canvas>
                    </div>
                </div>
                
                <!-- Recent Activity -->
                <div class="bg-gray-800/50 rounded-2xl p-6">
                    <h3 class="text-lg font-semibold mb-4">Recent Students</h3>
                    <div id="recentStudents" class="space-y-3">
                        <div class="loader mx-auto"></div>
                    </div>
                </div>
            </div>
        `;
        
        await this.loadStats();
        await this.loadCharts();
        await this.loadRecentStudents();
    },
    
    async loadStats() {
        try {
            const stats = {
                totalStudents: 156,
                totalTeachers: 24,
                totalClasses: 12,
                attendanceRate: 94
            };
            
            document.getElementById('statsCards').innerHTML = `
                <div class="bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl p-6 hover-lift">
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="text-purple-200 text-sm">Total Students</p>
                            <p class="text-3xl font-bold mt-1">${stats.totalStudents}</p>
                        </div>
                        <i class="fas fa-users text-3xl text-purple-200"></i>
                    </div>
                    <div class="mt-4">
                        <span class="text-xs text-purple-200">↑ 12% from last year</span>
                    </div>
                </div>
                <div class="bg-gradient-to-br from-pink-500 to-pink-700 rounded-2xl p-6 hover-lift">
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="text-pink-200 text-sm">Total Teachers</p>
                            <p class="text-3xl font-bold mt-1">${stats.totalTeachers}</p>
                        </div>
                        <i class="fas fa-chalkboard-user text-3xl text-pink-200"></i>
                    </div>
                </div>
                <div class="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 hover-lift">
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="text-blue-200 text-sm">Total Classes</p>
                            <p class="text-3xl font-bold mt-1">${stats.totalClasses}</p>
                        </div>
                        <i class="fas fa-school text-3xl text-blue-200"></i>
                    </div>
                </div>
                <div class="bg-gradient-to-br from-green-500 to-green-700 rounded-2xl p-6 hover-lift">
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="text-green-200 text-sm">Attendance Rate</p>
                            <p class="text-3xl font-bold mt-1">${stats.attendanceRate}%</p>
                        </div>
                        <i class="fas fa-calendar-check text-3xl text-green-200"></i>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    },
    
    async loadCharts() {
        const enrollmentCtx = document.getElementById('enrollmentChart')?.getContext('2d');
        if (enrollmentCtx) {
            new Chart(enrollmentCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'New Students',
                        data: [12, 19, 15, 17, 14, 23],
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: { responsive: true, maintainAspectRatio: true }
            });
        }
        
        const attendanceCtx = document.getElementById('attendanceChart')?.getContext('2d');
        if (attendanceCtx) {
            new Chart(attendanceCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Present', 'Absent', 'Late'],
                    datasets: [{
                        data: [85, 10, 5],
                        backgroundColor: ['#8b5cf6', '#ef4444', '#f59e0b']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: true }
            });
        }
    },
    
    async loadRecentStudents() {
        try {
            const students = [
                { name: 'John Doe', class: 'Class 5A', admission: '2024001' },
                { name: 'Jane Smith', class: 'Class 4B', admission: '2024002' },
                { name: 'Mike Johnson', class: 'Class 6A', admission: '2024003' }
            ];
            
            document.getElementById('recentStudents').innerHTML = students.map(s => `
                <div class="flex items-center justify-between p-4 bg-gray-700/30 rounded-xl hover:bg-gray-700/50 transition">
                    <div class="flex items-center space-x-4">
                        <div class="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                            <i class="fas fa-user text-white"></i>
                        </div>
                        <div>
                            <p class="font-medium">${s.name}</p>
                            <p class="text-sm text-gray-400">${s.class} • ${s.admission}</p>
                        </div>
                    </div>
                    <button class="text-purple-400 hover:text-purple-300 transition">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            `).join('');
        } catch (error) {
            document.getElementById('recentStudents').innerHTML = '<p class="text-gray-400 text-center">No recent students</p>';
        }
    }
};

window.Dashboard = Dashboard;
const Attendance = {
    selectedDate: new Date().toISOString().split('T')[0],
    selectedClass: '',
    
    async load() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6 animate-fade-up">
                <div>
                    <h1 class="text-3xl font-bold mb-2">Attendance</h1>
                    <p class="text-gray-400">Mark and track student attendance</p>
                </div>
                
                <div class="bg-gray-800/50 rounded-2xl p-6">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div>
                            <label class="block text-sm font-medium mb-2">Select Class</label>
                            <select id="classSelect" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                                <option value="">Select Class</option>
                                <option value="1">Class 1 - A</option>
                                <option value="2">Class 1 - B</option>
                                <option value="3">Class 2 - A</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Date</label>
                            <input type="date" id="dateSelect" value="${this.selectedDate}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                        </div>
                        <div class="flex items-end">
                            <button id="loadAttendanceBtn" class="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 transition w-full">
                                <i class="fas fa-search mr-2"></i>Load Students
                            </button>
                        </div>
                    </div>
                    
                    <div id="attendanceList" class="space-y-3">
                        <p class="text-center text-gray-400 py-8">Select a class and date to load attendance</p>
                    </div>
                    
                    <div id="attendanceActions" class="hidden mt-6 flex justify-end">
                        <button id="saveAttendanceBtn" class="px-6 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition">
                            <i class="fas fa-save mr-2"></i>Save Attendance
                        </button>
                    </div>
                </div>
                
                <div class="bg-gray-800/50 rounded-2xl p-6">
                    <h3 class="text-lg font-semibold mb-4">Attendance Statistics</h3>
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4" id="attendanceStats">
                        <div class="text-center p-4 bg-gray-700/30 rounded-xl">
                            <p class="text-2xl font-bold text-green-400" id="presentCount">0</p>
                            <p class="text-sm text-gray-400">Present</p>
                        </div>
                        <div class="text-center p-4 bg-gray-700/30 rounded-xl">
                            <p class="text-2xl font-bold text-red-400" id="absentCount">0</p>
                            <p class="text-sm text-gray-400">Absent</p>
                        </div>
                        <div class="text-center p-4 bg-gray-700/30 rounded-xl">
                            <p class="text-2xl font-bold text-yellow-400" id="lateCount">0</p>
                            <p class="text-sm text-gray-400">Late</p>
                        </div>
                        <div class="text-center p-4 bg-gray-700/30 rounded-xl">
                            <p class="text-2xl font-bold text-blue-400" id="totalCount">0</p>
                            <p class="text-sm text-gray-400">Total</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('loadAttendanceBtn').addEventListener('click', () => this.loadStudents());
        document.getElementById('saveAttendanceBtn')?.addEventListener('click', () => this.saveAttendance());
        document.getElementById('classSelect').addEventListener('change', (e) => {
            this.selectedClass = e.target.value;
        });
        document.getElementById('dateSelect').addEventListener('change', (e) => {
            this.selectedDate = e.target.value;
        });
    },
    
    async loadStudents() {
        if (!this.selectedClass) {
            Auth.showToast('Please select a class', 'error');
            return;
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay.classList.remove('hidden');
        
        try {
            const students = [
                { id: 1, admission_number: '20240001', name: 'John Doe', roll_number: 1, status: 'present' },
                { id: 2, admission_number: '20240002', name: 'Jane Smith', roll_number: 2, status: 'present' },
                { id: 3, admission_number: '20240003', name: 'Mike Johnson', roll_number: 3, status: 'absent' }
            ];
            
            const container = document.getElementById('attendanceList');
            container.innerHTML = `
                <div class="bg-gray-700/30 rounded-xl overflow-hidden">
                    <table class="w-full">
                        <thead class="bg-gray-700/50">
                            <tr>
                                <th class="px-4 py-3 text-left">Roll No</th>
                                <th class="px-4 py-3 text-left">Admission No</th>
                                <th class="px-4 py-3 text-left">Student Name</th>
                                <th class="px-4 py-3 text-left">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${students.map(student => `
                                <tr class="border-t border-gray-700">
                                    <td class="px-4 py-3">${student.roll_number}</td>
                                    <td class="px-4 py-3">${student.admission_number}</td>
                                    <td class="px-4 py-3">${student.name}</td>
                                    <td class="px-4 py-3">
                                        <select data-student-id="${student.id}" class="attendance-status px-3 py-1 rounded-lg bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none">
                                            <option value="present" ${student.status === 'present' ? 'selected' : ''}>Present</option>
                                            <option value="absent" ${student.status === 'absent' ? 'selected' : ''}>Absent</option>
                                            <option value="late" ${student.status === 'late' ? 'selected' : ''}>Late</option>
                                        </select>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            
            document.getElementById('attendanceActions').classList.remove('hidden');
            this.updateStats();
            
        } catch (error) {
            Auth.showToast('Error loading students', 'error');
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    },
    
    updateStats() {
        const statuses = document.querySelectorAll('.attendance-status');
        let present = 0, absent = 0, late = 0;
        
        statuses.forEach(select => {
            const value = select.value;
            if (value === 'present') present++;
            else if (value === 'absent') absent++;
            else if (value === 'late') late++;
        });
        
        document.getElementById('presentCount').textContent = present;
        document.getElementById('absentCount').textContent = absent;
        document.getElementById('lateCount').textContent = late;
        document.getElementById('totalCount').textContent = statuses.length;
    },
    
    saveAttendance() {
        const attendanceData = [];
        document.querySelectorAll('.attendance-status').forEach(select => {
            attendanceData.push({
                student_id: select.dataset.studentId,
                status: select.value
            });
        });
        
        Auth.showToast('Attendance saved successfully!', 'success');
        console.log('Attendance data:', attendanceData);
    }
};

window.Attendance = Attendance;
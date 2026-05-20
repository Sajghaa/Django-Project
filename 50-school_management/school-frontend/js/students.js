const Students = {
    async load() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6 animate-fade-up">
                <div class="flex justify-between items-center">
                    <div>
                        <h1 class="text-3xl font-bold mb-2">Students</h1>
                        <p class="text-gray-400">Manage all student records</p>
                    </div>
                    <button id="addStudentBtn" class="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition shadow-lg">
                        <i class="fas fa-plus mr-2"></i>Add Student
                    </button>
                </div>
                
                <!-- Search & Filter -->
                <div class="bg-gray-800/50 rounded-2xl p-4">
                    <div class="flex gap-4">
                        <div class="flex-1">
                            <input type="text" id="searchInput" placeholder="Search by name, admission number..." class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                        </div>
                        <select id="classFilter" class="px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none transition">
                            <option value="">All Classes</option>
                            <option value="1">Class 1</option>
                            <option value="2">Class 2</option>
                            <option value="3">Class 3</option>
                            <option value="4">Class 4</option>
                            <option value="5">Class 5</option>
                        </select>
                        <button id="searchBtn" class="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 transition">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Students Table -->
                <div class="bg-gray-800/50 rounded-2xl overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-gray-700/50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Admission No</th>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Student Name</th>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Class</th>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Roll No</th>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Phone</th>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="studentsTableBody">
                                <tr><td colspan="6" class="text-center py-8"><div class="loader mx-auto"></div></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Pagination -->
                <div id="pagination" class="flex justify-center space-x-2"></div>
            </div>
        `;
        
        await this.loadStudents();
        
        document.getElementById('addStudentBtn').addEventListener('click', () => this.showStudentModal());
        document.getElementById('searchBtn').addEventListener('click', () => this.loadStudents());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.loadStudents();
        });
    },
    
    async loadStudents(page = 1) {
        const search = document.getElementById('searchInput')?.value || '';
        const classFilter = document.getElementById('classFilter')?.value || '';
        
        try {
            const students = [
                { id: 1, admission_number: '20240001', first_name: 'John', last_name: 'Doe', class_name: 'Class 1', class_section: 'A', roll_number: 1, phone: '9876543210' },
                { id: 2, admission_number: '20240002', first_name: 'Jane', last_name: 'Smith', class_name: 'Class 1', class_section: 'A', roll_number: 2, phone: '9876543211' },
                { id: 3, admission_number: '20240003', first_name: 'Mike', last_name: 'Johnson', class_name: 'Class 2', class_section: 'A', roll_number: 1, phone: '9876543212' }
            ];
            
            const filtered = students.filter(s => 
                (!search || `${s.first_name} ${s.last_name}`.toLowerCase().includes(search.toLowerCase()) || s.admission_number.includes(search)) &&
                (!classFilter || s.class_name === `Class ${classFilter}`)
            );
            
            const tbody = document.getElementById('studentsTableBody');
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center py-8 text-gray-400">No students found</td></tr>';
                return;
            }
            
            tbody.innerHTML = filtered.map(student => `
                <tr class="border-t border-gray-700 hover:bg-gray-700/30 transition">
                    <td class="px-6 py-4">${student.admission_number}</td>
                    <td class="px-6 py-4 font-medium">${student.first_name} ${student.last_name}</td>
                    <td class="px-6 py-4">${student.class_name}${student.class_section}</td>
                    <td class="px-6 py-4">${student.roll_number}</td>
                    <td class="px-6 py-4">${student.phone}</td>
                    <td class="px-6 py-4">
                        <div class="flex space-x-2">
                            <button onclick="Students.viewStudent(${student.id})" class="text-blue-400 hover:text-blue-300">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button onclick="Students.editStudent(${student.id})" class="text-yellow-400 hover:text-yellow-300">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="Students.deleteStudent(${student.id})" class="text-red-400 hover:text-red-300">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            Auth.showToast('Error loading students', 'error');
        }
    },
    
    showStudentModal(student = null) {
        const isEdit = !!student;
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-gray-800 rounded-2xl w-full max-w-2xl p-6 relative animate-fade-up max-h-[90vh] overflow-y-auto">
                <button onclick="this.closest('.fixed').remove()" class="absolute top-4 right-4 text-gray-400 hover:text-white transition">
                    <i class="fas fa-times text-xl"></i>
                </button>
                <h2 class="text-2xl font-bold mb-6">${isEdit ? 'Edit Student' : 'Add New Student'}</h2>
                <form id="studentForm" class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div><input type="text" name="first_name" placeholder="First Name" value="${student?.first_name || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none" required></div>
                        <div><input type="text" name="last_name" placeholder="Last Name" value="${student?.last_name || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none" required></div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div><input type="date" name="date_of_birth" placeholder="Date of Birth" value="${student?.date_of_birth || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none" required></div>
                        <div>
                            <select name="gender" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none" required>
                                <option value="">Select Gender</option>
                                <option value="M" ${student?.gender === 'M' ? 'selected' : ''}>Male</option>
                                <option value="F" ${student?.gender === 'F' ? 'selected' : ''}>Female</option>
                            </select>
                        </div>
                    </div>
                    <div><textarea name="address" placeholder="Address" rows="2" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none">${student?.address || ''}</textarea></div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div><input type="text" name="phone" placeholder="Phone" value="${student?.phone || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                        <div><input type="email" name="email" placeholder="Email" value="${student?.email || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <select name="class_id" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none" required>
                                <option value="">Select Class</option>
                                <option value="1" ${student?.class_id === 1 ? 'selected' : ''}>Class 1</option>
                                <option value="2" ${student?.class_id === 2 ? 'selected' : ''}>Class 2</option>
                                <option value="3" ${student?.class_id === 3 ? 'selected' : ''}>Class 3</option>
                            </select>
                        </div>
                        <div><input type="number" name="roll_number" placeholder="Roll Number" value="${student?.roll_number || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    </div>
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" onclick="this.closest('.fixed').remove()" class="px-5 py-2 rounded-xl bg-gray-700 hover:bg-gray-600 transition">Cancel</button>
                        <button type="submit" class="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition">${isEdit ? 'Update' : 'Add'} Student</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        
        document.getElementById('studentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            // Here you would call API to save student
            Auth.showToast(isEdit ? 'Student updated!' : 'Student added!', 'success');
            modal.remove();
            await this.loadStudents();
        });
    },
    
    viewStudent(id) {
        Auth.showToast('View student details - Coming soon', 'info');
    },
    
    editStudent(id) {
        const student = { id: 1, first_name: 'John', last_name: 'Doe', class_id: 1, roll_number: 1 };
        this.showStudentModal(student);
    },
    
    async deleteStudent(id) {
        if (confirm('Are you sure you want to delete this student?')) {
            Auth.showToast('Student deleted!', 'success');
            await this.loadStudents();
        }
    }
};

window.Students = Students;
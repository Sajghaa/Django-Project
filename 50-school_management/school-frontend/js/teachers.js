const Teachers = {
    async load() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6 animate-fade-up">
                <div class="flex justify-between items-center">
                    <div>
                        <h1 class="text-3xl font-bold mb-2">Teachers</h1>
                        <p class="text-gray-400">Manage teaching staff</p>
                    </div>
                    <button id="addTeacherBtn" class="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition shadow-lg">
                        <i class="fas fa-plus mr-2"></i>Add Teacher
                    </button>
                </div>
                
                <div class="bg-gray-800/50 rounded-2xl overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-gray-700/50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Employee ID</th>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Teacher Name</th>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Qualification</th>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Phone</th>
                                    <th class="px-6 py-3 text-left text-sm font-semibold">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="teachersTableBody">
                                <tr><td colspan="5" class="text-center py-8"><div class="loader mx-auto"></div></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        await this.loadTeachers();
        document.getElementById('addTeacherBtn').addEventListener('click', () => this.showTeacherModal());
    },
    
    async loadTeachers() {
        try {
            const teachers = [
                { id: 1, employee_id: 'TCH2024001', first_name: 'Sarah', last_name: 'Johnson', qualification: 'M.Sc. Mathematics', phone: '9876543210' },
                { id: 2, employee_id: 'TCH2024002', first_name: 'Michael', last_name: 'Brown', qualification: 'M.A. English', phone: '9876543211' }
            ];
            
            const tbody = document.getElementById('teachersTableBody');
            tbody.innerHTML = teachers.map(teacher => `
                <tr class="border-t border-gray-700 hover:bg-gray-700/30 transition">
                    <td class="px-6 py-4">${teacher.employee_id}</td>
                    <td class="px-6 py-4 font-medium">${teacher.first_name} ${teacher.last_name}</td>
                    <td class="px-6 py-4">${teacher.qualification}</td>
                    <td class="px-6 py-4">${teacher.phone}</td>
                    <td class="px-6 py-4">
                        <div class="flex space-x-2">
                            <button onclick="Teachers.editTeacher(${teacher.id})" class="text-yellow-400 hover:text-yellow-300">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="Teachers.deleteTeacher(${teacher.id})" class="text-red-400 hover:text-red-300">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            Auth.showToast('Error loading teachers', 'error');
        }
    },
    
    showTeacherModal(teacher = null) {
        const isEdit = !!teacher;
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-gray-800 rounded-2xl w-full max-w-md p-6 relative animate-fade-up">
                <button onclick="this.closest('.fixed').remove()" class="absolute top-4 right-4 text-gray-400 hover:text-white transition">
                    <i class="fas fa-times text-xl"></i>
                </button>
                <h2 class="text-2xl font-bold mb-6">${isEdit ? 'Edit Teacher' : 'Add New Teacher'}</h2>
                <form id="teacherForm" class="space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div><input type="text" name="first_name" placeholder="First Name" value="${teacher?.first_name || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none" required></div>
                        <div><input type="text" name="last_name" placeholder="Last Name" value="${teacher?.last_name || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none" required></div>
                    </div>
                    <div><input type="text" name="qualification" placeholder="Qualification" value="${teacher?.qualification || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    <div><input type="text" name="specialization" placeholder="Specialization" value="${teacher?.specialization || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    <div><input type="date" name="joining_date" placeholder="Joining Date" value="${teacher?.joining_date || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    <div><input type="text" name="phone" placeholder="Phone" value="${teacher?.phone || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    <div><input type="email" name="email" placeholder="Email" value="${teacher?.email || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    <div><textarea name="address" placeholder="Address" rows="2" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none">${teacher?.address || ''}</textarea></div>
                    <div><input type="number" name="salary" placeholder="Salary" value="${teacher?.salary || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" onclick="this.closest('.fixed').remove()" class="px-5 py-2 rounded-xl bg-gray-700 hover:bg-gray-600 transition">Cancel</button>
                        <button type="submit" class="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition">${isEdit ? 'Update' : 'Add'} Teacher</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        
        document.getElementById('teacherForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            Auth.showToast(isEdit ? 'Teacher updated!' : 'Teacher added!', 'success');
            modal.remove();
            await this.loadTeachers();
        });
    },
    
    editTeacher(id) {
        const teacher = { id: 1, first_name: 'Sarah', last_name: 'Johnson', qualification: 'M.Sc. Mathematics' };
        this.showTeacherModal(teacher);
    },
    
    async deleteTeacher(id) {
        if (confirm('Are you sure you want to delete this teacher?')) {
            Auth.showToast('Teacher deleted!', 'success');
            await this.loadTeachers();
        }
    }
};

window.Teachers = Teachers;
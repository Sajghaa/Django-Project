const Classes = {
    async load() {
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="space-y-6 animate-fade-up">
                <div class="flex justify-between items-center">
                    <div>
                        <h1 class="text-3xl font-bold mb-2">Classes</h1>
                        <p class="text-gray-400">Manage classes, subjects, and timetable</p>
                    </div>
                    <button id="addClassBtn" class="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition shadow-lg">
                        <i class="fas fa-plus mr-2"></i>Add Class
                    </button>
                </div>
                
                <!-- Classes Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="classesGrid">
                    <div class="loader mx-auto col-span-full"></div>
                </div>
                
                <!-- Selected Class Details -->
                <div id="classDetails" class="hidden bg-gray-800/50 rounded-2xl p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-xl font-semibold" id="selectedClassName"></h3>
                        <button id="closeDetails" class="text-gray-400 hover:text-white">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div>
                            <h4 class="font-semibold mb-3">Students</h4>
                            <div id="classStudents" class="space-y-2 max-h-96 overflow-y-auto"></div>
                        </div>
                        <div>
                            <h4 class="font-semibold mb-3">Subjects</h4>
                            <div id="classSubjects" class="space-y-2 max-h-96 overflow-y-auto"></div>
                        </div>
                    </div>
                    <div class="mt-6">
                        <h4 class="font-semibold mb-3">Timetable</h4>
                        <div id="classTimetable" class="overflow-x-auto"></div>
                    </div>
                </div>
            </div>
        `;
        
        await this.loadClasses();
        
        document.getElementById('addClassBtn').addEventListener('click', () => this.showClassModal());
        document.getElementById('closeDetails')?.addEventListener('click', () => {
            document.getElementById('classDetails').classList.add('hidden');
        });
    },
    
    async loadClasses() {
        try {
            const classes = [
                { id: 1, name: 'Class 1', section: 'A', class_teacher_name: 'Sarah Johnson', student_count: 28 },
                { id: 2, name: 'Class 1', section: 'B', class_teacher_name: 'Michael Brown', student_count: 25 },
                { id: 3, name: 'Class 2', section: 'A', class_teacher_name: 'Emily Davis', student_count: 30 },
                { id: 4, name: 'Class 3', section: 'A', class_teacher_name: 'David Wilson', student_count: 27 },
                { id: 5, name: 'Class 4', section: 'A', class_teacher_name: 'Lisa Anderson', student_count: 32 },
                { id: 6, name: 'Class 5', section: 'A', class_teacher_name: 'Robert Taylor', student_count: 29 }
            ];
            
            const grid = document.getElementById('classesGrid');
            grid.innerHTML = classes.map(cls => `
                <div class="bg-gray-800/50 rounded-2xl p-6 hover-lift cursor-pointer" onclick="Classes.viewClass(${cls.id})">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h3 class="text-xl font-bold">${cls.name}${cls.section}</h3>
                            <p class="text-gray-400 text-sm">Class Teacher: ${cls.class_teacher_name}</p>
                        </div>
                        <div class="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <i class="fas fa-users text-white"></i>
                        </div>
                    </div>
                    <div class="flex justify-between items-center">
                        <div>
                            <p class="text-2xl font-bold">${cls.student_count}</p>
                            <p class="text-xs text-gray-400">Students</p>
                        </div>
                        <button class="text-purple-400 hover:text-purple-300" onclick="event.stopPropagation();Classes.editClass(${cls.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            Auth.showToast('Error loading classes', 'error');
        }
    },
    
    async viewClass(classId) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay.classList.remove('hidden');
        
        try {
            const classData = { id: classId, name: 'Class 1', section: 'A' };
            document.getElementById('selectedClassName').textContent = `${classData.name}${classData.section} - Details`;
            
            const students = [
                { id: 1, name: 'John Doe', roll_number: 1 },
                { id: 2, name: 'Jane Smith', roll_number: 2 },
                { id: 3, name: 'Mike Johnson', roll_number: 3 }
            ];
            
            document.getElementById('classStudents').innerHTML = students.map(s => `
                <div class="flex justify-between items-center p-2 bg-gray-700/30 rounded-lg">
                    <span>${s.name}</span>
                    <span class="text-sm text-gray-400">Roll: ${s.roll_number}</span>
                </div>
            `).join('');
            
            const subjects = [
                { id: 1, name: 'Mathematics', code: 'MATH101', teacher: 'Sarah Johnson' },
                { id: 2, name: 'Science', code: 'SCI101', teacher: 'Michael Brown' },
                { id: 3, name: 'English', code: 'ENG101', teacher: 'Emily Davis' }
            ];
            
            document.getElementById('classSubjects').innerHTML = subjects.map(s => `
                <div class="p-2 bg-gray-700/30 rounded-lg">
                    <div class="font-medium">${s.name}</div>
                    <div class="text-xs text-gray-400">${s.code} • ${s.teacher}</div>
                </div>
            `).join('');
            
            const timetable = [
                { day: 'Monday', subject: 'Mathematics', time: '9:00 AM - 10:00 AM', teacher: 'Sarah Johnson', room: '101' },
                { day: 'Monday', subject: 'Science', time: '10:00 AM - 11:00 AM', teacher: 'Michael Brown', room: '102' },
                { day: 'Tuesday', subject: 'English', time: '9:00 AM - 10:00 AM', teacher: 'Emily Davis', room: '103' }
            ];
            
            const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
            document.getElementById('classTimetable').innerHTML = `
                <table class="w-full">
                    <thead class="bg-gray-700/50">
                        <tr>
                            <th class="px-3 py-2 text-left">Day</th>
                            <th class="px-3 py-2 text-left">Subject</th>
                            <th class="px-3 py-2 text-left">Time</th>
                            <th class="px-3 py-2 text-left">Teacher</th>
                            <th class="px-3 py-2 text-left">Room</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${timetable.map(t => `
                            <tr class="border-t border-gray-700">
                                <td class="px-3 py-2">${t.day}</td>
                                <td class="px-3 py-2">${t.subject}</td>
                                <td class="px-3 py-2">${t.time}</td>
                                <td class="px-3 py-2">${t.teacher}</td>
                                <td class="px-3 py-2">${t.room}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            
            document.getElementById('classDetails').classList.remove('hidden');
        } catch (error) {
            Auth.showToast('Error loading class details', 'error');
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    },
    
    showClassModal(classData = null) {
        const isEdit = !!classData;
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-gray-800 rounded-2xl w-full max-w-md p-6 relative animate-fade-up">
                <button onclick="this.closest('.fixed').remove()" class="absolute top-4 right-4 text-gray-400 hover:text-white transition">
                    <i class="fas fa-times text-xl"></i>
                </button>
                <h2 class="text-2xl font-bold mb-6">${isEdit ? 'Edit Class' : 'Add New Class'}</h2>
                <form id="classForm" class="space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div><input type="text" name="name" placeholder="Class Name" value="${classData?.name || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none" required></div>
                        <div><input type="text" name="section" placeholder="Section" value="${classData?.section || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    </div>
                    <div><input type="text" name="room_number" placeholder="Room Number" value="${classData?.room_number || ''}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    <div><input type="number" name="capacity" placeholder="Capacity" value="${classData?.capacity || 30}" class="w-full px-4 py-2 rounded-xl bg-gray-700 border border-gray-600 focus:border-purple-500 focus:outline-none"></div>
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" onclick="this.closest('.fixed').remove()" class="px-5 py-2 rounded-xl bg-gray-700 hover:bg-gray-600 transition">Cancel</button>
                        <button type="submit" class="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition">${isEdit ? 'Update' : 'Add'} Class</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        
        document.getElementById('classForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            Auth.showToast(isEdit ? 'Class updated!' : 'Class added!', 'success');
            modal.remove();
            await this.loadClasses();
        });
    },
    
    editClass(id) {
        const classData = { id: 1, name: 'Class 1', section: 'A', room_number: '101', capacity: 30 };
        this.showClassModal(classData);
    }
};

window.Classes = Classes;
// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';

async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Accept': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Token ${token}`;
    }
    
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || error.message || `HTTP ${response.status}`);
        }
        
        if (response.status === 204) return {};
        return response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth endpoints
const register = (userData) => apiCall('/auth/register/', {
    method: 'POST',
    body: JSON.stringify(userData)
});

const login = (credentials) => apiCall('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(credentials)
});

// Dashboard
const getDashboardStats = () => apiCall('/dashboard/stats/');

// Students
const getStudents = (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiCall(`/students/${query ? `?${query}` : ''}`);
};
const getStudent = (id) => apiCall(`/students/${id}/`);
const createStudent = (data) => apiCall('/students/', {
    method: 'POST',
    body: JSON.stringify(data)
});
const updateStudent = (id, data) => apiCall(`/students/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data)
});
const deleteStudent = (id) => apiCall(`/students/${id}/`, { method: 'DELETE' });
const getStudentAttendance = (id) => apiCall(`/students/${id}/attendance/`);
const getStudentGrades = (id) => apiCall(`/students/${id}/grades/`);
const getStudentReportCard = (id, examId) => apiCall(`/students/${id}/report_card/?exam=${examId}`);

// Teachers
const getTeachers = () => apiCall('/teachers/');
const createTeacher = (data) => apiCall('/teachers/', {
    method: 'POST',
    body: JSON.stringify(data)
});

// Classes
const getClasses = () => apiCall('/classes/');
const getClassStudents = (id) => apiCall(`/classes/${id}/students/`);
const getClassSubjects = (id) => apiCall(`/classes/${id}/subjects/`);
const getClassTimetable = (id) => apiCall(`/classes/${id}/timetable/`);

// Attendance
const markAttendance = (data) => apiCall('/attendance/mark/', {
    method: 'POST',
    body: JSON.stringify(data)
});
const getAttendance = (params) => {
    const query = new URLSearchParams(params).toString();
    return apiCall(`/attendance/${query ? `?${query}` : ''}`);
};

// Grades
const enterMarks = (data) => apiCall('/grades/enter_marks/', {
    method: 'POST',
    body: JSON.stringify(data)
});
const getExams = () => apiCall('/exams/');

window.api = {
    register,
    login,
    getDashboardStats,
    getStudents,
    getStudent,
    createStudent,
    updateStudent,
    deleteStudent,
    getStudentAttendance,
    getStudentGrades,
    getStudentReportCard,
    getTeachers,
    createTeacher,
    getClasses,
    getClassStudents,
    getClassSubjects,
    getClassTimetable,
    markAttendance,
    getAttendance,
    enterMarks,
    getExams
};
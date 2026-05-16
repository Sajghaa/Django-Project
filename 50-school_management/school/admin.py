from django.contrib import admin
from .models import (
    Class, Student, Parent, Teacher, Subject, Timetable,
    Attendance, Exam, Grade, FeeStructure, FeePayment
)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'class_teacher', 'room_number', 'capacity']
    list_filter = ['name', 'section']
    search_fields = ['name', 'section']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'full_name', 'class_assigned', 'roll_number', 'status']
    list_filter = ['class_assigned', 'status', 'gender']
    search_fields = ['admission_number', 'first_name', 'last_name', 'phone']

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['student', 'father_name', 'mother_name', 'guardian_name']
    search_fields = ['father_name', 'mother_name']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'qualification', 'status']
    list_filter = ['status', 'gender']
    search_fields = ['employee_id', 'first_name', 'last_name']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'class_assigned', 'teacher']
    list_filter = ['class_assigned', 'is_elective']
    search_fields = ['name', 'code']

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['class_assigned', 'subject', 'teacher', 'day_of_week', 'start_time']
    list_filter = ['class_assigned', 'day_of_week']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'marked_by']
    list_filter = ['date', 'status']
    search_fields = ['student__first_name', 'student__last_name']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_assigned', 'term', 'exam_date', 'year']
    list_filter = ['class_assigned', 'term', 'year']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam', 'total_marks', 'percentage', 'grade']
    list_filter = ['exam', 'subject']
    search_fields = ['student__first_name', 'student__last_name']

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['class_assigned', 'fee_type', 'amount', 'due_date']
    list_filter = ['class_assigned', 'fee_type']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'student', 'fee_type', 'amount', 'payment_date', 'status']
    list_filter = ['status', 'payment_method']
    search_fields = ['receipt_number', 'student__first_name', 'student__last_name']
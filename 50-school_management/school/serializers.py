from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Class, Student, Parent, Teacher, Subject, Timetable,
    Attendance, Exam, Grade, FeeStructure, FeePayment
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=['admin', 'teacher', 'parent'])

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        return data

class ClassSerializer(serializers.ModelSerializer):
    class_teacher_name = serializers.CharField(source='class_teacher.full_name', read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'section', 'class_teacher', 'class_teacher_name', 
                  'room_number', 'capacity', 'student_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_student_count(self, obj):
        return obj.students.count()

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)
    class_section = serializers.CharField(source='class_assigned.section', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'admission_number', 'first_name', 'last_name', 'full_name',
                  'date_of_birth', 'gender', 'blood_group', 'address', 'phone', 'email',
                  'class_assigned', 'class_name', 'class_section', 'roll_number',
                  'joining_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'admission_number', 'created_at', 'updated_at']

class ParentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = Parent
        fields = ['id', 'student', 'student_name', 'father_name', 'father_phone', 'father_email',
                  'mother_name', 'mother_phone', 'mother_email', 'guardian_name', 
                  'guardian_phone', 'address']
        read_only_fields = ['id']

class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'employee_id', 'first_name', 'last_name', 'full_name',
                  'date_of_birth', 'gender', 'qualification', 'specialization',
                  'joining_date', 'phone', 'email', 'address', 'salary', 'status',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'employee_id', 'created_at', 'updated_at']

class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'class_assigned', 'class_name', 'teacher', 'teacher_name',
                  'theory_marks', 'practical_marks', 'is_elective', 'created_at']
        read_only_fields = ['id', 'created_at']

class TimetableSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Timetable
        fields = ['id', 'class_assigned', 'class_name', 'subject', 'subject_name',
                  'teacher', 'teacher_name', 'day_of_week', 'day_name', 'start_time',
                  'end_time', 'room_number']
        read_only_fields = ['id']
    
    def get_day_name(self, obj):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[obj.day_of_week - 1] if 1 <= obj.day_of_week <= 7 else ''

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'class_assigned', 'date', 
                  'status', 'remarks', 'marked_by', 'marked_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']

class ExamSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)
    
    class Meta:
        model = Exam
        fields = ['id', 'name', 'class_assigned', 'class_name', 'term', 'exam_date', 'year', 'created_at']
        read_only_fields = ['id', 'created_at']

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    
    class Meta:
        model = Grade
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'exam', 'exam_name',
                  'theory_marks', 'practical_marks', 'total_marks', 'percentage', 'grade', 'remarks',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'total_marks', 'percentage', 'grade', 'created_at', 'updated_at']

class FeeStructureSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = ['id', 'class_assigned', 'class_name', 'fee_type', 'amount', 'due_date', 'created_at']
        read_only_fields = ['id', 'created_at']

class FeePaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = FeePayment
        fields = ['id', 'student', 'student_name', 'fee_type', 'amount', 'payment_date',
                  'receipt_number', 'payment_method', 'transaction_id', 'status', 'remarks', 'created_at']
        read_only_fields = ['id', 'receipt_number', 'created_at']
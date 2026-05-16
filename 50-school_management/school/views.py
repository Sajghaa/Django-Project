from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    Class, Student, Parent, Teacher, Subject, Timetable,
    Attendance, Exam, Grade, FeeStructure, FeePayment
)
from .serializers import (
    UserSerializer, RegisterSerializer, ClassSerializer, StudentSerializer,
    ParentSerializer, TeacherSerializer, SubjectSerializer, TimetableSerializer,
    AttendanceSerializer, ExamSerializer, GradeSerializer, FeeStructureSerializer, FeePaymentSerializer
)
from .permissions import IsAdminUser, IsTeacherUser, IsParentUser
from .pagination import CustomPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        user_type = serializer.validated_data['user_type']
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'user_type': user_type
        }, status=status.HTTP_201_CREATED)

class CustomAuthToken(ObtainAuthToken):
    """Custom auth token endpoint"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        user_type = 'admin'
        if hasattr(user, 'teacher'):
            user_type = 'teacher'
        elif hasattr(user, 'parent'):
            user_type = 'parent'
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'user_type': user_type
        })

class ClassViewSet(viewsets.ModelViewSet):
    """ViewSet for classes"""
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'section']
    ordering_fields = ['name', 'section', 'created_at']
    ordering = ['name', 'section']
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get all students in this class"""
        class_obj = self.get_object()
        students = Student.objects.filter(class_assigned=class_obj)
        page = self.paginate_queryset(students)
        serializer = StudentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """Get all subjects for this class"""
        class_obj = self.get_object()
        subjects = Subject.objects.filter(class_assigned=class_obj)
        page = self.paginate_queryset(subjects)
        serializer = SubjectSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def timetable(self, request, pk=None):
        """Get timetable for this class"""
        class_obj = self.get_object()
        timetable = Timetable.objects.filter(class_assigned=class_obj)
        serializer = TimetableSerializer(timetable, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet for students"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'admission_number', 'phone']
    ordering_fields = ['first_name', 'last_name', 'admission_number', 'joining_date']
    ordering = ['first_name', 'last_name']
    
    @action(detail=True, methods=['get'])
    def parents(self, request, pk=None):
        """Get parents of this student"""
        student = self.get_object()
        parents = Parent.objects.filter(student=student)
        serializer = ParentSerializer(parents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get attendance records for this student"""
        student = self.get_object()
        attendance = Attendance.objects.filter(student=student).order_by('-date')
        page = self.paginate_queryset(attendance)
        serializer = AttendanceSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        """Get grades for this student"""
        student = self.get_object()
        grades = Grade.objects.filter(student=student)
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def fees(self, request, pk=None):
        """Get fee payments for this student"""
        student = self.get_object()
        fees = FeePayment.objects.filter(student=student)
        serializer = FeePaymentSerializer(fees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def report_card(self, request, pk=None):
        """Generate report card for student"""
        student = self.get_object()
        exam_id = request.query_params.get('exam')
        
        if exam_id:
            exam = get_object_or_404(Exam, id=exam_id, class_assigned=student.class_assigned)
            grades = Grade.objects.filter(student=student, exam=exam)
            
            total_marks = sum(g.total_marks for g in grades)
            max_marks = sum(g.subject.theory_marks + g.subject.practical_marks for g in grades)
            percentage = (total_marks / max_marks) * 100 if max_marks > 0 else 0
            
            return Response({
                'student': StudentSerializer(student).data,
                'exam': ExamSerializer(exam).data,
                'grades': GradeSerializer(grades, many=True).data,
                'total_marks': total_marks,
                'max_marks': max_marks,
                'percentage': round(percentage, 2),
                'result': 'Pass' if percentage >= 33 else 'Fail'
            })
        
        return Response({'error': 'Exam ID required'}, status=status.HTTP_400_BAD_REQUEST)

class ParentViewSet(viewsets.ModelViewSet):
    """ViewSet for parents"""
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['father_name', 'mother_name', 'guardian_name']

class TeacherViewSet(viewsets.ModelViewSet):
    """ViewSet for teachers"""
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'employee_id', 'phone']
    ordering_fields = ['first_name', 'last_name', 'joining_date']
    ordering = ['first_name']
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """Get subjects taught by this teacher"""
        teacher = self.get_object()
        subjects = Subject.objects.filter(teacher=teacher)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def timetable(self, request, pk=None):
        """Get timetable for this teacher"""
        teacher = self.get_object()
        timetable = Timetable.objects.filter(teacher=teacher)
        serializer = TimetableSerializer(timetable, many=True)
        return Response(serializer.data)

class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet for subjects"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_assigned', 'teacher']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']

class TimetableViewSet(viewsets.ModelViewSet):
    """ViewSet for timetable"""
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['class_assigned', 'teacher', 'day_of_week']

class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for attendance"""
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminUser, IsTeacherUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['class_assigned', 'date', 'status']
    
    @action(detail=False, methods=['post'])
    def mark(self, request):
        """Mark attendance for multiple students"""
        class_id = request.data.get('class_id')
        date = request.data.get('date', timezone.now().date())
        attendance_data = request.data.get('attendance', [])
        
        class_obj = get_object_or_404(Class, id=class_id)
        
        for item in attendance_data:
            student_id = item.get('student_id')
            status_val = item.get('status')
            remarks = item.get('remarks', '')
            
            student = get_object_or_404(Student, id=student_id, class_assigned=class_obj)
            
            attendance, created = Attendance.objects.update_or_create(
                student=student,
                date=date,
                defaults={
                    'status': status_val,
                    'remarks': remarks,
                    'marked_by': request.user.teacher if hasattr(request.user, 'teacher') else None,
                    'class_assigned': class_obj
                }
            )
        
        return Response({'message': 'Attendance marked successfully'})

class ExamViewSet(viewsets.ModelViewSet):
    """ViewSet for exams"""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['class_assigned', 'term', 'year']
    ordering_fields = ['exam_date', 'year']
    ordering = ['-exam_date']

class GradeViewSet(viewsets.ModelViewSet):
    """ViewSet for grades"""
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminUser, IsTeacherUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'subject', 'exam']
    
    @action(detail=False, methods=['post'])
    def enter_marks(self, request):
        """Enter marks for multiple students"""
        exam_id = request.data.get('exam_id')
        subject_id = request.data.get('subject_id')
        marks_data = request.data.get('marks', [])
        
        exam = get_object_or_404(Exam, id=exam_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        for item in marks_data:
            student_id = item.get('student_id')
            theory_marks = item.get('theory_marks', 0)
            practical_marks = item.get('practical_marks', 0)
            remarks = item.get('remarks', '')
            
            student = get_object_or_404(Student, id=student_id, class_assigned=exam.class_assigned)
            
            grade, created = Grade.objects.update_or_create(
                student=student,
                subject=subject,
                exam=exam,
                defaults={
                    'theory_marks': theory_marks,
                    'practical_marks': practical_marks,
                    'remarks': remarks
                }
            )
        
        return Response({'message': 'Marks entered successfully'})

class FeeStructureViewSet(viewsets.ModelViewSet):
    """ViewSet for fee structures"""
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['class_assigned', 'fee_type']

class FeePaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for fee payments"""
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'status', 'payment_method']
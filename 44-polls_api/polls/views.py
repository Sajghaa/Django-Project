from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.db.models import Q, Count, F
from django.shortcuts import get_object_or_404
from .models import Poll, Question, Choice, Response as PollResponse, Vote
from .serializers import (
    UserSerializer, PollListSerializer, PollDetailSerializer, PollCreateSerializer,
    PollResultSerializer, QuestionSerializer, ChoiceSerializer, VoteSubmitSerializer
)
from .permissions import IsPollCreatorOrReadOnly, CanVotePermission
from .pagination import CustomPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data.get('email', ''),
            password=request.data.get('password')
        )
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class CustomAuthToken(ObtainAuthToken):
    """Custom auth token endpoint"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })

class PollViewSet(viewsets.ModelViewSet):
    """ViewSet for polls"""
    queryset = Poll.objects.none()
    permission_classes = [IsAuthenticatedOrReadOnly, IsPollCreatorOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'total_responses']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Skip filtering for schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Poll.objects.none()
        
        user = self.request.user
        if user.is_authenticated:
            return Poll.objects.filter(Q(is_public=True) | Q(created_by=user))
        return Poll.objects.filter(is_public=True, is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PollListSerializer
        elif self.action == 'create':
            return PollCreateSerializer
        elif self.action == 'retrieve':
            return PollDetailSerializer
        elif self.action == 'results':
            return PollResultSerializer
        return PollDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_poll(self):
        """Helper to get poll from slug or pk"""
        if 'slug' in self.kwargs:
            return get_object_or_404(Poll, slug=self.kwargs['slug'])
        return self.get_object()
    
    @action(detail=False, methods=['get'], url_path='public')
    def public_polls(self, request):
        """Get all public active polls"""
        polls = Poll.objects.filter(is_public=True, is_active=True)
        page = self.paginate_queryset(polls)
        serializer = PollListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get questions for a poll"""
        poll = self.get_object()
        questions = poll.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get poll results"""
        poll = self.get_object()
        serializer = PollResultSerializer(poll)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate poll"""
        poll = self.get_object()
        poll.is_active = True
        poll.save()
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close poll"""
        poll = self.get_object()
        poll.is_active = False
        poll.save()
        return Response({'status': 'closed'})
    
    @action(detail=True, methods=['get'])
    def has_voted(self, request, pk=None):
        """Check if user has voted"""
        poll = self.get_object()
        has_voted = False
        
        if request.user.is_authenticated:
            has_voted = PollResponse.objects.filter(
                poll=poll, user=request.user
            ).exists()
        else:
            ip = get_client_ip(request)
            has_voted = PollResponse.objects.filter(
                poll=poll, ip_address=ip
            ).exists()
        
        return Response({'has_voted': has_voted})
    
    @action(detail=True, methods=['post'], permission_classes=[CanVotePermission])
    def vote(self, request, pk=None):
        """Submit vote for poll"""
        poll = self.get_object()
        serializer = VoteSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create response record
        response = PollResponse.objects.create(
            poll=poll,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        # Process each answer
        for answer in serializer.validated_data['answers']:
            question = get_object_or_404(Question, id=answer['question_id'], poll=poll)
            
            if question.question_type == 'text':
                Vote.objects.create(
                    response=response,
                    question=question,
                    text_answer=answer.get('text_answer', '')
                )
            else:
                choice_ids = answer.get('choice_ids', [])
                for choice_id in choice_ids:
                    choice = get_object_or_404(Choice, id=choice_id, question=question)
                    choice.vote_count += 1
                    choice.save()
                    
                    Vote.objects.create(
                        response=response,
                        question=question,
                        choice=choice
                    )
        
        # Update poll total responses
        poll.total_responses = PollResponse.objects.filter(poll=poll).count()
        poll.save()
        
        return Response({
            'message': 'Vote submitted successfully',
            'response_id': response.id
        }, status=status.HTTP_201_CREATED)

class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for questions"""
    queryset = Question.objects.none()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Skip filtering for schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Question.objects.none()
        
        if self.request.user.is_authenticated:
            return Question.objects.filter(poll__created_by=self.request.user)
        return Question.objects.none()
    
    @action(detail=True, methods=['post'])
    def add_choice(self, request, pk=None):
        """Add a choice to a question"""
        question = self.get_object()
        serializer = ChoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(question=question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for choices"""
    queryset = Choice.objects.none()
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Skip filtering for schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Choice.objects.none()
        
        if self.request.user.is_authenticated:
            return Choice.objects.filter(question__poll__created_by=self.request.user)
        return Choice.objects.none()

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
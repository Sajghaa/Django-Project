from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from .models import Customer, Interaction, Lead, Opportunity
from .serializers import (
    UserSerializer, CustomerSerializer, InteractionSerializer,
    LeadSerializer, OpportunitySerializer
)
from django.utils import timezone

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not username or not email or not password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.none()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def interactions(self, request, pk=None):
        customer = self.get_object()
        interactions = customer.interactions.all()
        serializer = InteractionSerializer(interactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_interaction(self, request, pk=None):
        customer = self.get_object()
        serializer = InteractionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer, user=request.user)
            customer.last_contact_at = serializer.instance.date_time
            customer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def opportunities(self, request, pk=None):
        customer = self.get_object()
        opportunities = customer.opportunities.all()
        serializer = OpportunitySerializer(opportunities, many=True)
        return Response(serializer.data)

class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.none()
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Interaction.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.none()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Lead.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        lead = self.get_object()
        
        customer_data = {
            'first_name': lead.first_name,
            'last_name': lead.last_name,
            'email': lead.email,
            'phone': lead.phone,
            'company': lead.company,
            'notes': f"Converted from lead\nOriginal notes: {lead.notes}",
            'status': 'lead',
            'user': request.user.id
        }
        
        customer_serializer = CustomerSerializer(data=customer_data, context={'request': request})
        if customer_serializer.is_valid():
            customer = customer_serializer.save()
            lead.converted_to_customer = customer
            lead.status = 'qualified'
            lead.save()
            
            Interaction.objects.create(
                customer=customer,
                user=request.user,
                type='note',
                subject='Lead Converted',
                description=f'Lead converted from {lead.source}',
                date_time=timezone.now()
            )
            
            return Response({
                'message': 'Lead converted successfully',
                'customer': customer_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(customer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.none()
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Opportunity.objects.filter(assigned_to=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404
from .models import Agent, PropertyType, PropertyFeature, Property, PropertyImage, Inquiry, SavedProperty, PropertyReview
from .serializers import (
    UserSerializer, RegisterSerializer, AgentSerializer, PropertyTypeSerializer,
    PropertyFeatureSerializer, PropertyListSerializer, PropertyDetailSerializer,
    PropertyCreateUpdateSerializer, PropertyImageSerializer, InquirySerializer,
    InquiryCreateSerializer, SavedPropertySerializer, PropertyReviewSerializer
)
from .permissions import IsAgentOrReadOnly, IsPropertyOwner, IsInquiryOwner
from .pagination import CustomPagination
from .filters import PropertyFilter
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
        
        # Create agent profile if agent
        if serializer.validated_data['user_type'] == 'agent':
            Agent.objects.create(
                user=user,
                phone='',
                company_name=''
            )
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'user_type': serializer.validated_data['user_type']
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
            'username': user.username,
            'is_agent': hasattr(user, 'agent_profile')
        })

class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for agents"""
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'company_name']
    ordering_fields = ['rating', 'listing_count', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def properties(self, request, pk=None):
        """Get all properties by this agent"""
        agent = self.get_object()
        properties = Property.objects.filter(agent=agent, listing_status='active')
        page = self.paginate_queryset(properties)
        serializer = PropertyListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

class PropertyTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for property types"""
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    pagination_class = CustomPagination

class PropertyFeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for property features"""
    queryset = PropertyFeature.objects.all()
    serializer_class = PropertyFeatureSerializer
    pagination_class = CustomPagination

class PropertyViewSet(viewsets.ModelViewSet):
    """ViewSet for properties"""
    queryset = Property.objects.none()
    permission_classes = [IsAuthenticatedOrReadOnly, IsPropertyOwner]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['title', 'description', 'address', 'city', 'state']
    ordering_fields = ['price', 'created_at', 'bedrooms', 'square_feet', 'views_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Property.objects.none()
        
        # For unauthenticated users, show only active listings
        if not self.request.user.is_authenticated:
            return Property.objects.filter(listing_status='active')
        
        # Agents see all their properties, others see only active
        if hasattr(self.request.user, 'agent_profile'):
            return Property.objects.filter(agent__user=self.request.user)
        return Property.objects.filter(listing_status='active')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PropertyCreateUpdateSerializer
        return PropertyDetailSerializer
    
    def perform_create(self, serializer):
        agent = get_object_or_404(Agent, user=self.request.user)
        serializer.save(agent=agent)
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view count"""
        property = self.get_object()
        property.views_count += 1
        property.save()
        return Response({'views_count': property.views_count})
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get property reviews"""
        property = self.get_object()
        reviews = property.reviews.all()
        serializer = PropertyReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        """Add a review for property"""
        property = self.get_object()
        
        # Check if user already reviewed
        if PropertyReview.objects.filter(property=property, user=request.user).exists():
            return Response({'error': 'You have already reviewed this property'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PropertyReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(property=property, user=request.user)
        
        # Update agent rating
        reviews = property.reviews.all()
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        property.agent.rating = avg_rating
        property.agent.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def save(self, request, pk=None):
        """Save property to favorites"""
        property = self.get_object()
        saved, created = SavedProperty.objects.get_or_create(user=request.user, property=property)
        
        if created:
            return Response({'saved': True})
        return Response({'saved': False, 'message': 'Already saved'})
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unsave(self, request, pk=None):
        """Remove property from favorites"""
        property = self.get_object()
        SavedProperty.objects.filter(user=request.user, property=property).delete()
        return Response({'saved': False})
    
    @action(detail=True, methods=['post'])
    def inquiry(self, request, pk=None):
        """Submit inquiry for property"""
        property = self.get_object()
        serializer = InquiryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        inquiry = serializer.save(
            property=property,
            user=request.user if request.user.is_authenticated else None
        )
        
        # Increment inquiry count
        property.inquiries_count += 1
        property.save()
        
        return Response(InquirySerializer(inquiry).data, status=status.HTTP_201_CREATED)

class PropertyImageViewSet(viewsets.ModelViewSet):
    """ViewSet for property images"""
    queryset = PropertyImage.objects.none()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PropertyImage.objects.none()
        return PropertyImage.objects.filter(property__agent__user=self.request.user)
    
    def perform_create(self, serializer):
        property_id = self.request.data.get('property')
        property = get_object_or_404(Property, id=property_id, agent__user=self.request.user)
        serializer.save(property=property)

class InquiryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for inquiries"""
    queryset = Inquiry.objects.none()
    serializer_class = InquirySerializer
    permission_classes = [IsAuthenticated, IsInquiryOwner]
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Inquiry.objects.none()
        
        # Agents see inquiries for their properties
        if hasattr(self.request.user, 'agent_profile'):
            return Inquiry.objects.filter(property__agent__user=self.request.user)
        # Users see their own inquiries
        return Inquiry.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update inquiry status (agent only)"""
        inquiry = self.get_object()
        
        # Check if user is agent for this property
        if inquiry.property.agent.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        if new_status not in dict(Inquiry.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        inquiry.status = new_status
        inquiry.save()
        
        return Response({'status': inquiry.status})

class SavedPropertyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for saved properties"""
    queryset = SavedProperty.objects.none()
    serializer_class = SavedPropertySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SavedProperty.objects.none()
        return SavedProperty.objects.filter(user=self.request.user)
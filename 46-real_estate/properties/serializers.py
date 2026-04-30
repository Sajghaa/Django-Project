from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Agent, PropertyType, PropertyFeature, Property, PropertyImage, Inquiry, SavedProperty, PropertyReview

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=['buyer', 'agent'])
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        return data

class AgentSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Agent
        fields = ['id', 'user', 'user_details', 'full_name', 'company_name', 'license_number',
                  'phone', 'bio', 'avatar', 'website', 'listing_count', 'rating', 'is_verified', 'created_at']
        read_only_fields = ['id', 'listing_count', 'rating', 'is_verified', 'created_at']

class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = ['id', 'name', 'slug', 'icon']

class PropertyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFeature
        fields = ['id', 'name', 'slug', 'icon']

class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url', 'caption', 'is_primary', 'order_position']
        read_only_fields = ['id']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer for property list view"""
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    agent_name = serializers.CharField(source='agent.user.get_full_name', read_only=True)
    agent_avatar = serializers.ImageField(source='agent.avatar', read_only=True)
    main_image = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'property_type', 'property_type_name',
            'price', 'price_display', 'address', 'city', 'state', 'zip_code',
            'bedrooms', 'bathrooms', 'square_feet', 'status', 'views_count',
            'agent_name', 'agent_avatar', 'main_image', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'created_at']
    
    def get_main_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None
    
    def get_price_display(self, obj):
        if obj.price_suffix:
            return f"{obj.price_currency} {obj.price:,.0f} {obj.price_suffix}"
        return f"{obj.price_currency} {obj.price:,.0f}"

class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for property detail view"""
    property_type = PropertyTypeSerializer(read_only=True)
    agent = AgentSerializer(read_only=True)
    features = PropertyFeatureSerializer(many=True, read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    price_display = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'property_type', 'agent', 'features', 'images',
            'description', 'price', 'price_display', 'price_currency', 'price_suffix',
            'address', 'city', 'state', 'zip_code', 'country', 'latitude', 'longitude',
            'bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built',
            'status', 'listing_status', 'views_count', 'inquiries_count',
            'average_rating', 'reviews_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'inquiries_count', 'created_at', 'updated_at']
    
    def get_price_display(self, obj):
        if obj.price_suffix:
            return f"{obj.price_currency} {obj.price:,.0f} {obj.price_suffix}"
        return f"{obj.price_currency} {obj.price:,.0f}"
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()

class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating properties"""
    features_input = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = Property
        fields = [
            'property_type', 'title', 'description', 'price', 'price_currency', 'price_suffix',
            'address', 'city', 'state', 'zip_code', 'country', 'latitude', 'longitude',
            'bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built',
            'status', 'listing_status', 'features_input'
        ]
    
    def create(self, validated_data):
        features_input = validated_data.pop('features_input', [])
        property = Property.objects.create(**validated_data)
        
        for feature_id in features_input:
            property.features.add(feature_id)
        
        return property
    
    def update(self, instance, validated_data):
        features_input = validated_data.pop('features_input', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if features_input is not None:
            instance.features.clear()
            for feature_id in features_input:
                instance.features.add(feature_id)
        
        return instance

class InquirySerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    
    class Meta:
        model = Inquiry
        fields = ['id', 'property', 'property_title', 'user', 'name', 'email', 'phone',
                  'message', 'inquiry_type', 'preferred_date', 'preferred_time',
                  'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

class InquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ['name', 'email', 'phone', 'message', 'inquiry_type', 'preferred_date', 'preferred_time']

class SavedPropertySerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)
    
    class Meta:
        model = SavedProperty
        fields = ['id', 'property', 'created_at']
        read_only_fields = ['id', 'created_at']

class PropertyReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PropertyReview
        fields = ['id', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
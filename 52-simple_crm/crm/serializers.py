from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer, Interaction, Lead, Opportunity

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'company', 'address', 'city', 'state', 'zip_code', 'country',
            'industry', 'status', 'notes', 'assigned_to', 'assigned_to_name',
            'created_at', 'updated_at', 'last_contact_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class InteractionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    
    class Meta:
        model = Interaction
        fields = [
            'id', 'customer', 'customer_name', 'user', 'user_name',
            'type', 'subject', 'description', 'date_time', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class LeadSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'company', 'source', 'status', 'notes', 'converted_to_customer',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class OpportunitySerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    
    class Meta:
        model = Opportunity
        fields = [
            'id', 'customer', 'customer_name', 'name', 'amount',
            'stage', 'probability', 'expected_close', 'assigned_to',
            'assigned_to_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
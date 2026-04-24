from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Poll, Question, Choice, Response, Vote

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'order_position', 'vote_count', 'allow_custom']
        read_only_fields = ['id', 'vote_count']

class ChoiceResultSerializer(serializers.ModelSerializer):
    """Serializer for results with percentage"""
    percentage = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    
    class Meta:
        model = Choice
        fields = ['id', 'text', 'vote_count', 'percentage', 'total_votes']
        read_only_fields = ['id', 'text', 'vote_count', 'percentage', 'total_votes']
    
    def get_percentage(self, obj):
        question = obj.question
        total_votes = question.votes.filter(choice__isnull=False).count()
        if total_votes > 0:
            return round((obj.vote_count / total_votes) * 100, 1)
        return 0
    
    def get_total_votes(self, obj):
        return obj.question.votes.filter(choice__isnull=False).count()

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'is_required', 'order_position', 'choices']
        read_only_fields = ['id']

class QuestionCreateSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'is_required', 'order_position', 'choices']
    
    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        
        return question

class QuestionResultSerializer(serializers.ModelSerializer):
    choices = ChoiceResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'choices']

class PollListSerializer(serializers.ModelSerializer):
    """Serializer for list view"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'slug', 'description', 'created_by', 'created_by_name',
            'start_date', 'end_date', 'is_active', 'is_public', 'total_responses',
            'is_open', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'total_responses', 'created_at']

class PollDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'slug', 'description', 'created_by', 'created_by_name',
            'start_date', 'end_date', 'is_active', 'is_public', 'allow_multiple_votes',
            'require_auth', 'total_responses', 'questions', 'is_open', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'total_responses', 'created_at', 'updated_at']

class PollCreateSerializer(serializers.ModelSerializer):
    questions = QuestionCreateSerializer(many=True)
    
    class Meta:
        model = Poll
        fields = [
            'title', 'description', 'start_date', 'end_date', 'is_active',
            'is_public', 'allow_multiple_votes', 'require_auth', 'questions'
        ]
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        poll = Poll.objects.create(**validated_data)
        
        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = Question.objects.create(poll=poll, **question_data)
            
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
        
        return poll

class PollResultSerializer(serializers.ModelSerializer):
    questions = QuestionResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = Poll
        fields = ['id', 'title', 'slug', 'total_responses', 'questions']

class VoteAnswerSerializer(serializers.Serializer):
    """Serializer for vote submission"""
    question_id = serializers.IntegerField()
    choice_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    text_answer = serializers.CharField(required=False, allow_blank=True)

class VoteSubmitSerializer(serializers.Serializer):
    """Serializer for vote submission"""
    answers = VoteAnswerSerializer(many=True)
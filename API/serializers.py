from rest_framework import serializers
from .models import Post, Comment, Vote
from django.contrib.auth.models import User
from django.db.models import Sum

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True, 'allow_blank': False}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            is_active=False
        )
        return user

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'content']
        read_only_fields = ['id']

    def create(self, validated_data):
        # Assuming you want to automatically set the user to the request user
        user = self.context['request'].user
        post = Post.objects.create(user=user, **validated_data)
        return post

class CommentSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['post', 'content', 'parent_comment']

class CommentSerializerReturn(serializers.ModelSerializer):
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'date_commented', 'parent_comment', 'total_votes']

    def get_total_votes(self, obj):
        # Count upvotes and downvotes separately
        upvotes = Vote.objects.filter(comment=obj, vote_type=True).count()
        downvotes = Vote.objects.filter(comment=obj, vote_type=False).count()
        # Subtract downvotes from upvotes to get total votes
        return upvotes - downvotes

class PostSerializerReturn(serializers.ModelSerializer):
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'date_posted', 'total_votes']


    def get_total_votes(self, obj):
        # Count upvotes and downvotes separately
        upvotes = Vote.objects.filter(post=obj, vote_type=True).count()
        downvotes = Vote.objects.filter(post=obj, vote_type=False).count()
        # Subtract downvotes from upvotes to get total votes
        return upvotes - downvotes

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'user', 'post', 'comment', 'vote_type']
        read_only_fields = ['id', 'user']  # User will be set based on the request

    def create(self, validated_data):
        user = self.context['request'].user
        post = validated_data.get('post')
        comment = validated_data.get('comment')

        # Ensure only one of post or comment is provided
        if post and comment:
            raise serializers.ValidationError("Cannot vote on both a post and a comment. Choose one.")

        if not post and not comment:
            raise serializers.ValidationError("A vote must be associated with either a post or a comment.")

        # Proceed based on whether it's a post or comment vote
        if post:
            # Voting or updating a vote on a post
            vote, created = Vote.objects.update_or_create(
                user=user, post=post, 
                defaults={'vote_type': validated_data['vote_type']})
        elif comment:
            # Voting or updating a vote on a comment
            vote, created = Vote.objects.update_or_create(
                user=user, comment=comment, 
                defaults={'vote_type': validated_data['vote_type']})

        return vote

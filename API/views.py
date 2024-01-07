from django.shortcuts import render
from rest_framework import generics, status
from .models import Post, Vote, Comment, ActivationToken
from .serializers import PostSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer, LoginSerializer, VoteSerializer, CommentSerializerCreate, CommentSerializerReturn, PostSerializerReturn
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from django.http import Http404
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .documents import PostDocument, UserDocument
from .serializers import PostSerializer  # You need to create a serializer for your Post model
from elasticsearch_dsl.query import MatchPhrasePrefix
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

AMOUNT_OF_TIME = 600
@method_decorator(cache_page(AMOUNT_OF_TIME), name='dispatch')
class PostViewSet(generics.ListAPIView):
    serializer_class = PostSerializer
    
    def get_queryset(self):
        return Post.objects.filter(deleted_at__isnull=True)

class CombinedSearchView(APIView):
    """
    View to search posts, users and comments using Elasticsearch.
    """
    def get(self, request, format=None):
        query = request.GET.get('q', '')
        combined_response = []

        if query:
            # Search in post comments
            comments_search = PostDocument.search().query('nested', path='comments', query={
                'match': {'comments.content': query}
            })
            comments_search = comments_search.extra(size=100)
            comments_response = comments_search.to_queryset()
            post_serializer = PostSerializer(comments_response, many=True)
            combined_response.extend(post_serializer.data)

            # Search in posts
            post_search = PostDocument.search().query("match_phrase_prefix", content=query)
            post_search = post_search.extra(size=100) 
            post_response = post_search.to_queryset()
            post_serializer = PostSerializer(post_response, many=True)
            combined_response.extend(post_serializer.data)

            # Search in users
            user_search = UserDocument.search().query("match_phrase_prefix", username=query)
            user_response = user_search.to_queryset()
            user_serializer = UserSerializer(user_response, many=True)
            combined_response.extend(user_serializer.data)

        return Response(combined_response)
class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Assign the logged-in user

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        activation_token = ActivationToken.objects.create(user=user)

        self.send_confirmation_email(user.email, str(activation_token.token))

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data}, 
            status=status.HTTP_201_CREATED)
    
    def send_confirmation_email(self, user_email, token):
        subject = 'Email Confirmation'
        message = f'Please confirm your email by clicking on this link: http://localhost:8000/api/activate/{token}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user_email]
        send_mail(subject, message, email_from, recipient_list)

def activate_account(request, token):
    token_instance = get_object_or_404(ActivationToken, token=token)

    user = token_instance.user

    if user is not None:
        user.is_active = True
        user.save()

        token_instance.delete()

        return HttpResponse('Your account has been activated successfully!')

    else:
        return HttpResponse('Invalid activation link')

class UserLoginView(APIView):
    # Authentication classes are not needed here as this is the login view

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                print("yo")
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the token to log out the user
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckAuthView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_data = UserSerializer(request.user).data
        return Response({'authenticated': True, 'user': user_data}, status=status.HTTP_200_OK)

@method_decorator(cache_page(AMOUNT_OF_TIME), name='dispatch')
class UserPostsView(generics.ListAPIView):
    serializer_class = PostSerializerReturn

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Post.objects.filter(user__id=user_id, deleted_at__isnull=True)

@method_decorator(cache_page(AMOUNT_OF_TIME), name='dispatch')
class UserLikedPostsView(generics.ListAPIView):
    serializer_class = PostSerializerReturn

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        liked_post_ids = Vote.objects.filter(
            user__id=user_id, 
            vote_type=1
        ).values_list('post_id', flat=True)

        return Post.objects.filter(
            id__in=liked_post_ids, 
            deleted_at__isnull=True
        )

@method_decorator(cache_page(AMOUNT_OF_TIME), name='dispatch')
class UserDislikedPostsView(generics.ListAPIView):
    serializer_class = PostSerializerReturn

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        liked_post_ids = Vote.objects.filter(
            user__id=user_id, 
            vote_type=0
        ).values_list('post_id', flat=True)

        return Post.objects.filter(
            id__in=liked_post_ids, 
            deleted_at__isnull=True
        )

@method_decorator(cache_page(AMOUNT_OF_TIME), name='dispatch')
# Retrieve a specific post from a user
class SpecificUserPostView(generics.RetrieveAPIView):
    serializer_class = PostSerializerReturn
    lookup_field = 'pk'

    def get_object(self):
        user_id = self.kwargs['user_id']
        pk = self.kwargs['pk']
        try:
            return Post.objects.get(user__id=user_id, pk=pk, deleted_at__isnull=True)
        except Post.DoesNotExist:
            raise Http404

class DeletePostView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own posts.")
        instance.delete()

class DeleteCommentView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own comments.")
        instance.delete()

@method_decorator(cache_page(AMOUNT_OF_TIME), name='dispatch')
class UserCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializerReturn

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Comment.objects.filter(user__id=user_id, deleted_at__isnull=True)

@method_decorator(cache_page(AMOUNT_OF_TIME), name='dispatch')
# Retrieve a specific comment from a user
class SpecificUserCommentView(generics.RetrieveAPIView):
    serializer_class = CommentSerializerReturn

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Comment.objects.filter(user__id=user_id, deleted_at__isnull=True)

# List all comments on a specific post
class PostCommentsView(generics.ListAPIView):
    serializer_class = PostSerializerReturn

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post__id=post_id, deleted_at__isnull=True)

@method_decorator(cache_page(AMOUNT_OF_TIME), name='dispatch')
# Retrieve a specific comment on a post
class SpecificPostCommentView(generics.RetrieveAPIView):
    serializer_class = CommentSerializerReturn

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post__id=post_id, deleted_at__isnull=True)

@method_decorator(cache_page(AMOUNT_OF_TIME), name='dispatch')
# Create a comment
class CreateCommentView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerCreate
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class VoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = VoteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
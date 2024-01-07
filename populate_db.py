import os
import django
from faker import Faker
from random import choice, randint
from datetime import datetime

# Configure the environment for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'echo.settings')
django.setup()

# Agora você pode importar seus modelos do Django
from django.contrib.auth.models import User
from API.models import Profile, Category, Post, Comment, Vote

fake = Faker()

def get_random_image():
    image= 'https://static.vecteezy.com/system/resources/previews/005/129/844/non_2x/profile-user-icon-isolated-on-white-background-eps10-free-vector.jpg'
    return image

def create_categories(num_categories=10):
    comment_content = fake.text()
    if len(comment_content) > 100:
        comment_content = comment_content[:100]
    categories = [Category(name=comment_content, description=fake.text()) for _ in range(num_categories)]
    Category.objects.bulk_create(categories)

def create_users(num_users=1000):
    created_count = 0
    while created_count < num_users:
        user_name = fake.user_name()
        if len(user_name) > 100:
            user_name = user_name[:100]

        email = fake.email()

        # Verifica se o nome de usuário ou email já existem
        if not User.objects.filter(username=user_name).exists() and \
           not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                username=user_name, 
                email=email, 
                password="testpassword"
            )
            profile_pic_url = get_random_image()  # Garanta que esta função esteja definida
            user.profile.profile_picture = profile_pic_url
            user.profile.save()
            created_count += 1

def create_posts(num_posts=2000):
    users = list(User.objects.all())
    categories = list(Category.objects.all())
    for _ in range(num_posts):
        post = Post(
            user=choice(users),
            content=fake.text(),
            date_posted=datetime.now(),
            last_updated=datetime.now(),
            category=choice(categories),
            status='active'
        )
        post_img_url = get_random_image()
        # Directly assign the URL to the image field
        post.image = post_img_url
        post.save()

def create_comments(num_comments=5000):
    users = list(User.objects.all())
    posts = list(Post.objects.all())
    comments = [
        Comment(
            user=choice(users),
            post=choice(posts),
            content=fake.text(),
            date_commented=datetime.now(),
            parent_comment=None  # or set a logic for parent comments
        ) for _ in range(num_comments)]
    Comment.objects.bulk_create(comments)

def create_votes(num_votes=10000):
    users = list(User.objects.all())
    posts = list(Post.objects.all())
    comments = list(Comment.objects.all())
    votes = []
    vote_combinations = set()

    while len(votes) < num_votes:
        user = choice(users)
        post_vote = randint(0, 1) == 1
        post = choice(posts) if post_vote else None
        comment = choice(comments) if not post_vote else None

        # Check for unique user, post, and comment combination
        if (user.id, post.id if post else None, comment.id if comment else None) not in vote_combinations:
            votes.append(Vote(
                user=user,
                post=post,
                comment=comment,
                vote_type=bool(randint(0, 1)),
                date_voted=datetime.now()
            ))
            vote_combinations.add((user.id, post.id if post else None, comment.id if comment else None))

    Vote.objects.bulk_create(votes)

if __name__ == '__main__':
    create_users()
    create_categories()
    create_posts()
    create_comments()
    create_votes()

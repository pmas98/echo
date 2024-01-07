# Echo

A social media platform that combines elements of Reddit and Twitter. Users can create posts, comment on posts, and vote on both posts and comments.

## Getting Started

You can run using the Dockerfile provided, everything is included, except for ElasticSearch, since it's kinda big, i recommended creating a separate VM instance for it on a cloud provider.
Also, for registering, i'm using SMTP, so you'll have to get your credentials with your mail provider.

### Prerequisites

- Python 3.8 or higher
- Django 3.2 or higher
- Django Rest Framework
- Elasticsearch
- PostgreSQL
- Redis

### Installation

1. Clone the repository(or you can just do `docker-compose up --build` and skip these steps)
2. Navigate into the project directory
3. Install the requirements

## Usage

Once the server is running, you can use the following endpoints:

`posts/create/`: This endpoint is used to create a new post. It uses the CreatePostView view.

`posts/`: This endpoint is used to retrieve all posts. It uses the PostViewSet view.

`login/`: This endpoint is used for user login. It uses the UserLoginView view.

`register/`: This endpoint is used to register a new user. It uses the UserRegistrationView view.

`activate/<str:token>/:` This endpoint is used to activate a user account. It uses the activate_account function and requires a token.

`auth/:` This endpoint is used to check user authentication. It uses the CheckAuthView view.

`logout/:` This endpoint is used for user logout. It uses the LogoutView view.

`posts/<int:user_id>/:` This endpoint is used to retrieve all posts by a specific user. It uses the UserPostsView view and requires a user ID.

`posts/liked/<int:user_id>/:` This endpoint is used to retrieve all posts liked by a specific user. It uses the UserLikedPostsView view and requires a user ID.

`posts/disliked/<int:user_id>/:` This endpoint is used to retrieve all posts disliked by a specific user. It uses the UserDislikedPostsView view and requires a user ID.

`posts/<int:user_id>/<int:pk>/:` This endpoint is used to retrieve a specific post by a specific user. It uses the SpecificUserPostView view and requires a user ID and a post ID.

`posts/<int:pk>/delete/:` This endpoint is used to delete a specific post. It uses the DeletePostView view and requires a post ID.

## Running the tests

No automated tests for now, but they are coming soon!

## Next Steps

I'm working on breaking the API app into a series of microservices, also looking into automated tests and a recommendation system.

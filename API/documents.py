# documents.py

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Post, User, Comment

@registry.register_document
class CommentDocument(Document):

    comments = fields.NestedField(properties={
        'content': fields.TextField(),
        # include other comment fields you want to index
    })

    class Index:
        name = 'posts'
        # settings...

    class Django:
        model = Post
        fields = [
            'content',
        ]
        related_models = [Comment]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Comment):
            return related_instance.post

@registry.register_document
class PostDocument(Document):
    class Index:
        name = 'posts'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1
        }

    class Django:
        model = Post  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'content'
            # add other fields you want to index
        ]
@registry.register_document
class UserDocument(Document):
    class Index:
        # Choose a suitable name for the user index
        name = 'users'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = User  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'username',  # Assuming the User model has a field 'username'
        ]
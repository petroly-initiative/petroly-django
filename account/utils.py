from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db.models.base import Model
from graphql.error.base import GraphQLError
from graphql_jwt.decorators import *
from graphene_django_crud.converter import convert_django_field as convert_django_field_crud
from graphene_django.converter import convert_django_field
from graphene_django_crud.utils import is_required
from graphene.types import String, Scalar


class ProfilePic(Scalar):
    '''
    A Scalar type for `CloudinaryField`
    '''

    @staticmethod
    def serialize(dt):
        print('serilize', dt)
        return dt.url

@convert_django_field_crud.register(CloudinaryField)
@convert_django_field.register(CloudinaryField)
def convert_profile_pic(field: CloudinaryField, registry=None, input_flag=None) -> ProfilePic:
    '''Register CloudinaryField `DjangoObjectType` classes'''
    return ProfilePic(
        description="CloudinaryField for profile_pic",
        required=is_required(field) and input_flag == "create",
    )



def is_owner_(user: User, obj: Model) -> bool:
    """Check if this user owns the object"""
    
    if user.pk == obj.user.pk:
        return True
    raise GraphQLError("You don't own this Profile")

def is_owner(func):
    """A decorator to check if the logged user owns the instance"""

    @login_required
    def wrapper(cls, parent, info, instance, data):
        if not info.context.user == instance.user:
            raise GraphQLError("You don't own this Profile")
        return func(cls, parent, info, instance, data)
    return wrapper
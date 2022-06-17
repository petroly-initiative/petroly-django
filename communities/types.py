from re import A
from strawberry import auto
from enum import Enum
from strawberry_django_plus import gql
from gqlauth.decorators import login_required


from . import models


@gql.enum
class CategoryEnum(Enum):
    EDU = 'edu'
    SEC = 'section'
    ENT = 'entertaining'


@gql.django.type(models.Community)
class CommunityType:
    name: auto
    category: CategoryEnum


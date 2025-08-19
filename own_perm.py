# permissions.py
from typing import Any
import strawberry
from strawberry_django.permissions import DjangoPermissionExtension


class IsOwner(DjangoPermissionExtension):
    """
    Permission extension to check if the user owns/created the object.
    Compares the object's owner/creator field with the current user.
    """
    
    def __init__(self, owner_field: str = "user"):
        """
        Initialize the permission extension.
        
        Args:
            owner_field: The field name on the model that references the owner/creator.
                        Default is "user", but could be "owner", "created_by", etc.
        """
        self.owner_field = owner_field
        super().__init__()
    
    async def resolve_for_user(
        self,
        resolver,
        user,
        *,
        root,
        info,
        source,
        **kwargs
    ) -> Any:
        """
        Check if the user owns the object being queried.
        
        Returns:
            The resolved value if user owns it, otherwise handles according to field type.
        """
        # First, resolve the actual value
        retval = await resolver(root, info, **kwargs)
        
        # If no return value or user is not authenticated, deny access
        if not retval or not user or not user.is_authenticated:
            return self.handle_no_permission(info, retval)
        
        # Handle list/queryset results - filter to only owned objects
        if hasattr(retval, '__iter__') and not isinstance(retval, str):
            if hasattr(retval, 'filter'):  # Django QuerySet
                return retval.filter(**{self.owner_field: user})
            else:  # Regular list/iterable
                owned_objects = []
                for obj in retval:
                    if self._check_ownership(obj, user):
                        owned_objects.append(obj)
                return owned_objects
        
        # Handle single object result
        if self._check_ownership(retval, user):
            return retval
        else:
            return self.handle_no_permission(info, retval)
    
    def _check_ownership(self, obj, user) -> bool:
        """
        Check if the user owns the given object.
        
        Args:
            obj: The object to check ownership for
            user: The current user
            
        Returns:
            True if user owns the object, False otherwise
        """
        if not obj or not user:
            return False
            
        # Get the owner field value using getattr with dot notation support
        owner = obj
        for field_part in self.owner_field.split('.'):
            owner = getattr(owner, field_part, None)
            if owner is None:
                return False
        
        return owner == user


# Example usage in types.py
import strawberry_django
from django.contrib.auth.models import User
from myapp.models import Post, Comment


@strawberry_django.type
class PostType:
    id: strawberry.ID
    title: str
    content: str
    
    # Only return posts owned by the current user
    @strawberry_django.field(extensions=[IsOwner(owner_field="author")])
    def user_posts(self, info) -> list["PostType"]:
        return Post.objects.all()
    
    # Only return comments owned by the current user
    comments: list["CommentType"] = strawberry_django.field(
        extensions=[IsOwner(owner_field="user")]
    )


@strawberry_django.type  
class CommentType:
    id: strawberry.ID
    content: str
    
    # Only show the post if current user owns this comment
    post: PostType = strawberry_django.field(
        extensions=[IsOwner(owner_field="user")]
    )


# Alternative: More flexible ownership checker
class IsOwnerFlexible(DjangoPermissionExtension):
    """
    More flexible ownership checker that accepts a callable to determine ownership.
    """
    
    def __init__(self, ownership_checker=None):
        """
        Args:
            ownership_checker: A callable that takes (obj, user) and returns bool.
                              If None, defaults to checking obj.user == user
        """
        self.ownership_checker = ownership_checker or (lambda obj, user: getattr(obj, 'user', None) == user)
        super().__init__()
    
    async def resolve_for_user(self, resolver, user, *, root, info, source, **kwargs) -> Any:
        retval = await resolver(root, info, **kwargs)
        
        if not user or not user.is_authenticated:
            return self.handle_no_permission(info, retval)
        
        # Handle collections
        if hasattr(retval, '__iter__') and not isinstance(retval, str):
            if hasattr(retval, 'filter'):  # QuerySet - can't easily filter with custom logic
                owned_objects = [obj for obj in retval if self.ownership_checker(obj, user)]
                return owned_objects
            else:
                return [obj for obj in retval if self.ownership_checker(obj, user)]
        
        # Handle single object
        if retval and self.ownership_checker(retval, user):
            return retval
        else:
            return self.handle_no_permission(info, retval)


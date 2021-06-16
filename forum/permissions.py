def has_object_permission(request, obj):
    return obj.user==request.user
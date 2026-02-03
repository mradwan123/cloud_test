from rest_framework.permissions import BasePermission

class CanUpdateReview(BasePermission):
    
    def has_object_permission(self, request, obj):
        
        if request.method in ['PUT', 'PATCH']:
            if obj.author is None:
                return False
            return request.user == obj.author
        return False
    
class IsAdminOrReviewAuthor(BasePermission):
    
    def has_object_permission(self, request, obj):
        if request.user and request.user.is_staff:
            return True
        if obj.author is None:
            return False
        if request.method == 'DELETE':
            return request.user == obj.author
        return False
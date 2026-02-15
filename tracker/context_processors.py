from .models import UserProfile

def user_role(request):
    """Context processor to add user role information to all templates"""
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            profile = request.user.profile
            return {
                'user_role': profile.role,
                'is_admin': profile.is_admin(),
                'is_shop_seller': profile.is_shop_seller(),
                'user_role_display': profile.get_role_display(),
            }
        except UserProfile.DoesNotExist:
            return {
                'user_role': 'shop_seller',
                'is_admin': False,
                'is_shop_seller': True,
                'user_role_display': 'Shop Seller',
            }
    
    return {
        'user_role': None,
        'is_admin': False,
        'is_shop_seller': False,
        'user_role_display': None,
    }

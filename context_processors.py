from .models import AddItem

def cart_item_count(request):
    if request.user.is_authenticated:
        return {'cart_item_count': AddItem.objects.filter(user=request.user).count()}
    return {}
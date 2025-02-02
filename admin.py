from django.contrib import admin
from .models import Product,AddItem,Contact,Category,Order,Productitem,BookingRequest,Turf,FAQ

class AdminProduct(admin.ModelAdmin):
    list_display = ['name','price','category']


admin.site.register(Product,AdminProduct)
admin.site.register(AddItem)
admin.site.register(Contact)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Productitem)
admin.site.register(BookingRequest)
admin.site.register(Turf)
admin.site.register(FAQ)

# nimixa11 :123
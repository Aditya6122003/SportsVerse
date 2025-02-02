from turtle import home

from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('contact/',views.contact,name="contact"),
    path('detail/',views.detail),
    path('about/',views.about,name='aboutus'),

    


    path('signup/',views.signup,name='signup'),
    path('signin/', views.signin ,name='signin'),
    path('signout/',views.signout,name= 'signout'),

    path('detail/<int:pk>/', views.detail, name='detail'),

    path('remove_from_cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),

    path('add_fav/<int:pk>/', views.add_fav, name='add_fav'),
    path('fav/', views.fav, name='fav'),
    path('remove_fav/<int:pk>/', views.remove_fav, name='remove_fav'),

    path('shop/',views.shop),

    path('faq/',views.faq, name='faq'),
    path('turfs/',views.turf_list,name='turfs'),
    path('book-turf/', views.book_turf_dynamic, name='book_turf_dynamic'),
    path('confirm-booking/<int:turf_id>/', views.confirm_booking, name='confirm_booking'),

    path('offers/', views.offers, name='offers'),

    path('change_quantity/<int:pk>/', views.change_quantity, name='change_quantity'),
    path('cart/',views.cart,name='cart'),
    path('add_cart/<int:pk>/', views.add_cart, name='add_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),

    # path('create_order/', views.create_order, name='create_order'),
    path('order_history/', views.order_history, name='order_history'),


    path('checkout/', views.checkout, name='checkout'),  # Checkout page
    path('place_order/', views.place_order, name='place_order'),  # Place order view
    path('razorpay_callback/', views.razorpay_callback, name='razorpay_callback'),  # Razorpay callback
    path('order_conf/', views.order_conf, name='order_conf'),  # Order confirmation page
]

# product_name = models.CharField(max_length=250)
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

STATUS_CHOICE=(
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On the way','On the way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel')
)


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=50,default="")
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Discounted Pric
    image = models.ImageField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


class AddItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.quantity} x {self.name}'

    def total_price(self):
        return self.quantity * self.product.price


class Contact(models.Model):
    username = models.CharField(max_length=50)
    email= models.EmailField()
    subject = models.CharField(max_length=100,default="")
    message = models.CharField(max_length=500,default="")


    def __str__(self):
        return self.username


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.name} - {self.product.name}"


PAYMENT_CHOICE=(
    ('COD','COD'),
    ('RAZORPAY','RAZORPAY'),
)

class Order(models.Model):
    user= models.ForeignKey(User,on_delete=models.CASCADE)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=50)
    email = models.EmailField()
    number = models.IntegerField()
    add1 = models.TextField(max_length=100)
    add2 = models.TextField(max_length=100)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    total_price = models.FloatField(null=False)
    payment_mode = models.CharField(max_length=100,default='COD',choices=PAYMENT_CHOICE)
    status = models.CharField(max_length=50, default='Pending', choices=STATUS_CHOICE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Productitem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity= models. IntegerField(null= False)


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)  # Answer can be provided later
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class Turf(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    available_from = models.TimeField()
    available_to = models.TimeField()
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='media/', null=True, blank=True)  # Image Field

    is_vacant = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class BookingRequest(models.Model):
    game = models.CharField(max_length=100)
    date = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    participants = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.game} on {self.date} ({self.time_start} - {self.time_end})"

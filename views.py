from datetime import datetime
from msvcrt import locking
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.core.paginator import Paginator
import razorpay
from django.conf import settings
# from ecommerce.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET 08/11/20214
from django.views.decorators.csrf import csrf_exempt




# client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET)) 08/11/20214


def place_order(request):
    if request.method == 'POST':
        neworder = Order()
        neworder.user = request.user
        neworder.firstname = request.POST.get('firstname')
        neworder.lastname = request.POST.get('lastname')
        neworder.email = request.POST.get('email')
        neworder.number = request.POST.get('number')
        neworder.add1 = request.POST.get('add1')
        neworder.add2 = request.POST.get('add2')
        neworder.country = request.POST.get('country')
        neworder.city = request.POST.get('city')
        neworder.state = request.POST.get('state')
        neworder.zipcode = request.POST.get('zipcode')

        cart_items = AddItem.objects.filter(user=request.user)
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        shipping_charge = 50
        total_price = subtotal + shipping_charge
        neworder.total_price = total_price
        neworder.payment_mode = request.POST.get('payment_mode')
        neworder.save()

        for item in cart_items:
            Productitem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        AddItem.objects.filter(user=request.user).delete()

        if neworder.payment_mode == 'Razorpay':
            # Razorpay integration
            # No need to wait for payment confirmation, just place the order
            return redirect('order_conf')
        else:
            # COD payment
            return redirect('order_conf')

    return redirect('checkout')




def checkout(request):
    if request.method == 'GET':
        cart_items = AddItem.objects.filter(user=request.user)
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        shipping_charge = 50  # Example shipping charge
        total = subtotal + shipping_charge
        total_in_paise = total * 100
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping_charge': shipping_charge,
            'total': total,
            'total_in_paise': total_in_paise,
            'api_key': 'rzp_test_CqYvQAdpbCofNO',  # Replace with your actual Razorpay API key
        }
        return render(request, 'checkout.html', context)
    else:
        return redirect('checkout')


@csrf_exempt
def razorpay_callback(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # Payment verification process here

        return redirect('order_conf')


def order_history(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'user_orders': user_orders})


# def create_order(request):
#     cart_items = AddItem.objects.filter(user=request.user)
#     total_price = sum(item.product.price * item.quantity for item in cart_items)
#     amount = int(total_price * 100)
#
#     payment_order = client.order.create({'amount': amount, 'currency': "INR", 'payment_capture': '1'})
#     payment_order_id = payment_order['id']
#
#     context = {'amount': amount, 'api_key': RAZORPAY_API_KEY, 'order_id': payment_order_id, 'total_price': total_price}
#     return render(request, 'payment.html', context)


def copy(request):
    return render(request, 'copy.html')

def turf_list(request):
    # Display all turfs (or filtered based on user preferences)
    turfs = Turf.objects.all()
    return render(request, 'turf.html', {'available_turfs': turfs})


def book_turf_dynamic(request):
    if request.method == "POST":
        game = request.POST['game']
        date = request.POST['date']
        time_start = request.POST['time_start']
        time_end = request.POST['time_end']
        participants = request.POST['participants']

        # Save booking details
        locking.objects.create(
            game=game,
            date=date,
            time_start=time_start,
            time_end=time_end,
            participants=participants
        )

        return redirect('turfs')  # Redirect to turf listing page

    return render(request, 'turf.html')

def confirm_booking(request, turf_id):
    if request.method == "POST":
        turf = get_object_or_404(Turf, id=turf_id)
        
        if not turf.is_vacant:
            return JsonResponse({"message": "Sorry, this turf is already booked."}, status=400)

        turf.is_vacant = False
        turf.save()
        
        return JsonResponse({"message": f"Booking confirmed for {turf.name}!"})
    
    return JsonResponse({"error": "Invalid request"}, status=400) 

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def faq(request):
    faq_items = FAQ.objects.all()  # Assuming you have an FAQ model
    return render(request, 'faq.html', {'faq_items': faq_items})

def submit_question(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        question = request.POST.get('question')
        
        # Save the question to the database or email it to support
        FAQ.objects.create(name=name, email=email, question=question)
        messages.success(request, 'Your question has been submitted successfully! We will get back to you shortly.')
        return redirect('faq')
    return redirect('faq')

def offers(request):
    # Fetch all categories
    categories = Category.objects.all()

    # Filter products with discounts or marked as offers
    discounted_products = Product.objects.filter(discounted_price__lt=models.F('original_price'))

    # Optional: Filter by category (if a category filter is applied)
    category_id = request.GET.get('category')
    if category_id:
        category_obj = Category.objects.get(id=category_id)
        discounted_products = discounted_products.filter(category=category_obj)

    # Categorize products by their category
    categorized_offers = {}
    for category in categories:
        products = discounted_products.filter(category=category)
        if products.exists():
            categorized_offers[category.name] = products

    # Apply pagination (optional)
    paginator = Paginator(discounted_products, 6)  # 6 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'offers.html', {
        'categorized_offers': categorized_offers,  # Products grouped by category
        'categories': categories,  # For category navigation
        'page_obj': page_obj,  # For pagination
        'category_id': category_id,  # Selected category
    })


from django.shortcuts import render
from django.contrib import messages
from .models import Contact

def contact(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        # Check if any field is empty
        if not username or not email or not subject or not message:
            messages.error(request, "All fields are required. Please fill out the form.")
        else:
            # Save the message only if all fields are filled
            contact = Contact(username=username, email=email, subject=subject, message=message)
            contact.save()
            messages.success(request, "Your message has been sent successfully!")

    return render(request, 'contact.html')


def shop(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    query = request.GET.get('q')  # Get the search query

    if category_id:
        category_obj = Category.objects.get(id=category_id)
        products = Product.objects.filter(category=category_obj)
    else:
        products = Product.objects.all()

    if query:  # If a search query is provided
        products = products.filter(name__icontains=query)  # Filter products by name

    paginator = Paginator(products, 6)  # 6 products per page (pagination)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop.html',
                  {'products': page_obj, 'categories': categories, 'query': query, 'category_id': category_id})


def cart(request):
    return render(request, 'cart.html')


# def signup(request):
#     if request.method == "POST":
#
#         username = request.POST['username']
#         fname = request.POST['fname']
#         lname = request.POST['lname']
#         email = request.POST['email']
#         pass1 = request.POST['pass1']
#         pass2 = request.POST['pass2']
#
#         if User.objects.filter(username=username):
#             messages.error(request, "username is already exist! please enter other username")
#             return redirect('index')
#         # if User.objects.filter(email=email):
#         #     messages.error(request,"email already registered !")
#         #     return redirect('signup')
#
#         if len(username) > 10:
#             messages.error(request, "username must be under 10 character")
#         if pass1 != pass2:
#             messages.error(request, "password did not match!")
#         if not username.isalnum():
#             messages.error(request, "username must be alpha-numeric!")
#
#             return redirect('index')
#
#         myuser = User.objects.create_user(username=username, email=email, password=pass1)
#
#         myuser.first_name = fname
#         myuser.last_name = lname
#
#         myuser.save()
#
#         messages.success(request, "Your account has been created \n email sent to your account !!")
#
#         return redirect('signin')
#
#     return render(request, 'signup.html')
#


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if pass1 != pass2:
            messages.error(request, "password did not match!")
            return redirect('signup')

        if len(username) > 10:
            messages.error(request, "username must be under 10 character")
            return redirect('signup')

        if not username.isalnum():
            messages.error(request, "username must be alpha-numeric!")
            return redirect('signup')

        if User.objects.filter(username=username):
            messages.error(request, "username is already exist! please enter other username")
            return redirect('signup')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "username already exists! please enter other username")
            return redirect('signup')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "email address already exists! please enter other email")
            return redirect('signup')

        myuser = User.objects.create_user(username=username, email=email, password=pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()

        messages.success(request, "Your account has been created")
        return redirect('signin')

    return render(request, 'signup.html')


def signin(request):
    if request.method == "POST":

        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, 'index.html', {'fname': fname})

        else:
            messages.error(request, "wrong pass!")
            return redirect('signin')

    return render(request, 'signin.html')


# def signout(request):
#     logout(request)
#     messages.success(request, "Logged out successfully...!!")
#     return redirect('index')

def signout(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "Logged out successfully...!!", extra_tags='safe')
    return redirect('index')


def detail(request, pk):
    products = Product.objects.all()
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'detail.html', {'product': product, 'products': products})


# CART
def add_cart(request, pk):
    product = Product.objects.get(id=pk)
    user = request.user
    cart_item, created = AddItem.objects.get_or_create(product=product, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')


def view_cart(request):
    cart_items = AddItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping_charge = 50
    total = subtotal + shipping_charge
    for item in cart_items:
        item.total_price = item.product.price * item.quantity

    return render(request, 'cart.html',
                  {'cart_items': cart_items, 'total_price': total_price, 'subtotal': subtotal, 'total': total,
                   'shipping_charge': shipping_charge})



# def checkout(request):
#     if request.method == 'POST':
#         # Get the checkout form data
#         firstname = request.POST['firstname']
#         lastname = request.POST['lastname']
#         email = request.POST['email']
#         number = request.POST['number']
#         add1 = request.POST['add1']
#         add2 = request.POST['add2']
#         country = request.POST['country']
#         city = request.POST['city']
#         state = request.POST['state']
#         zipcode = request.POST['zipcode']
#
#         # Calculate the total
#         cart_items = AddItem.objects.filter(user=request.user)
#         subtotal = sum(item.product.price * item.quantity for item in cart_items)
#         shipping_charge = 50
#         total = subtotal + shipping_charge
#
#         # Create an order instance
#         order = OrderDetail(
#             user=request.user,
#             total=total,
#             quantity=sum(item.quantity for item in cart_items),
#         )
#         order.save()
#
#
#         # Create a Checkout
#         checkout = Checkout(
#             order=order,
#             firstname=firstname,
#             lastname=lastname,
#             email=email,
#             number=number,
#             add1=add1,
#             add2=add2,
#             country=country,
#             city=city,
#             state=state,
#             zipcode=zipcode,
#         )
#         checkout.save()
#
#         # Update the order status to 'processing'
#         order.status = 'processing'
#         order.save()
#
#
#
#         # Razorpay Payment Gateway Callback
#         if request.POST.get('payment_id'):
#             # Update the order status to 'paid'
#             order.status = 'paid'
#             order.save()
#
#             # Display success message
#             messages.success(request, 'Payment successful! You can now place the order.')
#
#
#
#         # Clear the cart
#         cart_items.delete()
#
#         # Redirect to a success page
#         # messages.success(request, 'Order placed successfully!')
#         return redirect('order_conf')
#     else:
#         cart_items = AddItem.objects.filter(user=request.user)
#         subtotal = sum(item.product.price * item.quantity for item in cart_items)
#         shipping_charge = 50
#         total = subtotal + shipping_charge
#
#     return render(request, 'checkout.html', {
#             'cart_items': cart_items,
#             'subtotal': subtotal,
#             'shipping_charge': shipping_charge,
#             'total': total,
#         })
#

# def place_order(request):
#     if request.method =='POST':
#         neworder = Order()
#         neworder.user = request.user
#         neworder.firstname = request.POST.get('firstname')
#         neworder.lastname = request.POST.get('lastname')
#         neworder.email = request.POST.get('email')
#         neworder.number = request.POST.get('number')
#         neworder.add1 = request.POST.get('add1')
#         neworder.add2 = request.POST.get('add2')
#         neworder.country = request.POST.get('country')
#         neworder.city = request.POST.get('city')
#         neworder.state= request.POST.get('state')
#         neworder.zipcode= request.POST.get('zipcode')
#
#         neworder.payment_mode= request.POST.get('payment_mode')
#
#
#         cart_items = AddItem.objects.filter(user=request.user)
#         subtotal = sum(item.product.price * item.quantity for item in cart_items)
#         shipping_charge = 50
#         neworder.total_price = subtotal + shipping_charge
#         neworder.save()
#
#
#         neworderitems =  AddItem.objects.filter(user=request.user)
#         for item in neworderitems:
#             Orderitem.objects.create(
#                 order=neworder,
#                 product=item.product,
#                 price=item.product.price,
#                 quantity=item.product.quantity
#             )
#
#         AddItem.objects.filter(user=request.user).delete()
#         return redirect('order_conf')
#
#     return render(request, 'checkout.html',)
#


def order_conf(request):
    return render(request, 'order_conf.html')


def remove_from_cart(request, pk):
    cart_item = AddItem.objects.get(id=pk)
    cart_item.delete()
    return redirect('view_cart')


def change_quantity(request, pk):
    cart_item = AddItem.objects.get(id=pk)
    quantity = request.POST.get('quantity')
    cart_item.quantity = quantity
    cart_item.save()
    return redirect('view_cart')


# WISHLIST
def add_fav(request, pk):
    product = Product.objects.get(id=pk)
    favourite, created = Favourite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favourite.delete()
    return redirect('fav')


def fav(request):
    favourites = Favourite.objects.filter(user=request.user)
    wishlist = [f.product for f in favourites]
    return render(request, 'fav.html', {'wishlist': wishlist})


def remove_fav(request, pk):
    favourites = Favourite.objects.get(id=pk)
    favourites.delete()
    return redirect('fav')

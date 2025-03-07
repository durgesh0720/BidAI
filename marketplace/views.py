from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, Package, Purchase, Wallet, Transaction
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.urls import reverse
from django_ratelimit.decorators import ratelimit
from django.db.models import Sum
from django.db import models


def landing_page(request):
    return render(request, 'landing.html')

@login_required
@ratelimit(key='user', rate='10/m', method='GET', block=True)
def product_detail(request, product_id):
    cache_key = f'product_{product_id}'
    product = cache.get(cache_key)
    if not product:
        product = get_object_or_404(Product, id=product_id)
        cache.set(cache_key, product, timeout=300)  # Cache for 5 minutes

    if product.free_views_remaining > 0:
        product.free_views_remaining -= 1
    product.views += 1
    product.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'admin_dashboard',
        {
            'type': 'update_metrics',
            'total_listings': Product.objects.count(),
            'total_purchases': Purchase.objects.count(),
            'total_users': User.objects.count(),
            'total_views': Product.objects.aggregate(Sum('views'))['views__sum'] or 0,
        }
    )
    cache.set(cache_key, product, timeout=300)

    return render(request, 'product_detail.html', {
        'product': product,
    })

@login_required
def add_product(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        price = request.POST['price']
        image = request.FILES.get('image')  # Handle file upload
        product = Product(
            seller=request.user,
            title=title,
            description=description,
            price=price,
            image=image
        )
        product.save()
        messages.success(request, "Product added successfully!")
        return redirect('products')
    return render(request, 'add_product.html')
# Login View
def user_login(request):
    if request.user.is_authenticated:  # Redirect if already logged in
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

# Signup View
def user_signup(request):
    if request.user.is_authenticated:  # Redirect if already logged in
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            Wallet.objects.create(user=user)  # Create wallet for new user
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
    return render(request, 'signup.html')
# Logout View
def user_logout(request):
    logout(request)
    return redirect('landing_page')

# Add this new view
def products(request):
    product_list = Product.objects.filter(is_active=True)
    return render(request, 'products.html', {'products': product_list})

@login_required
def upgrade_listing(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    packages = Package.objects.all()
    if request.method == 'POST':
        package_id = request.POST.get('package')
        package = get_object_or_404(Package, id=package_id)
        order_id = f"order_{product.id}_{package.id}"  # Mock order ID
        return render(request, 'payment.html', {
            'product': product,
            'package': package,
            'order_id': order_id,
            'razorpay_key': 'mock_razorpay_key',
        })
    return render(request, 'upgrade_listing.html', {'product': product, 'packages': packages})

@login_required
def payment_success(request):
    product_id = request.GET.get('product_id')
    package_id = request.GET.get('package_id')
    if not product_id or not package_id:
        messages.error(request, "Missing product or package information.")
        return redirect('products')
    try:
        product_id = int(product_id)
        package_id = int(package_id)
    except (ValueError, TypeError):
        messages.error(request, "Invalid product or package ID.")
        return redirect('products')
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    package = get_object_or_404(Package, id=package_id)
    product.free_views_remaining += package.extra_views
    product.is_active = True
    product.save()
    Purchase.objects.create(user=request.user, product=product, package=package, amount=package.price)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'admin_dashboard',
        {
            'type': 'update_metrics',
            'total_listings': Product.objects.count(),
            'total_purchases': Purchase.objects.count(),
            'total_users': User.objects.count(),
            'total_views': Product.objects.aggregate(Sum('views'))['views__sum'] or 0,
        }
    )
    messages.success(request, "Payment simulated successfully! Views added to your listing.")
    return redirect('product_detail', product_id=product.id)

@login_required
def admin_dashboard(request):
    # Restrict to staff or superusers
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('landing_page')
    
    # Fetch data
    total_listings = Product.objects.count()
    total_purchases = Purchase.objects.count()
    total_users = User.objects.count()
    total_views = Product.objects.aggregate(Sum('views'))['views__sum'] or 0
    top_sellers = User.objects.annotate(num_listings=Count('product')).order_by('-num_listings')[:5]
    recent_purchases = Purchase.objects.select_related('user', 'product', 'package').order_by('-id')[:5]

    # Broadcast real-time updates via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'admin_dashboard',
        {
            'type': 'update_metrics',
            'total_listings': total_listings,
            'total_purchases': total_purchases,
            'total_users': total_users,
            'total_views': total_views,
        }
    )

    return render(request, 'admin_dashboard.html', {
        'total_listings': total_listings,
        'total_purchases': total_purchases,
        'total_users': total_users,
        'total_views': total_views,
        'top_sellers': top_sellers,
        'recent_purchases': recent_purchases,
    })

@login_required
def dashboard(request):
    cache_key = f'dashboard_{request.user.id}'
    data = cache.get(cache_key)
    if not data:
        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        transactions = Transaction.objects.filter(wallet__user=request.user).order_by('-timestamp')[:10]
        referral_link = request.build_absolute_uri(reverse('referral_signup', args=[request.user.username]))
        data = {
            'wallet': wallet,
            'transactions': transactions,
            'referral_link': referral_link,
        }
        cache.set(cache_key, data, timeout=300)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{request.user.id}',
            {
                'type': 'update_dashboard',
                'balance': str(wallet.balance),  # Convert Decimal to string for JSON
            }
        )
    return render(request, 'dashboard.html', data)

def referral_signup(request, username):
    referrer = get_object_or_404(User, username=username)
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST.get('email', '')  # Optional email
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        else:
            new_user = User.objects.create_user(username=username, email=email, password=password)
            Wallet.objects.get_or_create(user=new_user)  # Create wallet for new user
            referrer_wallet, _ = Wallet.objects.get_or_create(user=referrer)
            referrer_wallet.balance += 10  # Credit 10 points
            referrer_wallet.save()
            Transaction.objects.create(
                wallet=referrer_wallet,
                amount=10,
                description=f"Referral bonus for {new_user.username}"
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{referrer.id}',
                {
                    'type': 'update_dashboard',
                    'balance': str(referrer_wallet.balance),
                }
            )
            messages.success(request, "Sign up successful! Please log in.")
            return redirect('login')
    return render(request, 'referral_signup.html', {'referrer': referrer.username})

@login_required
def redeem_credits(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wallet = Wallet.objects.get_or_create(user=request.user)[0]

    # Check if the user owns the product
    if product.seller != request.user:
        messages.error(request, "You can only redeem credits for your own products.")
        return redirect('dashboard')

    if request.method == 'POST':
        credits = int(request.POST.get('credits', 0))
        if credits <= 0:
            messages.error(request, "Please enter a valid number of credits.")
        elif wallet.balance >= credits:
            wallet.balance -= credits
            product.free_views_remaining += credits
            wallet.save()
            product.save()
            Transaction.objects.create(
                wallet=wallet,
                amount=-credits,
                description=f"Redeemed {credits} credits for {product.title}"
            )
            messages.success(request, f"Successfully redeemed {credits} credits for {product.title}.")

            # Broadcast to user's dashboard (if applicable)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{request.user.id}',
                {
                    'type': 'update_dashboard',
                    'balance': str(wallet.balance),
                }
            )
            return redirect('dashboard')
        else:
            messages.error(request, "Insufficient credits.")
    
    return render(request, 'redeem_credits.html', {
        'product': product,
        'wallet': wallet,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, CustomLoginForm, ProductForm
from .models import Product, ProductTag


def index(request):
    """Home page view"""
    return render(request, 'index.html')


def about(request):
    """About page view"""
    return render(request, 'about.html')


def producers(request):
    """Producers page view"""
    return render(request, 'producers.html')


def buyers(request):
    """Buyers page view"""
    return render(request, 'buyers.html')


def calendar(request):
    """Calendar page view"""
    return render(request, 'calendar.html')


def contact(request):
    """Contact page view"""
    return render(request, 'contact.html')


def signup_view(request):
    """User registration view - creates signup request for admin approval"""
    if request.user.is_authenticated:
        return redirect('main:index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            signup_request = form.save()
            messages.success(
                request, 
                'Kayıt talebiniz alındı! Hesabınız yönetici onayından sonra aktif hale gelecektir. '
                'E-posta adresinize onay durumu hakkında bilgi gönderilecektir.'
            )
            return redirect('main:index')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = SignUpForm()
    
    return render(request, 'auth/signup.html', {'form': form})



def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Hoş geldiniz, {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'main:dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('main:index')


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'auth/profile.html')


@login_required
def dashboard_view(request):
    """Main dashboard view - redirects to appropriate dashboard based on user type"""
    try:
        profile = request.user.profile
        
        # If user is both producer and buyer, show a combined view or let them choose
        if profile.is_producer and profile.is_buyer:
            # For now, default to producer dashboard
            return redirect('main:producer_dashboard')
        elif profile.is_producer:
            return redirect('main:producer_dashboard')
        elif profile.is_buyer:
            return redirect('main:buyer_dashboard')
        else:
            messages.warning(request, 'Profiliniz henüz tamamlanmamış.')
            return redirect('main:profile')
    except:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')


@login_required
def producer_dashboard_view(request):
    """Producer dashboard view"""
    try:
        profile = request.user.profile
        if not profile.is_producer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('main:dashboard')
        
        # Get producer's products
        products = Product.objects.filter(producer=request.user).order_by('-created_at')
        
        context = {
            'profile': profile,
            'products': products,
            'total_products': products.count(),
            'active_products': products.filter(is_active=True).count(),
        }
        
        return render(request, 'user_area/producer_dashboard.html', context)
    except:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')


@login_required
def buyer_dashboard_view(request):
    """Buyer dashboard view"""
    try:
        profile = request.user.profile
        if not profile.is_buyer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('main:dashboard')
        
        # Get all approved and active products (buyers can browse products)
        all_products = Product.objects.filter(is_active=True, approval_status='approved').order_by('-created_at')
        
        context = {
            'profile': profile,
            'products': all_products,
            'total_products': all_products.count(),
        }
        
        return render(request, 'user_area/buyer_dashboard.html', context)
    except:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')


@login_required
def add_product_view(request):
    """Add new product view (producers only)"""
    try:
        profile = request.user.profile
        if not profile.is_producer:
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return redirect('main:dashboard')
    except:
        messages.error(request, 'Profil bilgileriniz bulunamadı.')
        return redirect('main:index')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.producer = request.user
            product.approval_status = 'pending'  # Set to pending for admin approval
            product.save()
            form.save_m2m()  # Save many-to-many relationships (tags)
            messages.success(request, 'Ürün başarıyla eklendi! Yönetici onayından sonra yayınlanacaktır.')
            return redirect('main:producer_dashboard')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ProductForm()
    
    return render(request, 'user_area/add_product.html', {'form': form})


@login_required
def edit_product_view(request, product_id):
    """Edit product view (producers only)"""
    product = get_object_or_404(Product, id=product_id, producer=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla güncellendi!')
            return redirect('main:producer_dashboard')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'user_area/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product_view(request, product_id):
    """Delete product view (producers only)"""
    product = get_object_or_404(Product, id=product_id, producer=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Ürün başarıyla silindi!')
        return redirect('main:producer_dashboard')
    
    return render(request, 'user_area/delete_product.html', {'product': product})


@login_required
def product_detail_view(request, product_id):
    """Product detail view"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has permission to view this product
    # Producers can see their own products (any status), buyers can see approved active products
    can_view = False
    if request.user == product.producer:
        can_view = True
    elif hasattr(request.user, 'profile') and request.user.profile.is_buyer and product.is_active and product.approval_status == 'approved':
        can_view = True
    
    if not can_view:
        messages.error(request, 'Bu ürünü görüntüleme yetkiniz yok.')
        return redirect('main:dashboard')
    
    context = {
        'product': product,
        'is_owner': request.user == product.producer,
    }
    
    return render(request, 'user_area/product_detail.html', context)

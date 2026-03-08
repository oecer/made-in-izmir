from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ExpoSignupForm
from .models import Expo, ExpoSignup


def calendar(request):
    """Calendar page view - public view of all expos"""
    from django.utils import timezone

    expos = Expo.objects.filter(is_active=True).order_by('start_date')

    today = timezone.now().date()
    upcoming_expos = expos.filter(start_date__gte=today)
    past_expos = expos.filter(start_date__lt=today)

    context = {
        'upcoming_expos': upcoming_expos,
        'past_expos': past_expos,
    }

    return render(request, 'calendar.html', context)


@login_required
def dashboard_calendar_view(request):
    """Dashboard calendar view - shows expos with signup functionality"""
    from django.utils import timezone

    expos = Expo.objects.filter(is_active=True).order_by('start_date')

    today = timezone.now().date()
    upcoming_expos = expos.filter(start_date__gte=today)
    past_expos = expos.filter(start_date__lt=today)

    tenant = request.user.profile.tenant
    user_signups = ExpoSignup.objects.filter(tenant=tenant).select_related('expo') if tenant else ExpoSignup.objects.none()
    user_signup_expo_ids = set(user_signups.values_list('expo_id', flat=True))
    confirmed_count = user_signups.filter(status='confirmed').count()

    context = {
        'upcoming_expos': upcoming_expos,
        'past_expos': past_expos,
        'user_signups': user_signups,
        'user_signup_expo_ids': user_signup_expo_ids,
        'confirmed_count': confirmed_count,
    }

    return render(request, 'user_area/dashboard_calendar.html', context)


@login_required
def expo_signup_view(request, expo_id):
    """Expo signup view - allows users to sign up for an expo"""
    expo = get_object_or_404(Expo, id=expo_id, is_active=True)

    if not expo.is_registration_open():
        messages.error(request, 'Bu fuar için kayıt süresi dolmuştur.')
        return redirect('expos:dashboard_calendar')

    profile = request.user.profile
    if profile.tenant_role == 'read_only':
        messages.error(request, 'Salt okunur kullanıcılar fuara kayıt olamaz.')
        return redirect('expos:dashboard_calendar')

    tenant = profile.tenant
    existing_signup = ExpoSignup.objects.filter(expo=expo, tenant=tenant).first()
    if existing_signup:
        messages.warning(request, 'Bu fuara firmanız zaten kayıt oldu.')
        return redirect('expos:dashboard_calendar')

    if request.method == 'POST':
        form = ExpoSignupForm(request.POST, user=request.user)
        if form.is_valid():
            signup = form.save(commit=False)
            signup.expo = expo
            signup.user = request.user
            signup.tenant = tenant
            signup.save()

            if form.cleaned_data.get('uses_listed_products'):
                signup.selected_products.set(form.cleaned_data.get('selected_products'))

            messages.success(request, f'{expo.title_tr} fuarına başarıyla kayıt oldunuz!')
            return redirect('expos:dashboard_calendar')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = ExpoSignupForm(user=request.user)

    return render(request, 'user_area/expo_signup.html', {'expo': expo, 'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import BuyerSignUpForm, CreatorSignUpForm
from .models import User, Referral
from content.models import SiteSettings

def buyer_register(request):
    ref_code = request.GET.get('ref')
    
    if request.method == 'POST':
        form = BuyerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'buyer'
            user.save()
            
            if ref_code:
                try:
                    referrer = User.objects.get(username=ref_code)
                    Referral.objects.create(referrer=referrer, referred=user)
                    
                    # Add referral commission to referrer's balance
                    settings = SiteSettings.get_settings()
                    commission_amount = settings.referral_commission
                    referrer.balance += commission_amount
                    referrer.save()
                    
                    messages.success(request, f'You were referred by {ref_code}! + Rs{commission_amount} added to your balance')
                except User.DoesNotExist:
                    messages.warning(request, 'Invalid referral code')
            
            login(request, user)
            return redirect('buyer_dashboard')
    else:
        form = BuyerSignUpForm()
    
    return render(request, 'registration/buyer_register.html', {'form': form, 'ref_code': ref_code})

def creator_register(request):
    ref_code = request.GET.get('ref')
    
    if request.method == 'POST':
        form = CreatorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'creator'
            user.save()
            
            if ref_code:
                try:
                    referrer = User.objects.get(username=ref_code)
                    Referral.objects.create(referrer=referrer, referred=user)
                    messages.success(request, f'You were referred by {ref_code}!')
                except User.DoesNotExist:
                    messages.warning(request, 'Invalid referral code')
            
            login(request, user)
            return redirect('creator_dashboard')
    else:
        form = CreatorSignUpForm()
    
    return render(request, 'registration/creator_register.html', {'form': form, 'ref_code': ref_code})
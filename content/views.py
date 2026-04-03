from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Content, Order, Video, PaymentMethod, CreatorPayoutInfo, SiteMessage
from .forms import ContentForm, VideoFormSet
from .models import Content

def home(request):
    contents = Content.objects.filter(is_active=True, is_approved=True)[:6]
    admin_message = SiteMessage.objects.filter(is_active=True).first()
    return render(request, 'content/home.html', {
        'contents': contents,
        'admin_message': admin_message.message if admin_message else None
    })

def content_list(request):
    contents = Content.objects.filter(is_active=True, is_approved=True)
    return render(request, 'content/content_list.html', {'contents': contents})

def content_detail(request, content_id):
    content = get_object_or_404(Content, id=content_id, is_active=True)
    return render(request, 'content/content_detail.html', {'content': content})

@login_required
def add_content(request):
    if request.user.role != 'creator':
        return redirect('home')
    
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.creator = request.user
            content.is_approved = False  # Needs admin approval
            content.save()
            
            formset = VideoFormSet(request.POST, request.FILES, instance=content)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Content submitted! Admin will review and approve it soon.')
                return redirect('creator_dashboard')
            else:
                content.delete()
                messages.error(request, 'Error uploading videos. Please try again.')
    else:
        form = ContentForm()
        formset = VideoFormSet()
    
    return render(request, 'content/add_content.html', {'form': form, 'formset': formset})

@login_required
def buyer_dashboard(request):
    # Get user's purchased orders
    orders = Order.objects.filter(buyer=request.user).select_related('content')
    
    # Get all available content (for recommendations)
    available_content = Content.objects.filter(is_active=True, is_approved=True).exclude(
        id__in=orders.values_list('content_id', flat=True)
    )[:6]
    
    settings = SiteSettings.get_settings()
    
    return render(request, 'content/buyer_dashboard.html', {
        'orders': orders,
        'available_content': available_content,
        'min_withdrawal': settings.min_withdrawal,
        'referral_commission': settings.referral_commission
    })

@login_required
def buy_content(request, content_id):
    content = get_object_or_404(Content, id=content_id, is_active=True)
    
    if request.user.role != 'buyer':
        messages.error(request, 'Only buyers can purchase content.')
        return redirect('content_list')
    
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id')
        payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id)
        
        Order.objects.create(
            buyer=request.user,
            content=content,
            payment_method=payment_method,
            transaction_id=transaction_id,
            amount_paid=content.price,
            commission_percentage=10.00,
            status='pending'
        )
        messages.success(request, 'Payment submitted! Admin will verify it soon.')
        return redirect('buyer_dashboard')
    
    return render(request, 'content/buy_content.html', {
        'content': content,
        'payment_methods': payment_methods,
    })

@login_required
def creator_payout_info(request):
    if request.user.role != 'creator':
        return redirect('home')
    
    try:
        payout_info = request.user.creatorpayoutinfo
    except CreatorPayoutInfo.DoesNotExist:
        payout_info = None
    
    if request.method == 'POST':
        form = CreatorPayoutForm(request.POST, instance=payout_info)
        if form.is_valid():
            payout = form.save(commit=False)
            payout.creator = request.user
            payout.save()
            messages.success(request, 'Payout information saved.')
            return redirect('creator_dashboard')
    else:
        form = CreatorPayoutForm(instance=payout_info)
    
    return render(request, 'content/creator_payout_form.html', {'form': form})

@login_required
def add_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user, status='verified')
    review = getattr(order, 'review', None)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('buyer_dashboard')
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'content/review_form.html', {'form': form, 'order': order})

@login_required
def report_content(request, content_id):
    content = get_object_or_404(Content, pk=content_id)
    
    if request.user.role != 'buyer':
        messages.error(request, 'Only buyers can report content.')
        return redirect('content_list')
    
    existing = Report.objects.filter(content=content, buyer=request.user, resolved=False).first()
    if existing:
        messages.warning(request, 'You have already reported this content.')
        return redirect('content_list')
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.content = content
            report.buyer = request.user
            report.save()
            messages.success(request, 'Thank you for reporting.')
            return redirect('content_list')
    else:
        form = ReportForm()
    
    return render(request, 'content/report_form.html', {'form': form, 'content': content})

def content_detail(request, content_id):
    content = get_object_or_404(Content, id=content_id, is_active=True)
    return render(request, 'content/content_detail.html', {'content': content})

from .models import SiteSettings, WithdrawalRequest
from .forms import WithdrawalForm

@login_required
def request_withdrawal(request):
    settings = SiteSettings.get_settings()
    
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            if amount < settings.min_withdrawal:
                messages.error(request, f'Minimum withdrawal amount is Rs {settings.min_withdrawal}')
                return redirect('request_withdrawal')
            
            if amount > request.user.balance:
                messages.error(request, f'Insufficient balance. Your balance is Rs {request.user.balance}')
                return redirect('request_withdrawal')
            
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user
            withdrawal.save()
            
            messages.success(request, 'Withdrawal request submitted successfully!')
            return redirect('buyer_dashboard')
    else:
        form = WithdrawalForm()
    
    return render(request, 'content/withdrawal_form.html', {
        'form': form,
        'balance': request.user.balance,
        'min_withdrawal': settings.min_withdrawal
    })

@login_required
def withdrawal_history(request):
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'content/withdrawal_history.html', {'withdrawals': withdrawals})

@login_required
def view_content_videos(request, content_id):
    content = get_object_or_404(Content, id=content_id, is_active=True)
    
    # Check if user has purchased this content
    has_purchased = Order.objects.filter(buyer=request.user, content=content, status='verified').exists()
    
    if not has_purchased:
        messages.error(request, 'You have not purchased this content.')
        return redirect('buyer_dashboard')
    
    return render(request, 'content/view_videos.html', {'content': content})

@login_required
def creator_dashboard(request):
    if request.user.role != 'creator':
        return redirect('home')
    
    contents = Content.objects.filter(creator=request.user)
    return render(request, 'content/creator_dashboard.html', {
        'user': request.user,
        'contents': contents
    })

from django.http import FileResponse, Http404
import os

@login_required
def download_zip(request, content_id):
    content = get_object_or_404(Content, id=content_id, is_active=True)
    
    # Check if user has purchased this content
    has_purchased = Order.objects.filter(buyer=request.user, content=content, status='verified').exists()
    
    if not has_purchased:
        messages.error(request, 'You have not purchased this content.')
        return redirect('buyer_dashboard')
    
    if not content.zip_file or not content.zip_file.path:
        raise Http404("ZIP file not available")
    
    # Serve the file for download
    response = FileResponse(open(content.zip_file.path, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{content.title}.zip"'
    return response
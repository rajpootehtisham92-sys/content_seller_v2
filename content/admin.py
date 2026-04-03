from django.contrib import admin
from .models import Content, PaymentMethod, Order, CreatorPayoutInfo, SiteMessage, Video
from .models import SiteSettings
from .models import WithdrawalRequest

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ('video_file', 'title', 'order')
    ordering = ('order',)

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'price', 'content_type', 'is_approved', 'is_active', 'created_at')
    list_filter = ('is_approved', 'is_active', 'content_type')
    search_fields = ('title', 'description')
    list_editable = ('is_approved', 'is_active')
    inlines = [VideoInline]

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'method_type', 'account_title', 'account_number', 'is_active')
    list_filter = ('method_type', 'is_active')
    search_fields = ('name', 'account_title', 'account_number')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'content', 'transaction_id', 'status', 'amount_paid', 'commission_percentage', 'created_at')
    list_filter = ('status',)
    actions = ['mark_as_verified']
    readonly_fields = ('created_at',)

    def mark_as_verified(self, request, queryset):
        queryset.update(status='verified')
    mark_as_verified.short_description = "Mark selected orders as verified"

@admin.register(CreatorPayoutInfo)
class CreatorPayoutInfoAdmin(admin.ModelAdmin):
    list_display = ('creator', 'payout_type', 'account_title', 'account_number')
    list_filter = ('payout_type',)
    search_fields = ('creator__username', 'account_title', 'account_number')

@admin.register(SiteMessage)
class SiteMessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'is_active', 'updated_at')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('content', 'title', 'order', 'uploaded_at')
    list_filter = ('content',)
    search_fields = ('title',)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('referral_commission', 'admin_commission', 'min_withdrawal')
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status',)
    actions = ['approve_withdrawals']

    def approve_withdrawals(self, request, queryset):
        for withdrawal in queryset:
            withdrawal.status = 'approved'
            withdrawal.processed_at = timezone.now()
            withdrawal.processed_by = request.user
            withdrawal.save()
            # Deduct from user balance
            user = withdrawal.user
            user.balance -= withdrawal.amount
            user.save()
        self.message_user(request, f"{queryset.count()} withdrawals approved")
    approve_withdrawals.short_description = "Approve selected withdrawals"
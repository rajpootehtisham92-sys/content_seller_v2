from django.db import models
from django.conf import settings

class Content(models.Model):
    CONTENT_TYPES = (
        ('link', 'Link'),
        ('video', 'Video'),
    )
    zip_file = models.FileField(upload_to='content_zips/', blank=True, null=True, help_text="Upload a ZIP file containing all videos")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'creator'})
    title = models.CharField(max_length=200)
    description = models.TextField()
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    link_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False, help_text="Admin approval required before buyers can see")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.title

class PaymentMethod(models.Model):
    METHOD_TYPES = (
        ('bank', 'Bank Account'),
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'Easypaisa'),
        ('other', 'Other'),
    )
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES, default='bank')
    name = models.CharField(max_length=100)
    account_title = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    iban = models.CharField(max_length=34, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    branch_code = models.CharField(max_length=50, blank=True)
    additional_details = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.account_title}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('cancelled', 'Cancelled'),
    )
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def creator_share(self):
        return self.amount_paid * (1 - self.commission_percentage / 100)

    def __str__(self):
        return f"Order {self.id} by {self.buyer.username}"

class CreatorPayoutInfo(models.Model):
    PAYOUT_TYPES = (
        ('bank', 'Bank Account'),
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'Easypaisa'),
        ('other', 'Other'),
    )
    creator = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'creator'})
    payout_type = models.CharField(max_length=20, choices=PAYOUT_TYPES, default='bank')
    account_title = models.CharField(max_length=200)
    account_number = models.CharField(max_length=100)
    iban = models.CharField(max_length=34, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    branch_code = models.CharField(max_length=50, blank=True)
    additional_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.creator.username} - {self.account_title}"

class SiteMessage(models.Model):
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin Message"
        verbose_name_plural = "Admin Messages"

    def __str__(self):
        return self.message[:50]

class Video(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='videos')
    video_file = models.FileField(upload_to='videos/')
    title = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

class SiteSettings(models.Model):
    referral_commission = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, help_text="Percentage for referral earnings")
    admin_commission = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Percentage admin takes from each sale")
    min_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=500.00, help_text="Minimum amount for withdrawal request")
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return "Site Settings"

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[
        ('bank', 'Bank Transfer'),
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'EasyPaisa'),
    ])
    account_details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Rs{self.amount} - {self.status}"
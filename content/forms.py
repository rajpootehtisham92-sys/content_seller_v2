from django import forms
from .models import Content, Video, WithdrawalRequest

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'description', 'content_type', 'link_url', 'video_file', 'zip_file', 'price', 'is_active']

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['video_file', 'title', 'order']

# This allows up to 5 videos per content
VideoFormSet = forms.inlineformset_factory(Content, Video, form=VideoForm, extra=5, can_delete=True)

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'payment_method', 'account_details']
        widgets = {
            'account_details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your bank account details, JazzCash number, or EasyPaisa number'}),
        }
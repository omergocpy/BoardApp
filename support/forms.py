# myapp/forms.py
from django import forms
from .models import SupportRequest, Message

class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['subject', 'message', 'attachment']
        labels = {
            'subject': 'Konu',
            'message': 'Mesaj',
            'attachment': 'Dosya Eki'
        }
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        labels = {
            'content': 'Mesaj İçeriği',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Mesajınızı yazın...'
            }),
        }

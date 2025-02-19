from django import forms
from .models import SupportRequest, Message

class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['category', 'subject', 'message']
        labels = {
            'category': 'Kategori',
            'subject': 'Konu',
            'message': 'Mesaj',
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
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

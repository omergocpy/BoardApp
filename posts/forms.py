# myapp/forms.py
from django import forms
from .models import Post, Comment, Rating, Poll, PollOption
from users.models import Progress

class PostForm(forms.ModelForm):
    # 4 adet anket seçeneği (opsiyonel)
    option1 = forms.CharField(max_length=100, required=False, label="Seçenek 1")
    option2 = forms.CharField(max_length=100, required=False, label="Seçenek 2")
    option3 = forms.CharField(max_length=100, required=False, label="Seçenek 3")
    option4 = forms.CharField(max_length=100, required=False, label="Seçenek 4")

    class Meta:
        model = Post
        fields = [
            'content', 'post_type',
            'media',
            'is_bold', 'text_color', 'bg_color'
        ]
        labels = {
            'content': 'Gönderi İçeriği',
            'post_type': 'Gönderi Türü',
            'media': 'Medya (Foto, Video)',
            'is_bold': 'Kalın Yazı',
            'text_color': 'Yazı Rengi',
            'bg_color': 'Arka Plan Rengi'
        }
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Bir Gönderi Ekle..'}
            ),
            'post_type': forms.Select(attrs={'class': 'form-control'}),
            'media': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_bold': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'bg_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Varsayılan değerleri gizle veya göster (örneğin metin rengi, arka plan)
        # Tek tek JS ile de kontrol edilebilir.

    def save(self, commit=True):
        """Anket seçenekleri varsa Poll ve PollOption oluştur."""
        instance = super().save(commit=False)
        instance.user = self.user

        if commit:
            # 1) Post nesnesini veritabanına kaydediyoruz (artık bir pk'si var).
            instance.save()

            # 2) Eğer post_type 'poll' ise Poll ve PollOptionları oluştur
            if instance.post_type == 'poll':
                poll, _ = Poll.objects.get_or_create(post=instance)
                # Form alanlarından anket seçeneklerini al
                opt1 = self.cleaned_data.get('option1')
                opt2 = self.cleaned_data.get('option2')
                opt3 = self.cleaned_data.get('option3')
                opt4 = self.cleaned_data.get('option4')

                for opt_text in [opt1, opt2, opt3, opt4]:
                    if opt_text:  # Boş olmayan seçenekleri ekle
                        PollOption.objects.create(poll=poll, text=opt_text)

        return instance



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Yorum Ekle...'
            }),
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.Select(
                choices=[(i, i) for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
        }

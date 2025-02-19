from django import forms
from .models import Post, Comment, Rating
from users.models import Progress

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'media']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Bir Gönderi Ekle..'}),
            'media': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the user object
        super().__init__(*args, **kwargs)

        # Ensure user is authenticated before checking their progress
        if user and user.is_authenticated:
            # Get or create the user's progress
            progress, created = Progress.objects.get_or_create(user=user)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Yorum Ekle...',
            }),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-control'}),
        }

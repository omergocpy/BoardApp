from django import forms
from .models import CustomUser, RegistrationCode

class RegisterForm(forms.ModelForm):
    registration_code = forms.CharField(
        label='Kayıt Kodu', 
        widget=forms.TextInput(attrs={'class': 'form-control code-input mb-3', 'maxlength': '6', 'placeholder': 'Kayıt Kodu'})
    )
    registration_password = forms.CharField(
        label='Kayıt Şifresi', 
        widget=forms.PasswordInput(attrs={'class': 'form-control code-input mb-3', 'maxlength': '6', 'placeholder': 'Kayıt Şifresi'})
    )
    gender = forms.ChoiceField(
        choices=[('male', 'Erkek'), ('female', 'Kadın'), ('other', 'Diğer')],
        widget=forms.Select(attrs={'class': 'form-control mb-3'})
    )
    avatar = forms.CharField(
        widget=forms.HiddenInput()  
    )
    password1 = forms.CharField(
        label='Şifre', 
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Şifre'})
    )
    password2 = forms.CharField(
        label='Şifreyi Tekrar Gir', 
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Şifreyi Tekrar Gir'})
    )

    class Meta:
        model = CustomUser
        fields = ['registration_code', 'registration_password', 'gender', 'avatar', 'password1', 'password2']

    def clean_registration_code(self):
        code = self.cleaned_data.get('registration_code')
        try:
            registration_code = RegistrationCode.objects.get(code=code, used=False)
        except RegistrationCode.DoesNotExist:
            raise forms.ValidationError("Geçersiz veya kullanılmış kayıt kodu.")
        return code

    def clean_registration_password(self):
        code = self.cleaned_data.get('registration_code')
        password = self.cleaned_data.get('registration_password')
        try:
            registration_code = RegistrationCode.objects.get(code=code, used=False)
            if registration_code.password != password:
                raise forms.ValidationError("Kayıt şifresi geçersiz.")
        except RegistrationCode.DoesNotExist:
            raise forms.ValidationError("Geçersiz kayıt kodu veya şifre.")
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Şifreler eşleşmiyor.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # Kayıt kodunu kullanılmış olarak işaretle
            registration_code = RegistrationCode.objects.get(code=self.cleaned_data['registration_code'])
            registration_code.used = True
            registration_code.save()
            user.registration_code_used = registration_code.code  # Kullanılan kayıt kodunu kaydet
            user.save()
        return user

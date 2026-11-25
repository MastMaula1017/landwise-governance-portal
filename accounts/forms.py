from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'Last name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'official@institution.gov.in / name@univ.edu'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'Create strong password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'Confirm password'
    }))
    
    # Profile Fields
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES[1:],  # Exclude Admin from public registration
        initial=Profile.ROLE_RESEARCHER,
        widget=forms.Select(attrs={'class': 'form-select lw-input'})
    )
    institution = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'e.g. National Institute of Land Administration, Ministry, University'
    }))
    designation = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'e.g. Senior Research Fellow, Director of Cadastral Policy'
    }))
    state_region = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'e.g. Maharashtra, New Delhi, Odisha'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control lw-input', 'placeholder': 'Unique username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            profile = user.profile
            profile.role = self.cleaned_data.get('role', Profile.ROLE_PUBLIC)
            profile.institution = self.cleaned_data.get('institution', '')
            profile.designation = self.cleaned_data.get('designation', '')
            profile.state_region = self.cleaned_data.get('state_region', '')
            profile.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'Username or Email',
        'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control lw-input',
        'placeholder': 'Password'
    }))


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control lw-input'}))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control lw-input'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control lw-input'}))

    class Meta:
        model = Profile
        fields = ['institution', 'designation', 'state_region', 'phone', 'bio']
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control lw-input'}),
            'designation': forms.TextInput(attrs={'class': 'form-control lw-input'}),
            'state_region': forms.TextInput(attrs={'class': 'form-control lw-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-control lw-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-control lw-input', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            user = profile.user
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save()
            profile.save()
        return profile

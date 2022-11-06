from django import forms

from .models import CustomUserModel, Profile, ProfilePhotosModel


class UploadPhotoForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-select'}))
    class Meta:
        model = ProfilePhotosModel
        exclude = ['profile', 'date']


class SignupForm(forms.ModelForm):

    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'id': 'username',
                                                                            'placeholder':'Username'}))
    password = forms.CharField(max_length=255, widget=forms.PasswordInput(attrs={'id': 'password',
                                                                                 'placeholder': 'Password'}))
    email = forms.EmailField(max_length=2500, widget=forms.EmailInput(attrs={'id': 'email',
                                                                             'placeholder': 'Email'}))

    class Meta:
        model = CustomUserModel
        fields = ['username', 'email']
        exclude = ['password', 'password1', 'password2']


class ProfileSetupForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',
                                                               'id': 'firstName'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'id': 'lastName'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'id': 'address'}))

    about = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'id': 'about'}))

    # profile_photo = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class':'form-select'}))
    gender = forms.ChoiceField(choices=(('1', 'Female'), ('0', 'Male')), widget=forms.Select(attrs={'class': 'form-select'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hobby = forms.MultipleChoiceField(choices=(('Dancing', 'Dancing'), ('Cooking', 'Cooking'), ('IT', 'IT')), widget=forms.SelectMultiple)
    class Meta:
        model = Profile
        exclude = ['user']
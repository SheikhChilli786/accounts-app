from django import forms
from accounts import models
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, UserChangeForm,PasswordResetForm
from django.contrib.auth import  get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q  # Add this import
from django.db import IntegrityError

User = get_user_model()

class SaveUser(UserCreationForm):
    pakistan_phone_validator = RegexValidator(
        regex=r'^\+?92[0-9]{10}$',
        message='Enter a valid phone number.',
    )
    phone_number = forms.CharField(
        label='Phone Number',
        validators=[pakistan_phone_validator],
        required=True
    )
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.",required=False)
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.",required=False)
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.",required=False)
    question = forms.TextInput()
    answer = forms.TextInput()
    password1 = forms.CharField(max_length=250)
    password2 = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ( 'username','phone_number','password1', 'password2','question','answer','email','first_name', 'last_name',)

class UpdateUser(UserChangeForm):
    pakistan_phone_validator = RegexValidator(
        regex=r'^(?:(?:\+92)|(?:0))(?:(?:3[0-9]{9})|(?:[1-9][0-9]{9}))$',
        message='Enter a valid phone number.',
    )
    phone_number = forms.CharField(
        label='Phone Number',
        validators=[pakistan_phone_validator],
        required=True
    )
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    question = forms.TextInput()
    answer = forms.TextInput()
    class Meta:
        model = User
        fields = ('username','phone_number','first_name', 'last_name','question','answer')

class SaveParty(forms.ModelForm):
    name = forms.CharField(max_length=255,required=True)
    address = forms.TextInput()
    pakistan_phone_validator = RegexValidator(
        regex=r'^(?:(?:\+92)|(?:0))(?:(?:3[0-9]{9})|(?:[1-9][0-9]{9}))$',
        message='Enter a valid phone number.',
    )
    phone_number = forms.CharField(
        label='Phone Number',
        validators=[pakistan_phone_validator],
        required=False
    )
    class Meta:
        model = models.Party
        fields = ['user', 'name', 'phone_number', 'address']

    


class SaveForm(forms.ModelForm):
    description = forms.TextInput()
    debit = forms.IntegerField(required=False)
    credit = forms.IntegerField(required=False)
    form = forms.IntegerField(required=False)
    party = forms.IntegerField(required=False)
    class Meta:
        model = models.Transaction
        fields = ['description','debit','credit','party','form']
    

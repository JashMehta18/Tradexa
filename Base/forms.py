from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django import forms
from crispy_forms.helper import FormHelper
import re


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields= ['username','email','password1','password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'"%s" is already in use.' % username)


    def clean_email(self):
        regex = "^[a-z0-9]+(?!.*(?:\+{2,}|\-{2,}|\.{2,}))(?:[\.+\-]{0,1}[a-z0-9])*@gmail\.com$"
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError("This field is required.")
        else:
            try:
                match = User.objects.get(email=email)
            except User.DoesNotExist:
                if not re.fullmatch(regex, email):
                    raise forms.ValidationError("Enter Correct Gmail Id")
                return email

         # A user was found with this as a username, raise an error.
            raise forms.ValidationError('This Email Id is already in use.')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        print(password1,"&&",password2)
        if password1 != password2:
            raise forms.ValidationError("Your Passwords don't match")


class ContactForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=12)
    message = forms.CharField(max_length=200, required=True)

    
class UserUpdateForm(forms.ModelForm):
    # username = forms.CharField(required=True, label="Username",
    #                          widget=forms.TextInput(
    #                              attrs={'placeholder': 'john_doe', 'class': 'form-control', 'id' : 'floatingInput'}))
                                
    email = forms.EmailField(required=True,label="Email",
                             widget=forms.TextInput(
                                 attrs={'placeholder': 'john.doe@gmail.com', 'class': 'form-control',"id":"floatingInput"}))

    # phone = forms.CharField(required=False,max_length=12,label="Phone",
    #                          widget=forms.TextInput(
    #                              attrs={'placeholder': '#', 'class': 'form-control',"id":"floatingInput"}))

    # street = forms.CharField(required=False,label="Street",
    #                          widget=forms.TextInput(
    #                              attrs={'placeholder': '#', 'class': 'form-control',"id":"floatingInput"}))

    # city = forms.CharField(required=False,label="City",
    #                          widget=forms.TextInput(
    #                              attrs={'placeholder': '#', 'class': 'form-control',"id":"floatingInput"}))

    # state = forms.CharField(required=False,label="State",
    #                          widget=forms.TextInput(
    #                              attrs={'placeholder': '#', 'class': 'form-control',"id":"floatingInput"}))

    # zip = forms.CharField(required=False,label="Zip Code",
    #                          widget=forms.TextInput(
    #                              attrs={'placeholder': '#', 'class': 'form-control',"id":"floatingInput"}))


    class Meta:
        model = User
        fields = ['first_name', 'last_name', "email" ,"username"]

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'"%s" is already in use.' % username)

    
    # def clean_email(self):
    #     regex = "^[a-z0-9]+(?!.*(?:\+{2,}|\-{2,}|\.{2,}))(?:[\.+\-]{0,1}[a-z0-9])*@gmail\.com$"
    #     email = self.cleaned_data['email']
    #     if not email:
    #         raise forms.ValidationError("This field is required.")
    #     else:
    #         try:
    #             match = User.objects.get(email=email)
    #         except User.DoesNotExist:
    #             if not re.fullmatch(regex, email):
    #                 raise forms.ValidationError("Enter Correct Gmail Id")
    #             return email

         # A user was found with this as a username, raise an error.
            # raise forms.ValidationError('This Email Id is already in use.')


class profileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image','phone_number','street','city','state','zip']

    # def clean_username(self):
    #     username = self.cleaned_data['username']
    #     try:
    #         user = User.objects.get(username=username)
    #     except User.DoesNotExist:
    #         return username
    #     raise forms.ValidationError(u'"%s" is already in use.' % username)

    
    def clean_email(self):
        regex = "^[a-z0-9]+(?!.*(?:\+{2,}|\-{2,}|\.{2,}))(?:[\.+\-]{0,1}[a-z0-9])*@gmail\.com$"
        email = self.cleaned_data['email']
        if not email:
            raise forms.ValidationError("This field is required.")
        else:
            try:
                match = User.objects.get(email=email)
            except User.DoesNotExist:
                if not re.fullmatch(regex, email):
                    raise forms.ValidationError("Enter Correct Gmail Id")
                return email

         # A user was found with this as a username, raise an error.
            raise forms.ValidationError('This Email Id is already in use.')
    
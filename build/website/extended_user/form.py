from django import forms


class RegisterNewUserForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'style': 'width:400px'}),
        required=True)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'style': 'width:400px'}),
        required=True)
    repeat_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'style': 'width:400px'}),
        required=True)

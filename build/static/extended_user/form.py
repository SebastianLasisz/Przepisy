from django import forms


class RegisterNewUserForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px', 'class': 'form-control'}),
        required=True)
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'style': 'width:400px', 'class': 'form-control'}),
        required=True)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'style': 'width:400px', 'class': 'form-control'}),
        required=True)
    repeat_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'style': 'width:400px', 'class': 'form-control'}),
        required=True)


class UserProfileForm(forms.Form):
    use_google = forms.BooleanField(required=False)
    use_trello = forms.BooleanField(required=False)
    trello_key = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=False)
    trello_board_name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=False)

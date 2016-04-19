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


class UserProfile(forms.Form):
    use_google = forms.BooleanField(required=False)
    google_calendar_name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=False)
    use_trello = forms.BooleanField(required=False)
    trello_key = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=False)
    trello_board_name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=False)

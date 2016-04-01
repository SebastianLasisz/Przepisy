from django import forms
import datetime


class AddNewRecipe(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)


class AddNewMeal(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)
    date = forms.DateField(initial=datetime.date.today)
    time = forms.TimeField(initial=datetime.datetime.now().strftime('%H:%M'))


class AddNewProductList(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)


class AddNewShoppingList(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)

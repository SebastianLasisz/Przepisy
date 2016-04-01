from django import forms
import datetime
from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class AddNewRecipe(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)
    description = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)
    private = forms.BooleanField()


class AddNewMeal(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:200px'}),
        required=True)
    date = forms.DateField(initial=datetime.date.today, widget=DateInput())
    time = forms.TimeField(initial=datetime.datetime.now().strftime('%H:%M'))


class AddNewProductList(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)


class AddNewShoppingList(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)

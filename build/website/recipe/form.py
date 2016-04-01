from django import forms
import datetime
from functools import partial
from django.forms.formsets import BaseFormSet

DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class AddIngredient(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)
    value = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)
    unit = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width:400px'}),
        required=True)


class AddNewRecipe(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddNewRecipe, self).__init__(*args, **kwargs)

        self.fields['name'] = forms.CharField(
            widget=forms.TextInput(attrs={'style': 'width:400px'}),
            required=True)
        self.fields['description'] = forms.CharField(
            widget=forms.TextInput(attrs={'style': 'width:400px'}),
            required=True)
        self.fields['private'] = forms.BooleanField()


class BaseLinkFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return


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

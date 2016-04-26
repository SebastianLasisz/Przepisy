from django import forms
from functools import partial
from django.forms.formsets import BaseFormSet
from recipe.models import *

DateInput = partial(forms.DateInput, {'class': 'datepicker form-control'})


class AddIngredient(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True)
    value = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True)
    unit = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True)


class AddNewRecipe(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddNewRecipe, self).__init__(*args, **kwargs)

        self.fields['name'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)
        self.fields['description'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)
        self.fields['Available to everyone'] = forms.BooleanField(initial=True, required=False)


class BaseLinkFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return


def get_recipes(username):
    choices_list = []
    queryset2 = Recipe.objects.filter(user=username, global_access=True)
    queryset = Recipe.objects.filter(global_access=False)
    for item in queryset:
        choices_list.insert(0, (item, item))
    for item in queryset2:
        choices_list.insert(0, (item, item))
    return choices_list


class AddNewMeal(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddNewMeal, self).__init__(*args, **kwargs)
        list_of_recipes = get_recipes(self.user)
        self.fields['name'] = forms.ChoiceField(choices=list_of_recipes,
                                                widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['date'] = forms.DateField(initial=datetime.date.today, widget=DateInput())
        self.fields['time'] = forms.TimeField(initial=datetime.datetime.now().strftime('%H:%M'),
                                              widget=forms.TextInput(attrs={'class': 'form-control'}))


class AddNewProductList(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddNewProductList, self).__init__(*args, **kwargs)

        self.fields['name'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)
        self.fields['description'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)


class AddNewShoppingList(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddNewShoppingList, self).__init__(*args, **kwargs)

        self.fields['name'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)
        self.fields['description'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)

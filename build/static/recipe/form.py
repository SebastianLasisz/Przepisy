from django import forms
from functools import partial
from django.forms.formsets import BaseFormSet
from recipe.models import *
from django_summernote.widgets import SummernoteWidget

DateInput = partial(forms.DateInput, {'class': 'datepicker form-control'})


class AddIngredient(forms.Form):
    product_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True)
    category_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True)
    quantity = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True)
    unit = forms.ModelChoiceField(queryset=Unit.objects.all().order_by('id'))


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
        self.fields['yields'] = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                                   required=True)
        self.fields['recipe_steps'] = forms.CharField(label="", min_length=3,
                                                      widget=SummernoteWidget(
                                                          attrs={'width': '100%', 'height': '300px',
                                                                 'placeholder': 'Body of the topic'}))
        self.fields['Available to everyone'] = forms.BooleanField(initial=True, required=False)


class BaseLinkFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


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
        self.fields['yields'] = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                                   required=True)
        self.fields['time'] = forms.TimeField(initial=datetime.datetime.now().strftime('%H:%M'),
                                              widget=forms.TextInput(attrs={'class': 'form-control'}))


class EditMeal(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EditMeal, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                              required=False)
        self.fields['date'] = forms.DateField(initial=datetime.date.today, widget=DateInput())
        self.fields['yields'] = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                                   required=True)
        self.fields['time'] = forms.TimeField(initial=datetime.datetime.now().strftime('%H:%M'),
                                              widget=forms.TextInput(attrs={'class': 'form-control'}))
        self.fields['name'].widget.attrs['disabled'] = 'disabled'


class AddNewShoppingList(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddNewShoppingList, self).__init__(*args, **kwargs)

        self.fields['name'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)


class AddNewProduct(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddNewProduct, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)
        self.fields['category'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)
        self.fields['quantity'] = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                                     required=True)
        self.fields['manufacturer'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)
        self.fields['quantity_in_box'] = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                                            required=True)
        self.fields['barcode'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=True)

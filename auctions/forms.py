from django import forms

class OrderForm(forms.Form):
    name = forms.CharField(label='Your Name', max_length=100)
    email = forms.EmailField(label='Your Email')
    phone_number = forms.CharField(label='Your Phone Number', max_length=15)
    address = forms.CharField(label='Your Address', widget=forms.Textarea)

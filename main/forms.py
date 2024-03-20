from django import forms

from main.models import Client, Mailing


class FormStyleMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ClientForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('is_active', 'user')


class MailingForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Mailing
        exclude = ('is_active', 'user', 'status', 'is_published')

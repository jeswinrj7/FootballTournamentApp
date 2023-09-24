from django import forms
from .models import Team
from django.forms import formset_factory
from django.core.exceptions import ValidationError

class TeamRegistrationForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    coach = forms.CharField(max_length=100, required=True)
    manager = forms.CharField(max_length=100, required=True)

    def clean(self):
        cleaned_data = super().clean()
        # Add custom validation for numericals in fields
        name = cleaned_data.get('name')
        if name and any(char.isdigit() for char in name):
            raise ValidationError('Team name should not contain numbers.')

class TeamMemberForm(forms.Form):
    member_name = forms.CharField(max_length=100,required=True)  # Adjust this to match your member field type

# Create a formset for the dynamic member fields ( For example, 11 players)
TeamMemberFormSet = formset_factory(TeamMemberForm, extra=11)
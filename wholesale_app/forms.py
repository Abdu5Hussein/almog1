# forms.py
from django import forms
from almogOil.models import ReturnPolicy ,TermsAndConditions
import json
import re

class ReturnPolicyForm(forms.ModelForm):
    class Meta:
        model = ReturnPolicy
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'overview': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'general_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'non_returnable_items': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'return_steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'refund_policy': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'exchange_policy': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'warranty_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'contact_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        }

class TermsAndConditionsForm(forms.ModelForm):
    class Meta:
        model = TermsAndConditions
        fields = "__all__"
        widgets = {
            "introduction": forms.Textarea(attrs={"rows": 5}),
            "acceptance_text": forms.Textarea(attrs={"rows": 5}),
            "contact_info": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize sections if instance exists
        if self.instance and hasattr(self.instance, 'sections'):
            for i, section in enumerate(self.instance.sections):
                self.fields[f'section_{i}_title'] = forms.CharField(
                    initial=section.get('title', ''),
                    label=f'Section {i+1} Title',
                    required=False
                )
                self.fields[f'section_{i}_content'] = forms.CharField(
                    initial=section.get('content', ''),
                    label=f'Section {i+1} Content',
                    widget=forms.Textarea(attrs={'rows': 5}),
                    required=False
                )

    def clean(self):
        cleaned_data = super().clean()
        sections = []
        
        # Collect all sections from the form data
        i = 0
        while True:
            title = self.data.get(f'section_{i}_title', '').strip()
            content = self.data.get(f'section_{i}_content', '').strip()
            
            # Stop if no more sections found
            if not title and not content and f'section_{i}_title' not in self.data:
                break
                
            if title or content:
                sections.append({
                    'title': title,
                    'content': content
                })
            i += 1
            
        cleaned_data['sections'] = sections
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sections = self.cleaned_data.get('sections', [])
        if commit:
            instance.save()
        return instance
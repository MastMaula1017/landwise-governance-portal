from django import forms
from .models import Document, Category, Tag


class DocumentUploadForm(forms.ModelForm):
    tag_input = forms.CharField(
        max_length=255, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control lw-input',
            'placeholder': 'e.g. Cadastral survey, Titling, FRA, Tenancy (or leave empty for auto-extraction)'
        }),
        help_text="Enter comma-separated keywords, or leave empty to auto-extract from PDF"
    )

    class Meta:
        model = Document
        fields = [
            'title', 'document_type', 'category', 'authors', 
            'institution', 'geography_region', 'publication_date', 
            'abstract', 'file'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control lw-input', 'placeholder': 'Title of the research paper or policy study'}),
            'document_type': forms.Select(attrs={'class': 'form-select lw-input'}),
            'category': forms.Select(attrs={'class': 'form-select lw-input'}),
            'authors': forms.TextInput(attrs={'class': 'form-control lw-input', 'placeholder': 'Lead authors (e.g. Dr. A. K. Rao, S. Nair)'}),
            'institution': forms.TextInput(attrs={'class': 'form-control lw-input', 'placeholder': 'e.g. Centre for Land Governance, NILA'}),
            'geography_region': forms.TextInput(attrs={'class': 'form-control lw-input', 'placeholder': 'e.g. National, Maharashtra, Odisha'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control lw-input', 'type': 'date'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control lw-input', 'rows': 5, 'placeholder': 'Comprehensive abstract or executive summary of research findings...'}),
            'file': forms.FileInput(attrs={'class': 'form-control lw-input', 'accept': '.pdf,.docx'}),
        }


class DocumentApprovalForm(forms.Form):
    ACTION_CHOICES = [
        ('approve', 'Approve & Publish to National Repository'),
        ('reject', 'Request Revisions / Reject Submission'),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect())
    rejection_reason = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={
            'class': 'form-control lw-input',
            'rows': 3,
            'placeholder': 'If requesting revision or rejecting, specify editorial feedback...'
        })
    )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control lw-input', 'placeholder': 'e.g. Urban Land Governance'}),
            'description': forms.Textarea(attrs={'class': 'form-control lw-input', 'rows': 3, 'placeholder': 'Brief description of this research domain...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control lw-input', 'min': 0}),
        }

from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control lw-input',
                'rows': 3,
                'placeholder': 'Share scholarly insights, policy implications, methodological queries, or constructive peer review...',
                'required': True
            })
        }

from django import forms

class ArticleFilterForm(forms.Form):
    """
    Form for filtering news articles.
    
    Fields:
        source_name: Filter by news source
        language: Filter by article language
        date_from: Filter articles from this date
        date_to: Filter articles until this date
    """
    source_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by source name...'
        })
    )
    
    language = forms.ChoiceField(
        choices=[
            ('', 'All Languages'),
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('it', 'Italian'),
            ('pt', 'Portuguese'),
            ('ar', 'Arabic'),
            ('zh', 'Chinese'),
            ('ja', 'Japanese'),
            ('ko', 'Korean'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
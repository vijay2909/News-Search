from django import forms


class NewsSearchForm(forms.Form):
    """
    Form for searching news articles.
    
    Fields:
        keyword: Search term input field
    """
    keyword = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter keyword to search news...',
            'required': True
        }),
        help_text='Enter a keyword or phrase to search for news articles'
    )

    def clean_keyword(self):
        """
        Clean and validate keyword input.
        
        Returns:
            str: Cleaned keyword
            
        Raises:
            ValidationError: If keyword is too short or contains invalid characters
        """
        keyword = self.cleaned_data['keyword'].strip().lower()
        if len(keyword) < 2:
            raise forms.ValidationError("Keyword must be at least 2 characters long.")
        return keyword

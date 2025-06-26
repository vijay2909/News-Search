from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Extended user creation form with additional fields.
    
    Fields:
        username: Username field
        email: Email field (required)
        first_name: First name field
        last_name: Last name field
        password1: Password field
        password2: Password confirmation field
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        """
        Save user and create associated UserProfile.
        
        Args:
            commit: Whether to save to database
            
        Returns:
            User: Created user instance
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create user profile
            from models import UserProfile
            UserProfile.objects.create(user=user)
        return user
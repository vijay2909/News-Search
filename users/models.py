from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    Extends the default User model to include additional user-specific information.

    Attributes:
        user (User): A one-to-one link to Django's built-in User model.
        is_blocked (bool): A boolean field to indicate if a user is blocked by an admin.
        keyword_quota (int): The maximum number of keywords a user is allowed to track.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)
    keyword_quota = models.PositiveIntegerField(default=5) # Default quota is 5

    def __str__(self):
        return f'{self.user.username} Profile'
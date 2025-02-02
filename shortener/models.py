import random
import string
from django.db import models
from django.contrib.auth.models import User

def generate_short_code():
    """Genera un código aleatorio de 6 caracteres para las URLs acortadas."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

class ShortenedURL(models.Model):
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True, default=generate_short_code)
    is_private = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_short_url(self):
        return f"http://127.0.0.1:8000/r/{self.short_code}"

    def __str__(self):
        return self.short_code

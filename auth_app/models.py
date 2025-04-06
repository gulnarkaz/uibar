from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    """
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Имя'
    )
    email = models.EmailField(
        unique=True, 
        blank=False, 
        null=False
    )
    city = models.CharField(
        max_length=100,
        blank=True,   
        null=True,      
        verbose_name='Город'
    )


    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        
    @property
    def full_name(self):
        """Возвращает полное имя пользователя."""
        return f"{self.first_name} {self.last_name}".strip()
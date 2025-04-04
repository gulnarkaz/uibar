# Generated by Django 5.2 on 2025-04-04 23:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apartments', '0003_review'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_date', models.DateField(verbose_name='Дата заезда')),
                ('check_out_date', models.DateField(verbose_name='Дата выезда')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Общая стоимость')),
                ('status', models.CharField(choices=[('PE', 'Ожидает подтверждения'), ('CO', 'Подтверждено'), ('CA', 'Отменено'), ('CM', 'Завершено')], default='CO', max_length=2, verbose_name='Статус бронирования')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('apartment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='apartments.apartment', verbose_name='Квартира')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL, verbose_name='Арендатор')),
            ],
            options={
                'verbose_name': 'Бронирование',
                'verbose_name_plural': 'Бронирования',
                'ordering': ['-created_at'],
            },
        ),
    ]

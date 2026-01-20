# Generated manually - add PhoneNumber model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_sitesettings_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20, verbose_name='Numéro de téléphone')),
                ('label', models.CharField(blank=True, max_length=50, verbose_name='Libellé', help_text='Ex: Principal, WhatsApp, Service client')),
                ('is_whatsapp', models.BooleanField(default=False, verbose_name='WhatsApp')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('order', models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")),
            ],
            options={
                'verbose_name': 'Numéro de téléphone',
                'verbose_name_plural': 'Numéros de téléphone',
                'ordering': ['order'],
            },
        ),
    ]

# Generated manually - increase phone field max_length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_add_gameprize_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='phone',
            field=models.CharField(
                default='+225 07 67 20 35 32 / +225 07 07 36 18 79 / +225 07 47 46 77 73',
                max_length=100,
                verbose_name='Téléphone'
            ),
        ),
    ]

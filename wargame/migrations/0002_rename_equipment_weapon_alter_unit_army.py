# Generated by Django 4.1.6 on 2023-02-09 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wargame', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Equipment',
            new_name='Weapon',
        ),
        migrations.AlterField(
            model_name='unit',
            name='army',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='units', to='wargame.army'),
        ),
    ]
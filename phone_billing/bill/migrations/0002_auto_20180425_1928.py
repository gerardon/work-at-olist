# Generated by Django 2.0.4 on 2018-04-25 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billrecord',
            name='call',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='call.Call'),
        ),
    ]

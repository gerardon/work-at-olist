# Generated by Django 2.0.4 on 2018-04-25 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('call', '0002_auto_20180425_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='call.Call')),
            ],
        ),
    ]

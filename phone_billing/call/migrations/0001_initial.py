# Generated by Django 2.0.4 on 2018-04-16 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('source', models.CharField(max_length=11)),
                ('destination', models.CharField(max_length=11)),
            ],
        ),
        migrations.CreateModel(
            name='CallRecord',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('record_type', models.CharField(choices=[('start', 'Start'), ('end', 'End')], max_length=5)),
                ('timestamp', models.DateTimeField()),
                ('call', models.ForeignKey(on_delete=True, to='call.Call')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='callrecord',
            unique_together={('call', 'record_type')},
        ),
    ]
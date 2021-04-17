# Generated by Django 2.2.16 on 2021-03-20 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commons', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='invite_status',
            field=models.IntegerField(choices=[(0, 'SENT'), (1, 'SENT_FAILED'), (2, 'ACCEPTED'), (3, 'CANCELLED'), (4, 'PENDING')], default=0),
        ),
    ]
# Generated by Django 2.2.16 on 2021-03-22 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_auto_20210320_0646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinvite',
            name='token',
            field=models.CharField(max_length=40),
        ),
    ]

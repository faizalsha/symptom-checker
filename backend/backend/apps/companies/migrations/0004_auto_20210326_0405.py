# Generated by Django 2.2.16 on 2021-03-26 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_auto_20210322_0852'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='companyinvite',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='employee',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='companyquestionnaire',
            name='currently_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='companyinvite',
            name='token',
            field=models.CharField(max_length=100),
        ),
    ]

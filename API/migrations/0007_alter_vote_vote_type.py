# Generated by Django 4.2.6 on 2024-01-06 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0006_alter_vote_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='vote_type',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]

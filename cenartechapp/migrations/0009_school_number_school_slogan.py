# Generated by Django 5.1.1 on 2024-10-18 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cenartechapp', '0008_admittedstudents_school_passedstudents_school_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='slogan',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

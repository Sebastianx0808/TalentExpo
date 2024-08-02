# Generated by Django 4.1.13 on 2024-05-21 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_app', '0006_location_talents_alter_candidate_profile_pic'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(default='Unknown', max_length=100)),
                ('state', models.CharField(default='Unknown', max_length=100)),
                ('city', models.CharField(default='Unknown', max_length=100)),
                ('pin_code', models.CharField(default='Unknown', max_length=20)),
            ],
            options={
                'verbose_name': 'Place',
                'verbose_name_plural': 'Places',
            },
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]

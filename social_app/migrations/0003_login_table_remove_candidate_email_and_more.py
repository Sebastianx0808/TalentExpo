# Generated by Django 4.1.13 on 2024-05-20 07:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social_app', '0002_remove_video_talent_remove_candidate_talents_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Login_Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='email',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='password',
        ),
        migrations.CreateModel(
            name='Director',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('contact_details', models.CharField(max_length=100)),
                ('designation', models.CharField(max_length=100)),
                ('company', models.CharField(max_length=100)),
                ('brief_description', models.TextField()),
                ('login', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='social_app.login_table')),
            ],
        ),
        migrations.AddField(
            model_name='candidate',
            name='login',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='social_app.login_table'),
        ),
    ]

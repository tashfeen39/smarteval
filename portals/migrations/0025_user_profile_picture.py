# Generated by Django 4.2.3 on 2024-04-15 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portals", "0024_remove_user_profile_picture"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="profile_picture",
            field=models.ImageField(
                blank=True, null=True, upload_to="profile_pictures"
            ),
        ),
    ]
# Generated by Django 4.2.3 on 2024-04-11 20:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portals", "0021_alter_student_marital_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="degree",
            name="department",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="portals.department"
            ),
        ),
    ]
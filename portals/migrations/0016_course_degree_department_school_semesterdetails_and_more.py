# Generated by Django 4.2.3 on 2024-03-24 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portals", "0015_alter_student_cnic_alter_student_date_of_birth_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("CourseID", models.AutoField(primary_key=True, serialize=False)),
                ("course_name", models.CharField(max_length=100)),
                ("course_description", models.TextField()),
                ("theory_credit_hours", models.IntegerField()),
                ("lab_credit_hours", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Degree",
            fields=[
                ("DegreeID", models.AutoField(primary_key=True, serialize=False)),
                ("degree_name", models.CharField(max_length=100)),
                ("degree_description", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("DepartmentID", models.AutoField(primary_key=True, serialize=False)),
                ("department_name", models.CharField(max_length=100)),
                ("department_intro", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="School",
            fields=[
                ("SchoolID", models.AutoField(primary_key=True, serialize=False)),
                ("school_name", models.CharField(max_length=100)),
                ("school_intro", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="SemesterDetails",
            fields=[
                (
                    "SemesterDetailsID",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("semester_number", models.PositiveIntegerField()),
                (
                    "degree",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="portals.degree"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SemesterCourses",
            fields=[
                (
                    "SemesterCoursesID",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("courses", models.ManyToManyField(to="portals.course")),
                (
                    "semester_details",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="portals.semesterdetails",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Program",
            fields=[
                ("ProgramID", models.AutoField(primary_key=True, serialize=False)),
                ("program_name", models.CharField(max_length=100)),
                ("program_description", models.TextField()),
                ("total_semester", models.IntegerField(default=8)),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="portals.department",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="department",
            name="school",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="portals.school"
            ),
        ),
        migrations.AddField(
            model_name="degree",
            name="program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="portals.program"
            ),
        ),
        migrations.CreateModel(
            name="CoursePrerequisite",
            fields=[
                (
                    "CoursePrerequisiteID",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("courses", models.ManyToManyField(to="portals.course")),
            ],
        ),
    ]
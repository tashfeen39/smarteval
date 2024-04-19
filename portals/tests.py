from django.test import TestCase
import pytest
from django.db import IntegrityError
from django.utils import timezone
from .models import User, Teacher, Student
from django.test import TransactionTestCase



@pytest.mark.django_db
class TestUserModel(TestCase):
    def test_user_creation_with_defaults(self):
        user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="securepassword123",
            username="johndoe"
        )
        assert user.is_student == False
        assert user.is_teacher == False
        assert user.phone_number == None  
        assert user.profile_picture == None

    def test_user_optional_fields_blank(self):
        user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="securepassword123",
            username="johndoe"
        )
        assert user.phone_number == None
        assert user.profile_picture == None

@pytest.mark.django_db
class TestUserModelTransaction(TransactionTestCase):
    def test_user_unique_email_and_username(self):
        # Create a user with a unique email address
        User.objects.create(
            first_name="John",
            last_name="Doe",
            email="unique@example.com",
            password="securepassword123",
            username="uniqueusername"
        )

        # Attempt to create another user with the same email address
        with pytest.raises(IntegrityError):
            User.objects.create(
                first_name="Jane",
                last_name="Doe",
                email="unique@example.com",  # This email is already used by the previous user
                password="securepassword123",
                username="anotherusername"
            )

        # Attempt to create another user with the same username
        with pytest.raises(IntegrityError):
            User.objects.create(
                first_name="Jane",
                last_name="Doe",
                email="another@example.com",  
                password="securepassword123",
                username="uniqueusername" # This username is already used by the previous user
            )


class TeacherModelTestCase(TestCase):
    def setUp(self):
        # Create a User instance for the Teacher
        self.teacher_user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="securepassword123",
            username="johndoe"
        )

    def test_teacher_creation(self):
        # Create and save a Teacher object with valid data
        teacher = Teacher.objects.create(
            user=self.teacher_user,
            date_of_birth="1990-01-01",
            gender="Male",
            marital_status="Single",
            religion="Christian",
            nationality="American",
            cnic="1234567890123",
            office_number="1234567890",
            address="123 Main St, City, Country"
        )
        # Assert that the Teacher object was created successfully
        self.assertIsNotNone(teacher)
        self.assertEqual(teacher.user, self.teacher_user)
        self.assertEqual(teacher.date_of_birth, "1990-01-01")
        self.assertEqual(teacher.gender, "Male")
        self.assertEqual(teacher.marital_status, "Single")
        self.assertEqual(teacher.religion, "Christian")
        self.assertEqual(teacher.nationality, "American")
        self.assertEqual(teacher.cnic, "1234567890123")
        self.assertEqual(teacher.office_number, "1234567890")
        self.assertEqual(teacher.address, "123 Main St, City, Country")
        self.assertTrue(teacher.created_at)

    def test_default_values(self):
        # Create and save a Teacher object without specifying optional fields
        teacher = Teacher.objects.create(user=self.teacher_user)
        # Assert that default values are correctly applied
        self.assertIsNotNone(teacher.created_at)

    def test_string_representation(self):
        # Create a Teacher object
        teacher = Teacher.objects.create(
            user=self.teacher_user,
            date_of_birth="1990-01-01",
            gender="Male",
            marital_status="Single",
            religion="Christian",
            nationality="American",
            cnic="1234567890123",
            office_number="1234567890",
            address="123 Main St, City, Country"
        )
        # Assert the string representation of the Teacher model
        expected_string = f"{self.teacher_user.first_name} {self.teacher_user.last_name}"
        self.assertEqual(str(teacher), expected_string)

    def test_optional_fields_blank(self):
        # Create and save a Teacher object without specifying optional fields
        teacher = Teacher.objects.create(user=self.teacher_user)
        # Assert that optional fields can be left blank or set to null
        self.assertIsNone(teacher.date_of_birth)
        self.assertIsNone(teacher.gender)
        self.assertIsNone(teacher.marital_status)
        self.assertIsNone(teacher.religion)
        self.assertIsNone(teacher.nationality)
        self.assertIsNone(teacher.cnic)
        self.assertIsNone(teacher.office_number)
        self.assertIsNone(teacher.address)

    def test_field_lengths(self):
        # Assert that fields with defined max lengths enforce the specified maximum lengths
        self.assertEqual(Teacher._meta.get_field('religion').max_length, 100)
        self.assertEqual(Teacher._meta.get_field('nationality').max_length, 100)
        self.assertEqual(Teacher._meta.get_field('cnic').max_length, 15)
        self.assertEqual(Teacher._meta.get_field('office_number').max_length, 20)
        self.assertEqual(Teacher._meta.get_field('address').max_length, 200)


class TeacherUserRelationshipTestCase(TestCase):
    def setUp(self):
        # Create a User instance for the Teacher
        self.teacher_user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="securepassword123",
            username="johndoe"
        )

        # Create a Teacher instance
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            date_of_birth="1990-01-01",
            gender="Male",
            marital_status="Single",
            religion="Christian",
            nationality="American",
            cnic="1234567890123",
            office_number="1234567890",
            address="123 Main St, City, Country"
        )

    def test_teacher_user_relationship(self):
        # Check if the Teacher object is associated with the correct User object
        self.assertEqual(self.teacher.user, self.teacher_user)
        # Check if the User object has the correct Teacher object associated with it
        self.assertEqual(self.teacher_user.teacher, self.teacher)


class StudentModelTestCase(TestCase):
    def setUp(self):
        # Create a User instance for the first Student
        self.student_user1 = User.objects.create(
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@example.com",
            password="securepassword123",
            username="alicesmith"
        )

        # Create a User instance for the second Student
        self.student_user2 = User.objects.create(
            first_name="Bob",
            last_name="Johnson",
            email="bob.johnson@example.com",
            password="securepassword123",
            username="bobjohnson"
        )

    def test_student_creation(self):
        # Create and save a Student object with valid data
        student = Student.objects.create(
            user=self.student_user1,
            date_of_birth="1995-05-15",
            gender="Female",
            marital_status="Single",
            religion="Christian",
            nationality="American",
            cnic="1234567890123",
            father_name="John Smith",
            father_occupation="Engineer",
            semester="Spring 2024",
            address="456 Elm St, City, Country"
        )
        # Assert that the Student object was created successfully
        self.assertIsNotNone(student)
        self.assertEqual(student.user, self.student_user1)
        self.assertEqual(student.date_of_birth, "1995-05-15")
        self.assertEqual(student.gender, "Female")
        self.assertEqual(student.marital_status, "Single")
        self.assertEqual(student.religion, "Christian")
        self.assertEqual(student.nationality, "American")
        self.assertEqual(student.cnic, "1234567890123")
        self.assertEqual(student.father_name, "John Smith")
        self.assertEqual(student.father_occupation, "Engineer")
        self.assertEqual(student.semester, "Spring 2024")
        self.assertEqual(student.address, "456 Elm St, City, Country")
        self.assertTrue(student.created_at)
        self.assertTrue(student.StudentID)  # Assert that StudentID is generated

    def test_default_values(self):
        # Create and save a Student object without specifying optional fields
        student = Student.objects.create(user=self.student_user1)
        # Assert that default values are correctly applied
        self.assertIsNotNone(student.created_at)
        self.assertTrue(student.StudentID)  # Assert that StudentID is generated

    def test_optional_fields_blank(self):
        # Create and save a Student object without specifying optional fields
        student = Student.objects.create(user=self.student_user1)
        # Assert that optional fields can be left blank or set to null
        self.assertIsNone(student.date_of_birth)
        self.assertIsNone(student.gender)
        self.assertIsNone(student.marital_status)
        self.assertIsNone(student.religion)
        self.assertIsNone(student.nationality)
        self.assertIsNone(student.cnic)
        self.assertIsNone(student.father_name)
        self.assertIsNone(student.father_occupation)
        self.assertIsNone(student.semester)
        self.assertIsNone(student.address)

    def test_field_lengths(self):
        # Assert that fields with defined max lengths enforce the specified maximum lengths
        self.assertEqual(Student._meta.get_field('religion').max_length, 100)
        self.assertEqual(Student._meta.get_field('nationality').max_length, 100)
        self.assertEqual(Student._meta.get_field('cnic').max_length, 15)
        self.assertEqual(Student._meta.get_field('father_name').max_length, 255)
        self.assertEqual(Student._meta.get_field('father_occupation').max_length, 100)
        self.assertEqual(Student._meta.get_field('semester').max_length, 100)
        self.assertEqual(Student._meta.get_field('address').max_length, 200)

    def test_studentid_unique(self):
        # Create two Student objects with different User instances
        student1 = Student.objects.create(user=self.student_user1)
        student2 = Student.objects.create(user=self.student_user2)

        # Assert that StudentID is unique for each student
        self.assertNotEqual(student1.StudentID, student2.StudentID)

    def test_studentid_generation(self):
        # Create a Student object without specifying StudentID
        student = Student.objects.create(user=self.student_user1)

        # Assert that StudentID is automatically generated
        self.assertTrue(student.StudentID)

    def test_student_save_method(self):
        # Create a Student object without specifying StudentID
        student = Student.objects.create(user=self.student_user1)

        # Save the Student object
        student.save()

        # Assert that StudentID is automatically generated upon save
        self.assertTrue(student.StudentID)

    def test_student_str_method(self):
        # Create a Student object
        student = Student.objects.create(user=self.student_user1)

        # Assert that the __str__ method returns the expected string representation
        self.assertEqual(str(student), "Alice Smith")

    
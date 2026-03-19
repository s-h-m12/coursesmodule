from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import Course, Module, Material, Enrollment, Test, Question, Answer


class CourseModelTest(TestCase):
    """Тестирование модели Course"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.user = User.objects.create_user(
            username='mentor1',
            password='testpass123',
            first_name='Иван',
            last_name='Петров'
        )

    def test_course_difficulty_choices(self):
        course1 = Course.objects.create(
            created_by=self.user,
            title='Начальный курс',
            duration=20,
            difficulty='beginner',
            is_published=True
        )
        course2 = Course.objects.create(
            created_by=self.user,
            title='Средний курс',
            duration=30,
            difficulty='intermediate',
            is_published=True
        )
        course3 = Course.objects.create(
            created_by=self.user,
            title='Продвинутый курс',
            duration=50,
            difficulty='advanced',
            is_published=True
        )

        self.assertEqual(course1.get_difficulty_display(), 'Начальный')
        self.assertEqual(course2.get_difficulty_display(), 'Средний')
        self.assertEqual(course3.get_difficulty_display(), 'Продвинутый')


class MaterialModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='mentor1')
        self.course = Course.objects.create(
            created_by=self.user,
            title='Тестовый курс',
            duration=10,
            difficulty='beginner'
        )
        self.module = Module.objects.create(
            course=self.course,
            title='Тестовый модуль',
            order=1
        )

    def test_material_validation_file_only(self):
        material = Material(
            module=self.module,
            title='Тестовый материал',
            type='document',
            file=SimpleUploadedFile('test.txt', b'content')
        )
        try:
            material.full_clean()
            material.save()
            self.assertTrue(Material.objects.filter(id=material.id).exists())
        except ValidationError:
            self.fail("ValidationError не должна возникать при наличии файла")

    def test_material_validation_url_only(self):
        material = Material(
            module=self.module,
            title='Тестовый материал',
            type='link',
            external_url='https://example.com'
        )
        try:
            material.full_clean()
            material.save()
            self.assertTrue(Material.objects.filter(id=material.id).exists())
        except ValidationError:
            self.fail("ValidationError не должна возникать при наличии ссылки")

    def test_material_validation_both_empty(self):
        material = Material(
            module=self.module,
            title='Тестовый материал',
            type='document'
        )
        with self.assertRaises(ValidationError):
            material.full_clean()

    def test_material_validation_both_present(self):
        material = Material(
            module=self.module,
            title='Тестовый материал',
            type='document',
            file=SimpleUploadedFile('test.txt', b'content'),
            external_url='https://example.com'
        )
        with self.assertRaises(ValidationError):
            material.full_clean()


class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(username='mentor1')
        self.student = User.objects.create_user(username='student1')
        self.course = Course.objects.create(
            created_by=self.mentor,
            title='Тестовый курс',
            duration=10,
            difficulty='beginner',
            is_published=True
        )

    def test_enrollment_creation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            status='active',
            progress=0.00
        )

        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.status, 'active')
        self.assertEqual(float(enrollment.progress), 0.00)
        self.assertIsNotNone(enrollment.enrolled_date)

    def test_enrollment_status_choices(self):
        statuses = ['active', 'completed', 'suspended', 'expired']
        for status in statuses:
            enrollment = Enrollment.objects.create(
                student=self.student,
                course=self.course,
                status=status,
                progress=50.00
            )
            self.assertEqual(enrollment.status, status)
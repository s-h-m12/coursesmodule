from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.core.validators import URLValidator
from django.core.validators import ValidationError
from django.contrib import auth

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Начальный'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField()
    difficulty = models.CharField(max_length=100, choices=DIFFICULTY_CHOICES)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='courses/%Y/%m/%d/')

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.IntegerField()
    content = RichTextField()

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('completed', 'Завершен'),
        ('suspended', 'Приостановлен'),
        ('expired', 'Просрочен'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    progress = models.DecimalField(decimal_places=2, max_digits=5)
    last_accessed = models.DateTimeField(auto_now=True)

class Material(models.Model):
    MATERIAL_TYPES = [
        ('video', 'Видео'),
        ('presentation', 'Презентация'),
        ('document', 'Документ'),
        ('link', 'Внешняя ссылка'),
        ('archive', 'Архив')
    ]
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    file = models.FileField(upload_to='materials/%Y/%m/%d/', blank=True, null=True)
    external_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    """Валидация: проверка заполнение файла или ссылки"""
    def clean(self):
        if not self.file and not self.external_url:
            raise ValidationError("Необходимо загрузить файл или указать ссылку")

        if self.file and self.external_url:
            raise ValidationError("Заполните только одно поле: файл или ссылка")

    """Свойство получение URL материала"""
    def file_url(self):
        if self.file:
            return self.file.url
        elif self.external_url:
            return self.external_url
        return None

class Test(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    time_limit = models.IntegerField()
    passing_score = models.IntegerField()
    max_attempts = models.IntegerField(default=1)
    shuffle_questions = models.BooleanField(default=False)

class TestAvailability(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    group = models.ForeignKey('auth.Group', on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)

class Question(models.Model):
    QUESTION_TYPES = [
        ('single', 'Одиночный выбор'),
        ('multiple', 'Множественный выбор'),
        ('text', 'Текстовый ответ'),
    ]
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(choices=QUESTION_TYPES)
    points = models.IntegerField(default=1)
    order = models.IntegerField()
    explanation = models.TextField()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

class Grade(models.Model):
    GRADE_TYPES = [
        ('test', 'Тест'),
        ('assignment', 'Практическое задание'),
        ('project', 'Проектная работа'),
        ('final', 'Итоговая аттестация')
    ]
    STATUS_CHOICES = [
        ('pending', 'Ожидает проверки'),
        ('graded', 'Оценено'),
        ('appealed', 'На апелляции'),
        ('revised', 'Перепроверено'),
    ]
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField()
    submission_date = models.DateField(auto_now_add=True)
    test = models.ForeignKey(Test, on_delete=models.SET_NULL) # Даже если тест удалят оценка за него останется
    grade_type = models.CharField(choices=GRADE_TYPES)
    status = models.CharField(choices=STATUS_CHOICES)
    student_comment = models.CharField()
    updated_at = models.DateTimeField(auto_now=True)

class TestAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Student'})
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class TestResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField(null=True)
    completed_date = models.DateField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment,on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField(null=True, blank=True)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField()
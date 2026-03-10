from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.core.validators import URLValidator
from django.core.validators import ValidationError

class Course(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField()
    difficulty = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.IntegerField()
    content = RichTextField()

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=100)
    progress = models.DecimalField(decimal_places=2, max_digits=3)
    last_accessed = models.DateField()

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




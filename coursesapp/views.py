from django.shortcuts import render
from django.db.models import Count, Q
from .models import Course, User, TestResult


def course_list(request):
    # Получаем все опубликованные курсы
    courses = Course.objects.filter(is_published=True).select_related('created_by')

    # Фильтры
    difficulty = request.GET.get('difficulty')
    mentor_id = request.GET.get('mentor')
    search = request.GET.get('search')

    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    if mentor_id:
        courses = courses.filter(created_by_id=mentor_id)
    if search:
        courses = courses.filter(Q(title__icontains=search) | Q(description__icontains=search))

    # Все менторы для фильтра и блока внизу
    mentors = User.objects.filter(groups__name='Mentor').annotate(
        courses_count=Count('courses_created')
    )

    context = {
        'courses': courses,
        'mentors': mentors,
        'total_courses': Course.objects.filter(is_published=True).count(),
        'total_students': User.objects.filter(groups__name='Student').count(),
        'total_mentors': User.objects.filter(groups__name='Mentor').count(),
        'total_tests_passed': TestResult.objects.filter(passed=True).count(),
        'selected_difficulty': difficulty,
        'selected_mentor': mentor_id,
        'search_query': search,
    }

    return render(request, 'course_list.html', context)
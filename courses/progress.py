from lessons.models import LessonCompletion
from quizzes.models import QuizAttempt


def get_completed_lesson_ids(course, student):
    return set(
        LessonCompletion.objects.filter(
            student=student,
            lesson__module__course=course,
        ).values_list('lesson_id', flat=True)
    )


def get_completed_quiz_ids(course, student):
    return set(
        QuizAttempt.objects.filter(
            student=student,
            quiz__module__course=course,
            completed_at__isnull=False,
        ).values_list('quiz_id', flat=True)
    )


def get_module_access_map(course, student):
    completed_lesson_ids = get_completed_lesson_ids(course, student)
    module_access = {}
    previous_module_completed = True

    for module in course.modules.prefetch_related('lessons').all():
        lesson_ids = [lesson.id for lesson in module.lessons.all()]
        module_completed = all(lesson_id in completed_lesson_ids for lesson_id in lesson_ids)

        module_access[module.id] = {
            'unlocked': previous_module_completed,
            'completed': module_completed,
        }

        previous_module_completed = module_completed

    return module_access, completed_lesson_ids

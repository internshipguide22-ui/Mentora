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
            passed=True,
        ).values_list('quiz_id', flat=True)
    )


def get_module_access_map(course, student):
    if not getattr(student, 'is_student', False):
        module_access = {
            module.id: {'unlocked': True, 'completed': False}
            for module in course.modules.all()
        }
        return module_access, set()

    completed_lesson_ids = get_completed_lesson_ids(course, student)
    completed_quiz_ids = get_completed_quiz_ids(course, student)
    module_access = {}
    previous_module_completed = True

    for module in course.modules.prefetch_related('lessons', 'quizzes').all():
        lesson_ids = [lesson.id for lesson in module.lessons.all()]
        quiz_ids = [quiz.id for quiz in module.quizzes.all()]
        lessons_completed = all(lesson_id in completed_lesson_ids for lesson_id in lesson_ids)
        quizzes_completed = all(quiz_id in completed_quiz_ids for quiz_id in quiz_ids)
        module_completed = lessons_completed and quizzes_completed

        module_access[module.id] = {
            'unlocked': previous_module_completed,
            'completed': module_completed,
        }

        previous_module_completed = module_completed

    return module_access, completed_lesson_ids

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from courses.models import Course, Enrollment, Module, Lesson
from lessons.models import LessonCompletion
from quizzes.models import Quiz, QuizAttempt


class ModuleUnlockingTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor_unlock',
            password='pass123',
            user_type='instructor',
        )
        self.student = User.objects.create_user(
            username='student_unlock',
            password='pass123',
            user_type='student',
        )
        self.course = Course.objects.create(
            title='Unlock Test Course',
            description='Course for module unlock tests',
            instructor=self.instructor,
        )
        self.module1 = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.module2 = Module.objects.create(course=self.course, title='Module 2', order=2)
        self.lesson1 = Lesson.objects.create(module=self.module1, title='Lesson 1', order=1)
        self.lesson2 = Lesson.objects.create(module=self.module2, title='Lesson 2', order=1)
        self.quiz1 = Quiz.objects.create(
            title='Module 1 Quiz',
            module=self.module1,
            instructor=self.instructor,
        )
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.login(username='student_unlock', password='pass123')

    def test_second_module_lesson_is_locked_until_previous_module_requirements_are_completed(self):
        response = self.client.get(reverse('courses:lesson_detail', kwargs={'pk': self.lesson2.pk}))
        self.assertRedirects(response, reverse('courses:course_detail', kwargs={'pk': self.course.pk}))

    def test_second_module_lesson_stays_locked_when_previous_module_quiz_is_incomplete(self):
        LessonCompletion.objects.create(student=self.student, lesson=self.lesson1)
        response = self.client.get(reverse('courses:lesson_detail', kwargs={'pk': self.lesson2.pk}))
        self.assertRedirects(response, reverse('courses:course_detail', kwargs={'pk': self.course.pk}))

    def test_second_module_lesson_stays_locked_when_previous_module_quiz_is_failed(self):
        LessonCompletion.objects.create(student=self.student, lesson=self.lesson1)
        QuizAttempt.objects.create(
            student=self.student,
            quiz=self.quiz1,
            attempt_number=1,
            completed_at=timezone.now(),
            score=40,
            passed=False,
        )
        response = self.client.get(reverse('courses:lesson_detail', kwargs={'pk': self.lesson2.pk}))
        self.assertRedirects(response, reverse('courses:course_detail', kwargs={'pk': self.course.pk}))

    def test_second_module_lesson_unlocks_after_previous_module_lesson_and_quiz_are_completed(self):
        LessonCompletion.objects.create(student=self.student, lesson=self.lesson1)
        QuizAttempt.objects.create(
            student=self.student,
            quiz=self.quiz1,
            attempt_number=1,
            completed_at=timezone.now(),
            score=100,
            passed=True,
        )
        response = self.client.get(reverse('courses:lesson_detail', kwargs={'pk': self.lesson2.pk}))
        self.assertEqual(response.status_code, 200)

    def test_instructor_sees_all_modules_as_unlocked(self):
        self.client.logout()
        self.client.login(username='instructor_unlock', password='pass123')
        response = self.client.get(reverse('courses:course_detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 200)
        modules = response.context['modules']
        self.assertTrue(all(module.is_unlocked and not module.is_locked for module in modules))

    def test_admin_sees_all_modules_as_unlocked(self):
        admin = User.objects.create_user(
            username='admin_unlock',
            password='pass123',
            user_type='admin',
        )
        self.client.logout()
        self.client.login(username='admin_unlock', password='pass123')
        response = self.client.get(reverse('courses:course_detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 200)
        modules = response.context['modules']
        self.assertTrue(all(module.is_unlocked and not module.is_locked for module in modules))

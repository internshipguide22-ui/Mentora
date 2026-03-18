from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from courses.models import Course, Enrollment, Module, Lesson
from lessons.models import LessonCompletion


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
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.login(username='student_unlock', password='pass123')

    def test_second_module_lesson_is_locked_until_first_module_completed(self):
        response = self.client.get(reverse('courses:lesson_detail', kwargs={'pk': self.lesson2.pk}))
        self.assertRedirects(response, reverse('courses:course_detail', kwargs={'pk': self.course.pk}))

    def test_second_module_lesson_unlocks_after_first_module_completed(self):
        LessonCompletion.objects.create(student=self.student, lesson=self.lesson1)
        response = self.client.get(reverse('courses:lesson_detail', kwargs={'pk': self.lesson2.pk}))
        self.assertEqual(response.status_code, 200)

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson, Enrollment, Category
from lessons.models import LessonCompletion
from certificates.models import Certificate
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Sets up test data for courses, enrollments, and certificate generation.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Setting up test data...'))

        # 1. Create Users (Instructor and Student)
        self.stdout.write('Creating users...')
        try:
            instructor, created = User.objects.get_or_create(
                username='instructor',
                email='instructor@example.com',
                defaults={'user_type': 'admin', 'is_staff': True, 'is_superuser': True}
            )
            if created:
                instructor.set_password('password')
                instructor.save()
            self.stdout.write(self.style.SUCCESS(f'Instructor: {instructor.username}'))

            student, created = User.objects.get_or_create(
                username='student',
                email='student@example.com',
                defaults={'user_type': 'student'}
            )
            if created:
                student.set_password('password')
                student.save()
            self.stdout.write(self.style.SUCCESS(f'Student: {student.username}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating users: {e}'))
            return

        # 2. Create Category
        self.stdout.write('Creating category...')
        category, created = Category.objects.get_or_create(
            name='Programming'
        )
        self.stdout.write(self.style.SUCCESS(f'Category: {category.name}'))

        # 3. Create Course
        self.stdout.write('Creating course...')
        course, created = Course.objects.get_or_create(
            title='Introduction to Python',
            defaults={
                'description': 'A comprehensive introduction to Python programming.',
                'instructor': instructor,
                'category': category
            }
        )
        self.stdout.write(self.style.SUCCESS(f'Course: {course.title}'))

        # 4. Create Modules and Lessons
        self.stdout.write('Creating modules and lessons...')
        module1, created = Module.objects.get_or_create(
            course=course,
            title='Module 1: Basics',
            defaults={'description': 'Fundamentals of Python', 'order': 1}
        )
        lesson1, created = Lesson.objects.get_or_create(
            module=module1,
            title='Lesson 1.1: Hello World',
            defaults={'description': 'Your first Python program', 'order': 1}
        )
        lesson2, created = Lesson.objects.get_or_create(
            module=module1,
            title='Lesson 1.2: Variables',
            defaults={'description': 'Understanding variables', 'order': 2}
        )
        self.stdout.write(self.style.SUCCESS(f'Module: {module1.title}, Lessons: {lesson1.title}, {lesson2.title}'))

        module2, created = Module.objects.get_or_create(
            course=course,
            title='Module 2: Control Flow',
            defaults={'description': 'Conditional statements and loops', 'order': 2}
        )
        lesson3, created = Lesson.objects.get_or_create(
            module=module2,
            title='Lesson 2.1: If/Else',
            defaults={'description': 'Conditional logic', 'order': 1}
        )
        lesson4, created = Lesson.objects.get_or_create(
            module=module2,
            title='Lesson 2.2: For Loops',
            defaults={'description': 'Iterating with for loops', 'order': 2}
        )
        self.stdout.write(self.style.SUCCESS(f'Module: {module2.title}, Lessons: {lesson3.title}, {lesson4.title}'))

        # 5. Enroll Student in Course
        self.stdout.write('Enrolling student in course...')
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            course=course,
            defaults={'completed': False, 'progress': 0.00}
        )
        self.stdout.write(self.style.SUCCESS(f'Student {student.username} enrolled in {course.title}'))

        # 6. Mark all lessons as complete for the student
        self.stdout.write('Marking all lessons as complete...')
        all_lessons = Lesson.objects.filter(module__course=course)
        for lesson in all_lessons:
            LessonCompletion.objects.get_or_create(student=student, lesson=lesson)
            self.stdout.write(self.style.SUCCESS(f'Lesson {lesson.title} marked complete for {student.username}'))

        # 7. Update Enrollment to completed=True
        self.stdout.write('Updating enrollment to completed...')
        enrollment.completed = True
        enrollment.completion_date = timezone.now()
        enrollment.progress = 100.00
        enrollment.save()
        self.stdout.write(self.style.SUCCESS(f'Enrollment for {student.username} in {course.title} marked as completed.'))

        # 8. Verify Certificate Creation
        self.stdout.write('Verifying certificate creation...')
        certificate = Certificate.objects.filter(enrollment=enrollment).first()
        if certificate:
            self.stdout.write(self.style.SUCCESS(f'Certificate created for {student.username} in {course.title} with ID: {certificate.id}'))
        else:
            self.stdout.write(self.style.ERROR('Certificate not found for the completed enrollment.'))

        self.stdout.write(self.style.SUCCESS('Test data setup complete!'))

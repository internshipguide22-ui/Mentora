from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from courses.models import Category, Course, Enrollment
from reviews.models import Review


class AddReviewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.student = user_model.objects.create_user(
            username='student1',
            password='testpass123',
            user_type='student',
        )
        self.instructor = user_model.objects.create_user(
            username='instructor1',
            password='testpass123',
            user_type='instructor',
        )
        self.category = Category.objects.create(name='Testing')
        self.course = Course.objects.create(
            title='Review Lock Course',
            description='Course for review tests',
            instructor=self.instructor,
            category=self.category,
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            completed=True,
            progress=100,
        )
        self.url = reverse('reviews:add_review', args=[self.course.id])

    def test_completed_student_can_submit_first_review(self):
        self.client.login(username='student1', password='testpass123')

        response = self.client.post(self.url, {'rating': '5', 'comment': 'Great course!'})

        self.assertRedirects(response, reverse('courses:course_detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(Review.objects.filter(course=self.course, student=self.student).count(), 1)

    def test_second_review_submission_is_blocked(self):
        Review.objects.create(course=self.course, student=self.student, rating=4, comment='First review')
        self.client.login(username='student1', password='testpass123')

        response = self.client.post(self.url, {'rating': '2', 'comment': 'Changed review'})

        self.assertRedirects(response, reverse('courses:course_detail', kwargs={'pk': self.course.pk}))
        review = Review.objects.get(course=self.course, student=self.student)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, 'First review')
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertIn('You have already submitted a review for this course.', messages)

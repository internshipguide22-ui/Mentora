from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson, Enrollment, Category
from quizzes.models import Quiz, Question, Choice

User = get_user_model()

print("Deleting all users except admin...")
User.objects.exclude(username='admin').delete()

print("Creating users...")
instructors = []
for i in range(1, 4):
    inst, _ = User.objects.get_or_create(
        username=f'instructor{i}',
        defaults={
            'email': f'instructor{i}@lms.com',
            'user_type': 'instructor',
            'first_name': f'Instructor{i}',
            'last_name': 'Teacher',
            'phone': f'555-010{i}',
            'bio': 'Experienced instructor specializing in technology.'
        }
    )
    inst.set_password('pass123')
    inst.save()
    instructors.append(inst)

students = []
for i in range(1, 6):
    stud, _ = User.objects.get_or_create(
        username=f'student{i}',
        defaults={
            'email': f'student{i}@lms.com',
            'user_type': 'student',
            'first_name': f'Student{i}',
            'last_name': 'Learner',
            'phone': f'555-020{i}'
        }
    )
    stud.set_password('pass123')
    stud.save()
    students.append(stud)

print("Creating categories...")
categories = []
cat_data = [
    ('Web Development', 'Learn modern web development'),
    ('Data Science', 'Master data analysis and ML'),
    ('Mobile Development', 'Build mobile applications'),
    ('Cloud Computing', 'Learn cloud technologies')
]
for name, desc in cat_data:
    cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
    categories.append(cat)

print("Creating courses...")
courses_data = [
    {'title': 'Complete Python Programming', 'description': 'Master Python from basics to advanced', 'instructor': instructors[0], 'category': categories[0]},
    {'title': 'Web Development with Django', 'description': 'Build web apps with Django', 'instructor': instructors[0], 'category': categories[0]},
    {'title': 'Data Science Fundamentals', 'description': 'Intro to data science', 'instructor': instructors[1], 'category': categories[1]},
    {'title': 'React Native Mobile Apps', 'description': 'Create mobile apps', 'instructor': instructors[1], 'category': categories[2]},
    {'title': 'AWS Cloud Essentials', 'description': 'Learn AWS basics', 'instructor': instructors[2], 'category': categories[3]}
]

courses = []
for cd in courses_data:
    course, _ = Course.objects.get_or_create(title=cd['title'], defaults={'description': cd['description'], 'instructor': cd['instructor'], 'category': cd['category']})
    courses.append(course)

print("Creating modules and lessons...")
for course in courses:
    for m_idx in range(1, 4):
        module, _ = Module.objects.get_or_create(course=course, title=f'Module {m_idx}: {course.title} Part {m_idx}', defaults={'description': f'Learn key concepts', 'order': m_idx})
        for l_idx in range(1, 4):
            Lesson.objects.get_or_create(module=module, title=f'Lesson {l_idx}: Topic {l_idx}', defaults={'content': 'Study this lesson carefully.', 'description': f'Learn topic {l_idx}', 'order': l_idx})

print("Creating quizzes...")
for course in courses:
    modules = list(course.modules.all()[:2])
    for module in modules:
        lessons = list(module.lessons.all())
        if lessons:
            lesson = lessons[0]
            quiz, _ = Quiz.objects.get_or_create(title=f'{lesson.title} Quiz', lesson=lesson, defaults={'instructor': course.instructor, 'description': 'Test knowledge', 'time_limit_minutes': 20, 'is_published': True})
            for q_idx in range(1, 4):
                question, _ = Question.objects.get_or_create(quiz=quiz, text=f'Question {q_idx} about {lesson.title}?', defaults={'question_type': 'multiple_choice', 'points': 10, 'order': q_idx})
                choices_data = [('Correct answer', True), ('Wrong answer 1', False), ('Wrong answer 2', False), ('Wrong answer 3', False)]
                for choice_text, is_correct in choices_data:
                    Choice.objects.get_or_create(question=question, text=choice_text, defaults={'is_correct': is_correct})

print("Creating enrollments...")
for student in students[:3]:
    for course in courses[:3]:
        Enrollment.objects.get_or_create(student=student, course=course, defaults={'is_active': True})

print("\n" + "="*60)
print("SEED DATA CREATED!")
print("="*60)
print("\nCredentials:")
print("Admin: admin / admin123")
print("Instructors: instructor1-3 / pass123")
print("Students: student1-5 / pass123")
print("="*60)

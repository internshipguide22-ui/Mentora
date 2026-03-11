# Learning Management System (LMS)

A complete, fully functional Learning Management System built with Django and SQLite.

## Features

### 🔐 User Roles & Authentication
- **Admin**: Full system access, manage all users, courses, and data
- **Instructor**: Create and manage their own courses, lessons, and quizzes
- **Student**: Enroll in courses, complete lessons, take quizzes, earn certificates
- **Password Reset**: Complete password reset flow with email verification

### 📚 Course Management
- Create courses with title, description, thumbnail, and syllabus (PDF)
- Organize content into modules and lessons
- Upload lesson materials (videos, PDFs, images)
- Support for YouTube/Vimeo video embedding
- Track course progress automatically

### 📝 Lesson System
- Rich text content for lessons
- Video support (YouTube, Vimeo, or uploaded)
- File attachments (PDFs, images, documents)
- Lesson completion tracking
- Sequential learning path

### 🎯 Quiz System
- Create quizzes for each lesson
- Multiple choice, true/false, and short answer questions
- **Attempt limits** - Configurable max attempts per quiz (default: 3)
- Quiz attempts history with counter
- Instructor can manage questions and choices
- Clear feedback when attempt limit reached

### 🎓 Certificate Generation
- Automatic certificate generation upon course completion
- PDF certificates with student name, course title, instructor name, and completion date
- Unique certificate ID for verification
- Download certificates anytime

### 📊 Dashboards
- **Student Dashboard**: View enrolled courses, track progress, access certificates
- **Instructor Dashboard**: Manage courses, view student enrollments
- **Admin Dashboard**: System overview, user management, full control

### 🔍 Search & Navigation
- **Course Search**: Search courses by title, description, or instructor
- **Pagination**: Browse courses with page navigation (9 per page)
- **Breadcrumbs**: Clear navigation path on all pages

### ⭐ Reviews & Ratings
- **Course Reviews**: Students can rate completed courses (1-5 stars)
- **Comments**: Add detailed feedback on courses
- **Average Rating**: Display course ratings on detail pages
- **Review History**: View all student reviews

### 💬 Doubts & Clarifications
- **Ask Questions**: Students can submit doubts on any lesson
- **Instructor Responses**: Instructors receive notifications and can respond
- **Resolution Tracking**: Mark doubts as resolved/unresolved
- **In-App Notifications**: Instructors see unresolved doubt count
- **Communication Hub**: Centralized Q&A for each lesson

### 📧 Email Notifications
- **Enrollment Confirmation**: Automatic email when student enrolls
- **Course Details**: Email includes course info and direct link
- **Console Output**: Development mode prints to console
- **SMTP Ready**: Production-ready email configuration

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install django djangorestframework djangorestframework-simplejwt django-widget-tweaks pillow reportlab
```

### Step 2: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Demo Data

```bash
python manage.py shell < seed_complete.py
```

This creates:
- Admin user (username: `admin`, password: `admin123`)
- 3 Instructors (username: `instructor1-3`, password: `pass123`)
- 5 Students (username: `student1-5`, password: `pass123`)
- 5 Sample courses with modules, lessons, and quizzes

### Step 4: Run the Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Usage Guide

### For Students

1. **Register**: Go to `/accounts/register/` and create an account with user_type='student'
2. **Browse Courses**: View available courses on the homepage or courses page
3. **Enroll**: Click on a course and click "Enroll Now"
4. **Learn**: Access lessons, watch videos, read content
5. **Complete Lessons**: Mark lessons as complete to track progress
6. **Take Quizzes**: Complete quizzes to test your knowledge
7. **Get Certificate**: Once all lessons are completed, generate your certificate

### For Instructors

1. **Register**: Create an account with user_type='instructor'
2. **Create Course**: Go to Dashboard → Create New Course
3. **Add Modules**: Organize your course into modules (use Django admin)
4. **Add Lessons**: Create lessons with content, videos, and attachments
5. **Create Quizzes**: Add quizzes to lessons with questions and choices
6. **Manage Students**: View enrolled students and their progress

### For Admins

1. **Access Admin Panel**: Go to `/admin/` and login with superuser credentials
2. **View Analytics**: Access `/admin/analytics/` for system reports and quick access to all features
3. **Track Student-Instructor Relationships**:
   - View all students learning under each instructor
   - View all instructors teaching each student
   - Access via "Students by Instructor" button
4. **Monitor Progress**:
   - Course-level progress tracking
   - Module-level progress breakdown
   - Lesson-level completion tracking
   - Visual progress bars and color coding
5. **Manage Instructors**:
   - View all instructors with statistics
   - See courses and student counts
   - Access detailed instructor profiles
   - View students in instructor's courses
3. **Manage Users**:
   - View all users (students, instructors, admins)
   - Create, edit, delete user accounts
   - Assign/change user roles (student, instructor, admin)
   - Reset user passwords
   - Activate/deactivate accounts
   - Bulk actions for role changes
4. **Manage Courses**:
   - View, create, edit, delete any course
   - Assign instructors to courses
   - Manage course categories
   - View enrollment statistics
5. **Manage Lessons & Modules**:
   - Create, edit, delete modules and lessons
   - Add videos, attachments, and content
   - Organize lesson order
6. **Manage Quizzes**:
   - Create, edit, delete quizzes
   - Manage questions and choices
   - View quiz attempts and results
7. **Manage Enrollments**:
   - View all student enrollments
   - Track student progress
   - Mark courses as complete/incomplete
   - Activate/deactivate enrollments
8. **Manage Certificates**:
   - View all issued certificates
   - Revoke certificates
   - Regenerate certificate PDFs
   - Verify certificate authenticity
9. **Manage Reviews**:
   - View all course reviews
   - Moderate review content
   - Delete inappropriate reviews
10. **System Analytics**:
    - User statistics (students, instructors, admins)
    - Course statistics (enrollments, completions)
    - Quiz statistics (attempts, completions)
    - Recent activity reports
    - Popular courses
11. **Media Management**:
    - View all uploaded media files
    - Manage course thumbnails
    - Manage lesson attachments
    - Organize media library

## Project Structure

```
trae_lms/
├── accounts/           # User authentication and profiles
├── courses/            # Course, Module, Lesson, Enrollment models
├── lessons/            # Lesson completion tracking
├── quizzes/            # Quiz, Question, Choice models
├── certificates/       # Certificate generation and verification
├── frontend/           # Homepage and general views
├── templates/          # HTML templates
├── media/              # Uploaded files (thumbnails, videos, etc.)
├── static/             # CSS, JavaScript, images
└── lms_project/        # Project settings and URLs
```

## Key Models

### User (accounts/models.py)
- Custom user model with role-based access (student, instructor, admin)
- Profile fields: phone, bio, date_of_birth, profile_picture

### Course (courses/models.py)
- Title, description, instructor, thumbnail, syllabus
- Related: Module, Lesson, Enrollment

### Enrollment (courses/models.py)
- Links students to courses
- Tracks progress and completion status

### Lesson (courses/models.py)
- Content, video_url, attachment
- Belongs to a Module

### Quiz (quizzes/models.py)
- Title, description, lesson, instructor
- Related: Question, Choice, QuizAttempt

### Certificate (certificates/models.py)
- Generated PDF certificate
- Unique UUID for verification

## URLs

### Public URLs
- `/` - Homepage
- `/accounts/register/` - User registration
- `/accounts/login/` - User login
- `/accounts/password-reset/` - Password reset
- `/accounts/dashboard/` - Role-based dashboard
- `/courses/` - Course list (with search & pagination)
- `/courses/<id>/` - Course detail (with reviews)
- `/courses/<id>/enroll/` - Enroll in course
- `/courses/lessons/<id>/` - Lesson detail
- `/quizzes/quiz/<id>/` - Quiz detail
- `/reviews/add/<course_id>/` - Add course review
- `/certificates/generate/<enrollment_id>/` - Generate certificate
- `/certificates/view/<uuid>/` - View certificate

### Admin URLs
- `/admin/` - Django admin panel
- `/admin/analytics/` - Admin analytics dashboard
- `/manage/instructor-students/` - Students by instructor view
- `/manage/student-instructors/` - Instructors by student view
- `/manage/instructors/` - All instructors management
- `/manage/instructors/<id>/` - Instructor details
- `/manage/courses/<id>/students/` - Course student progress
- `/manage/students/progress/` - All students progress
- `/manage/students/<sid>/course/<cid>/` - Student course details

## Role-Based Access Control

The system uses decorators to enforce role-based access:

- `@student_required` - Only students can access
- `@instructor_required` - Only instructors can access
- `@admin_required` - Only admins can access
- `@login_required` - Any authenticated user

## Database

Uses SQLite (db.sqlite3) for simplicity. All data is stored locally.

## Media Files

Uploaded files are stored in the `media/` directory:
- `course_thumbnails/` - Course images
- `syllabi/` - Course syllabus PDFs
- `lesson_attachments/` - Lesson files
- `certificates/` - Generated certificate PDFs
- `profile_pictures/` - User profile images

## Customization

### Adding New Features

1. Create models in appropriate app
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Create views and templates
5. Add URLs

### Styling

- Bootstrap 5 is used for styling
- Custom CSS is in `static/css/style.css`
- Templates extend `base.html`
- All styles are separated from HTML

## Troubleshooting

### Issue: Cannot login
- Ensure you created a user with correct user_type
- Check password is correct
- Verify user is active

### Issue: Cannot enroll in course
- Ensure you're logged in as a student
- Check if already enrolled

### Issue: Certificate not generating
- Ensure course is 100% complete
- Check all lessons are marked as complete
- Verify reportlab is installed

### Issue: Media files not showing
- Ensure `MEDIA_URL` and `MEDIA_ROOT` are set in settings.py
- Check file permissions
- Verify files are uploaded to correct directory

### Issue: Password reset email not received
- Check console/terminal where server is running (emails print there in development)
- For production, configure SMTP settings in `settings.py`
- See `EMAIL_SETUP_GUIDE.md` for detailed instructions

### Issue: Cannot access admin management pages
- Ensure you're logged in as admin/staff user
- Check `is_staff` flag is True for your user
- Verify you're accessing correct URLs (start with `/admin/analytics/`)

## Security Notes

- Change `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Use environment variables for sensitive data
- Implement proper user authentication
- Add CSRF protection (already included)

## Recent Updates

✅ **Pagination** - Course list with page navigation
✅ **Breadcrumbs** - Navigation path on all pages
✅ **Search** - Search courses by title, description, instructor
✅ **Password Reset** - Complete password reset flow
✅ **Reviews & Ratings** - Students can rate and review courses
✅ **Separate CSS** - All styles moved to `static/css/style.css`
✅ **Enhanced Admin** - Improved Django admin with filters and actions
✅ **Advanced Admin Features**
  - Student-Instructor relationship tracking
  - Detailed progress monitoring (course, module, lesson level)
  - Enhanced Django admin with statistics
  - Visual progress indicators and color coding
  - Comprehensive instructor and student management
✅ **NEW: January 2025 Updates**
  - Fixed navbar dropdown (single arrow)
  - Admin-only course creation
  - Quiz attempt limits (customizable per quiz)
  - Email notifications on enrollment
  - Student doubts & clarifications system
  - Instructor notification system
  - See documentation: `UPDATES_IMPLEMENTATION.md`

## Future Enhancements

- Email notifications for enrollments
- Discussion forums
- Live video classes
- Advanced quiz scoring with grades
- Payment integration
- Mobile app
- Real-time notifications

## License

This project is for educational purposes.

## Documentation

### Admin Features Documentation
- **QUICK_START_ADMIN.md** - Quick start guide for admin features
- **COMPLETE_ADMIN_FEATURES.md** - Complete list of all admin features
- **ADMIN_MANAGEMENT_GUIDE.md** - Detailed admin management guide
- **STUDENT_INSTRUCTOR_TRACKING.md** - Student-instructor relationship tracking
- **ADMIN_NAVIGATION_MAP.md** - Visual navigation map
- **TESTING_CHECKLIST.md** - Testing checklist for all features

### Setup Documentation
- **EMAIL_SETUP_GUIDE.md** - Email configuration for password reset
- **IMPLEMENTATION_SUMMARY.md** - Summary of implemented features

### Latest Updates Documentation (January 2025)
- **UPDATES_IMPLEMENTATION.md** - Complete implementation details for all updates
- **QUICK_FIXES_SUMMARY.md** - Quick reference for all fixes
- **GOOGLE_REVIEWS_GUIDE.md** - Guide for Google Reviews integration (optional)

## Support

For issues or questions:
1. Check the documentation files listed above
2. Review code comments
3. Consult Django documentation
4. Check troubleshooting section

---

**Built with Django 4.2+ and Python 3.12**

## Quick Start for Admins

1. Start server: `python manage.py runserver`
2. Login: http://127.0.0.1:8000/admin/ (admin/admin123)
3. Access dashboard: http://127.0.0.1:8000/admin/analytics/
4. Explore features using quick access buttons
5. See `QUICK_START_ADMIN.md` for detailed guide

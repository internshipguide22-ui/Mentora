# LMS Admin Guide

## Complete Admin Capabilities

### 1. User Management

**Access**: `/admin/accounts/user/`

#### View All Users
- List of all registered users (students, instructors, admins)
- Filter by user type, active status, staff status
- Search by username, email, name, phone
- Sort by date joined

#### Create Users
- Add new users with username, email, password
- Assign user type (student, instructor, admin)
- Set personal information (name, phone, bio)
- Upload profile pictures

#### Edit Users
- Modify user details (name, email, phone, bio)
- Change user roles
- Update profile pictures
- Edit permissions

#### Delete Users
- Remove user accounts
- Bulk delete multiple users
- Cascade delete related data

#### Assign Roles
- **Make Instructor**: Convert users to instructor role
- **Make Student**: Convert users to student role
- **Make Admin**: Promote users to admin with staff access
- Bulk role assignment

#### Reset Passwords
- Access password reset for any user
- Send password reset emails
- Set new passwords directly

#### Activate/Deactivate
- Enable or disable user accounts
- Bulk activate/deactivate users
- View active user count

---

### 2. Course Management

**Access**: `/admin/courses/course/`

#### View All Courses
- List of all courses regardless of instructor
- Filter by category, instructor, creation date
- Search by title, description, instructor
- View enrollment counts

#### Create Courses
- Add new courses with title and description
- Assign instructor
- Set category
- Upload thumbnail and syllabus PDF

#### Edit Courses
- Modify course details
- Change instructor assignment
- Update media files
- Edit course content

#### Delete Courses
- Remove courses from system
- Bulk delete multiple courses
- Cascade delete modules and lessons

#### Assign Instructors
- Change course instructor
- Reassign courses to different instructors
- View instructor's course load

#### Course Statistics
- View enrollment count per course
- See module and lesson counts
- Track course completion rates

---

### 3. Module & Lesson Management

**Access**: `/admin/courses/module/` and `/admin/courses/lesson/`

#### Manage Modules
- Create modules for courses
- Edit module titles and descriptions
- Set module order
- View lesson count per module
- Inline module creation from course page

#### Manage Lessons
- Create lessons within modules
- Add text content, descriptions
- Upload videos (YouTube/Vimeo URLs)
- Attach files (PDFs, documents, images)
- Set lesson order
- View which lessons have videos/attachments
- Edit lesson content
- Delete lessons

---

### 4. Quiz Management

**Access**: `/admin/quizzes/quiz/`

#### Create Quizzes
- Add quizzes to lessons
- Set quiz title and description
- Configure time limits
- Set passing scores
- Publish/unpublish quizzes

#### Manage Questions
- Add multiple choice questions
- Add true/false questions
- Add short answer questions
- Set question points
- Order questions
- Inline question creation

#### Manage Choices
- Add answer choices to questions
- Mark correct answers
- Edit choice text
- Inline choice creation

#### View Quiz Results
- See all quiz attempts
- View student scores
- Track completion rates
- Filter by quiz, student, date
- Export quiz results

---

### 5. Enrollment Management

**Access**: `/admin/courses/enrollment/`

#### View Enrollments
- List all student enrollments
- Filter by course, completion status, date
- Search by student or course
- View progress percentages

#### Track Progress
- See student progress bars
- View completion percentages
- Track lesson completions
- Monitor quiz attempts

#### Manage Enrollments
- Mark enrollments as complete/incomplete
- Activate/deactivate enrollments
- Bulk enrollment actions
- View enrollment dates

#### Student Performance
- View individual student progress
- See course completion dates
- Track learning paths
- Generate progress reports

---

### 6. Certificate Management

**Access**: `/admin/certificates/certificate/`

#### View Certificates
- List all issued certificates
- Filter by issue date
- Search by student or course
- View certificate IDs

#### Issue Certificates
- Manually generate certificates
- Regenerate certificate PDFs
- Bulk certificate generation

#### Revoke Certificates
- Delete/revoke certificates
- Bulk revoke certificates
- Track revoked certificates

#### Verify Certificates
- Check certificate authenticity
- View certificate details
- Download certificate PDFs

---

### 7. Review Management

**Access**: `/admin/reviews/review/`

#### View Reviews
- List all course reviews
- Filter by rating, date
- Search by student, course, comment
- View average ratings

#### Moderate Reviews
- Edit review content
- Delete inappropriate reviews
- Bulk delete reviews
- Track review dates

---

### 8. System Analytics

**Access**: `/admin/analytics/`

#### User Statistics
- Total users count
- Students, instructors, admins breakdown
- Active users count
- Recent user registrations
- User growth trends

#### Course Statistics
- Total courses count
- Total enrollments
- Active enrollments
- Completed courses
- Course completion rates
- Popular courses

#### Quiz Statistics
- Total quizzes
- Quiz attempts
- Completed quizzes
- Average scores

#### Certificate Statistics
- Total certificates issued
- Certificates by course
- Recent certificates

#### Activity Reports
- Recent enrollments
- Recent user registrations
- Recent quiz attempts
- System activity logs

---

### 9. Media Management

**Access**: Django Admin File Browser

#### Upload Media
- Course thumbnails
- Course syllabus PDFs
- Lesson attachments
- Lesson videos
- Profile pictures

#### Organize Media
- View all uploaded files
- Delete unused media
- Manage file storage
- Check file sizes

---

### 10. Admin Dashboard

**Access**: `/accounts/dashboard/` (when logged in as admin)

#### Quick Actions
- Access Admin Panel
- View Analytics
- Manage Users
- Manage Courses
- Manage Enrollments
- Manage Quizzes
- Manage Certificates
- Manage Reviews

#### Statistics Overview
- Total users, courses, enrollments, certificates
- User type breakdown
- Active users count
- System health indicators

---

## Admin Bulk Actions

### User Bulk Actions
- Change role to Instructor
- Change role to Student
- Change role to Admin
- Activate selected users
- Deactivate selected users
- Delete selected users

### Course Bulk Actions
- Delete selected courses
- Assign to instructor

### Enrollment Bulk Actions
- Mark as completed
- Mark as incomplete
- Activate enrollments
- Deactivate enrollments

### Certificate Bulk Actions
- Revoke selected certificates
- Regenerate certificates

### Quiz Bulk Actions
- Publish quizzes
- Unpublish quizzes
- Delete quizzes

---

## Admin Permissions

### Superuser Access
- Full access to all features
- Can create other admins
- Can modify any data
- Access to Django admin panel

### Staff Access
- Access to admin panel
- Limited to assigned permissions
- Can manage specific models
- Cannot create superusers

---

## Admin Best Practices

1. **Regular Backups**: Export data regularly
2. **User Management**: Review user accounts periodically
3. **Content Moderation**: Monitor reviews and course content
4. **Analytics Review**: Check system analytics weekly
5. **Certificate Verification**: Audit certificates monthly
6. **Security**: Change admin passwords regularly
7. **Media Cleanup**: Remove unused media files
8. **Performance**: Monitor enrollment and course counts

---

## Admin URLs

- **Admin Panel**: `/admin/`
- **Analytics**: `/admin/analytics/`
- **Users**: `/admin/accounts/user/`
- **Courses**: `/admin/courses/course/`
- **Modules**: `/admin/courses/module/`
- **Lessons**: `/admin/courses/lesson/`
- **Enrollments**: `/admin/courses/enrollment/`
- **Quizzes**: `/admin/quizzes/quiz/`
- **Questions**: `/admin/quizzes/question/`
- **Certificates**: `/admin/certificates/certificate/`
- **Reviews**: `/admin/reviews/review/`
- **Categories**: `/admin/courses/category/`

---

## Creating a Superuser

```bash
python manage.py createsuperuser
```

Follow prompts to set:
- Username
- Email
- Password

---

## Admin Login

1. Go to `/admin/`
2. Enter superuser credentials
3. Access full admin panel

---

## Support

For admin support, refer to Django documentation or contact system administrator.

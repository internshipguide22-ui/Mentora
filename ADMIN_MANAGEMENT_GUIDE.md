# Admin Panel Management Guide

## Overview
The admin panel now provides comprehensive management of instructors, students, courses, and detailed progress tracking.

## Accessing Admin Features

### 1. Django Admin Panel
URL: `http://127.0.0.1:8000/admin/`

Login with admin credentials:
- Username: `admin`
- Password: `admin123`

### 2. Admin Analytics Dashboard
URL: `http://127.0.0.1:8000/admin/analytics/`

Quick access to:
- Manage Instructors
- Student Progress
- Manage Users
- Manage Courses
- Manage Enrollments

## Managing Instructors

### View All Instructors
**URL:** `/manage/instructors/`

**Features:**
- List all instructors with statistics
- View number of courses per instructor
- View total students enrolled in instructor's courses
- Check instructor status (Active/Inactive)
- Quick access to detailed view

### View Instructor Details
**URL:** `/manage/instructors/<instructor_id>/`

**Features:**
- Instructor profile information
- Total courses created
- Total students across all courses
- List of all courses with:
  - Enrollment count
  - Completion count
  - Completion rate
  - Quick link to view students

**Actions:**
- Click "View Students" to see all students in a specific course

## Managing Student Progress

### View Course Students
**URL:** `/manage/courses/<course_id>/students/`

**Features:**
- List all students enrolled in a course
- Overall progress percentage for each student
- Lesson completion count (e.g., 5/10 lessons)
- Module-wise progress breakdown
- Visual progress bars
- Enrollment date
- Status (Completed/In Progress)

**Module Progress Table:**
- Shows each module in the course
- Displays lessons completed per module
- Progress percentage per module
- Color-coded status:
  - Green: 100% complete
  - Yellow: In progress
  - Red: Not started

**Actions:**
- Click "View Detailed Progress" to see lesson-level details

### View Student Course Details
**URL:** `/manage/students/<student_id>/course/<course_id>/`

**Features:**
- Student information (name, email, username)
- Course information (title, instructor, enrollment date)
- Overall progress with visual progress bar
- Complete module and lesson breakdown

**Lesson-Level Details:**
- Lesson title
- Completion status (✓ Completed / Not Started)
- Completion date and time
- Video/Attachment indicators
- Quiz attempts count
- Last quiz attempt date

**Color Coding:**
- Green rows: Completed lessons
- White rows: Not started lessons

### View All Students Progress
**URL:** `/manage/students/progress/`

**Features:**
- List all students in the system
- Total enrollments per student
- Completed courses count
- Average progress across all courses
- Visual progress bars
- Account status

## Django Admin Panel Features

### 1. Users Management
**Location:** Admin → Accounts → Users

**Enhanced Features:**
- **Statistics Column:** Shows course/student counts for instructors, enrollment/completion for students
- **Filters:** By user type, status, join date
- **Search:** By username, email, name, phone
- **Bulk Actions:**
  - Change role to Instructor
  - Change role to Student
  - Change role to Admin
  - Activate/Deactivate users

### 2. Courses Management
**Location:** Admin → Courses → Courses

**Enhanced Features:**
- **Lesson Count:** Total lessons in course
- **Completion Rate:** Percentage of students who completed
- **Course Statistics:** Shows enrollments, active students, completed count
- **Enrolled Students Details:** Complete table with:
  - Student name and email
  - Progress percentage
  - Lessons completed
  - Status
  - Enrollment date

**View in Admin:**
- Click on a course
- Scroll down to see "Course Statistics" section
- View "Enrolled Students Details" table

### 3. Enrollments Management
**Location:** Admin → Courses → Enrollments

**Enhanced Features:**
- **Instructor Column:** Shows which instructor's course
- **Lesson Progress:** Shows X/Y lessons completed
- **Detailed Progress:** Expandable section showing:
  - Overall progress summary
  - Student and course information
- **Module Progress:** Complete table showing:
  - Each module's progress
  - Lessons completed per module
  - Completed lesson names
  - Color-coded rows (green=complete, yellow=in progress, red=not started)

**Filters:**
- By completion status
- By course
- By instructor
- By enrollment date

**Bulk Actions:**
- Mark as completed
- Mark as incomplete
- Activate enrollments
- Deactivate enrollments

### 4. Lesson Completions Management
**Location:** Admin → Lessons → Lesson Completions

**Enhanced Features:**
- **Student Email:** Quick reference
- **Module Column:** Shows which module
- **Instructor Column:** Shows course instructor
- **Completion Details:** Expandable section showing:
  - Student information
  - Lesson, module, and course details
  - Course progress (X/Y lessons, percentage)
  - Completion timestamp

**Filters:**
- By course
- By instructor
- By module
- By completion date

**Search:**
- By student username/email
- By lesson title
- By course title
- By instructor username

## Instructor Self-Management

Instructors can also manage their own courses and view student progress through:

**URL:** `/courses/instructor/students/`

**Features:**
- View all students across all their courses
- Filter by specific course
- See student progress
- Track lesson completions

## Use Cases

### Use Case 1: Admin Checks Instructor Performance
1. Go to `/manage/instructors/`
2. View list of all instructors with course/student counts
3. Click "View Details" on an instructor
4. See all their courses and enrollment statistics
5. Click "View Students" on a specific course
6. Review student progress and completion rates

### Use Case 2: Admin Monitors Student Progress
1. Go to `/manage/students/progress/`
2. View all students with average progress
3. Or go to specific course: `/manage/courses/<course_id>/students/`
4. See module-wise progress for each student
5. Click "View Detailed Progress" for lesson-level details
6. Check which lessons are completed and quiz attempts

### Use Case 3: Admin Reviews Course Performance
1. Go to Django Admin → Courses
2. Click on a course
3. Scroll to "Course Statistics" section
4. View total enrollments, active students, completions
5. Scroll to "Enrolled Students Details"
6. See complete table of all students with progress

### Use Case 4: Admin Tracks Lesson Completions
1. Go to Django Admin → Lesson Completions
2. Filter by instructor to see their students' progress
3. Filter by course to see specific course completions
4. Click on a completion record
5. View "Completion Details" for full context

## Tips for Admins

1. **Quick Navigation:**
   - Use Admin Analytics dashboard for quick access links
   - Bookmark frequently used pages

2. **Filtering:**
   - Use Django admin filters to narrow down data
   - Combine multiple filters for precise results

3. **Bulk Actions:**
   - Select multiple records in Django admin
   - Use bulk actions for efficient management

4. **Progress Monitoring:**
   - Check module-wise progress to identify struggling students
   - Use completion rates to evaluate course effectiveness

5. **Instructor Oversight:**
   - Regularly review instructor statistics
   - Monitor student enrollment and completion rates
   - Identify courses that need improvement

## Color Coding Reference

### Progress Bars
- **Green:** Completed (100%)
- **Orange/Yellow:** In Progress (1-99%)
- **Gray:** Not Started (0%)

### Status Badges
- **Green (Success):** Active, Completed
- **Yellow (Warning):** In Progress
- **Red (Danger):** Inactive, Not Started
- **Blue (Primary):** Course count
- **Info (Light Blue):** Lesson count

### Table Rows
- **Light Green Background:** Completed modules/lessons
- **Light Yellow Background:** In progress
- **Light Red Background:** Not started

## Troubleshooting

### Issue: Can't see instructor management links
**Solution:** Ensure you're logged in as admin/staff and accessing `/admin/analytics/`

### Issue: Student progress not updating
**Solution:** Progress updates when lessons are marked complete. Check lesson completion records.

### Issue: Module progress shows 0%
**Solution:** Ensure the module has lessons and students have completed some lessons.

### Issue: Can't access management pages
**Solution:** These pages require staff/admin permissions. Check user `is_staff` flag.

## Security Notes

- Only staff members (admins) can access management pages
- All views are protected with `@staff_member_required` decorator
- Regular instructors and students cannot access these admin features
- Instructors can only manage their own courses through instructor dashboard

## Future Enhancements

Potential additions:
- Export student progress to CSV/PDF
- Email notifications to students
- Bulk progress updates
- Advanced analytics charts
- Student performance reports
- Instructor performance metrics

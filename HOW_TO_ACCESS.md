# How to Access Admin Features

## Step-by-Step Instructions

### Step 1: Start the Server
```bash
python manage.py runserver
```

### Step 2: Login to Admin Panel
1. Open browser
2. Go to: **http://127.0.0.1:8000/admin/**
3. Login:
   - Username: `admin`
   - Password: `admin123`

### Step 3: Access Analytics Dashboard
After logging in, go to:
**http://127.0.0.1:8000/admin/analytics/**

You should see buttons at the top:
- 👨🏫 Students by Instructor
- 📚 Manage Instructors
- 👥 Student Progress
- 👤 Manage Users
- 📖 Manage Courses

### Step 4: Click "Students by Instructor"
This will take you to: **http://127.0.0.1:8000/manage/instructor-students/**

Here you will see:
- All instructors listed
- For each instructor: which students are learning from them
- Click "View Courses" to see which courses
- Click "Details" for lesson-level progress

## Direct URLs (After Login)

```
Admin Analytics:        http://127.0.0.1:8000/admin/analytics/
Students by Instructor: http://127.0.0.1:8000/manage/instructor-students/
All Instructors:        http://127.0.0.1:8000/manage/instructors/
Student Progress:       http://127.0.0.1:8000/manage/students/progress/
```

## What You'll See

### Students by Instructor Page
```
👨🏫 Instructor Name (email@example.com)
    5 Students
    
    Table showing:
    - Student Name
    - Email
    - Courses Enrolled (with this instructor)
    - Completed Courses
    - Average Progress
    - [View Courses] button
```

### When You Click "View Courses"
```
Courses:
• Course 1 - 80% - Completed
• Course 2 - 60% - In Progress
• Course 3 - 45% - In Progress
[Details] button for each course
```

## Troubleshooting

### If you don't see the buttons:
1. Make sure you're at: http://127.0.0.1:8000/admin/analytics/
2. NOT just: http://127.0.0.1:8000/admin/
3. Scroll down if needed

### If you get an error:
1. Make sure server is running
2. Make sure you're logged in as admin
3. Check the URL is correct

### If no data shows:
1. Load demo data: `python manage.py shell < seed_complete.py`
2. Refresh the page

## Quick Test

1. Start server: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/analytics/
3. Click: "👨🏫 Students by Instructor"
4. You should see instructors with their students!

---

**If you still can't see it, send me a screenshot of what you see at:**
http://127.0.0.1:8000/admin/analytics/

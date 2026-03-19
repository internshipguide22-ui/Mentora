from django.db import migrations


def sync_quiz_module_column(apps, schema_editor):
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(quizzes_quiz)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'module_id' not in columns:
            cursor.execute("ALTER TABLE quizzes_quiz ADD COLUMN module_id bigint NULL")

        if 'lesson_id' in columns:
            cursor.execute(
                """
                UPDATE quizzes_quiz
                SET module_id = (
                    SELECT module_id
                    FROM courses_lesson
                    WHERE courses_lesson.id = quizzes_quiz.lesson_id
                )
                WHERE module_id IS NULL
                  AND lesson_id IS NOT NULL
                """
            )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS quizzes_quiz_module_id_idx ON quizzes_quiz(module_id)"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(sync_quiz_module_column, migrations.RunPython.noop),
    ]

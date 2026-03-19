from django.db import migrations


def rebuild_quiz_table(apps, schema_editor):
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(quizzes_quiz)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'lesson_id' not in columns:
            return

        cursor.execute("PRAGMA foreign_keys=OFF")

        cursor.execute(
            """
            CREATE TABLE quizzes_quiz_new (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                title varchar(200) NOT NULL,
                description text NOT NULL,
                instructions text NOT NULL,
                start_date datetime NULL,
                end_date datetime NULL,
                time_limit_minutes integer unsigned NOT NULL CHECK ("time_limit_minutes" >= 0),
                passing_score integer unsigned NOT NULL CHECK ("passing_score" >= 0),
                max_attempts integer unsigned NOT NULL CHECK ("max_attempts" >= 0),
                is_published bool NOT NULL,
                shuffle_questions bool NOT NULL,
                show_correct_answers bool NOT NULL,
                created_at datetime NOT NULL,
                updated_at datetime NOT NULL,
                instructor_id bigint NOT NULL REFERENCES accounts_user (id) DEFERRABLE INITIALLY DEFERRED,
                module_id bigint NULL REFERENCES courses_module (id) DEFERRABLE INITIALLY DEFERRED
            )
            """
        )

        cursor.execute(
            """
            INSERT INTO quizzes_quiz_new (
                id, title, description, instructions, start_date, end_date,
                time_limit_minutes, passing_score, max_attempts, is_published,
                shuffle_questions, show_correct_answers, created_at, updated_at,
                instructor_id, module_id
            )
            SELECT
                id, title, description, instructions, start_date, end_date,
                time_limit_minutes, passing_score, max_attempts, is_published,
                shuffle_questions, show_correct_answers, created_at, updated_at,
                instructor_id, module_id
            FROM quizzes_quiz
            """
        )

        cursor.execute("DROP TABLE quizzes_quiz")
        cursor.execute("ALTER TABLE quizzes_quiz_new RENAME TO quizzes_quiz")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS quizzes_quiz_instructor_id_idx ON quizzes_quiz(instructor_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS quizzes_quiz_module_id_idx ON quizzes_quiz(module_id)"
        )
        cursor.execute("PRAGMA foreign_keys=ON")


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_sync_quiz_module_column'),
    ]

    operations = [
        migrations.RunPython(rebuild_quiz_table, migrations.RunPython.noop),
    ]

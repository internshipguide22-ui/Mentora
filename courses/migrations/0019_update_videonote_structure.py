import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def set_missing_video_note_timestamps(apps, schema_editor):
    VideoNote = apps.get_model('courses', 'VideoNote')
    VideoNote.objects.filter(timestamp_seconds__isnull=True).update(timestamp_seconds=0)


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0018_videonote'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='videonote',
            old_name='student',
            new_name='created_by',
        ),
        migrations.AlterField(
            model_name='videonote',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_video_notes',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(set_missing_video_note_timestamps, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='videonote',
            name='timestamp_seconds',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterModelOptions(
            name='videonote',
            options={'ordering': ['timestamp_seconds', 'created_at']},
        ),
    ]

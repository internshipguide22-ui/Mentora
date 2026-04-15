from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0019_update_videonote_structure'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_access_type',
            field=models.CharField(
                choices=[('free', 'Free'), ('paid', 'Paid')],
                default='free',
                help_text='Choose whether learners can access this course for free or as a paid course.',
                max_length=10,
            ),
        ),
    ]

# Generated by Django 4.2 on 2023-05-07 16:17

from django.db import migrations


def add_clear_tokens_task(apps, scheme_editor):
    # Set a task for celery to execute in the background
    from django_celery_beat.models import IntervalSchedule, PeriodicTask
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=60,
        period=IntervalSchedule.SECONDS,
    )

    PeriodicTask.objects.create(
        interval=schedule,
        name='Clear expired tokens',
        task="oauthsample.tasks.clear_tokens",
        args='[]',
    )


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.RunPython(add_clear_tokens_task)
    ]

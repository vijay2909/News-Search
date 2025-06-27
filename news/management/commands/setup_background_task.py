from django.core.management.base import BaseCommand
from background_task.models import Task
from news.tasks import refresh_all_keywords
import os


class Command(BaseCommand):
    help = 'Sets up the single repeating background task to refresh all keywords.'

    def handle(self, *args, **options):
        """
        The main logic of the management command.
        It checks if the task already exists and, if not, schedules it.
        """
        task_name = "news.tasks.refresh_all_keywords"

        # Check if the repeating task is already scheduled to avoid duplicates
        if Task.objects.filter(verbose_name=task_name).exists():
            self.stdout.write(
                self.style.WARNING(f'Repeating task "{task_name}" is already scheduled. No action taken.'))
            self.stdout.write(self.style.SUCCESS(
                'To reschedule with a new interval, first delete the task from the Django Admin panel under "Background Tasks".'))
            return

        # Fetch the interval from .env file, defaulting to 1 hour (3600 seconds)
        refresh_interval = int(os.getenv('BACKGROUND_TASK_REFRESH_INTERVAL', 3600))

        # Schedule the task to run.
        # It runs 10 seconds after scheduling (from the decorator)
        # and will repeat every `refresh_interval` seconds.
        refresh_all_keywords(
            repeat=refresh_interval,
            verbose_name=task_name,
            remove_existing_tasks=True
        )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully scheduled the repeating task "{task_name}" to run every {refresh_interval} seconds.'))


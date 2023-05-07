import time

from celery import shared_task


@shared_task
def clear_tokens():
    from oauth2_provider.models import clear_expired

    clear_expired()
    from oauthsample.models import EmailToken
    EmailToken.objects.filter(is_expired=False, expires_at__lte=int(time.time())).update(is_expired=True)


@shared_task(email="", token="")
def send_mails(email, token):
    from django.core.mail import send_mail
    from django.conf import settings

    is_sent = send_mail(
        subject="Password Reset",
        message="Please click the link below to reset"
                f" your password on oauthsample {settings.BASE_URL}/reset-password/{token}/",
        recipient_list=[email], fail_silently=False, from_email=None)
    print(f"Email sent {is_sent}")

    # Remove task for sent email
    if is_sent:
        from django_celery_beat.models import PeriodicTask
        task = PeriodicTask.objects.filter(name=token)
        task.delete()

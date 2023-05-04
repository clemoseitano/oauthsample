import secrets
import secrets
import time

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser, User
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, \
    HTTP_408_REQUEST_TIMEOUT
from rest_framework.views import APIView

from oauthsample import services
from oauthsample.models import Product, EmailToken
from oauthsample.permissions import IsOwnerOrStaff
from oauthsample.serializers import RegistrationSerializer, LoginSerializer, ProductSerializer


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"success": "User registered successfully"}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class LoginView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        print(request.data)
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=email, password=password)
        print(type(user))
        if user is not None and not isinstance(user, AnonymousUser):
            # Get access tokens
            token = services.generate_access_token(user)
            serializer = LoginSerializer(user)
            return Response({'user': {**serializer.data}, 'token': token}, status=HTTP_200_OK)
        return Response({"error": "Invalid email or password"}, status=HTTP_401_UNAUTHORIZED)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        user = User.objects.filter(email=email)
        if not user:
            return Response({"error": "Invalid email"}, status=HTTP_401_UNAUTHORIZED)

        email_token = secrets.token_urlsafe()

        expiry = int(time.time()) + int(settings.EMAIL_TIMEOUT)
        EmailToken.objects.create(
            token=email_token,
            user=user.first(),
            expires_at=expiry)

        # Set a task for celery to execute in the background
        from django_celery_beat.models import IntervalSchedule, PeriodicTask
        import json
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=15,
            period=IntervalSchedule.SECONDS,
        )

        PeriodicTask.objects.create(
            interval=schedule,
            name=email_token,
            task="oauthsample.tasks.send_mails",
            args=json.dumps([email, email_token]),
        )
        return Response({'success': f'Email will be sent to {email} in a moment'}, status=HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        tokens = EmailToken.objects.filter(token=token)
        if not tokens:
            return Response({"error": "Not found"}, status=HTTP_404_NOT_FOUND)
        used_token = tokens.first()
        password = request.data.get("password")
        if not password:
            return Response({"error": "Password must be provided"}, status=HTTP_400_BAD_REQUEST)
        if not used_token.is_expired and used_token.expires_at >= int(time.time()):
            user = used_token.user
            user.set_password(password)
            user.save()
            used_token.is_expired = True
            used_token.save()
            return Response({'success': 'Password reset successful'}, status=HTTP_200_OK)
        return Response({'success': 'Email verification link has expired'}, status=HTTP_408_REQUEST_TIMEOUT)


class ProductViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    permission_classes = [IsOwnerOrStaff]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

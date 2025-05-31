

from datetime import date
# adjust import as needed
import json
from webauthn import generate_authentication_options
from knox.views import LogoutView as KnoxLogoutView
from knox.models import AuthToken
from knox.auth import TokenAuthentication as KnoxTokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.views.decorators.http import require_POST
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.core.mail import send_mail
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, FormView
# from .origin_check import verify_frontend_origin
from .models import *
from .forms import *
from .serializers import *
from .permissions import *
from .logger import logger
from .base_code import base64url_encode


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


@method_decorator(csrf_exempt, name='dispatch')
class SessionLoginView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                django_login(request, user)
                return JsonResponse({'message': 'Session login successful'})
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
        except Exception as e:
            logger.error(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)


# Ensures CSRF cookie is set
@method_decorator(ensure_csrf_cookie, name='dispatch')
class SessionView(APIView):
    permission_classes = []  # Allow all users (unauthenticated) to access

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                django_login(request, user)
                # Optional: regenerate CSRF after login
                csrf_token = get_token(request)
                return Response({'message': 'Session login successful', 'csrfToken': csrf_token})
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Login error: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


@require_POST
def login_view(request):

    try:

        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        if email is None or password is None:
            return JsonResponse({'error': 'Email and password are required'}, status=400)
        user = authenticate(request, username=email, password=password)
        if user is None:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        django_login(request, user)

        return JsonResponse({'message': 'Login successful'}, status=200)
    except Exception as e:
        logger.error(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def html_logout_view(request):
    django_logout(request)
    return redirect(('http://localhost:8000/login'))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        # Knox logout
        request._auth.delete()
        AuthToken.objects.filter(user=request.user).delete()

        # Django session logout
        django_logout(request)

        # Clear cookies
        response = Response({'message': 'Logout successful'}, status=200)
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        return response
    except Exception as e:
        logger.error(f"Error: {e}")
        return Response({'error': str(e)}, status=500)


@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False}, status=401)

    return JsonResponse({
        'isAuthenticated': True,
        'email': request.user.email
    }, status=200)


def whoami(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'user': {
                'id': request.user.id,
                'email': request.user.email,
            }
        })
    else:
        return JsonResponse({'error': 'User not logged in'}, status=401)


@login_required
@ensure_csrf_cookie
def current_user(request):
    print(f"Session User: {request.user}")
    if request.user.is_authenticated:
        return JsonResponse({
            'user': {
                # 'id': request.user.id,
                'email': request.user.email,
            }
        })
    else:
        return JsonResponse({'error': 'User not logged in'}, status=401)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        logger.info(" Login attempt received")

        try:
            serializer = self.serializer_class(data=request.data)

            if not serializer.is_valid():
                logger.warning(f" Invalid login data: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            logger.debug(f" Authenticating user with email: {email}")

            user = authenticate(request, email=email, password=password)

            if user:
                logger.info(
                    f" Authentication successful for user: {user.email}")

                django_login(request, user)
                logger.info(f" User {user.email} logged in to session")

                _, token = AuthToken.objects.create(user)
                user_data = UserDetailSerializer(user).data

                logger.info(
                    f" Token generated and user data serialized for {user.email}")

                return Response({
                    'user': user_data,
                    'token': token
                })

            else:
                logger.warning(f" Invalid credentials for email: {email}")
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            logger.error(
                f" Unexpected error during login: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


# @ensure_csrf_cookie
# def get_csrf_token(request):
#     try:

#         return JsonResponse({"detail": "CSRF cookie set"})
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# @method_decorator(ensure_csrf_cookie, name='dispatch')
# class GetCRSFToken(APIView):
#     permission_classes = [permissions.AllowAny]

#     def get(self, request, format=None):
#         try:
#             logger.debug("Setting CSRF cookie for request: %s", request)
#             return Response({
#                 'success': 'CSRF cookie set'
#             })
#         except Exception as e:
#             logger.error("Error setting CSRF cookie: %s", str(e))
#             return Response({
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCRSFToken(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        try:
            csrfToken = get_token(request)
            logger.debug(
                "Setting CSRF cookie for request: %s, token: %s", request, csrfToken)
            return Response({
                'success': 'CSRF cookie set',
                'csrfToken': csrfToken
            })
        except Exception as e:
            logger.error("Error setting CSRF cookie: %s", str(e))
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomLogoutView(KnoxLogoutView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        try:
            django_logout(request)
            return super().post(request, format=format)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterViewSet(viewsets.ModelViewSet):

    # queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Override to prevent accessing the list of users
        # This will return an empty queryset, effectively blocking the list view.
        return CustomUser.objects.none()

    # def get_permissions(self):
    #     # This ensures that only the `create` action is accessible, blocking `list` and `retrieve`
    #     if self.action == 'create':
    #         # You can replace this with your desired permission
    #         return [permissions.AllowAny()]
    #     return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        try:
            # origin_check = verify_frontend_origin(request)
            # if origin_check:
            #     return origin_check

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HrManagerRegisterViewSet(viewsets.ModelViewSet):

    # queryset = CustomUser.objects.all()
    serializer_class = HrManagerRegisterSerializer
    # permission_classes = [permissions.AllowAny]

    def get_queryset(self):

        return CustomUser.objects.none()

    def get_permissions(self):

        if self.action == 'create':

            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        try:
            # origin_check = verify_frontend_origin(request)
            # if origin_check:
            #     return origin_check

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ManagerRegisterViewSet(viewsets.ModelViewSet):

    # queryset = CustomUser.objects.all()
    serializer_class = ManagerRegisterSerializer
    # permission_classes = [permissions.AllowAny]

    def get_queryset(self):

        return CustomUser.objects.none()

    def get_permissions(self):

        if self.action == 'create':

            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        try:
            # origin_check = verify_frontend_origin(request)
            # if origin_check:
            #     return origin_check

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeRegisterViewSet(viewsets.ModelViewSet):

    serializer_class = EmployeeRegisterSerializer
    # permission_classes = [permissions.AllowAny]

    def get_queryset(self):

        return CustomUser.objects.none()

    def get_permissions(self):

        if self.action == 'create':

            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        try:
            # origin_check = verify_frontend_origin(request)
            # if origin_check:
            #     return origin_check

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OverallAdminRegisterViewSet(viewsets.ModelViewSet):

    # queryset = CustomUser.objects.all()
    serializer_class = OverallAdminRegisterSerializer
    # permission_classes = [permissions.AllowAny]

    def get_queryset(self):

        return CustomUser.objects.none()

    def get_permissions(self):

        if self.action == 'create':

            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        try:
            # origin_check = verify_frontend_origin(request)
            # if origin_check:
            #     return origin_check

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            # origin_check = verify_frontend_origin(request)
            # if origin_check:
            #     return origin_check
            queryset = CustomUser.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailView(FormView, ListView):
    template_name = 'emails.html'
    form_class = EmailForm
    success_url = '/emails'
    model = Emails
    context_object_name = 'mydata'

    def get_queryset(self):
        return Emails.objects.all().order_by('-created_at')

    def form_valid(self, form):
        try:
            my_subject = 'Email from our Django App'
            my_message = 'This is a message from our app'
            my_recipient = form.cleaned_data['email']
            send_mail(
                subject=my_subject,
                message=my_message,
                from_email=None,
                recipient_list=[my_recipient],
                fail_silently=False


            )
            obj = Emails(
                subject=my_subject,
                message=my_message,
                email=my_recipient
            )
            obj.save()
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CreateProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [KnoxTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            return Profile.objects.filter(user=self.request.user)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            user = request.user

            if Profile.objects.filter(user=user).exists():
                raise ValidationError(
                    {"detail": "A profile for this user already exists."})

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CreateProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    queryset = Profile.objects.all()
    authentication_classes = [
        KnoxTokenAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            user = request.user

            if Profile.objects.filter(user=request.user).exists():
                raise ValidationError(
                    {"detail": "Profile already exists for this user."})

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateProfileAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = []  # Or [KnoxAuthentication, ...]
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if Profile.objects.filter(user=request.user).exists():
            raise ValidationError(
                {"detail": "Profile already exists for this user."})

        request.data['user'] = request.user.id

        serializer = CreateProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewProfileViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                profile = Profile.objects.get(user=request.user)
                # Use the serializer to serialize the profile object
                serializer = ViewProfileSerializer(profile)
                return Response(serializer.data)
            except Profile.DoesNotExist:
                return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = EditProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = EditProfileSerializer(
            profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewAllProfilesViewSet(viewsets.ViewSet):
    def list(self, request):
        # Fetch all profiles
        profiles = Profile.objects.all()
        serializer = ViewProfileSerializer(
            profiles, many=True)  # Serialize multiple profiles
        return Response(serializer.data)


class EditProfileViewSet(viewsets.ModelViewSet):
    serializer_class = EditProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:

            return Profile.objects.filter(user=self.request.user)
        else:
            return Profile.objects.none()

    def update(self, request, *args, **kwargs):
        try:

            instance = self.get_object()

            if instance.user != request.user:
                return Response({"error": "Unauthorized"}, status=403)

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial)

            serializer.is_valid(raise_exception=True)

            self.perform_update(serializer)

            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceView(APIView):
    def get(self, request):

        user = request.user
        today = timezone.now().date()
        logger.info(f"GET request: user={user},date={today}")
        try:
            biometric_scan = BiometricAttendance.objects.filter(
                employee=user, date=today, method='biometric').first()
            if biometric_scan and (biometric_scan.check_in or biometric_scan.check_out):
                return Response({
                    "error": "You started with biometrics attendance today. Please continue using biometric.",
                    "biometric_attendance": BiometricAttendanceSerializer(biometric_scan).data,
                    "manual_attendance": None
                }, status=403)
        except Exception as e:
            logger.warning(f"BiometricAttendance check failed: {str(e)}")
        try:
            attendance = ManualAttendance.objects.filter(
                employee=user,
                date=today
            ).order_by('-check_in').first()
            if attendance:
                serializer = ManualAttendanceSerializer(attendance)
                logger.info(
                    f"Returning attendance: id={attendance.id}, check_in={attendance.check_in}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.info("No attendance record found, enabling check-in")
                return Response({
                    'should_show_check_in': True,
                    'should_show_check_out': False,
                    'can_check_out': False,
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"GET error: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        user = request.user
        today = timezone.now().date()
        action = request.data.get('action')
        logger.info(
            f"POST request: user={user}, action={action}, date={today}")

        if not action:
            logger.error("Action is required")
            return Response({'error': 'Action is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            biometric_scan = BiometricAttendance.objects.filter(
                employee=user, date=today, method='biometric').first()
            if biometric_scan and (biometric_scan.check_in or biometric_scan.check_out):
                return Response({
                    "error": "You started with biometrics attendance today. Please continue using biometric.",
                    "biometric_attendance": BiometricAttendanceSerializer(biometric_scan).data,
                    "manual_attendance": None
                }, status=403)
        except Exception as e:
            logger.warning(f"BiometricAttendance check failed: {str(e)}")
        biometric_attendance = ManualAttendance.objects.filter(
            employee=user,
            date=today,
            method='biometric'
        ).exists()
        logger.info(f"Biometric attendance exists: {biometric_attendance}")

        try:
            with transaction.atomic():
                attendance, created = ManualAttendance.objects.get_or_create(
                    employee=user,
                    date=today,
                    method='manual',
                    defaults={'manual_check_in': True}
                )
                logger.info(
                    f"Attendance record: id={attendance.id}, created={created}, check_in={attendance.check_in}")

                if action == 'check_in':
                    if biometric_attendance:
                        logger.warning(
                            "Check-in blocked: biometric attendance exists")
                        return Response(
                            {'error': 'Already checked in with biometric, complete it'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    if not attendance.should_show_check_in():
                        logger.warning("Check-in blocked: already checked in")
                        return Response(
                            {'error': 'Already checked in'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    attendance.check_in = timezone.now()
                    logger.info(f"Setting check_in: {attendance.check_in}")
                    attendance.save()
                    logger.info(
                        f"Check-in saved: id={attendance.id}, check_in={attendance.check_in}, worked_hours={attendance.worked_hours}")
                    serializer = ManualAttendanceSerializer(attendance)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                elif action == 'check_out':
                    if biometric_attendance:
                        logger.warning(
                            "Check-out blocked: biometric attendance exists")
                        return Response(
                            {'error': 'Already checked in with biometric, complete it'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    if not attendance.can_check_out() or not attendance.should_show_check_out():
                        logger.warning("Check-out not allowed yet")
                        return Response(
                            {'error': 'Check-out not allowed yet'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    attendance.check_out = timezone.now()
                    logger.info(f"Setting check_out: {attendance.check_out}")
                    attendance.save()
                    logger.info(
                        f"Check-out saved: id={attendance.id}, check_out={attendance.check_out}, worked_hours={attendance.worked_hours}")
                    serializer = ManualAttendanceSerializer(attendance)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    logger.error(f"Invalid action: {action}")
                    return Response(
                        {'error': 'Invalid action'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            logger.error(f"POST error: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def save(self, *args, **kwargs):
        logger.info(
            f"Saving attendance: id={self.id}, check_in={self.check_in}, check_out={self.check_out}")
        try:
            if self.check_in and self.check_out:
                self.worked_hours = self.calculate_worked_hours()
                self.calculate_overtime()
                super().save(*args, **kwargs)
                logger.info(
                    f"Saved attendance: id={self.id}, check_in={self.check_in}, worked_hours={self.worked_hours}")
        except Exception as e:
            logger.error(f"Error saving attendance: {str(e)}", exc_info=True)
            raise


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_method(request):
    try:
        user = request.user
        today = date.today()

        # Has user already used manual today?
        manual_today = ManualAttendance.objects.filter(
            user=user,
            date=today,
            method='manual'
        ).exists()

        if manual_today:
            return Response({'method': 'manual', 'reason': 'Already used manual today'})

        # Fingerprint registered?
        if user.profile.fingerprint_registered:
            return Response({'method': 'biometric'})
        else:
            return Response({'method': 'manual', 'reason': 'No fingerprint registered'})
    except Exception as e:
        logger.error(f"Error: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BiometricAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            today = timezone.now().date()
            biometric_registered = WebAuthnCredential.objects.filter(
                user=user).exists()

            if not biometric_registered:
                return Response({
                    "error": "No biometric credential registered. Please register your biometric first.",
                    "done_for_today": False,
                    "can_check_in": False,
                    "can_check_out": False,
                    "biometric_attendance": None,
                    "manual_attendance": None,
                }, status=403)

            biometric = BiometricAttendance.objects.filter(
                employee=user, date=today).first()
            manual = ManualAttendance.objects.filter(
                employee=user, date=today).first()

            biometric_done = biometric and biometric.check_in and biometric.check_out
            manual_done = manual and manual.check_in and manual.check_out
            done_for_today = biometric_done or manual_done

            if manual and (manual.check_in or manual.check_out):
                return Response({
                    "error": "You started with manual attendance today. Please continue manually.",
                    "manual_attendance": ManualAttendanceSerializer(manual).data,
                    "biometric_attendance": None
                }, status=403)

            can_check_in = not done_for_today and (
                (biometric is None or biometric.check_in is None) and
                (manual is None or manual.check_in is None)
            )

            can_check_out = False
            if not done_for_today:
                if biometric and biometric.check_in and biometric.check_out is None:
                    can_check_out = biometric.should_show_check_out()
                elif manual and manual.check_in and manual.check_out is None:
                    can_check_out = manual.should_show_check_out()

            overtime = biometric.overtime_hours if biometric else None

            return Response({
                "done_for_today": done_for_today,
                "can_check_in": can_check_in,
                "can_check_out": can_check_out,
                "overtime_hours": overtime,
                "biometric_attendance": BiometricAttendanceSerializer(biometric).data if biometric else None,
                "manual_attendance": ManualAttendanceSerializer(manual).data if manual else None,
            })
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            user = request.user
            today = date.today()
            credential_id = request.data.get("credential_id")
            action = request.data.get("action")

            if not credential_id or action not in ["check_in", "check_out"]:
                return Response({"error": "Missing credential or action"}, status=400)

            if ManualAttendance.objects.filter(employee=user, date=today).exists():
                return Response({"error": "Already used manual method today. Please continue manually."}, status=400)

            try:
                credential = WebAuthnCredential.objects.get(
                    user=user, credential_id=credential_id)
            except WebAuthnCredential.DoesNotExist:
                return Response({"error": "Credential not found"}, status=404)

            attendance, created = BiometricAttendance.objects.get_or_create(
                employee=user, credential=credential, date=today,
                defaults={'biometric_verified': True, 'method': 'biometric'}
            )

            if action == "check_in":
                if attendance.check_in:
                    return Response({"error": "Already checked in"}, status=400)
                attendance.check_in = now()

            elif action == "check_out":
                if not attendance.check_in:
                    return Response({"error": "Check in first"}, status=400)
                if attendance.check_out:
                    return Response({"error": "Already checked out"}, status=400)
                if not attendance.should_show_check_out():  # Add check for 1-hour delay
                    return Response({"error": "Check-out not allowed yet. Please wait 1 hour after check-in."}, status=400)
                attendance.check_out = now()
                attendance.calculate_worked_hours()

            attendance.calculate_overtime()
            attendance.save()

            return Response({
                "status": "success",
                "message": f"{action} recorded",
                "attendance": BiometricAttendanceSerializer(attendance).data
            })
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BiometricAttendanceStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            today = date.today()

            # If manual attendance was used, deny biometric entirely
            if ManualAttendance.objects.filter(employee=user, date=today).exists():
                return Response({
                    "error": "Manual attendance already used today. You must continue manually.",
                    "can_check_in": False,
                    "can_check_out": False,
                    "attendance": None
                }, status=200)

            attendance = BiometricAttendance.objects.filter(
                employee=user, date=today).first()
            if not attendance:
                return Response({
                    "can_check_in": True,
                    "can_check_out": False,
                    "attendance": None
                })

            return Response({
                "can_check_in": attendance.should_show_check_in(),
                "can_check_out": attendance.should_show_check_out(),
                "attendance": BiometricAttendanceSerializer(attendance).data,
                "overtime_hours": attendance.overtime_hours
            })
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateCompanyProfile(viewsets.ModelViewSet):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsOverallAdmin]

    def create(self, request, *args, **kwargs):
        try:
            if request.user.role != 'Overall_Admin':
                raise PermissionDenied(
                    'Only Admins can create a group profile')
            if CompanyProfile.objects.filter(user=request.user).exists():
                raise ValidationError(
                    {
                        "detail": "Company profile already exists for this user."
                    }

                )
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            if request.user.role != "Overall_Admin":
                raise PermissionDenied(
                    "Only Overall_Admins can update a company profile.")
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        try:
            if request.user.role != "Overall_Admin":
                raise PermissionDenied(
                    "Only Overall_Admins can update a company profile.")
            return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ---------- DESTROY ----------
    def destroy(self, request, *args, **kwargs):
        try:
            if request.user.role != "Overall_Admin":
                raise PermissionDenied(
                    "Only Overall_Admins can delete a company profile.")
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateWebAuthnCredentialViewSet(viewsets.ModelViewSet):
    serializer_class = WebAuthnCredentialCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    # queryset = WebAuthnCredential.objects.all()

    # In your WebAuthnCredential viewset (DRF)
    def get_queryset(self):
        return WebAuthnCredential.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FingerprintRequestOptionsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            credentials = WebAuthnCredential.objects.all()
            if not credentials.exists():
                return JsonResponse({'error': 'No credentials found'}, status=status.HTTP_404_NOT_FOUND)

            allow_credentials = [
                {
                    'id': credential.credential_id,
                    'type': 'public-key',
                }
                for credential in credentials
            ]

            options = generate_authentication_options(

                rp_id=settings.WEBAUTHN_RP_ID,
                timeout=60000,
                user_verification='required',
                allow_credentials=allow_credentials,
            )

            public_key_options = {
                'challenge': base64url_encode(options.challenge),
                'rpId': options.rp_id,
                'timeout': options.timeout,
                'userVerification': options.user_verification,
                'allowCredentials': allow_credentials,
            }

            return JsonResponse({'publicKey': public_key_options})
        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FingerprintAuthenticateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):

        credential_id = request.data.get('credential_id')

        if not credential_id:
            logger.error(f"Error: {e}")
            return Response({'error': 'Credential ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Search by credential ID (assumed to be a base64url string)
            credential = WebAuthnCredential.objects.get(
                credential_id=credential_id)
            user = credential.user

            # Log the user in
            django_login(request, user)

            # Generate auth token
            token = AuthToken.objects.create(user=user)

            return Response({
                'token': token[1],
                'user_id': user.id,
                'email': user.email,
                'role': user.role,
                'department': user.department,

            })

        except WebAuthnCredential.DoesNotExist:
            logger.error(f"Error: {e}")
            return Response({'error': 'Invalid credential ID'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error: {e}")
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

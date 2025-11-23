"""
Authentication views including password reset with OTP
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from .models import PasswordResetOTP
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request password reset - sends OTP to user's email
    """
    try:
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return Response({
                'message': 'If an account exists with this email, you will receive an OTP shortly.'
            }, status=status.HTTP_200_OK)
        
        # Invalidate any existing OTPs for this user
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Generate new OTP
        otp_code = PasswordResetOTP.generate_otp()
        otp = PasswordResetOTP.objects.create(
            user=user,
            otp=otp_code
        )
        
        # Send email with OTP
        try:
            subject = 'Password Reset OTP - Chemical Equipment Visualizer'
            message = f"""
Hello {user.username},

You have requested to reset your password for Chemical Equipment Parameter Visualizer.

Your OTP is: {otp_code}

This OTP will expire in 5 minutes.

If you did not request this password reset, please ignore this email.

Best regards,
Chemical Equipment Visualizer Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            logger.info(f"Password reset OTP sent to {email}")
            
            return Response({
                'message': 'OTP has been sent to your email address',
                'email': email
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return Response({
                'error': 'Failed to send email. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error in request_password_reset: {str(e)}")
        return Response({
            'error': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP before allowing password reset
    """
    try:
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        
        if not email or not otp_code:
            return Response({
                'error': 'Email and OTP are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find valid OTP
        try:
            otp = PasswordResetOTP.objects.get(
                user=user,
                otp=otp_code,
                is_used=False
            )
            
            if not otp.is_valid():
                return Response({
                    'error': 'OTP has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # OTP is valid, return success
            return Response({
                'message': 'OTP verified successfully',
                'token': otp_code  # We'll use this to verify during password reset
            }, status=status.HTTP_200_OK)
            
        except PasswordResetOTP.DoesNotExist:
            return Response({
                'error': 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in verify_otp: {str(e)}")
        return Response({
            'error': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset password after OTP verification
    """
    try:
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not email or not otp_code or not new_password:
            return Response({
                'error': 'Email, OTP, and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength
        if len(new_password) < 8:
            return Response({
                'error': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid request'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        try:
            otp = PasswordResetOTP.objects.get(
                user=user,
                otp=otp_code,
                is_used=False
            )
            
            if not otp.is_valid():
                return Response({
                    'error': 'OTP has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Reset password
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            otp.is_used = True
            otp.save()
            
            logger.info(f"Password reset successful for {email}")
            
            return Response({
                'message': 'Password has been reset successfully. You can now login with your new password.'
            }, status=status.HTTP_200_OK)
            
        except PasswordResetOTP.DoesNotExist:
            return Response({
                'error': 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in reset_password: {str(e)}")
        return Response({
            'error': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Enhanced registration with email validation
    """
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validation
        if not username or not email or not password:
            return Response({
                'error': 'Username, email, and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 8:
            return Response({
                'error': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already registered. If you deleted your account, please use a different email or contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        logger.info(f"New user registered: {username}")
        
        return Response({
            'message': 'Registration successful. Please login.',
            'username': username
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        return Response({
            'error': 'An error occurred during registration. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password for authenticated user
    """
    try:
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'error': 'Current password and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current password
        if not user.check_password(current_password):
            return Response({
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password
        if len(new_password) < 8:
            return Response({
                'error': 'New password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Change password
        user.set_password(new_password)
        user.save()
        
        # Update token (force re-login)
        Token.objects.filter(user=user).delete()
        Token.objects.create(user=user)
        
        logger.info(f"Password changed for user: {user.username}")
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in change_password: {str(e)}")
        return Response({
            'error': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user profile (email)
    """
    try:
        user = request.user
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email is already taken by another user
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            return Response({
                'error': 'Email is already in use by another account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update email
        user.email = email
        user.save()
        
        logger.info(f"Profile updated for user: {user.username}")
        
        return Response({
            'message': 'Profile updated successfully',
            'email': email
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in update_profile: {str(e)}")
        return Response({
            'error': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """
    Delete user account permanently
    """
    try:
        user = request.user
        username = user.username
        
        # Delete all user's tokens
        Token.objects.filter(user=user).delete()
        
        # Delete user (cascade will delete related data)
        user.delete()
        
        logger.info(f"Account deleted for user: {username}")
        
        return Response({
            'message': 'Account deleted successfully'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in delete_account: {str(e)}")
        return Response({
            'error': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

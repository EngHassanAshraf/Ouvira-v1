"""
OTP Service - Handles OTP generation, validation, and management
"""
import logging
from datetime import timedelta
from random import randint
from django.utils import timezone
from django.db import DatabaseError

from ..models import OTP
from apps.shared.exceptions import BusinessException
from apps.shared.messages.error import ERROR_MESSAGES

logger = logging.getLogger(__name__)

# Constants
MAX_ATTEMPTS = 3
BLOCK_MINUTES = 15
OTP_EXPIRY_MINUTES = 60


class OTPService:
    """Service for managing OTP operations"""

    @staticmethod
    def generate_otp_code() -> str:
        """Generate a 6-digit OTP code"""
        return str(randint(100000, 999999))

    @staticmethod
    def create_otp(phone_number: str, expiry_minutes: int = OTP_EXPIRY_MINUTES) -> OTP:
        """
        Create a new OTP for a phone number.
        Deletes any existing OTPs for the phone number first.
        
        Args:
            phone_number: Phone number to create OTP for
            expiry_minutes: OTP expiry time in minutes
            
        Returns:
            Created OTP instance
        """
        # Delete existing OTPs for this phone number
        OTP.objects.filter(phone_number=phone_number).delete()
        
        otp_code = OTPService.generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        otp = OTP.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at,
            attempts=0,
            is_blocked=False,
            blocked_until=None,
        )
        
        logger.info(f"OTP created for phone number: {phone_number}")
        return otp

    @staticmethod
    def get_otp(phone_number: str) -> OTP | None:
        """Get the most recent OTP for a phone number"""
        return OTP.objects.filter(phone_number=phone_number).first()

    @staticmethod
    def verify_otp(phone_number: str, otp_code: str) -> tuple[bool, str]:
        """
        Verify an OTP code.
        
        Args:
            phone_number: Phone number associated with OTP
            otp_code: OTP code to verify
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        otp_entry = OTPService.get_otp(phone_number)
        
        if not otp_entry:
            return False, ERROR_MESSAGES["OTP_EXPIRED"]
        
        # Check if OTP is blocked
        if otp_entry.is_blocked:
            if otp_entry.blocked_until and otp_entry.blocked_until > timezone.now():
                return False, ERROR_MESSAGES["OTP_EXPIRED"]
            # Unblock if block period has passed
            otp_entry.is_blocked = False
            otp_entry.attempts = 0
            otp_entry.blocked_until = None
            otp_entry.save()
        
        # Check expiration
        if otp_entry.expires_at < timezone.now():
            otp_entry.delete()
            return False, ERROR_MESSAGES["OTP_EXPIRED"]
        
        # Verify OTP code
        if otp_entry.otp_code != otp_code:
            otp_entry.attempts += 1
            
            if otp_entry.attempts >= MAX_ATTEMPTS:
                otp_entry.is_blocked = True
                otp_entry.blocked_until = timezone.now() + timedelta(minutes=BLOCK_MINUTES)
            
            otp_entry.save()
            return False, ERROR_MESSAGES["INCORRECT_OTP"]
        
        # OTP is valid
        return True, ""

    @staticmethod
    def delete_otp(phone_number: str) -> None:
        """Delete all OTPs for a phone number"""
        OTP.objects.filter(phone_number=phone_number).delete()
        logger.info(f"OTPs deleted for phone number: {phone_number}")

    @staticmethod
    def cleanup_expired_otps() -> int:
        """
        Clean up expired OTPs.
        
        Returns:
            Number of deleted OTPs
        """
        count, _ = OTP.objects.filter(expires_at__lt=timezone.now()).delete()
        logger.info(f"Cleaned up {count} expired OTPs")
        return count

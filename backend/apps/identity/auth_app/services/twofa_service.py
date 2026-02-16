"""
Two-Factor Authentication Service - Handles 2FA operations
"""
import logging
import secrets
import pyotp
from random import randint
from django.utils import timezone

from apps.identity.account.models.user import CustomUser, TwoALoginSession
from apps.shared.exceptions import BusinessException
from apps.shared.messages.error import ERROR_MESSAGES

logger = logging.getLogger(__name__)


class TwoFAService:
    """Service for Two-Factor Authentication operations"""

    @staticmethod
    def generate_secret() -> str:
        """Generate a TOTP secret"""
        return pyotp.random_base32()

    @staticmethod
    def generate_backup_codes(count: int = 5) -> list[str]:
        """
        Generate backup codes for 2FA.
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            List of backup codes
        """
        return [secrets.token_hex(4) for _ in range(count)]

    @staticmethod
    def enable_2fa(user: CustomUser) -> dict:
        """
        Enable 2FA for a user.
        
        Args:
            user: User instance
            
        Returns:
            Dictionary with backup codes
        """
        user.is_2fa_enabled = True
        user.two_fa_secret = TwoFAService.generate_secret()
        user.backup_codes = TwoFAService.generate_backup_codes()
        user.save(update_fields=["is_2fa_enabled", "two_fa_secret", "backup_codes"])
        
        logger.info(f"2FA enabled for user: {user.primary_mobile}")
        
        return {
            "backup_codes": user.backup_codes,
        }

    @staticmethod
    def create_login_session(user: CustomUser) -> TwoALoginSession:
        """
        Create a 2FA login session.
        
        Args:
            user: User instance
            
        Returns:
            Created TwoALoginSession instance
        """
        session = TwoALoginSession.objects.create(user=user)
        logger.info(f"2FA login session created: {session.session_id}")
        return session

    @staticmethod
    def generate_2fa_code(user: CustomUser) -> str:
        """
        Generate a 2FA code based on user's 2FA type.
        
        Args:
            user: User instance
            
        Returns:
            Generated 2FA code (for testing/dev purposes)
        """
        if user.two_fa_type == "AUTHENTICATOR":
            totp = pyotp.TOTP(user.two_fa_secret)
            return totp.now()
        elif user.two_fa_type == "SMS":
            # Generate SMS code (in production, this would be sent via SMS)
            return str(randint(100000, 999999))
        else:
            raise BusinessException("Invalid 2FA type")

    @staticmethod
    def verify_totp_code(secret: str, code: str, valid_window: int = 6) -> bool:
        """
        Verify a TOTP code.
        
        Args:
            secret: TOTP secret
            code: Code to verify
            valid_window: Time window for code validity
            
        Returns:
            True if code is valid, False otherwise
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=valid_window)

    @staticmethod
    def verify_backup_code(user: CustomUser, backup_code: str) -> bool:
        """
        Verify a backup code and remove it if valid.
        
        Args:
            user: User instance
            backup_code: Backup code to verify
            
        Returns:
            True if code is valid, False otherwise
        """
        if backup_code not in user.backup_codes:
            return False
        
        # Remove used backup code
        user.backup_codes.remove(backup_code)
        user.save(update_fields=["backup_codes"])
        
        logger.info(f"Backup code used for user: {user.primary_mobile}")
        return True

    @staticmethod
    def verify_2fa_session(session_id: str, code: str) -> tuple[CustomUser | None, str]:
        """
        Verify a 2FA session with code.
        
        Args:
            session_id: Session ID
            code: 2FA code to verify
            
        Returns:
            Tuple of (user, error_message)
        """
        try:
            session = TwoALoginSession.objects.get(
                session_id=session_id, is_verified=False
            )
        except TwoALoginSession.DoesNotExist:
            return None, "Invalid or expired session"
        
        if session.is_expired():
            return None, "Expired session"
        
        user = session.user
        
        # Verify code based on 2FA type
        if user.two_fa_type == "AUTHENTICATOR":
            if not TwoFAService.verify_totp_code(user.two_fa_secret, code):
                return None, "Invalid 2FA code"
        elif user.two_fa_type == "SMS":
            # TODO: Implement SMS code verification
            return None, "SMS verification not implemented yet"
        else:
            return None, "Invalid 2FA type"
        
        # Mark session as verified
        session.is_verified = True
        session.save()
        
        return user, ""

    @staticmethod
    def verify_2fa_backup_session(session_id: str, backup_code: str) -> tuple[CustomUser | None, str]:
        """
        Verify a 2FA session with backup code.
        
        Args:
            session_id: Session ID
            backup_code: Backup code to verify
            
        Returns:
            Tuple of (user, error_message)
        """
        try:
            session = TwoALoginSession.objects.get(
                session_id=session_id, is_verified=False
            )
        except TwoALoginSession.DoesNotExist:
            return None, ERROR_MESSAGES["ACCOUNT_NOT_FOUND"]
        
        if session.is_expired():
            return None, ERROR_MESSAGES["OTP_EXPIRED"]
        
        user = session.user
        
        if not TwoFAService.verify_backup_code(user, backup_code):
            return None, ERROR_MESSAGES["INCORRECT_OTP"]
        
        # Mark session as verified
        session.is_verified = True
        session.save()
        
        return user, ""

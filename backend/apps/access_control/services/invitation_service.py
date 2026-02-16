"""
Invitation Service - Handles company invitations
"""
import logging
import secrets
from django.utils import timezone
from django.db.models import QuerySet

from ..models import Invitation, UserCompany, UserCompanyRole
from apps.identity.account.models import CustomUser
from apps.company.models import Company
from apps.shared.exceptions import BusinessException

logger = logging.getLogger(__name__)


class InvitationService:
    """Service for invitation operations"""

    @staticmethod
    def get_user_company_ids(user) -> QuerySet:
        """Get active company IDs for a user"""
        return UserCompany.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False
        ).values_list("company_id", flat=True)

    @staticmethod
    def get_invitations_for_user(user, company_id: int = None, status: str = None) -> QuerySet:
        """
        Get invitations accessible to a user.
        
        Args:
            user: User instance
            company_id: Optional company ID to filter by
            status: Optional status to filter by
            
        Returns:
            QuerySet of Invitation instances
        """
        user_companies = InvitationService.get_user_company_ids(user)
        
        queryset = Invitation.objects.filter(company_id__in=user_companies)
        
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by("-created_at")

    @staticmethod
    def get_invitation(pk: int, user=None) -> Invitation:
        """
        Get a specific invitation.
        
        Args:
            pk: Invitation primary key
            user: Optional user to verify access
            
        Returns:
            Invitation instance
        """
        invitation = Invitation.objects.get(pk=pk)
        
        # Verify user has access if provided
        if user:
            user_companies = InvitationService.get_user_company_ids(user)
            if invitation.company_id not in user_companies:
                raise BusinessException("You don't have access to this invitation.")
        
        return invitation

    @staticmethod
    def create_invitation(
        company: Company,
        email: str,
        role,
        invited_by: CustomUser,
        expires_at=None,
        token: str = None
    ) -> Invitation:
        """
        Create a new invitation.
        
        Args:
            company: Company instance
            email: Invitee email
            role: Role instance
            invited_by: User creating the invitation
            expires_at: Optional expiry datetime
            token: Optional token (generated if not provided)
            
        Returns:
            Created Invitation instance
        """
        # Validate role belongs to company
        if role.company is not None and role.company != company:
            raise BusinessException("Selected role does not belong to the target company.")
        
        # Check for existing pending invitation
        if Invitation.objects.filter(email=email, company=company, status="pending").exists():
            raise BusinessException("There is already a pending invitation for this email and company.")
        
        if not token:
            token = secrets.token_urlsafe(32)
        
        if not expires_at:
            expires_at = Invitation.default_expiry()
        
        invitation = Invitation.objects.create(
            company=company,
            email=email.lower().strip(),
            role=role,
            token=token,
            expires_at=expires_at,
            invited_by=invited_by
        )
        
        logger.info(f"Invitation created for {email} to company {company.name}")
        return invitation

    @staticmethod
    def accept_invitation(token: str, user: CustomUser) -> tuple[UserCompany, UserCompanyRole]:
        """
        Accept an invitation.
        
        Args:
            token: Invitation token
            user: User accepting the invitation
            
        Returns:
            Tuple of (UserCompany, UserCompanyRole) instances
            
        Raises:
            BusinessException: If invitation is invalid or expired
        """
        try:
            invitation = Invitation.objects.get(token=token, status="pending")
        except Invitation.DoesNotExist:
            raise BusinessException("Invalid or expired invitation token.")
        
        # Check expiration
        if invitation.is_expired():
            invitation.mark_expired()
            raise BusinessException("Invitation has expired.")
        
        # Verify email matches
        if user.email.lower() != invitation.email.lower():
            raise BusinessException("Invitation email does not match your account email.")
        
        # Create or reactivate UserCompany association
        from ..services.user_company_service import UserCompanyService
        user_company = UserCompanyService.associate_user_with_company(
            user=user,
            company=invitation.company
        )
        
        # Assign role
        from ..services.user_company_role_service import UserCompanyRoleService
        user_company_role = UserCompanyRoleService.assign_role_to_user(
            user_company=user_company,
            role=invitation.role
        )
        
        # Update invitation status
        invitation.status = "accepted"
        invitation.accepted_by = user
        invitation.save()
        
        logger.info(f"Invitation accepted by {user.email} for company {invitation.company.name}")
        return user_company, user_company_role

    @staticmethod
    def revoke_invitation(invitation: Invitation) -> None:
        """
        Revoke an invitation.
        
        Args:
            invitation: Invitation instance to revoke
            
        Raises:
            BusinessException: If invitation cannot be revoked
        """
        if invitation.status != "pending":
            raise BusinessException(f"Cannot revoke invitation with status '{invitation.status}'.")
        
        invitation.status = "revoked"
        invitation.save()
        logger.info(f"Invitation revoked: {invitation.email}")

    @staticmethod
    def resend_invitation(invitation: Invitation) -> Invitation:
        """
        Resend an invitation (extends expiry).
        
        Args:
            invitation: Invitation instance to resend
            
        Returns:
            Updated Invitation instance
            
        Raises:
            BusinessException: If invitation cannot be resent
        """
        if invitation.status != "pending":
            raise BusinessException(f"Cannot resend invitation with status '{invitation.status}'.")
        
        invitation.expires_at = Invitation.default_expiry()
        invitation.save()
        
        logger.info(f"Invitation resent: {invitation.email}")
        return invitation

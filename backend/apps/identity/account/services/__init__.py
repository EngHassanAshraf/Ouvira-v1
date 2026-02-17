"""
Account services module.
"""

from .account_service import AccountService

# Aliases for backward compatibility
UserService = AccountService

__all__ = [
    "AccountService",
    "UserService",
]

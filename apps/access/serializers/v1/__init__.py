# flake8: noqa
from .base import (
    SimpleUserReadOnlyModelSerializer,
    CommonUserUpdateSerializer,
    CommonUserDetailUpdateSerializer,
    UserProfilePictureRetrieveSerializer,
    CommonLearningDashboardSerializer,
)
from .tenant_admin import TenantAdminUserCreateModelSerializer, TenantAdminUserDetailCreateModelSerializer
from .user import (
    UserCreateModelSerializer,
    UserDetailReadOnlyModelSerializer,
    UserReadOnlyModelSerializer,
)
from .profile import (
    AdminDetailUpdateSerializer,
    AdminProfileUpdateSerializer,
    UserDetailUpdateSerializer,
    UserProfileUpdateSerializer,
    UserSkillDetailCreateSerializer,
    UserEducationDetailCreateSerializer,
    UserAreaOfInterestUpdateSerializer,
    UserSkillDetailRetrieveSerializer,
)

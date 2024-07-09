from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum

from apps.access.config import GenderChoices, MaritalStatusChoices
from apps.access.managers import AppUserManagerQuerySet
from apps.access_control.config import RoleTypeChoices
from apps.common.config import DEFAULT_PASSWORD_LENGTH
from apps.common.helpers import random_n_token
from apps.common.model_fields import AppPhoneNumberField
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    ArchivableModel,
    BaseModel,
    ImageOnlyModel,
)
from apps.common.validators import validate_pincode
from apps.my_learning.tasks import SkillOntologyProgressUpdateTask
from apps.tenant_service.middlewares import get_current_db_name


class User(ArchivableModel, AbstractUser):
    """
    Default custom user model for IIHT-B2B.

    Model Fields -
        PK          - id
        FKs         - role, groups, user_permissions, profile_picture
        Fields      - uuid, username, email, first_name, middle_name, last_name, password, idp_id
        Datetime    - date_joined, last_login, created, modified
        Bool        - is_staff, is_superuser, is_active, is_deleted

    App QuerySet Manager Methods -
        create_user, create_superuser, get_or_none, active, inactive, alive, dead, delete, hard_delete
    """

    # objects manager
    objects = AppUserManagerQuerySet.as_manager()

    # FK fields
    roles = models.ManyToManyField("access_control.UserRole", blank=True, related_name="related_user_roles")
    profile_picture = models.ForeignKey(
        "access.UserProfilePicture", on_delete=models.SET_NULL, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Fields
    email = models.EmailField(unique=True)
    middle_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    last_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    idp_id = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    data = models.JSONField(default=dict)
    current_role = models.ForeignKey(
        "access_control.UserRole",
        on_delete=models.SET_NULL,
        related_name="related_current_role",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        """Email as string representation."""

        return self.email

    @property
    def name(self):
        """Full name of the user."""

        full_name = "{} {}".format(self.first_name, self.last_name or "")
        return full_name.strip()

    @property
    def total_leaderboard_points(self):
        """Total leaderboard points earned."""

        return self.related_leaderboard_activities.aggregate(total_points=Sum("points"))["total_points"] or 0

    @property
    def user_detail(self):
        """Return UserDetail instance of the User."""

        detail, created = UserDetail.objects.get_or_create(user=self)
        return detail

    def get_active_role(self, is_reset=False):
        """get currently active role the user is in."""

        if not self.roles.exists():
            return None

        if is_reset or not self.current_role:
            if self.roles.filter(role_type__in=[RoleTypeChoices.admin, RoleTypeChoices.manager]).exists():
                admin_role = self.roles.filter(role_type=RoleTypeChoices.admin).first()
                if admin_role:
                    self.current_role = admin_role
                else:
                    manager_role = self.roles.filter(role_type=RoleTypeChoices.manager).first()
                    self.current_role = manager_role
                self.save()
            else:
                any_role = self.roles.all().first()
                self.current_role = any_role
                self.save()
        return self.current_role.role_type

    def get_user_init_data_idp(self):
        """Used one time when user is getting onboarded."""

        password = random_n_token(DEFAULT_PASSWORD_LENGTH)
        return {
            "email": self.email,
            "name": self.first_name,
            "surname": self.last_name if self.last_name else "",
            "role": "TenantUser",
            "password": password,
            "businessUnitName": "string",
            "userIdNumber": self.user_detail.user_id_number,
            "managerName": "string",
            "managerEmail": "string",
        }

    def related_skill_ontology_progress_update(self, learning_type, learning_obj, db_name=None):
        """Function to update the user related skill ontologies progress."""

        filter_params = {f"skill_ontology__{learning_type}": learning_obj}
        tracker_ids = self.related_user_skill_ontology_trackers.filter(**filter_params).values_list("id", flat=True)
        if tracker_ids:
            if not db_name:
                db_name = get_current_db_name()
            SkillOntologyProgressUpdateTask().run_task(db_name=db_name, tracker_ids=list(tracker_ids))

        return True

    def report_data(self):
        """Function to return user details for report."""

        return {
            "user_email": self.email,
            "user_id": self.id,
            "user_uuid": self.uuid,
            "user_username": self.username,
            "user_first_name": self.first_name,
            "user_last_name": self.last_name,
            "user_status": self.is_active,
            "user_employee_id": self.user_detail.employee_id,
            "user_group_names": list(self.related_user_groups.all().values_list("name", flat=True)),
        }


class UserDetail(BaseModel):
    """
    Model to store user details.

    Model Fields -
        PK          - id,
        FK          - user
        Fields      - uuid, user_id_number, user_grade, manager_name, manager_email, organization_unit_id,
                        business_unit_name, manager_id, config_str, birth_date, contact_number, gender,
                        current_address, current_city, current_state, current_country, current_pincode,
                        permanent_address, permanent_city, permanent_state, permanent_country, permanent_pincode,
                        promotion_date, certifications
        Datetime    - created_at, modified_at, deleted_at
        Bool        - is_onsite_user

    App QuerySet Manager Methods -
        get_or_none
    """

    class Meta(ArchivableModel.Meta):
        default_related_name = "related_user_details"

    # FK fields
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Fields
    user_id_number = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    user_grade = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    manager_name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    manager_email = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    business_unit_name = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    organization_unit_id = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    manager_id = models.PositiveIntegerField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    config_str = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    birth_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    contact_number = AppPhoneNumberField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    gender = models.CharField(
        choices=GenderChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH, default=GenderChoices.not_selected
    )
    marital_status = models.CharField(
        choices=MaritalStatusChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        default=MaritalStatusChoices.not_selected,
    )
    employment_start_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    employee_id = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    manager_two_email = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    manager_three_email = models.EmailField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    job_description = models.ForeignKey(
        "meta.JobDescription",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    job_title = models.ForeignKey(
        "meta.JobTitle",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    department_code = models.ForeignKey(
        "meta.DepartmentCode",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    department_title = models.ForeignKey(
        "meta.DepartmentTitle",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    employment_status = models.ForeignKey(
        "meta.EmploymentStatus",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    promotion_date = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    certifications = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    identification_type = models.ForeignKey(
        "meta.IdentificationType",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    identification_number = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    # Local address
    current_address = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    current_country = models.ForeignKey(
        "meta.Country",
        on_delete=models.SET_NULL,
        related_name="current_address_country",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    current_state = models.ForeignKey(
        "meta.State",
        on_delete=models.SET_NULL,
        related_name="current_address_state",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    current_city = models.ForeignKey(
        "meta.City",
        on_delete=models.SET_NULL,
        related_name="current_address_city",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    current_pincode = models.PositiveIntegerField(
        validators=[validate_pincode], **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    # Permanent address
    permanent_address = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    permanent_country = models.ForeignKey(
        "meta.Country",
        on_delete=models.SET_NULL,
        related_name="permanent_address_country",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    permanent_state = models.ForeignKey(
        "meta.State",
        on_delete=models.SET_NULL,
        related_name="permanent_address_state",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    permanent_city = models.ForeignKey(
        "meta.City",
        on_delete=models.SET_NULL,
        related_name="permanent_address_city",
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    permanent_pincode = models.PositiveIntegerField(
        validators=[validate_pincode], **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )

    # Bool fields
    is_onsite_user = models.BooleanField(default=False)

    # M2M Fields
    education_detail = models.ManyToManyField("access.UserEducationDetail", blank=True)
    skill_detail = models.ManyToManyField(to="access.UserSkillDetail", blank=True)
    role = models.ManyToManyField(to="learning.CategoryRole", blank=True)
    category = models.ManyToManyField(to="learning.Category", blank=True)

    def __str__(self):
        """Email as string representation."""

        return self.user.email


class UserProfilePicture(ImageOnlyModel):
    """
    Image data for a `User`.

    Model Fields -
        PK          - id
        Fields      - uuid, image
        Datetime    - created_at, modified_at
    """

    pass


class UserConnection(BaseModel):
    """
    Model to Store User connections for IIHT-B2B.

    ********************* Model Fields *********************

        PK          - id,
        FK          - user,
        mtom        - friends, followers
        Datetime    - created_at, modified_at,

    App QuerySet Manager Methods -
        get_or_none
    """

    # FK Fields
    user = models.OneToOneField("access.User", on_delete=models.CASCADE, related_name="related_user_connections")
    friends = models.ManyToManyField("access.User", related_name="related_user_friends", blank=True)
    followers = models.ManyToManyField("access.User", related_name="related_user_followers", blank=True)


class UserFriendRequest(BaseModel):
    """
    Model to Store friend request for IIHT-B2B.

    ********************* Model Fields *********************

        PK          - id,
        FK          - from_user, to_user
        Datetime    - created_at, modified_at,

    App QuerySet Manager Methods -
        get_or_none
    """

    # FK Fields
    from_user = models.ForeignKey("access.User", on_delete=models.CASCADE, related_name="related_request_users")
    to_user = models.ForeignKey("access.User", on_delete=models.CASCADE, related_name="related_respond_users")

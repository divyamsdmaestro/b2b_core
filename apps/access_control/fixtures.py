from djchoices import ChoiceItem, DjangoChoices


class PolicyCategoryChoices(DjangoChoices):
    """Choices for PolicySlugChoices."""

    tenant_management = ChoiceItem("tenant_management", "Tenant Management")
    user_management = ChoiceItem("user_management", "User Management")
    user_role_management = ChoiceItem("user_role_management", "User Role Management")
    user_group_management = ChoiceItem("user_group_management", "User Group Management")
    course_management = ChoiceItem("course_management", "Course Management")
    learning_path_management = ChoiceItem("learning_path_management", "Learning Path Management")
    advanced_learning_path_management = ChoiceItem(
        "advanced_learning_path_management", "Advanced Learning Path Management"
    )
    enrollment_management = ChoiceItem("enrollment_management", "Enrollment Management")


class PolicyChoices(DjangoChoices):
    """Choices for Policy Choices."""

    tenant_management = ChoiceItem("tenant_management_policy", "Tenant Management Policy")
    user_management = ChoiceItem("user_management_policy", "User Management Policy")
    user_role_management = ChoiceItem("user_role_management_policy", "User Role Management Policy")
    user_group_management = ChoiceItem("user_group_management_policy", "User Group Management Policy")
    course_management = ChoiceItem("course_management_policy", "Course Management Policy")
    learning_path_management = ChoiceItem("learning_path_management_policy", "Learning Path Management Policy")
    advanced_learning_path_management = ChoiceItem(
        "advanced_learning_path_management_policy", "Advanced Learning Path Management Policy"
    )
    enrollment_management = ChoiceItem("enrollment_management_policy", "Enrollment Management Policy")


SUPER_TENANT_POLICY_FIXTURE = {
    PolicyCategoryChoices.tenant_management: {
        "name": PolicyCategoryChoices.labels.tenant_management,
        "policies": [{"name": PolicyChoices.labels.tenant_management, "slug": PolicyChoices.tenant_management}],
    }
}

SHARED_POLICY_FIXTURE = {
    PolicyCategoryChoices.user_management: {
        "name": PolicyCategoryChoices.labels.user_management,
        "policies": [{"name": PolicyChoices.labels.user_management, "slug": PolicyChoices.user_management}],
    },
    PolicyCategoryChoices.user_role_management: {
        "name": PolicyCategoryChoices.labels.user_role_management,
        "policies": [{"name": PolicyChoices.labels.user_role_management, "slug": PolicyChoices.user_role_management}],
    },
    PolicyCategoryChoices.user_group_management: {
        "name": PolicyCategoryChoices.labels.user_group_management,
        "policies": [
            {"name": PolicyChoices.labels.user_group_management, "slug": PolicyChoices.user_group_management}
        ],
    },
    PolicyCategoryChoices.course_management: {
        "name": PolicyCategoryChoices.labels.course_management,
        "policies": [{"name": PolicyChoices.labels.course_management, "slug": PolicyChoices.course_management}],
    },
    PolicyCategoryChoices.learning_path_management: {
        "name": PolicyCategoryChoices.labels.learning_path_management,
        "policies": [
            {"name": PolicyChoices.labels.learning_path_management, "slug": PolicyChoices.learning_path_management}
        ],
    },
    PolicyCategoryChoices.advanced_learning_path_management: {
        "name": PolicyCategoryChoices.labels.advanced_learning_path_management,
        "policies": [
            {
                "name": PolicyChoices.labels.advanced_learning_path_management,
                "slug": PolicyChoices.advanced_learning_path_management,
            }
        ],
    },
    PolicyCategoryChoices.enrollment_management: {
        "name": PolicyCategoryChoices.labels.enrollment_management,
        "policies": [
            {"name": PolicyChoices.labels.enrollment_management, "slug": PolicyChoices.enrollment_management}
        ],
    },
}

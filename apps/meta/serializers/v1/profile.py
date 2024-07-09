from apps.common.serializers import AppWriteOnlyModelSerializer
from apps.meta.models import (
    DepartmentCode,
    DepartmentTitle,
    EducationType,
    EmploymentStatus,
    IdentificationType,
    JobDescription,
    JobTitle,
)


class EducationTypeCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Education Type model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = EducationType
        fields = ["name"]


class IdentificationTypeCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Identification Type model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = IdentificationType
        fields = ["name"]


class JobDescriptionCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Job Code model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = JobDescription
        fields = ["name"]


class JobTitleCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Job Title model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = JobTitle
        fields = ["name"]


class DepartmentCodeCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Department Code model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = DepartmentCode
        fields = ["name"]


class DepartmentTitleCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Department Title model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = DepartmentTitle
        fields = ["name"]


class EmploymentStatusCUDModelSerializer(AppWriteOnlyModelSerializer):
    """Employment Status model serializer holds create, update & destroy."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = EmploymentStatus
        fields = ["name"]

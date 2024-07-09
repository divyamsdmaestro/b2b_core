from apps.common.serializers import get_app_read_only_serializer as read_serializer
from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet
from apps.meta.models import (
    DepartmentCode,
    DepartmentTitle,
    EducationType,
    EmploymentStatus,
    IdentificationType,
    JobDescription,
    JobTitle,
)
from apps.meta.serializers.v1 import (
    DepartmentCodeCUDModelSerializer,
    DepartmentTitleCUDModelSerializer,
    EducationTypeCUDModelSerializer,
    EmploymentStatusCUDModelSerializer,
    IdentificationTypeCUDModelSerializer,
    JobDescriptionCUDModelSerializer,
    JobTitleCUDModelSerializer,
)


class EducationTypeCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete education type"""

    serializer_class = EducationTypeCUDModelSerializer
    queryset = EducationType.objects.all()


class EducationTypeListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to retrieve education types"""

    queryset = EducationType.objects.all().order_by("created_at")
    serializer_class = read_serializer(
        meta_model=EducationType,
        meta_fields=["id", "name"],
    )
    search_fields = ["name"]


class IdentificationTypeCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete Identification type"""

    serializer_class = IdentificationTypeCUDModelSerializer
    queryset = IdentificationType.objects.all()


class IdentificationTypeListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to retrieve Identification types"""

    queryset = IdentificationType.objects.all().order_by("created_at")
    serializer_class = read_serializer(
        meta_model=IdentificationType,
        meta_fields=["id", "name"],
    )
    search_fields = ["name"]


class JobDescriptionCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete Job Code"""

    serializer_class = JobDescriptionCUDModelSerializer
    queryset = JobDescription.objects.all()


class JobDescriptionListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list Job Codes"""

    queryset = JobDescription.objects.all().order_by("created_at")
    serializer_class = read_serializer(
        meta_model=JobDescription,
        meta_fields=["id", "name"],
    )
    search_fields = ["name"]


class JobTitleCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete Job Title"""

    serializer_class = JobTitleCUDModelSerializer
    queryset = JobTitle.objects.all()


class JobTitleListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list Job Titles"""

    queryset = JobTitle.objects.all().order_by("created_at")
    serializer_class = read_serializer(
        meta_model=JobTitle,
        meta_fields=["id", "name"],
    )
    search_fields = ["name"]


class DepartmentCodeCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete Department Code"""

    serializer_class = DepartmentCodeCUDModelSerializer
    queryset = DepartmentCode.objects.all()


class DepartmentCodeListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list Department Codes"""

    queryset = DepartmentCode.objects.all().order_by("created_at")
    serializer_class = read_serializer(
        meta_model=DepartmentCode,
        meta_fields=["id", "name"],
    )
    search_fields = ["name"]


class DepartmentTitleCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete Department Title"""

    serializer_class = DepartmentTitleCUDModelSerializer
    queryset = DepartmentTitle.objects.all()


class DepartmentTitleListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list Department Titles"""

    queryset = DepartmentTitle.objects.all().order_by("created_at")
    serializer_class = read_serializer(
        meta_model=DepartmentTitle,
        meta_fields=["id", "name"],
    )
    search_fields = ["name"]


class EmploymentStatusCUDApiViewSet(AppModelCUDAPIViewSet):
    """Api viewset to create, update & delete Department Title"""

    serializer_class = EmploymentStatusCUDModelSerializer
    queryset = EmploymentStatus.objects.all()


class EmploymentStatusListApiViewSet(AppModelListAPIViewSet):
    """Api viewset to list Department Titles"""

    queryset = EmploymentStatus.objects.all().order_by("created_at")
    serializer_class = read_serializer(
        meta_model=EmploymentStatus,
        meta_fields=["id", "name"],
    )
    search_fields = ["name"]

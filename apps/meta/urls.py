from django.urls import path

from apps.common.routers import AppSimpleRouter
from apps.meta.views.api.v1 import (
    CityCUDApiViewSet,
    CityListApiViewSet,
    CountryCUDApiViewSet,
    CountryListApiViewSet,
    DepartmentCodeCUDApiViewSet,
    DepartmentCodeListApiViewSet,
    DepartmentTitleCUDApiViewSet,
    DepartmentTitleListApiViewSet,
    EducationTypeCUDApiViewSet,
    EducationTypeListApiViewSet,
    EmploymentStatusCUDApiViewSet,
    EmploymentStatusListApiViewSet,
    FacultyCUDModelApiViewSet,
    FacultyImageUploadAPIView,
    FacultyListModelApiViewSet,
    FeedbackTemplateCUDApiViewset,
    FeedbackTemplateListApiViewset,
    FeedbackTemplateRetrieveApiViewset,
    HashtagCUDApiViewSet,
    HashtagListApiViewSet,
    IdentificationTypeCUDApiViewSet,
    IdentificationTypeListApiViewSet,
    JobDescriptionCUDApiViewSet,
    JobDescriptionListApiViewSet,
    JobTitleCUDApiViewSet,
    JobTitleListApiViewSet,
    LanguageCUDApiViewSet,
    LanguageListApiViewSet,
    MMLConfigCUDModelApiViewSet,
    MMLConfigListModelApiViewSet,
    StateCUDApiViewSet,
    StateListApiViewSet,
    VendorCUDModelApiViewset,
    VendorListModelApiViewSet,
    YakshaConfigCUDApiViewSet,
    YakshaConfigListApiViewSet,
)

app_name = "meta"
API_URL_PREFIX = "api/v1/meta"

router = AppSimpleRouter()

# Country Api's
router.register(f"{API_URL_PREFIX}/country/cud", CountryCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/country/list", CountryListApiViewSet)

# State Api's
router.register(f"{API_URL_PREFIX}/state/cud", StateCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/state/list", StateListApiViewSet)

# City Api's
router.register(f"{API_URL_PREFIX}/city/cud", CityCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/city/list", CityListApiViewSet)

# Faculty Api's
router.register(f"{API_URL_PREFIX}/faculty/cud", FacultyCUDModelApiViewSet)
router.register(f"{API_URL_PREFIX}/faculty/list", FacultyListModelApiViewSet)

router.register(f"{API_URL_PREFIX}/feedback/cud", FeedbackTemplateCUDApiViewset),
router.register(f"{API_URL_PREFIX}/feedback/list", FeedbackTemplateListApiViewset),
router.register(f"{API_URL_PREFIX}/feedback/detail", FeedbackTemplateRetrieveApiViewset),

# Identification Type Api's
router.register(f"{API_URL_PREFIX}/identification_type/cud", IdentificationTypeCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/identification_type/list", IdentificationTypeListApiViewSet)

# Education Type Api's
router.register(f"{API_URL_PREFIX}/education_type/cud", EducationTypeCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/education_type/list", EducationTypeListApiViewSet)

# Job Description Api's
router.register(f"{API_URL_PREFIX}/job/description/cud", JobDescriptionCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/job/description/list", JobDescriptionListApiViewSet)

# Job Title Api's
router.register(f"{API_URL_PREFIX}/job/title/cud", JobTitleCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/job/title/list", JobTitleListApiViewSet)

# Department Code Api's
router.register(f"{API_URL_PREFIX}/department/code/cud", DepartmentCodeCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/department/code/list", DepartmentCodeListApiViewSet)

# Department Title Api's
router.register(f"{API_URL_PREFIX}/department/title/cud", DepartmentTitleCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/department/title/list", DepartmentTitleListApiViewSet)

# Employment Status Api's
router.register(f"{API_URL_PREFIX}/employment/status/cud", EmploymentStatusCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/employment/status/list", EmploymentStatusListApiViewSet)

# Language Api's
router.register(f"{API_URL_PREFIX}/language/cud", LanguageCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/language/list", LanguageListApiViewSet)

# Hashtag Api's
router.register(f"{API_URL_PREFIX}/hashtag/cud", HashtagCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/hashtag/list", HashtagListApiViewSet)

# Yaksha confi Api's
router.register(f"{API_URL_PREFIX}/yaksha/config/cud", YakshaConfigCUDApiViewSet)
router.register(f"{API_URL_PREFIX}/yaksha/config/list", YakshaConfigListApiViewSet)

# MML config Api's
router.register(f"{API_URL_PREFIX}/mml/config/cud", MMLConfigCUDModelApiViewSet)
router.register(f"{API_URL_PREFIX}/mml/config/list", MMLConfigListModelApiViewSet)

# Vendor API's
router.register(f"{API_URL_PREFIX}/vendor/cud", VendorCUDModelApiViewset)
router.register(f"{API_URL_PREFIX}/vendor/list", VendorListModelApiViewSet)

urlpatterns = [
    path(
        f"{API_URL_PREFIX}/faculty/image/upload/",
        FacultyImageUploadAPIView.as_view(),
        name="faculty-image-upload",
    ),
] + router.urls

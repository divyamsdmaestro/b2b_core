# flake8: noqa
from .location import (
    CityCUDApiViewSet,
    CityListApiViewSet,
    CountryCUDApiViewSet,
    CountryListApiViewSet,
    StateCUDApiViewSet,
    StateListApiViewSet,
)
from .faculty import FacultyCUDModelApiViewSet, FacultyListModelApiViewSet, FacultyImageUploadAPIView
from .profile import (
    EducationTypeCUDApiViewSet,
    EducationTypeListApiViewSet,
    IdentificationTypeCUDApiViewSet,
    IdentificationTypeListApiViewSet,
    JobDescriptionCUDApiViewSet,
    JobDescriptionListApiViewSet,
    JobTitleCUDApiViewSet,
    JobTitleListApiViewSet,
    DepartmentCodeCUDApiViewSet,
    DepartmentCodeListApiViewSet,
    DepartmentTitleCUDApiViewSet,
    DepartmentTitleListApiViewSet,
    EmploymentStatusCUDApiViewSet,
    EmploymentStatusListApiViewSet,
)
from .language import LanguageCUDApiViewSet, LanguageListApiViewSet
from .hashtag import HashtagCUDApiViewSet, HashtagListApiViewSet
from .yaksha_config import YakshaConfigCUDApiViewSet, YakshaConfigListApiViewSet
from .mml_config import MMLConfigCUDModelApiViewSet, MMLConfigListModelApiViewSet
from .feedback import FeedbackTemplateCUDApiViewset, FeedbackTemplateListApiViewset, FeedbackTemplateRetrieveApiViewset
from .vendor import VendorListModelApiViewSet, VendorCUDModelApiViewset

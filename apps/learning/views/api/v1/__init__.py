# flake8: noqa
from apps.learning.views.api.v1.common import BaseLearningSkillRoleListApiViewSet
from apps.learning.views.api.v1.assignment.assignment import (
    AssignmentImageUploadAPIView,
    AssignmentDocumentUploadAPIView,
    AssignmentCUDApiViewSet,
    AssignmentListApiViewSet,
    AssignmentRetrieveApiViewSet,
    AssignmentResourceApiViewSet,
    AssignmentResourceListApiViewSet,
)
from apps.learning.views.api.v1.assignment.assignment_group import (
    AssignmentGroupCUDApiViewSet,
    AssignmentGroupListApiViewSet,
    AssignmentGroupRetrieveApiViewSet,
    AssignmentRelationCUDApiViewSet,
    AssignmentRelationListApiViewSet,
    AssignmentGroupImageUploadAPIView,
)
from apps.learning.views.api.v1.alp.advanced_learning_path import (
    AdvancedLearningPathCUDApiViewSet,
    AdvancedLearningPathImageUploadAPIView,
    AdvancedLearningPathListApiViewSet,
    AdvancedLearningPathRetrieveApiViewSet,
    ALPLearningPathCUDApiViewSet,
    ALPLearningPathListApiViewSet,
    AdvancedLearningPathResourceApiViewSet,
    AdvancedLearningPathResourceListApiViewSet,
)
from apps.learning.views.api.v1.alp.assessment import (
    ALPAssessmentCUDApiViewSet,
    ALPAssessmentListAPiViewSet,
    ALPAssessmentRetrieveApiViewSet,
)
from apps.learning.views.api.v1.alp.assignment import (
    ALPAssignmentCUDApiViewSet,
    ALPAssignmentListApiViewSet,
    ALPAssignmentRetrieveApiViewSet,
)
from apps.learning.views.api.v1.skill_traveller.skill_traveller import (
    SkillTravellerCourseListApiViewSet,
    SkillTravellerCourseCUDApiViewSet,
    SkillTravellerCUDApiViewSet,
    SkillTravellerCloneApiView,
    SkillTravellerImageUploadAPIView,
    SkillTravellerListApiViewSet,
    SkillTravellerRetrieveApiViewSet,
    SkillTravellerResourceApiViewSet,
    SkillTravellerResourceListApiViewSet,
)
from .skill_traveller.assessment import (
    STAssessmentListAPiViewSet,
    STAssessmentRetrieveApiViewSet,
    STAssessmentCUDApiViewSet,
)
from .skill_traveller.assignment import (
    STAssignmentListApiViewSet,
    STAssignmentCUDApiViewSet,
    STAssignmentRetrieveApiViewSet,
)
from .catalogue.catalogue import (
    CatalogueCUDApiViewSet,
    CatalogueListApiViewSet,
    CatalogueRetrieveApiViewSet,
    CatalogueLockStatusUpdateApiViewSet,
    CatalogueRelationListApiView,
    CatalogueRelationCUDApiViewSet,
    UserCatalogueListApiViewSet,
    CatalogueCloneApiView,
)
from .course.assignment import (
    CourseAssignmentListApiViewSet,
    CourseAssignmentCUDApiViewSet,
    CourseAssignmentRetrieveApiViewSet,
)
from .course.assessment import (
    CourseAssessmentCUDApiViewSet,
    CourseAssessmentListAPiViewSet,
    CourseAssessmentRetrieveApiViewSet,
    YakshaAssessmentListApiView,
)
from .course.course import (
    CourseCUDApiViewSet,
    CourseRetrieveApiViewSet,
    CourseImageUploadAPIView,
    CourseListApiViewSet,
    CourseResourceApiViewSet,
    CourseResourceListApiViewSet,
    CourseBulkUploadAPIView,
    CourseBulkUploadSampleFileAPIView,
    CourseCloneApiView,
)
from .course.module import (
    CourseModuleCUDApiViewSet,
    CourseModuleListApiViewSet,
    CourseModuleRetrieveApiViewSet,
    CourseModuleSequenceUpdateAPIView,
)
from .course.sub_module import CourseSubModuleCUDApiViewSet, CourseSubModuleListApiViewSet
from .expert.expert import ExpertCUDApiViewSet, ExpertListApiViewSet, ExpertRetrieveApiViewSet, ExpertApproveApiView
from .learning_path.learning_path import (
    LPCourseAllocationCUDApiViewSet,
    LPCourseListApiViewSet,
    LearningPathCUDApiViewSet,
    LearningPathImageUploadAPIView,
    LearningPathListApiViewSet,
    LearningPathRetrieveApiViewSet,
    LearningPathCloneApiView,
    LearningPathResourceApiViewSet,
    LearningPathResourceListApiViewSet,
)
from .learning_path.assessment import (
    LPAssessmentListAPiViewSet,
    LPAssessmentRetrieveApiViewSet,
    LPAssessmentCUDApiViewSet,
)
from .learning_path.assignment import (
    LPAssignmentListApiViewSet,
    LPAssignmentCUDApiViewSet,
    LPAssignmentRetrieveApiViewSet,
)
from .playground.playground import (
    PlaygroundCUDApiViewSet,
    PlaygroundImageUploadAPIView,
    PlaygroundListApiViewSet,
    PlaygroundRetrieveApiViewSet,
)
from .playground.playground_group import (
    PlaygroundGroupCUDApiViewSet,
    PlaygroundGroupImageUploadAPIView,
    PlaygroundGroupListApiViewSet,
    PlaygroundGroupRetrieveApiViewSet,
)
from .playground.playground_relation import (
    PlaygroundRelationModelRetrieveApiViewSet,
    PlaygroundRelationCUDApiViewSet,
)
from .skill_ontology.skill_ontology import (
    SkillOntologyCreateApiViewSet,
)
from .talent_management.category import CategoryCUDApiViewSet, CategoryImageUploadAPIView, CategoryListApiViewSet
from .talent_management.role import (
    CategoryRoleCUDApiViewSet,
    CategoryRoleImageUploadAPIView,
    CategoryRoleListApiViewSet,
)
from .talent_management.skill import (
    CategorySkillCUDApiViewSet,
    CategorySkillImageUploadAPIView,
    CategorySkillListApiViewSet,
)
from .learning_update.learning_update import (
    LearningUpdateCUDApiViewSet,
    LearningUpdateListApiViewSet,
    LearningUpdateImageUploadAPIView,
    LearningUpdateTypeListAPIView,
)
from .scorm.scorm import ScormUDApiViewSet, ScormListApiViewSet, ScormUploadApiView
from .learning_retire.learning_retire import LearningRetireApiView
from .clone.clone import LearningCloneApiView

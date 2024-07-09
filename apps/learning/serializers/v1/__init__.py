# flake8: noqa
from .common import (
    BASIC_LEARNING_MODEL_FIELDS,
    BaseAssignmentCUDModelSerializer,
    BaseAssignmentRetrieveModelSerializer,
    BaseCommonFieldCUDModelSerializer,
    BaseLearningCUDModelSerializer,
    BaseLearningSkillCUDModelSerializer,
    BaseLearningSkillRoleCUDModelSerializer,
    BaseLearningListModelSerializer,
    BaseCommonFieldRetrieveModelSerializer,
    BaseLearningRetrieveModelSerializer,
    BaseLearningSkillRetrieveModelSerializer,
    BaseLearningSkillRoleRetrieveModelSerializer,
    CommonResourceCreateModelSerializer,
    CommonResourceListModelSerializer,
    talent_managements,
    BaseDependentCourseListSerializer,
)
from .talent_management.common import CommonTalentManagementCUDModelSerializer, CommonTalentManagementListSerializer
from .talent_management.category import (
    CategoryCUDModelSerializer,
    CategoryStatusUpdateSerializer,
    CategoryListSerializer,
)
from .talent_management.role import (
    CategoryRoleCUDModelSerializer,
    CategoryRoleRetrieveSerializer,
    CategoryRoleStatusUpdateSerializer,
    CategoryRoleListSerializer,
)
from .talent_management.skill import (
    CategorySkillCUDModelSerializer,
    CategorySkillRetrieveSerializer,
    CategorySkillStatusUpdateSerializer,
    CategorySkillListSerializer,
)
from .assignment.assignment import (
    AssignmentDocumentRetrieveModelSerializer,
    AssignmentCUDModelSerializer,
    AssignmentListModelSerializer,
    AssignmentRetrieveModelSerializer,
    AssignmentResourceCreateModelSerializer,
    AssignmentResourceListModelSerializer,
)
from .assignment.assignment_group import (
    AssignmentGroupListSerializer,
    AssignmentGroupCUDModelSerializer,
    AssignmentAllocationCUDSerializer,
    AssignmentGroupRetrieveSerializer,
    AssignmentRelationListSerializer,
)
from .course.assignment import CourseAssignmentCUDModelSerializer, CourseAssignmentListModelSerializer
from .course.assessment import CourseAssessmentCUDModelSerializer, CourseAssessmentListModelSerializer
from .course.sub_module import CourseSubModuleCUDSerializer, CourseSubModuleListSerializer
from .course.module import (
    CourseModuleCUDModelSerializer,
    CourseModuleListModelSerializer,
    CourseModuleRetrieveSerializer,
)
from .course.course import (
    CourseCUDModelSerializer,
    CourseRetrieveModelSerializer,
    CourseListModelSerializer,
    CourseResourceCreateModelSerializer,
    CourseResourceListModelSerializer,
)
from .learning_path.assessment import LPAssessmentListModelSerializer, LPAssessmentCUDModelSerializer
from .learning_path.assignment import LPAssignmentListModelSerializer, LPAssignmentCUDModelSerializer
from .learning_path.learning_path import (
    LPCourseAllocationCUDSerializer,
    LPCourseListModelSerializer,
    LearningPathCUDModelSerializer,
    LearningPathListModelSerializer,
    LearningPathRetrieveModelSerializer,
    LearningPathResourceCreateModelSerializer,
    LearningPathResourceListModelSerializer,
)
from apps.learning.serializers.v1.alp.assessment import (
    ALPAssessmentListModelSerializer,
    ALPAssessmentCUDModelSerializer,
)
from apps.learning.serializers.v1.alp.assignment import (
    ALPAssignmentListModelSerializer,
    ALPAssignmentCUDModelSerializer,
)
from apps.learning.serializers.v1.alp.advanced_learning_path import (
    AdvancedLearningPathCUDModelSerializer,
    AdvancedLearningPathListModelSerializer,
    AdvancedLearningPathRetrieveModelSerializer,
    ALPLearningPathCUDModelSerializer,
    ALPLearningPathListModelSerializer,
    AlpResourceCreateModelSerializer,
    AlpResourceListModelSerializer,
)
from apps.learning.serializers.v1.skill_traveller.skill_traveller import (
    STCourseAllocationCUDSerializer,
    SkillTravellerCourseModelListSerializer,
    SkillTravellerCUDModelSerializer,
    SkillTravellerListModelSerializer,
    SkillTravellerRetrieveModelSerializer,
    SkillTravellerResourceCreateModelSerializer,
    SkillTravellerResourceListModelSerializer,
)
from .skill_traveller.assessment import STAssessmentListModelSerializer, STAssessmentCUDModelSerializer
from .skill_traveller.assignment import STAssignmentListModelSerializer, STAssignmentCUDModelSerializer
from apps.learning.serializers.v1.playground.playground import (
    PlaygroundCUDModelSerializer,
    PlaygroundListModelSerializer,
    PlaygroundRetrieveSerializer,
)
from apps.learning.serializers.v1.playground.playground_group import (
    PlaygroundGroupCUDModelSerializer,
    PlaygroundGroupListSerializer,
    PlaygroundGroupRetrieveSerializer,
)
from apps.learning.serializers.v1.playground.playground_relation import (
    PlaygroundRelationModelRetrieveSerializer,
    PlaygroundAllocationCUDSerializer,
)
from .catalogue.catalogue import (
    CatalogueCUDModelSerializer,
    CatalogueListModelSerializer,
    CatalogueRetrieveSerializer,
    CatalogueRelationListModelSerializer,
    CatalogueRelationCUDModelSerializer,
)
from apps.learning.serializers.v1.skill_ontology.skill_ontology import (
    SkillOntologyListModelSerializer,
    SkillOntologyCreateSerializer,
)
from .expert.expert import (
    ExpertCUDModelSerializer,
    ExpertListSerializer,
    ExpertApprovalSerializer,
)
from .learning_update.learning_update import (
    LearningUpdateCUDModelSerializer,
    LearningUpdateListSerializer,
)
from .scorm.scorm import ScormCUDModelSerializer, ScormListSerializer
from .learning_retire.learning_retire import LearningRetireSerializer

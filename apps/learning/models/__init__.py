# flake8: noqa
from apps.learning.models.common import (
    BaseCommonFieldModel,
    BaseLearningModel,
    BaseSkillLearningModel,
    BaseRoleSkillLearningModel,
    BaseResourceModel,
    BaseAssessmentModel,
)
from apps.learning.models.assignment.assignment import (
    AssignmentTopic,
    AssignmentSubTopic,
    AssignmentImageModel,
    AssignmentDocument,
    Assignment,
    AssignmentResource,
)
from apps.learning.models.assignment.assignment_group import (
    AssignmentGroupImageModel,
    AssignmentGroup,
    AssignmentRelation,
)
from apps.learning.models.talent_management.common import PerformanceMetrix
from apps.learning.models.learning_path.base import (
    LearningPathCommonModel,
    BaseLPEvaluationModel,
    SkillRoleBaseModel,
)
from apps.learning.models.learning_path.learning_path import (
    LearningPathCourse,
    LearningPathImageModel,
    LearningPath,
    LearningPathResource,
)
from apps.learning.models.learning_path.assessment import LPAssessment
from apps.learning.models.learning_path.assignment import LPAssignment
from apps.learning.models.alp.base import BaseALPEvaluationModel
from apps.learning.models.alp.assessment import ALPAssessment
from apps.learning.models.alp.assignment import ALPAssignment
from apps.learning.models.alp.advanced_learning_path import (
    AdvancedLearningPathImageModel,
    AdvancedLearningPath,
    ALPLearningPath,
    AdvancedLearningPathResource,
)
from apps.learning.models.course.common import BaseCourseEvaluationModel
from apps.learning.models.course.assessment import CourseAssessment
from apps.learning.models.course.course import Course, CourseImageModel, CourseResource
from apps.learning.models.course.module import CourseModule
from apps.learning.models.course.sub_module import CourseSubModule
from apps.learning.models.course.assignment import CourseAssignment
from apps.learning.models.skill_traveller.skill_traveller import (
    SkillTravellerCourse,
    SkillTravellerImageModel,
    SkillTraveller,
    SkillTravellerResource,
)
from apps.learning.models.skill_traveller.base import BaseSTEvaluationModel
from apps.learning.models.skill_traveller.assessment import STAssessment
from apps.learning.models.skill_traveller.assignment import STAssignment
from apps.learning.models.talent_management.category import Category, CategoryImageModel
from apps.learning.models.talent_management.skill import CategorySkill, CategorySkillImageModel
from apps.learning.models.talent_management.role import CategoryRole, CategoryRoleImageModel, RoleSkillRelation
from apps.learning.models.playground.base import PlaygroundSkeletonModel
from apps.learning.models.playground.playground import (
    PlaygroundImage,
    Playground,
    PlaygroundGroupImage,
    PlaygroundGroup,
    PlaygroundRelationModel,
)
from .catalogue.catalogue import Catalogue, CatalogueRelation
from apps.learning.models.skill_ontology.skill_ontology import SkillOntology
from .expert.expert import Expert
from .learning_update.learning_update import LearningUpdate, LearningUpdateImageModel
from .scorm.scorm import Scorm

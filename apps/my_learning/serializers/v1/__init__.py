# flake8: noqa
from .tracker.common import (
    UserBaseLearningListSerializer,
    UserBaseLearningCertificateListSerializer,
    UserBaseLearningRetrieveModelSerializer,
    BaseLearningFKCUDModelSerializer,
    BaseYakshaAssessmentScheduleListSerializer,
    BaseYakshaAssessmentResultListSerializer,
    tracker_related_fields,
    Basic_enrollment_fields,
    LEARNING_RELATED_FIELDS,
    BASE_LEARNING_TYPES,
    BaseEnrollmentListModelSerializer,
    BaseAssessmentTrackerListSerializer,
    BaseMultipleFileUploadSerializer,
    BaseEnrollmentTrackerCreateSerializer,
)
from apps.my_learning.serializers.v1.tracker.course.notes import (
    UserCourseNotesCUDSerializer,
    UserCourseNotesListModelSerializer,
)
from apps.my_learning.serializers.v1.tracker.course.bookmark import (
    UserCourseBookMarkCUDSerializer,
    UserCourseBookMarkListSerializer,
)
from apps.my_learning.serializers.v1.tracker.course.course import (
    UserCourseRetrieveModelSerializer,
    UserCourseListSerializer,
    UserCourseTrackerCreateModelSerializer,
    UserCourseTrackerListSerializer,
    UserCourseAssignmentListSerializer,
)
from apps.my_learning.serializers.v1.tracker.course.assessment import (
    CATrackerListSerializer,
    CAYakshaScheduleListSerializer,
    CAYakshaResultListSerializer,
    UserCourseAssessmentListSerializer,
    CATrackerCreateSerializer,
)
from apps.my_learning.serializers.v1.tracker.course.module import (
    CourseModuleTrackerListSerializer,
    UserCourseModuleListSerializer,
    CourseModuleTrackerCreateSerializer,
)
from apps.my_learning.serializers.v1.tracker.course.sub_module import (
    CourseSubModuleTrackerListSerializer,
    CourseSubModuleTrackerUpdateSerializer,
    SubModuleFileSubmissionCreateSerializer,
    SubModuleFileSubmissionListSerializer,
    SubModuleFileSubmissionUpdateSerializer,
    UserCourseSubModuleListSerializer,
    CourseSubModuleTrackerCreateSerializer,
    CourseSubModuleTrackerRetrieveSerializer,
)
from apps.my_learning.serializers.v1.tracker.learning_path.assessment import (
    UserLPAssessmentListSerializer,
    LPATrackerListSerializer,
    LPAYakshaScheduleListSerializer,
    LPAYakshaResultListSerializer,
    LPATrackerCreateSerializer,
)
from apps.my_learning.serializers.v1.tracker.learning_path.assignment import UserLPAssignmentListSerializer
from apps.my_learning.serializers.v1.tracker.learning_path.learning_path import (
    UserLearningPathTrackerCreateModelSerializer,
    UserLearningPathListSerializer,
    UserLearningPathRetrieveSerializer,
    UserLearningPathCourseListSerializer,
    UserLearningPathTrackerListSerializer,
)
from .tracker.advanced_learning_path import (
    UserAdvancedLearningPathListSerializer,
    UserAdvancedLearningPathRetrieveModelSerializer,
    UserALPTrackerCreateModelSerializer,
    UserALPLearningPathListSerializer,
    UserALPTrackerListSerializer,
)
from apps.my_learning.serializers.v1.tracker.skill_traveller.assessment import (
    UserSTAssessmentListSerializer,
    STATrackerListSerializer,
    STAYakshaScheduleListSerializer,
    STAYakshaResultListSerializer,
)
from apps.my_learning.serializers.v1.tracker.skill_traveller.assignment import UserSTAssignmentListSerializer
from .tracker.skill_traveller.skill_traveller import (
    UserSkillTravellerListSerializer,
    UserSkillTravellerRetrieveSerializer,
    UserSkillTravellerTrackerCreateSerializer,
    UserSkillTravellerTrackerListSerializer,
    UserSkillTravellerCourseListSerializer,
)
from .tracker.playground import (
    UserPlaygroundListSerializer,
    UserPlaygroundRetrieveSerializer,
    UserPlaygroundTrackerCreateSerializer,
    UserPlaygroundTrackerListSerializer,
)
from .tracker.playground_group import (
    UserPlaygroundGroupListSerializer,
    UserPlaygroundGroupRetrieveSerializer,
    UserPlaygroundGroupTrackerCreateSerializer,
    UserPlaygroundRelationListSerializer,
)
from .tracker.skill_ontology import (
    UserSkillOntologyTrackerCreateSerializer,
    UserSkillOntologyRetrieveSerializer,
)
from .tracker.enrollment import (
    UserEnrollmentCreateModelSerializer,
    EnrollmentListModelSerializer,
    UserEnrollmentListModelSerializer,
)
from .tracker.enrollment import (
    UserEnrollmentCreateModelSerializer,
    UserEnrollmentListModelSerializer,
    UserEnrollmentUpdateModelSerializer,
    UserBulkEnrollSerializer,
    EnrollmentReminderCUDModelSerializer,
    EnrollmentReminderListModelSerializer,
)
from .tracker.assignment import (
    UserAssignmentListModelSerializer,
    UserAssignmentRetrieveModelSerializer,
    SubmissionFileRetrieveSerializer,
    AssignmentSubmissionCreateModelSerializer,
    AssignmentSubmissionListModelSerializer,
    AssignmentSubmissionUpdateModelSerializer,
    UserAssignmentTrackerListSerializer,
    AssignmentYakshaScheduleListSerializer,
    AssignmentYakshaResultListSerializer,
    UserAssignmentTrackerCreateModelSerializer,
    UserAssignmentStartSerializer,
)
from .tracker.assignment_group import (
    UserAssignmentGroupListSerializer,
    UserAssignmentGroupRetrieveSerializer,
    UserAssignmentGroupTrackerCreateSerializer,
    UserAssignmentGroupTrackerListSerializer,
    UserAssignmentRelationListSerializer,
)
from .user_favourite import UserFavouriteSerializer
from .user_rating import UserRatingCUDSerializer
from .feedback import (
    FeedbackResponseCreateSerializer,
    FeedbackResponseTemplateListSerializer,
    FeedbackResponseListSerializer,
)
from .report import ReportCreateSerializer, ReportListSerializer, ReportEmailCreateSerializer
from .one_profile import (
    OneProfileUserInfoSerializer,
    OneProfileCourseInfoSerializer,
    OneProfileCourseAssessmentSerializer,
    OneProfileLPAssessmentSerializer,
)
from .announcement import AnnouncementCUDModelSerializer, AnnouncementListModelSerializer

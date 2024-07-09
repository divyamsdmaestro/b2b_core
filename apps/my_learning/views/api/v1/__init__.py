# flake8: noqa
from .common import BaseMyLearningSkillRoleListApiViewSet
from .yaksha import YakshaAssessmentTrackerListApiView, YakshaAttemptUpdateApiView
from .advanced_learning_path import (
    UserAlpTrackerCreateApiViewSet,
    UserALPListModelApiViewSet,
    UserALPRetrieveApiViewSet,
    UserALPLearningPathListApiViewSet,
    UserCCMSALPListApiView,
    UserCCMSALPRetrieveApiView,
    UserCCMSALPLearningPathListApiView,
)
from .enrollment import (
    UserEnrollmentCreateApiViewSet,
    EnrollmentListApiViewSet,
    UserEnrollmentListApiViewSet,
    EnrollmentUpdateApiViewSet,
    UserBulkEnrollApiView,
    EnrolledUserListApiViewSet,
    EnrollmentBulkUploadAPIView,
    EnrollmentBulkUploadSampleFileAPIView,
    UnenrollmentBulkUploadAPIView,
    UnenrollmentBulkUploadSampleFileAPIView,
    EnrollmentReminderListApiViewSet,
    EnrollmentReminderCUDApiViewSet,
)
from apps.my_learning.views.api.v1.course.course import (
    UserCourseDetailedRetrieveApiViewSet,
    UserCourseListApiViewSet,
    UserCourseMMLVMStartAPIView,
    UserCourseTrackerCreateApiViewSet,
    UserCourseFinalEvaluationListApiView,
    UserCCMSCourseListApiView,
    UserCCMSCourseRetrieveApiView,
)
from apps.my_learning.views.api.v1.course.module import (
    UserCourseModuleListApiViewSet,
    CourseModuleTrackerCreateApiViewSet,
    UserCCMSCourseModuleListApiView,
)
from apps.my_learning.views.api.v1.course.sub_module import (
    SubModuleTrackerUpdateApiViewSet,
    SubModuleTrackerRetrieveApiViewSet,
    SubModuleFileSubmissionCreateApiViewSet,
    SubModuleFileUploadApiView,
    SubModuleFileSubmissionListApiViewSet,
    SubModuleFileSubmissionRetrieveApiViewSet,
    SubModuleFileSubmissionUpdateApiViewSet,
    FileSubmissionReattemptEnableApiView,
    UserCourseSubModuleListApiViewSet,
    SubModuleTrackerCreateApiViewSet,
    UserCCMSCourseSubModuleListApiView,
    FileSubmissionReattemptEnableApiView,
)
from apps.my_learning.views.api.v1.course.assessment import (
    CAStartApiView,
    CAYakshaResultApiView,
    CATrackerCreateApiViewSet,
)
from apps.my_learning.views.api.v1.course.notes import UserCourseNotesCUDApiViewSet, UserCourseNotesListApiViewSet
from apps.my_learning.views.api.v1.course.bookmark import (
    UserCourseBookMarkCUDApiViewSet,
    UserCourseBookMarkListApiViewSet,
)
from apps.my_learning.views.api.v1.learning_path.assessment import (
    LPAssessmentTrackerCreateAPiViewSet,
    LPAssessmentStartApiView,
    LPAYakshaResultApiView,
    LPAssessmentRetrieveApiViewSet,
    CCMSLPAssessmentRetrieveApiView,
)
from apps.my_learning.views.api.v1.learning_path.assignment import UserLPAssignmentRetrieveApiViewSet
from apps.my_learning.views.api.v1.learning_path.learning_path import (
    UserLearningPathTrackerCreateApiViewSet,
    UserLearningPathListApiViewSet,
    UserLearningPathRetrieveApiViewSet,
    UserLPCourseListApiViewSet,
    UserLPFinalEvaluationListApiView,
    UserCCMSLPListApiView,
    UserCCMSLPCourseListApiView,
    UserCCMSLPRetrieveApiView,
)
from apps.my_learning.views.api.v1.skill_traveller.assessment import (
    STAssessmentTrackerCreateApiView,
    STAssessmentStartApiView,
    STAYakshaResultApiView,
    STAssessmentRetrieveApiViewSet,
)
from apps.my_learning.views.api.v1.skill_traveller.assignment import UserSTAssignmentRetrieveApiViewSet
from .skill_traveller.skill_traveller import (
    UserSkillTravellerListApiViewSet,
    UserSkillTravellerRetrieveApiViewSet,
    UserSTTrackerCreateApiViewSet,
    UserSTCourseListApiViewSet,
    UserSTFinalEvaluationListApiView,
)
from .playground import (
    UserPlaygroundTrackerCreateApiViewSet,
    UserPlaygroundListApiViewSet,
    UserPlaygroundRetrieveApiViewSet,
)
from .playground_group import (
    UserPlaygroundGroupListApiViewSet,
    UserPGTrackerCreateApiViewSet,
    UserPlaygroundGroupRetrieveApiViewSet,
    UserPlaygroundRelationListApiViewSet,
)
from .assignment_group import (
    UserAssignmentGroupListApiViewSet,
    UserAssignmentGroupRetrieveApiViewSet,
    UserAssignmentGroupTrackerCreateApiViewSet,
    UserAssignmentRelationListApiViewSet,
)
from .assignment import (
    UserAssignmentListApiViewSet,
    UserAssignmentRetrieveApiViewSet,
    SubmissionFileUploadApiView,
    AssignmentSubmissionCreateApiViewSet,
    AssignmentSubmissionListApiViewSet,
    AssignmentSubmissionRetrieveApiViewSet,
    AssignmentSubmissionUpdateApiViewSet,
    UserAssignmentTrackerListApiViewSet,
    UserAssignmentStartApiView,
    UserAssignmentResultApiView,
    UserAssignmentTrackerCreateApiViewSet,
    AssignmentReattemptApiView,
    UserCCMSAssignmentRetrieveApiView,
)
from .catalogue import UserCatalogueMetaAPIView
from .skill_ontology import (
    UserSkillOntologyTrackerCreateApiViewSet,
    UserSkillOntologyRetrieveApiViewSet,
)
from .user_favourite import UserFavouriteCUDApiViewset
from .user_rating import UserRatingCUDApiViewSet
from .feedback import (
    FeedbackResponseCreateApiViewset,
    UserFeedbackTemplateListApiViewset,
    UserFeedbackResponseListApiViewset,
)
from .user_feed import UserFeedPageApiView
from .report import ReportCreateAPIViewSet, ReportListAPIViewSet, ReportFileAPIView
from .one_profile import OneProfileUserInfoAPIView, OneProfileAssessmentInfoAPIView, OneProfileCourseInfoAPIView
from .announcement import AnnouncementCUDApiViewSet, AnnouncementListApiViewSet, AnnouncementImageUploadAPIView
from .user_notification import UserNotificationAPIView
from .recommendation import LearningRecommendationAPIView

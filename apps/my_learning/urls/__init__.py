from apps.my_learning.urls.v1.course import urlpatterns as course_urls
from apps.my_learning.urls.v1.enrollment import urlpatterns as enrollment_urls
from apps.my_learning.urls.v1.learning_path import urlpatterns as learning_path_urls
from apps.my_learning.urls.v1.advanced_learning_path import urlpatterns as alp_urls
from apps.my_learning.urls.v1.skill_traveller import urlpatterns as skill_traveller_urls
from apps.my_learning.urls.v1.skill_ontology import urlpatterns as skill_ontology_urls
from apps.my_learning.urls.v1.playground import urlpatterns as playground_urls
from apps.my_learning.urls.v1.playground_group import urlpatterns as playground_group_urls
from apps.my_learning.urls.v1.assignment import urlpatterns as assignment_urls
from apps.my_learning.urls.v1.user_favourite import urlpatterns as user_favourite_urls
from apps.my_learning.urls.v1.user_rating import urlpatterns as user_rating_urls
from apps.my_learning.urls.v1.feedback import urlpatterns as feedback_urls
from apps.my_learning.urls.v1.user_feed import urlpatterns as user_feed_urls
from apps.my_learning.urls.v1.report import urlpatterns as report_urls
from apps.my_learning.urls.v1.yaksha import urlpatterns as yaksha_urls
from apps.my_learning.urls.v1.one_profile import urlpatterns as one_profile_urls
from apps.my_learning.urls.v1.announcement import urlpatterns as announcement_urls
from apps.my_learning.urls.v1.user_notification import urlpatterns as user_notification_urls
from apps.my_learning.urls.v1.assignment_group import urlpatterns as assignment_group_urls
from apps.my_learning.urls.v1.recommendation import urlpatterns as recommendation_urls

urlpatterns = (
    course_urls
    + enrollment_urls
    + learning_path_urls
    + alp_urls
    + skill_traveller_urls
    + playground_urls
    + playground_group_urls
    + user_favourite_urls
    + user_rating_urls
    + assignment_urls
    + feedback_urls
    + user_feed_urls
    + report_urls
    + one_profile_urls
    + announcement_urls
    + user_notification_urls
    + yaksha_urls
    + assignment_group_urls
    + skill_ontology_urls
    + recommendation_urls
)

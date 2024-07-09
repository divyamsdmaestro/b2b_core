# flake8: noqa
from .v1.expert.expert import urlpatterns as expert_urls
from .v1.alp.urls import urlpatterns as alp_urls
from .v1.course.urls import urlpatterns as course_urls
from .v1.learning_path.urls import urlpatterns as learning_path_urls
from .v1.skill_traveller.urls import urlpatterns as skill_traveller_urls
from .v1.talent_management.urls import urlpatterns as talent_management_urls
from .v1.playground.urls import urlpatterns as playground_urls
from .v1.catalogue.urls import urlpatterns as catalog_urls
from .v1.skill_ontology.skill_ontology import urlpatterns as skill_ontology_urls
from .v1.assignment.assignment import urlpatterns as assignment_urls
from .v1.learning_update.learning_update import urlpatterns as learning_update_urls
from .v1.scorm.urls import urlpatterns as scorm_urls
from .v1.learning_retire.learning_retire import urlpatterns as learning_retire_urls
from .v1.clone.urls import urlpatterns as learning_clone_urls

urlpatterns = (
    course_urls
    + learning_path_urls
    + expert_urls
    + alp_urls
    + skill_traveller_urls
    + talent_management_urls
    + playground_urls
    + catalog_urls
    + skill_ontology_urls
    + assignment_urls
    + learning_update_urls
    + scorm_urls
    + learning_retire_urls
    + learning_clone_urls
)

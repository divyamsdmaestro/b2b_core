from apps.common.managers import ArchivableObjectManagerQuerySet


class CategoryRoleObjectManagerQueryset(ArchivableObjectManagerQuerySet):
    """
    Custom QuerySet for CourseRole models.

    Usage on the model class -
        objects = CategoryRoleObjectManagerQueryset.as_manager()

    Available methods -
        get_or_none
        alive
        dead
        delete
        hard_delete
        role_course_count_update
    """

    def role_course_count_update(self):
        """Updated the total no of courses assigned to the role."""

        roles = self.filter()
        for role in roles:
            role.no_of_course = role.related_courses.alive().count()
            role.save()
        return super()

    def role_learning_path_count_update(self):
        """Updated the total no of learning paths assigned to the role."""

        roles = self.filter()
        for role in roles:
            role.no_of_lp = role.related_learning_paths.alive().count()
            role.save()
        return super()

    def role_advanced_learning_path_count_update(self):
        """Updated the total no of advanced learning paths assigned to the role."""

        roles = self.filter()
        for role in roles:
            role.no_of_alp = role.related_advanced_learning_paths.alive().count()
            role.save()
        return super()


class CategorySkillObjectManagerQueryset(ArchivableObjectManagerQuerySet):
    """
    Custom QuerySet for CourseSkill models.

    Usage on the model class -
        objects = CategorySkillObjectManagerQueryset.as_manager()

    Available methods -
        get_or_none
        alive
        dead
        delete
        hard_delete
        skill_course_count_update
    """

    def skill_course_count_update(self):
        """Updated the total no of courses assigned to the skill."""

        skills = self.filter()
        for skill in skills:
            skill.no_of_course = skill.related_courses.alive().count()
            skill.save()
        return super()

    def skill_learning_path_count_update(self):
        """Updated the total no of learning paths assigned to the skill."""

        skills = self.filter()
        for skill in skills:
            skill.no_of_lp = skill.related_learning_paths.alive().count()
            skill.save()
        return super()

    def skill_advanced_learning_path_count_update(self):
        """Updated the total no of advanced learning paths assigned to the skill."""

        skills = self.filter()
        for skill in skills:
            skill.no_of_alp = skill.related_advanced_learning_paths.alive().count()
            skill.save()
        return super()

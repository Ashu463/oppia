"""Validation job for ClassroomModel."""

from typing import Iterator, List, Type

import apache_beam as beam

from core.domain import classroom_config_domain
from core.jobs.types import base_jobs
from core.jobs.types import base_validation_errors
from core.jobs.types import job_run_result
from core.platform import models
from core.platform.datastore import datastore_services

(classroom_models,) = models.Registry.import_models([models.NAMES.classroom])
(topic_models,) = models.Registry.import_models([models.NAMES.topic])

class InvalidClassroomNameError(base_validation_errors.BaseValidationError):
    """Error class for ClassroomModels with invalid names."""

    def __init__(self, model: classroom_models.ClassroomModel) -> None:
        message = 'Classroom has invalid name: %s' % model.name
        super().__init__(message, model.id, 'ClassroomModel')


class InvalidClassroomURLFragmentError(base_validation_errors.BaseValidationError):
    """Error class for ClassroomModels with invalid URL fragments."""

    def __init__(self, model: classroom_models.ClassroomModel) -> None:
        message = 'Classroom has invalid URL fragment: %s' % model.url_fragment
        super().__init__(message, model.id, 'ClassroomModel')


class CyclicTopicPrerequisitesError(base_validation_errors.BaseValidationError):
    """Error class for ClassroomModels with cyclic topic prerequisites."""

    def __init__(self, model: classroom_models.ClassroomModel) -> None:
        message = 'Classroom has cyclic topic prerequisites'
        super().__init__(message, model.id, 'ClassroomModel')


class MissingRequiredFieldsForPublishedClassroomError(base_validation_errors.BaseValidationError):
    """Error class for published ClassroomModels missing required fields."""

    def __init__(self, model: classroom_models.ClassroomModel, missing_fields: List[str]) -> None:
        message = 'Published classroom missing required fields: %s' % ', '.join(missing_fields)
        super().__init__(message, model.id, 'ClassroomModel')


class InvalidTopicReferenceError(base_validation_errors.BaseValidationError):
    """Error class for ClassroomModels with invalid topic references."""

    def __init__(self, model: classroom_models.ClassroomModel, invalid_topic_ids: List[str]) -> None:
        message = 'Classroom references non-existent topics: %s' % ', '.join(invalid_topic_ids)
        super().__init__(message, model.id, 'ClassroomModel')


class ClassroomModelValidationJob(base_jobs.BaseValidationJob):
    """Job that validates ClassroomModel objects."""

    def __init__(self) -> None:
        """Initializes the ClassroomModelValidationJob."""
        validation_functions = [
            self._validate_classroom_name,
            self._validate_url_fragment,
            self._validate_topic_prerequisites,
            self._validate_published_classroom_fields,
            self._validate_topic_references
        ]
        super().__init__(validation_functions)

    def _validate_classroom_name(
            self, model: classroom_models.ClassroomModel
    ) -> Iterator[job_run_result.JobRunResult]:
        """Validates that the classroom has a valid name.

        Args:
            model: The ClassroomModel to validate.

        Yields:
            JobRunResult. The result of the validation (if any error is found).
        """
        try:
            classroom_config_domain.Classroom.require_valid_name(model.name)
        except Exception:
            yield InvalidClassroomNameError(model)

    def _validate_url_fragment(
            self, model: classroom_models.ClassroomModel
    ) -> Iterator[job_run_result.JobRunResult]:
        """Validates that the classroom has a valid URL fragment.

        Args:
            model: The ClassroomModel to validate.

        Yields:
            JobRunResult. The result of the validation (if any error is found).
        """
        try:
            classroom_config_domain.Classroom.require_valid_url_fragment(model.url_fragment)
        except Exception:
            yield InvalidClassroomURLFragmentError(model)
            
    def _validate_topic_prerequisites(
            self, model: classroom_models.ClassroomModel
    ) -> Iterator[job_run_result.JobRunResult]:
        """Validates that the classroom has no cyclic topic prerequisites.

        Args:
            model: The ClassroomModel to validate.

        Yields:
            JobRunResult. The result of the validation (if any error is found).
        """
        if model.topic_id_to_prerequisite_topic_ids:
            try:
                classroom_config_domain.Classroom.check_for_cycles_in_topic_id_to_prerequisite_topic_ids(
                    model.topic_id_to_prerequisite_topic_ids)
            except Exception:
                yield CyclicTopicPrerequisitesError(model)

    def _validate_published_classroom_fields(
            self, model: classroom_models.ClassroomModel
    ) -> Iterator[job_run_result.JobRunResult]:
        """Validates that published classrooms have all required fields.

        Args:
            model: The ClassroomModel to validate.

        Yields:
            JobRunResult. The result of the validation (if any error is found).
        """
        if not model.is_published:
            return

        missing_fields = []
        if not model.thumbnail_filename:
            missing_fields.append('thumbnail_filename')
        if not model.banner_filename:
            missing_fields.append('banner_filename')
        if not model.topic_id_to_prerequisite_topic_ids:
            missing_fields.append('topic_id_to_prerequisite_topic_ids')
        if not model.course_details:
            missing_fields.append('course_details')
        if not model.teaser_text:
            missing_fields.append('teaser_text')
        if not model.topic_list_intro:
            missing_fields.append('topic_list_intro')

        if missing_fields:
            yield MissingRequiredFieldsForPublishedClassroomError(model, missing_fields)

    def _validate_topic_references(
            self, model: classroom_models.ClassroomModel
    ) -> Iterator[job_run_result.JobRunResult]:
        """Validates that all referenced topics exist.

        Args:
            model: The ClassroomModel to validate.

        Yields:
            JobRunResult. The result of the validation (if any error is found).
        """
        if not model.topic_id_to_prerequisite_topic_ids:
            return

        # Collect all topic IDs referenced in the classroom
        all_topic_ids = set()
        for topic_id, prereq_topic_ids in model.topic_id_to_prerequisite_topic_ids.items():
            all_topic_ids.add(topic_id)
            all_topic_ids.update(prereq_topic_ids)

        # Check if these topics exist in the database
        topic_models_dict = topic_models.TopicModel.get_multi(list(all_topic_ids))
        
        # Find topic IDs that don't exist
        invalid_topic_ids = []
        for topic_id in all_topic_ids:
            if topic_id not in topic_models_dict or topic_models_dict[topic_id] is None:
                invalid_topic_ids.append(topic_id)

        if invalid_topic_ids:
            yield InvalidTopicReferenceError(model, invalid_topic_ids)
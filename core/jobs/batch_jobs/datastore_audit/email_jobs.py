# coding: utf-8
#
# Copyright 2021 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Validation Jobs for blog models"""

from __future__ import annotations

from core import feconf
from core.jobs import base_jobs
from core.jobs.io import ndb_io
from core.jobs.transforms import job_result_transforms
from core.jobs.types import job_run_result
from core.platform import models

import apache_beam as beam

MYPY = False
if MYPY:  # pragma: no cover
    from mypy_imports import email_models

(email_models,) = models.Registry.import_models([
    models.Names.EMAIL
])


class GetEmailsWithInvalidRecipientEmailJob(base_jobs.JobBase):
    """Validates that recipient email don't
    ends with dot and must have '@' in it.
    """

    def run(self) -> beam.PCollection[job_run_result.JobRunResult]:

        all_emails = (
            self.pipeline
            | 'Get all SentEmailModel' >> (
                ndb_io.GetModels(email_models.SentEmailModel.get_all()))
            | 'Extract recipient email form model' >> beam.Map(
                lambda sentEmail: (
                    sentEmail.recipient_email, sentEmail.sender_email))
        )
        all_emails | 'Debug: Print all emails' >> beam.Map(print)

        recipient_emails_without_special_symbol_and_with_dot = (
            all_emails
            | 'Get all emails without @ symbols or ending with dot.' >> 
                beam.Filter(
                    lambda email_tuple:
                        not isinstance(email_tuple[0], str)
                        or email_tuple[0].endswith('.')
                        or '@' not in email_tuple[0]
                )
        )
        sender_emails_without_special_symbol_and_with_dot = (
            all_emails
            | 'Get all emails without @ symbols or ending with dot.' >> 
                beam.Filter(
                    lambda email_tuple:
                        not isinstance(email_tuple[1], str)
                        or email_tuple[1].endswith('.')
                        or '@' not in email_tuple[1]
                )
        )
        no_of_invalid_recipient_emails = (
            recipient_emails_without_special_symbol_and_with_dot
            | 'Report count of invalid email models' >> (
                job_result_transforms.CountObjectsToJobRunResult(
                    'CountInvalidEmails'
                )
            )
        )
        no_of_invalid_sender_emails = (
            sender_emails_without_special_symbol_and_with_dot
            | 'Report count of invalid email models' >> (
                job_result_transforms.CountObjectsToJobRunResult(
                    'CountInvalidEmails'
                )
            )
        )
        report_invalid_recipient_emails = ( 
            recipient_emails_without_special_symbol_and_with_dot
            | 'Report info on each invalid email' >> beam.Map(
                lambda invalid_email:
                    job_run_result.JobRunResult.stderr(
                        'Invalid recipient email: "%s"'
                        % (invalid_email[0])
                    ))
        )
        report_invalid_sender_emails = ( 
            sender_emails_without_special_symbol_and_with_dot
            | 'Report info on each invalid email' >> beam.Map(
                lambda invalid_email:
                    job_run_result.JobRunResult.stderr(
                        'Invalid sender email: "%s"'
                        % (invalid_email[1])
                    ))
        )

        return (
            (
                no_of_invalid_recipient_emails,
                no_of_invalid_sender_emails,
                report_invalid_recipient_emails,
                report_invalid_sender_emails
            )
            | 'Combine reported results' >> beam.Flatten()
        )
  
class GetEmailsWithInavalidIntentJob(base_jobs.JobBase):
    """Validates that intent must be one of intent list[].
    """

    def run(self) -> beam.PCollection[job_run_result.JobRunResult]:

        valid_intents = [
            feconf.EMAIL_INTENT_SIGNUP,
            feconf.EMAIL_INTENT_MARKETING,
            feconf.EMAIL_INTENT_DAILY_BATCH,
            feconf.EMAIL_INTENT_EDITOR_ROLE_NOTIFICATION,
            feconf.EMAIL_INTENT_FEEDBACK_MESSAGE_NOTIFICATION,
            feconf.EMAIL_INTENT_SUBSCRIPTION_NOTIFICATION,
            feconf.EMAIL_INTENT_SUGGESTION_NOTIFICATION,
            feconf.EMAIL_INTENT_UNPUBLISH_EXPLORATION,
            feconf.EMAIL_INTENT_DELETE_EXPLORATION,
            feconf.EMAIL_INTENT_REPORT_BAD_CONTENT,
            feconf.EMAIL_INTENT_QUERY_STATUS_NOTIFICATION,
            feconf.EMAIL_INTENT_ONBOARD_CD_USER,
            feconf.EMAIL_INTENT_REMOVE_CD_USER,
            feconf.EMAIL_INTENT_ADDRESS_CONTRIBUTOR_DASHBOARD_SUGGESTIONS,
            feconf.EMAIL_INTENT_REVIEW_CREATOR_DASHBOARD_SUGGESTIONS,
            feconf.EMAIL_INTENT_REVIEW_CONTRIBUTOR_DASHBOARD_SUGGESTIONS,
            feconf.EMAIL_INTENT_ADD_CONTRIBUTOR_DASHBOARD_REVIEWERS,
            feconf.EMAIL_INTENT_ACCOUNT_DELETED,
            feconf.BULK_EMAIL_INTENT_TEST,
            feconf.EMAIL_INTENT_NOTIFY_CONTRIBUTOR_DASHBOARD_ACHIEVEMENTS
        ]
        all_intents = (
            self.pipeline
            | 'Get all SentEmailModel' >> (
                ndb_io.GetModels(email_models.SentEmailModel.get_all()))
            | 'Extract sender email form model' >> beam.Map(
                lambda sentEmail: (
                    sentEmail.intent))
        )
        intent_out_of_all_intents = (
            all_intents
            | 'Get all emails without @ symbols or ending with dot.' >> 
                beam.Filter(
                    lambda intent:
                    not isinstance(intent, str)
                    or intent not in valid_intents
                )
        )
        no_of_invalid_intents = (
            intent_out_of_all_intents
            | 'Report count of invalid email models' >> (
                job_result_transforms.CountObjectsToJobRunResult(
                    'CountInvalidEmails'
                )
            )
        )
        report_invalid_intent = ( 
            intent_out_of_all_intents
            | 'Report info on each invalid email' >> beam.Map(
                lambda invalid_intent:
                    job_run_result.JobRunResult.stderr(
                        'Email with "%s" sender_email'
                        % (invalid_intent)
                    ))
        )

        return (
            (
                no_of_invalid_intents,
                report_invalid_intent,
            )
            | 'Combine reported results' >> beam.Flatten()
        )


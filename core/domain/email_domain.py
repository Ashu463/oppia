# coding: utf-8
#
# Copyright 2022 The Oppia Authors. All Rights Reserved.
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
"""Domain objects for Email."""
from __future__ import annotations

import copy
from core import utils
from core.constants import constants
import datetime
from typing import Dict, List, TypedDict
from core import feconf


class SentEmailDict(TypedDict):
    """Dict type for Classroom object."""
    recipient_id: str
    recipient_email: str
    sender_id: str
    sender_email: str
    intent: str
    subject: str
    html_body: str
    sent_datetime: datetime
    
class BulkEmailDict(TypedDict):
    """Dict type for Classroom object."""
    recipient_id: str
    recipient_email: str
    sender_id: str
    sender_email: str
    intent: str
    subject: str
    html_body: str
    sent_datetime: datetime
    
allowed_intents = [
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
allowed_sender_emails = [
    feconf.SYSTEM_EMAIL_ADDRESS, 
    feconf.NOREPLY_EMAIL_ADDRESS
]
allowed_bulkEmails_intents = [
    feconf.BULK_EMAIL_INTENT_MARKETING,
    feconf.BULK_EMAIL_INTENT_IMPROVE_EXPLORATION,
    feconf.BULK_EMAIL_INTENT_CREATE_EXPLORATION,
    feconf.BULK_EMAIL_INTENT_CREATOR_REENGAGEMENT,
    feconf.BULK_EMAIL_INTENT_LEARNER_REENGAGEMENT,
    feconf.EMAIL_INTENT_NOTIFY_CURRICULUM_ADMINS_CHAPTERS
]

class SentEmail:
    """Domain object for an email sent from Oppia.
    
    This class represents a record of an email sent to a user, including
    metadata about the sender, recipient, purpose, and content of the email.
    SentEmail objects are immutable once created.
    """

    def __init__(
            self,
            recipient_id: str,
            recipient_email: str,
            sender_id: str,
            sender_email: str,
            intent: str,
            subject: str,
            html_body: str,
            sent_datetime: datetime
        ):
        """Constructs a SentEmail domain object.

        Args:
            recipient_id: str. The user ID of the email recipient.
            recipient_email: str. The email address of the recipient.
            sender_id: str. The user ID of the email sender.
            sender_email: str. The email address used to send the notification.
            intent: str. The intent/purpose of the email.
            subject: str. The subject line of the email.
            html_body: str. The HTML content of the email body.
            sent_datetime: datetime. The datetime the email was sent, in UTC.
        """
        self.recipient_id = recipient_id
        self.recipient_email = recipient_email
        self.sender_id = sender_id
        self.sender_email = sender_email
        self.intent = intent
        self.subject = subject
        self.html_body = html_body
        self.sent_datetime = sent_datetime

    @classmethod
    def from_dict(cls, email: SentEmail) -> SentEmailDict:
        """Returns a image data domain object from a dict.

        Args:
            email: dict. The dict representation of the bulkEmail
                object.

        Returns:
            BulkEmail. The BulkEmail object instance.
        """
        return cls(
            email['recipient_id'],
            email['recipient_email'],
            email['sender_id'],
            email['sender_email'],
            email['intent'],
            email['subject'],
            email['html_body'],
            email['sent_datetime']
        )

    def to_dict(self) -> SentEmailDict:
        """Returns a dict representing a email domain object.

        Returns:
            dict. A dict, mapping all fields of email instance.
        """
        return {
            'recipient_id': self.recipient_id,
            'recipient_email': self.recipient_email,
            'sender_id': self.sender_id,
            'sender_email': self.sender_email,
            'intent': self.intent,
            'subject': self.subject,
            'html_body': self.html_body,
            'sent_datetime': self.sent_datetime
        }

    def validate(self):
        """Validates the SentEmail domain object.
        
        Performs validation of all fields to ensure data integrity.
        
        Raises:
            ValidationError: One or more attributes of the SentEmail are invalid.
        """
        # Validating receipient_id.
        if not self.recipient_id:
            raise utils.ValidationError(
                'recipient_id cannot be empty as it is required to identify the email recipient'
            )
        if not isinstance(self.recipient_id, str):
            raise utils.ValidationError(
                'Expected recipient_id to be a string, received %s' % 
                type(self.recipient_id)
            )

        # Validating receipient_email.
        if not self.recipient_email:
            raise utils.ValidationError('recipient_email cannot be empty')
        if not isinstance(self.recipient_email, str):
            raise utils.ValidationError(
                'Expected recipient_email to be a string, received %s' % 
                type(self.recipient_email)
            )
        # Email format validation - basic check for @ symbol
        if '@' not in self.recipient_email:
            raise utils.ValidationError(
                'recipient_email %s is not a valid email address' % self.recipient_email)

        # Validating sender_id.
        if not self.sender_id:
            raise utils.ValidationError(
                'sender_id cannot be empty as it is required to track the email sender')
        if not isinstance(self.sender_id, str):
            raise utils.ValidationError(
                'Expected sender_id to be a string, received %s' % type(self.sender_id)
            )
        # Special check for system-generated emails
        if (self.sender_id != feconf.SYSTEM_COMMITTER_ID and 
                not self.sender_id.isalnum()):
            raise utils.ValidationError(
                'sender_id must be alphanumeric or the system ID')
        
        # Validating sender_email.
        if not self.sender_email:
            raise utils.ValidationError('sender_email cannot be empty')
        if not isinstance(self.sender_email, str):
            raise utils.ValidationError(
                'Expected sender_email to be a string, received %s' % 
                type(self.sender_email)
            )
        # Email format validation - basic check for @ symbol
        if '@' not in self.sender_email:
            raise utils.ValidationError(
                'sender_email %s is not a valid email address' % self.sender_email)
        # Verify sender email is a system email
        allowed_sender_emails = [feconf.SYSTEM_EMAIL_ADDRESS, feconf.NOREPLY_EMAIL_ADDRESS]
        if self.sender_email not in allowed_sender_emails:
            raise utils.ValidationError(
                'sender_email must be either the system email or noreply email'
            )

        # Validating intent.
        if not self.intent:
            raise utils.ValidationError('intent cannot be empty')
        if not isinstance(self.intent, str):
            raise utils.ValidationError(
                'Expected intent to be a string, received %s' % type(self.intent))
        # Validate intent is one of the allowed values
        if self.intent not in allowed_intents:
            raise utils.ValidationError(
                'intent %s is not allowed' % self.intent)
        
        # Validating subject.
        if not self.subject:
            raise utils.ValidationError(
                'subject cannot be empty as it is required for all emails')
        if not isinstance(self.subject, str):
            raise utils.ValidationError(
                'Expected subject to be a string, received %s' % type(self.subject))
        # Check subject length - reasonable limit for email subjects
        # We need to create new variable for max no of words limit.
        if len(self.subject) > 500:
            raise utils.ValidationError(
                'subject is too long (%s chars), maximum allowed is 500 chars' % 
                len(self.subject))

        # Validating html_body.
        if not self.html_body:
            raise utils.ValidationError(
                'html_body cannot be empty as it contains the email content')
        if not isinstance(self.html_body, str):
            raise utils.ValidationError(
                'Expected html_body to be a string, received %s' % type(self.html_body))
        # Basic HTML validation - look for closing tags
        if '<html' in self.html_body.lower() and '</html>' not in self.html_body.lower():
            raise utils.ValidationError('html_body contains unclosed HTML tags')

        if not isinstance(self.sent_datetime, datetime.datetime):
            raise utils.ValidationError(
                'Expected sent_datetime to be a datetime object, received %s' % 
                type(self.sent_datetime))

        # Validating datetime.
        # Ensure datetime is in UTC
        if self.sent_datetime.tzinfo is not None:
            raise utils.ValidationError(
                'sent_datetime should be a naive datetime (no timezone) in UTC')
            
        # Ensure datetime is not in the future
        if self.sent_datetime > datetime.datetime.utcnow():
            raise utils.ValidationError(
                'sent_datetime cannot be in the future')
        

class BulkEmail:
    """Domain object for a bulk email sent from Oppia to multiple users.
    
    This class represents a record of an email sent to multiple users, 
    storing the common content and metadata. The actual recipients are tracked 
    separately in UserBulkEmailsModel.
    BulkEmail objects are immutable once created.
    """

    def __init__(
            self,
            sender_id: str,
            sender_email: str,
            intent: str,
            subject: str, 
            html_body: str,
            sent_datetime: datetime
        ):
        """Constructs a BulkEmail domain object.

        Args:
            sender_id: str. The user ID of the email sender.
            sender_email: str. The email address used to send the notification.
            intent: str. The intent/purpose of the bulk email.
            subject: str. The subject line of the email.
            html_body: str. The HTML content of the email body.
            sent_datetime: datetime. The datetime the email was sent, in UTC.
        """
        self.sender_id = sender_id
        self.sender_email = sender_email
        self.intent = intent
        self.subject = subject
        self.html_body = html_body
        self.sent_datetime = sent_datetime

    @classmethod
    def from_dict(cls, email: BulkEmail) -> BulkEmailDict:
        """Returns a image data domain object from a dict.

        Args:
            email: dict. The dict representation of the bulkEmail
                object.

        Returns:
            BulkEmail. The BulkEmail object instance.
        """
        return cls(
            email['sender_id'],
            email['sender_email'],
            email['intent'],
            email['subject'],
            email['html_body'],
            email['sent_datetime'],
        )

    def to_dict(self) -> BulkEmailDict:
        """Returns a dict representing a email domain object.

        Returns:
            dict. A dict, mapping all fields of email instance.
        """
        return {
            'sender_id': self.sender_id,
            'sender_email': self.sender_email,
            'intent': self.intent,
            'subject': self.subject,
            'html_body': self.html_body,
            'sent_datetime': self.sent_datetime
        }

    def validate(self):
        """Validates the BulkEmail domain object.
        
        Performs thorough validation of all fields to ensure data integrity
        for bulk email records. Validation includes type checking, format
        verification, and ensuring alignment with system requirements.
        
        Raises:
            ValidationError: One or more attributes of the BulkEmail are invalid.
        """
        # Validating sender_id.
        if not self.sender_id:
            raise utils.ValidationError(
                'sender_id cannot be empty as it identifies the email sender')
        if not isinstance(self.sender_id, str):
            raise utils.ValidationError(
                'Expected sender_id to be a string, received %s' % 
                type(self.sender_id))
        if (self.sender_id != feconf.SYSTEM_COMMITTER_ID and 
                not utils.is_user_id_valid(self.sender_id)):
            raise utils.ValidationError(
                'sender_id must be a valid user ID or the system ID')
        # Validating sender_email.
        if not self.sender_email:
            raise utils.ValidationError(
                'sender_email cannot be empty as it is required for sending bulk emails')
        if not isinstance(self.sender_email, str):
            raise utils.ValidationError(
                'Expected sender_email to be a string, received %s' % 
                type(self.sender_email))
        if '@' not in self.sender_email:
            raise utils.ValidationError(
                'sender_email %s is not a valid email address' % self.sender_email)
        if self.sender_email not in allowed_sender_emails:
            raise utils.ValidationError(
                'sender_email for bulk emails must be an authorized system email')
        # Validating intent.
        if not self.intent:
            raise utils.ValidationError('intent cannot be empty.')
        if not isinstance(self.intent, str):
            raise utils.ValidationError(
                'Expected intent to be a string, received %s' % type(self.intent))
        if self.intent not in allowed_bulkEmails_intents:
            raise utils.ValidationError(
                'intent %s is not an allowed bulk email intent' % self.intent)
        # Validating subject.
        if not self.subject:
            raise utils.ValidationError(
                'subject cannot be empty as it is required for all emails')
        if not isinstance(self.subject, str):
            raise utils.ValidationError(
                'Expected subject to be a string, received %s' % type(self.subject))
            
        # CONSTANT: Maximum length of subject could be created.
        if len(self.subject) > 200:
            raise utils.ValidationError(
                'subject is too long (%s chars), maximum allowed for bulk emails is 200 chars' % 
                len(self.subject))
        # Validate against common spam trigger words in subject.
        spam_words = ['free', 'guarantee', 'no obligation', 'winner', 'congratulations']
        for word in spam_words:
            if word.lower() in self.subject.lower():
                raise utils.ValidationError(
                    'Subject contains potential spam trigger word: %s' % word)
        # Validating html_body.
        if not self.html_body:
            raise utils.ValidationError(
                'html_body cannot be empty as it contains the email content')
        if not isinstance(self.html_body, str):
            raise utils.ValidationError(
                'Expected html_body to be a string, received %s' % type(self.html_body))
        # Validating throgh html tags.
        if '<html' in self.html_body.lower() and '</html>' not in self.html_body.lower():
            raise utils.ValidationError('html_body contains unclosed HTML tags')
        # CONSTANT: Maximum reasonable size for bulk email could be created.
        if len(self.html_body) > 100000:
            raise utils.ValidationError(
                'html_body is too large for a bulk email (%s bytes)' % len(self.html_body))
        # Validating dattetime. 
        if not isinstance(self.sent_datetime, datetime.datetime):
            raise utils.ValidationError(
                'Expected sent_datetime to be a datetime object, received %s' % 
                type(self.sent_datetime))
        if self.sent_datetime.tzinfo is not None:
            raise utils.ValidationError(
                'sent_datetime should be a naive datetime (no timezone) in UTC')
        if self.sent_datetime > datetime.datetime.utcnow():
            raise utils.ValidationError(
                'sent_datetime cannot be in the future')
        # For bulk emails, we should validate the sent_datetime isn't too old
        # to prevent accidental resending of old campaigns.
        thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        if self.sent_datetime < thirty_days_ago:
            raise utils.ValidationError(
                'sent_datetime cannot be more than 30 days in the past')


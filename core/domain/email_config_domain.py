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

"""Domain objects for email configuration."""

from __future__ import annotations
import datetime
from typing import Dict, List, TypedDict


class EmailDict(TypedDict):
    """Dict type for Email object."""
    recipient_id: str
    recipient_email: str
    sender_id: str
    sender_email: str
    intent: str
    subject: str
    html_body: str
    sent_datetime: datetime
    email_hash: str

class SentEamil:
    """Domain object for bulk email."""

    def __init__(
            self,
            recipient_id: str,
            recipient_email: str,
            sender_id: str,
            sender_email: str,
            intent: str,
            subject: str,
            html_body: str,
            sent_datetime: datetime,
            email_hash: str
    ) -> None:
        """Constructs a SentEmail domain object.

        Args:
            recipient_id: str. The user ID of the email recipient. A non-empty string with having only alphabetical characters. 
            recipient_email: str. The email address of the recipient. A valid email address, i.e. adding validation to check '@' symbols in the email address.
            sender_id: str. The user ID of the email sender. A non-empty string with having only alphabetical characters. 
            sender_email: str. The email address used to send the notification. A valid email address, i.e. adding validation to check '@' symbols in the email address.
            intent: str. The intent/purpose of the email. A non empty string from one of the intents list[]. 
            subject: str. The subject line of the email. A non-empty string, with a maximum length of some characters(as specified/discussed here).
            html_body: str. The HTML content of the email body. A non-empty string, with basic checks for HTML tags.e.g. searching for <html> tag in the body. 
            sent_datetime: datetime. The datetime the email was sent, in UTC. A valid datetime object, with sent_datetime > current_datetime.       
            email_hash: str. The hash of the email. A non-empty string, with a maximum length of some characters(as specified/discussed here).
        """
        self.recipient_id = recipient_id
        self.recipient_email = recipient_email
        self.sender_id = sender_id
        self.sender_email = sender_email
        self.intent = intent
        self.subject = subject
        self.html_body = html_body
        self.sent_datetime = sent_datetime
        self.email_hash = email_hash

    def to_dict(self) -> EmailDict:
        """Returns a dict representation of the SentEmail domain object.

        Returns:
            EmailDict. A dict representation of the SentEmail domain object.
        """
        return {
            'recipient_id': self.recipient_id,
            'recipient_email': self.recipient_email,
            'sender_id': self.sender_id,
            'sender_email': self.sender_email,
            'intent': self.intent,
            'subject': self.subject,
            'html_body': self.html_body,
            'sent_datetime': self.sent_datetime,
            'email_hash': self.email_hash
        }
    
    @classmethod
    def from_dict(cls, email_dict: EmailDict) -> SentEamil:
        """Returns a SentEmail domain object from a dict.

        Args:
            email_dict: EmailDict. A dict representation of the SentEmail domain object.

        Returns:
            SentEmail. A SentEmail domain object.
        """
        return cls(
            email_dict['recipient_id'],
            email_dict['recipient_email'],
            email_dict['sender_id'],
            email_dict['sender_email'],
            email_dict['intent'],
            email_dict['subject'],
            email_dict['html_body'],
            email_dict['sent_datetime'],
            email_dict['email_hash']
        )
    
    @classmethod
    def require_valid_recipient_id(cls, recipient_id: str) -> None:
        """Validates the recipient_id.

        Args:
            recipient_id: str. The user ID of the email recipient.

        Raises:
            Exception. The recipient_id is invalid.
        """
        if not recipient_id:
            raise Exception('Invalid recipient_id: %s' % recipient_id)
        if not isinstance(recipient_id, str) :
            raise Exception('Invalid recipient_id: %s' % recipient_id)
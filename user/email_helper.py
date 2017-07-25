import os
import logging

import sendgrid
from sendgrid.helpers.mail import *
from api.settings import SENDGRID_API_KEY
#
# logger = logging.getLogger('clienthub')

class Email_Helper(object):
    @classmethod
    def send(cls, to=None, subject=None, html=None, text=None, message_from=None):
        sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        from_email = Email(message_from)
        to_email = Email(to)
        content = Content("text/html", html)
        mail = Mail(from_email, subject, to_email, content)

        sg.client.mail.send.post(request_body=mail.get())
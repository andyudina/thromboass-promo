from urllib2 import HTTPError

import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content

from thromboass_webapp.settings import SENDGRID_API_KEY

class SendgridError(ValueError):
    pass
    
_DEFAULT_CONTENT_TYPE = 'text/plain'
_ACCEPTED_STATUS_CODE = 202
      
def send_email(**kwargs):
    print kwargs
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    mail = Mail(
        Email(kwargs.get('from_email')), 
        kwargs.get('subject'),
        Email(kwargs.get('to_email')),
        Content(kwargs.get('content_type', _DEFAULT_CONTENT_TYPE), kwargs.get('content'))
    )
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except HTTPError as e:
        raise SendgridError(str(e))
        return
        
    if not response.status_code == _ACCEPTED_STATUS_CODE:
        raise SendgridError(response.content)

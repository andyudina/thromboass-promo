import sendgrid
from thromboass_webapp.settings import SENDGRID_API_KEY
from sendgrid.helpers.mail import Email, Mail, Content

class SendgridError(ValueError):
    pass
    
_DEFAULT_CONTENT_TYPE = 'text/plain'
_ACCEPTED_STATUS_CODE = 202
      
def send_email(**kwargs):
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    mail = Mail(
        Email(kwargs.get('from_email')), 
        kwargs.get('subject'),
        Email(kwargs.get('to_email')),
        Content(kwargs.get('content_type', _DEFAULT_CONTENT_TYPE), kwargs.get('content'))
    )
    response = self.sg.client.mail.send.post(request_body=mail.get())
    if not response.status_code == ACCEPTED_STATUS_CODE:
        raise SendgridError(response.content)

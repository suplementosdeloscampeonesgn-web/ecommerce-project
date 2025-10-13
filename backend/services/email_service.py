from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from core.config import settings

def send_order_confirmation_email(to_email: str, order_details: str):
    message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=to_email,
        subject='Confirmación de su pedido',
        html_content=order_details,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        print(f'Error enviando email: {e}')
        return False

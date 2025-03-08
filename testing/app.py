import smtplib
import ssl
from email.message import EmailMessage
import mimetypes
import os

# Define email sender and receiver
email_sender = os.environ.get('EMAIL_SENDER')
email_password = os.environ.get('EMAIL_PASSWORD')

# Add SSL (of security)
context = ssl.create_default_context()

def send_email(email_receiver, subject, body, pdf_path=None, is_html=False): 
    # Create the email message object
    em = EmailMessage()
    
    # Set email headers
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    
    # Set the content of the email (HTML or plaintext)
    if is_html:
        em.add_alternative(body, subtype='html')
    else:
        em.set_content(body)
    
    # Attach PDF if provided
    if pdf_path:
        # Guess the MIME type and subtype
        mime_type, _ = mimetypes.guess_type(pdf_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        mime_type, mime_subtype = mime_type.split('/')
        
        # Read the PDF and attach it
        with open(pdf_path, 'rb') as pdf_file:
            em.add_attachment(
                pdf_file.read(),
                maintype=mime_type,
                subtype=mime_subtype,
                filename=os.path.basename(pdf_path)
            )
    
    # Attempt to connect to Gmail SMTP server using SSL
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            # Login to the Gmail account using App Password
            smtp.login(email_sender, email_password)
            
            # Send the email
            smtp.sendmail(email_sender, email_receiver, em.as_string())
            print(f"✅ Email successfully sent to {email_receiver}")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication Error: Check your email/password or App Password.")
    except smtplib.SMTPException as e:
        print(f"❌ Failed to send email: {e}")


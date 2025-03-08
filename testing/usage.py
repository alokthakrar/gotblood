from app import send_email

# Set the subject of the email
subject = 'Test email'

# Read the HTML content from the file
with open("testing/index.html", 'r') as file:
    body = file.read()

email_receiver = 'alokthakrar1@gmail.com'



send_email(email_receiver, subject, body, is_html=True)
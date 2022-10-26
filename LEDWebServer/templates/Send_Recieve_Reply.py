# Import libraries
import ssl
import time
import email
import random
import smtplib
import imaplib
from email.header import decode_header
from email.message import EmailMessage

# Variables
n_email_to_send = 1
n_email_to_receive = 1
display_temperature_message =  True
imap_url = 'imap.gmail.com'
email_sender = 'turcanmadalina10@gmail.com'
email_password = 'mrnnlubhiibuhasp'
email_receiver = 'turcanmadalina10@gmail.com'

###########################################################################
### Function to send an email with Simple Mail Transfer Protocol (SMTP) ###
###########################################################################
# Requirement 1: Enable two-step verification of google Gmail
# https://myaccount.google.com/signinoptions/two-step-verification

# Requirement 2: Define an authorization and a specific password for the application 
# https://myaccount.google.com/u/0/apppasswords

def send_email(email_sender, email_receiver, email_password, subject, body):
    # Initialization
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    # Add SSL (layer of security)
    context = ssl.create_default_context()
    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    time.sleep(1)
    # Display sending confirmation message
    print("Message sent")

##############################################################################
### Function to receive email with Internet Message Access Protocol (IMAP) ###
##############################################################################
def receive_email(email_receiver, email_password, imap_url, n_email_to_receive):
    # Connection with GMAIL using SSL
    imap = imaplib.IMAP4_SSL(imap_url)
    imap.login(email_receiver, email_password)
    status, messages = imap.select("INBOX")
    # Total number of emails
    messages = int(messages[0])
    # Iterate to display email
    n = 0
    for i in range(messages, messages - n_email_to_receive, -1):
        n = n + 1
        # Fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # Parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # Decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # If it is a bytes, decode to str
                    try: subject = subject.decode(encoding)
                    except: pass
                # Decode email sender
                sender, encoding = decode_header(msg.get("From"))[0]
                if isinstance(sender, bytes):
                    try: sender = sender.decode(encoding)
                    except: pass
                # If the email message is multipart
                if msg.is_multipart():
                    # Iterate over email parts\saved\
                    for part in msg.walk():
                        # Extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # Get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # Return informations
                            return subject, sender, body                               
                else:
                    # Extract content type of email
                    content_type = msg.get_content_type()
                    # Get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # Return informations
                        return subject, sender, body

                print("="*100)
    # Close the connection and logout
    imap.close()
    imap.logout()

############
### Main ###
############
subject = "Phase 2 "
temperature =  random.randint(15, 25)
body = "The temperature is " + str(temperature) + "C. Would you like to turn on the fan?"
send_email(email_sender, email_receiver, email_password, subject, body)

# Iterate until having an user answer
while(True): 
    time.sleep(5)
    subject, sender, body = receive_email(email_receiver, email_password, imap_url, n_email_to_receive)
    if body.count("The temperature is") and display_temperature_message == True:
        print("\nSender:", sender)
        print("Subject:", subject)
        print("Message:", body)
        display_temperature_message = False
    elif body.upper().count("YES"): 
        print("Fan is activated")
        send_email(email_sender, email_receiver, email_password, subject, "Fan is activated")
        quit()
    elif body.upper().count("NO"):
        print("Fan is not activated") 
        send_email(email_sender, email_receiver, email_password, subject, "Fan is not activated")
        quit() 
    else: pass

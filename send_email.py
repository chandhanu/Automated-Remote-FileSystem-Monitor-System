import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv
from email.mime.application import MIMEApplication

# Load environment variables
load_dotenv(override=True)
EMAIL_SERVER = os.getenv('EMAIL_SERVER')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT')

#----------------------- Remove all of this --------------------------#
# EMAIL_SERVER="smtp.office365.com"
# EMAIL_PORT=587
# EMAIL_SENDER="chandhanumk@tradingblock.com"
# EMAIL_RECEIVER="chanstorm69@gmail.com" 
# EMAIL_USERNAME="chandhanumk@tradingblock.com"
# EMAIL_PASSWORD="-----------" 
#---------------------------------------------------------------------#
import pandas as pd

def save_errors_to_spreadsheet(account_errors, output_file):
    rows = []
    for account, errors in account_errors.items():
        row = {
            "Account Number": account,
            "Error Codes": ", ".join(errors["Error Codes"]),
            "Error Descriptions": ", ".join(errors["Error Descriptions"]),
            "External IDs": "<br>".join(errors["External IDs"])
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Generate HTML table
    html_table = df.to_html(index=False, escape=False)

    # Style the table with inline CSS
    html_table = f"""
    <html>
    <head>
    <style>
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .external-ids {{
            max-height: 20px;
            overflow: hidden;
            transition: max-height 0.5s ease-in-out;
        }}
        input[type="checkbox"]:checked + div {{
            max-height: 300px;
            overflow: auto;
        }}
        label {{
            display: block;
            margin-top: 5px;
        }}
    </style>
    </head>
    <body>
    <h2>{EMAIL_SUBJECT}</h2>
    {html_table}
    </body>
    </html>
    """

    
    return html_table

def send_email(subject, body, attachments=None):
    # Create a MIME object
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject

    # Attach the HTML body with the msg instance
    msg.attach(MIMEText(body, 'html'))

    # Attach files if there are any
    if attachments:
        for attachment in attachments:
            try:
                with open(attachment, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(attachment))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                    msg.attach(part)
            except Exception as e:
                print(f"Error attaching file {attachment}: {e}")

    # Create SMTP session
    try:
        with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
            #server.starttls()  # Secure the connection
            #server.login(EMAIL_USERNAME, EMAIL_PASSWORD)  # Login with your Outlook account
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Example usage
account_errors = {
    "ACC1": {
        "Error Codes": [" "],
        "Error Descriptions": ["Access denied to account."],
        "External IDs": [
            "2A0000030C8000C32_1536", "2A0000030CC000C34_1537", "2A000003A88000EA3_1799", 
            "2A0000030C8000C32_1536", "2A0000030CC000C34_1537", "2A000003A88000EA3_1799", 
            "2A0000030C8000C32_1536", "2A0000030CC000C34_1537", "2A000003A88000EA3_1799", 
            "2A0000030C8000C32_1536", "2A0000030CC000C34_1537", "2A000003A88000EA3_1799", 
            # (add more IDs as needed)
        ]
    },
    "ACC2": {
        "Error Codes": ["BRG101"],
        "Error Descriptions": ["Access denied to account."],
        "External IDs": [
            "2A0000030C8000C32_1536", "2A0000030CC000C34_1537", "2A000003A88000EA3_1799", 
            "2A0000030C8000C32_1536", "2A0000030CC000C34_1537", "2A000003A88000EA3_1799", 
            "2A0000030C8000C32_1536", "2A0000030CC000C34_1537", "2A000003A88000EA3_1799", 
            "2A0000030C8000C32_1536", "2A0000030CC000C34_1537", "2A000003A88000EA3_1799", 
            # (add more IDs as needed)
        ]
    }
}

email_body = save_errors_to_spreadsheet(account_errors, "error_report")
send_email(subject = EMAIL_SUBJECT, body = email_body, attachments=["attachment1"])

import os
import time
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv
from collections import defaultdict
import pandas as pd
import json
import re
import paramiko
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


# Load environment variables
load_dotenv(override=True)

SFTP_HOST = os.getenv('SFTP_HOST')
SFTP_PORT = int(os.getenv('SFTP_PORT'))
SFTP_USERNAME = os.getenv('SFTP_USERNAME')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD')
SFTP_DIRECTORY = os.getenv('SFTP_DIRECTORY')
EMAIL_SERVER = os.getenv('EMAIL_SERVER')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
TIME_TO_CHECK = int(os.getenv('TIME_TO_CHECK'))
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT')

#DEBUG
DEBUG = True 
DAYS_BEHIND_TO_CHECK = 7

def connect_sftp():
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

def check_for_new_files(sftp, last_checked):
    today_str = datetime.now().strftime('%Y%m%d')

    ############## DEBUG ########################
    if DEBUG: 
        today = datetime.now()
        yesterday = today - timedelta(days=DAYS_BEHIND_TO_CHECK)
        today_str = yesterday.strftime('%Y%m%d')
    ############################################

    # Only parses two files 1. Parsing response and 2. Submission response for the current date 
    pattern = re.compile(f'^AOSD_{today_str}_\d+\.csv\.(parsing_response|submission_response)$')

    sftp.chdir('/')
    sftp.chdir('/upload/response')


    files = sftp.listdir()
    new_files = [file for file in files if pattern.match(file) and sftp.stat(file).st_mtime > last_checked]
    
    return new_files

def parse_file_for_error(sftp, filename):
    account_errors = defaultdict(lambda: {"External IDs": [], "Error Codes": [], "Error Descriptions": []})

    with sftp.open(filename) as f:
        file_content = f.read().decode('utf-8')
    
    try:
        data = json.loads(file_content)
        
        if 'failedTrades' in data:
            for trade in data['failedTrades']:
                error_message_json = json.loads(trade['errorMessage'])
                
                for error in error_message_json.get('errorList', []):
                    account_number = error.get('errorDetails', {}).get('value')
                    error_code = error.get('errorCode')
                    error_description = error.get('errorDescription')
                    
                    if account_number:
                        account_errors[account_number]["External IDs"].append(trade['externalID'])
                        
                        if error_code not in account_errors[account_number]["Error Codes"]:
                            account_errors[account_number]["Error Codes"].append(error_code)
                        
                        if error_description not in account_errors[account_number]["Error Descriptions"]:
                            account_errors[account_number]["Error Descriptions"].append(error_description)
    
    except json.JSONDecodeError:
        return True, f"Error: Failed to parse JSON in file {filename}"
    
    if account_errors:
        return True, account_errors
    else:
        return False, None

def write_email_body(account_errors):
    rows = []
    for account, errors in account_errors.items():
        row = {
            "Account Number": account,
            "Error Codes": ", ".join(errors["Error Codes"]),
            "Error Descriptions": ", ".join(errors["Error Descriptions"]),
            "External IDs": ", ".join(errors["External IDs"]),
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
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

def save_errors_to_spreadsheet(account_errors, output_file):
    rows = []
    for account, errors in account_errors.items():
        row = {
            "Account Number": account,
            "Error Codes": ", ".join(errors["Error Codes"]),
            "Error Descriptions": ", ".join(errors["Error Descriptions"]),
            "External IDs": ", ".join(errors["External IDs"]),
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    folder_name = create_folder_with_current_date()
    full_output_path = os.path.join(folder_name, output_file)
    df.to_excel(full_output_path+".xlsx", index=False)
    df.to_csv(full_output_path+".csv", index=False)
    df.to_html(full_output_path+".html", index=False)
    with open(full_output_path+".json", 'w', encoding='utf-8') as f:
        df.to_json(f, force_ascii=False, indent=4)
    print(f"Errors saved to {full_output_path}(xlsx|csv|html|json)")
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

def create_folder_with_current_date():
    year = datetime.now().strftime('%Y')
    month_day = datetime.now().strftime('%m-%d')
    folder_path = os.path.join(year, month_day)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


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

def monitor_folder():
    last_checked = time.time() 

    ############### DEBUG  ########################
    if DEBUG:
        seconds_in_24_hours = 24*60*60*DAYS_BEHIND_TO_CHECK
        last_checked = time.time() - seconds_in_24_hours
    ##################################################
    
    count = 0
    while count < 10: # while True:
        current_time = datetime.now()
        if True:#current_time.weekday() < 5: # and current_time.hour >= 15 and current_time.minute >= 45:
            sftp, transport = connect_sftp()
            try:
                new_files = check_for_new_files(sftp, last_checked)
                error_files = []
                passed_files = []
                if new_files:
                    for new_file in new_files:
                        isError, error_records  = parse_file_for_error(sftp, new_file)
                        if isError:
                            output_file = f"errors_{new_file.replace('.csv.', '_')}"
                            #email_body = save_errors_to_spreadsheet(error_records, output_file)
                            email_body = write_email_body(error_records)
                            send_email(subject = EMAIL_SUBJECT, body = email_body, attachments=None)
                            error_files.append([new_file, error_records])
                        else:
                            passed_files.append(new_file)
                last_checked = time.time()
            finally:
                sftp.close()
                transport.close()    
        time.sleep(1)
        print(count)
        count += 1

if __name__ == "__main__":
    monitor_folder()
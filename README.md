### README

# Automated LOG/Dump File/Folder Monitor (SFTP) and Email Notification Script(SMTP)

## Overview
This script monitors a specified directory for any new or modified files in the remote server using SFTP(Paramiko). If it detects an error in the log files, it sends an email notification immediately with the error details and attaches the relevant files. The following is the log file that is dumped by APEX trading engine based on the logged transaction failures and messages. 

## Features
- Monitors the `/upload/response` directory for new or modified files.
- Parses files to detect errors.
- Sends email notifications with error details and attaches the relevant files.
- Does not create or save any files locally.

## Prerequisites
- Python 3.x
- Required Python libraries: `paramiko`, `pandas`, `smtplib`, `email`, `python-dotenv`

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/chandhanu/Automated-Remote-Server-FileSystem-monitor-email-notification.git
    cd Automated-Remote-Server-FileSystem-monitor
    ```

2. Install the required Python libraries:
    ```bash
    pip install paramiko pandas python-dotenv
    ```

## Configuration
1. Set up your environment variables:
    Create a `.env` file in the root directory of your project and add your email and SFTP server configurations (NOTE: `load_dotenv`is in override mode):
    
    ```
    EMAIL_SERVER=smtp.office365.com
    EMAIL_PORT=587
    EMAIL_SENDER=your_email@example.com
    EMAIL_RECEIVER=receiver_email@example.com
    EMAIL_SUBJECT=Error Notification
    SFTP_HOST=your_sftp_host
    SFTP_PORT=22
    SFTP_USERNAME=your_sftp_username
    SFTP_PASSWORD=your_sftp_password
    ```

2. You can configure debugging options in the script itself:
    ```python
    DEBUG = True
    DAYS_BEHIND_TO_CHECK = 7
    ```

## Usage
1. Run the script:
    ```bash
    python monitor_file.py
    ```

2. The script will continuously monitor the `/upload/response` directory for any new or modified files. If it detects an error, it will send an email notification with the error details and attach the relevant files. You can overload the current script to check the past days instead of from current time by setting `DEBUG` flag and modifying `DAYS_BEHIND_TO_CHECK` to test and check. 

## Code Structure
- `monitor_file.py`: Main script that monitors the directory and sends email notifications.
- `check_for_new_files`: Function to check for new or modified files in the `/upload/response` directory and read their contents.
- `send_email`: Function to send email notifications with error details and attach relevant files directly from the directory.

## Example
Here is an example of how the script works:
1. The script detects a new file in the `/upload/response` directory.
2. It parses the file and finds an error.
3. The script sends an email notification with the error details and attaches the file without saving it locally.

3. Add the script as a CRON job to monitor indefinetly and incase of any failures, the cron will spin it up again. 

## Troubleshooting
- Ensure that the SMTP server and SFTP server configurations are correct in the `.env` file.
- Make sure that the required Python libraries are installed.
- Check any error messages printed to the console for clues on what might be going wrong.
- Use DEBUG Flag, set it to create and monitor logs 

## Additional usage 
- use `create_spreadsheet` function to generate exporting formats, that will be stored in @project/{YYYY}/{MM-DD}/files

## Contributing
Feel free to submit issues or pull requests if you find any bugs or have suggestions for improvements.


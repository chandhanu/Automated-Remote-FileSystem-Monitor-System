from datetime import datetime
import re


files = ['AOSD_20240731_1.csv.parsing_response', 'AOSD_20240731_1.csv.submission_response', 'AOSD_20240716_1.csv.parsing_response', 'AOSD_20240716_1.csv.submission_response', 'AOSD_20240717_1.csv.parsing_response', 'AOSD_20240717_1.csv.submission_response', 'AOSD_20240718_1.csv.parsing_response', 'AOSD_20240718_1.csv.submission_response', 'AOSD_20240719_1.csv.parsing_response', 'AOSD_20240719_1.csv.submission_response', 'AOSD_20240722_1.csv.parsing_response', 'AOSD_20240722_1.csv.submission_response', 'AOSD_20240723_1.csv.parsing_response', 'AOSD_20240723_1.csv.submission_response', 'AOSD_20240724_1.csv.parsing_response', 'AOSD_20240724_1.csv.submission_response', 'AOSD_20240725_1.csv.parsing_response', 'AOSD_20240725_1.csv.submission_response', 'AOSD_20240726_1.csv.parsing_response', 'AOSD_20240726_1.csv.submission_response', 'AOSD_20240729_1.csv.parsing_response', 'AOSD_20240729_1.csv.submission_response', 'AOSD_20240730_1.csv.parsing_response', 'AOSD_20240730_1.csv.submission_response']

today_str = datetime.now().strftime('%Y%m%d')
pattern = re.compile(f'^AOSD_{today_str}_\d+\.csv\.(parsing_response|submission_response)$')

for file in files :
        if pattern.match(file):
            print("Matched:", file)
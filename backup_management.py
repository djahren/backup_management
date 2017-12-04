"""
Name: Backup Management
Author: Ahren Bader-Jarvis
Version: 1.0.1
Revision Date: 2017-12-02
Description: This script is designed to manage daily backups using a set schedule.
             It will keep daily backups from the last 2 weeks, after that, 1 for
             every week for 2 months, and finally 1 backup every month indefinitely.
Assumptions: The backup directory (defined in backup_dir) receives 1 backup daily.
             The backup files have the filename format of: backupname-YYYY-MM-DD.tgz
"""

import os
import re
import calendar
import datetime

backup_dir = "E:\Backup\Minecraft Server\\"
log_file_name = "backup_management.log"
date_format = "%Y-%m-%d"
do_deletion = False

files_to_delete = []
files_to_save = []
today = datetime.date.today()
two_weeks_ago = today - datetime.timedelta(14)
if today.month > 2:
    two_months_ago = datetime.date(today.year, today.month - 2, 1)
else:
    two_months_ago = datetime.date(today.year - 1, 12 + (today.month - 2), 1)


def date_from_filename(fn):
    match = re.search(r"(\d{4}-\d{2}-\d{2})", fn)
    if match:
        return datetime.datetime.strptime(match.group(1), date_format).date()
    else:
        return None


def get_last_day(dt):
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    return datetime.date(dt.year, dt.month, last_day)


for filename in os.listdir(backup_dir):
    # Get a list of all .tgz files in directory
    if filename.endswith(".tgz") and not (date_from_filename(filename) is None):
        d = date_from_filename(filename)
        if today >= d > two_weeks_ago:
            # If the file is within the last two weeks ignore it
            files_to_save.append(filename)
        else:
            # Else add it to the files_to_delete list
            files_to_delete.append(filename)

files_to_delete.sort(reverse=True)  # sort

# ---WEEK---
# Loop through dates from 2 weeks to 2 months ago decrementing by week
newer_date = two_weeks_ago
file_index = 0
while newer_date > today - datetime.timedelta(60):  # while newer_date is greater than 60 days ago
    # Generate the week boundaries
    older_date = newer_date - datetime.timedelta(7)  # 1 week before newer date

    # Get list of files that are within those boundaries
    range_files = []
    while len(files_to_delete) != file_index and date_from_filename(files_to_delete[file_index]) > older_date:
        range_files.append(file_index)
        file_index += 1

    # Remove the most recent one from the deletion scope
    if len(range_files) > 0:
        files_to_save.append(files_to_delete[range_files[0]])
        files_to_delete.pop(range_files[0])
        file_index -= 1

    newer_date = older_date

# ---MONTH---
# Loop through dates from 2 months ago to the earliest backup decrementing by month
newer_date = get_last_day(two_months_ago)  # end of the month
while len(files_to_delete) > 0 and newer_date >= date_from_filename(sorted(files_to_delete)[0]):
    # Generate the month boundaries
    older_date = datetime.date(newer_date.year, newer_date.month, 1)

    # Get list of files that are within those boundaries
    range_files = []
    while len(files_to_delete) != file_index and \
            date_from_filename(files_to_delete[file_index]) >= older_date:
        cur_file = date_from_filename(files_to_delete[file_index])
        range_files.append(file_index)
        file_index += 1

    # Remove the most recent one from the deletion scope
    if len(range_files) > 0:
        files_to_save.append(files_to_delete[range_files[0]])
        files_to_delete.pop(range_files[0])
        file_index -= 1

    newer_date = older_date - datetime.timedelta(1)  # the 1st of the current month minus 1 day

# Delete all files remaining in the deletion scope
print(today, " Save (", len(files_to_save), "): ", files_to_save, sep='')
print(today, " Delete (", len(files_to_delete), "): ", files_to_delete, sep='')
log_file = open(backup_dir + log_file_name, "ab+")
if do_deletion:
    for filename in files_to_delete:
        os.remove(backup_dir + filename)
    log_file.write(bytes((today.strftime(date_format) + " Saved (" + str(len(files_to_save)) +
                          "): " + ", ".join(files_to_save) + "\r\n"), "UTF-8"))
    log_file.write(bytes((today.strftime(date_format) + " Deleted (" + str(len(files_to_delete)) +
                          "): " + ", ".join(files_to_delete) + "\r\n"), "UTF-8"))

log_file.close()

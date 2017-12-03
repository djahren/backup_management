"""
Name: Backup Management
Author: Ahren Bader-Jarvis
Version: 1.0
Revision Date: 2017-12-02
Description: This script is designed to manage daily backups using a set schedule.
             It will keep daily backups from the last 2 weeks, after that, 1 for
             every week for 2 months, and finally 1 backup every month indefinitely.
Assumptions: The backup directory (defined in backup_dir) receives 1 backup daily.
             The backup files have the filename format of: backupname-YYYY-MM-DD.tgz
"""

import os
import datetime
backup_dir = "E:\Backup\Minecraft Server\\"
log_file_name = "backup_management.log"
date_format = "%Y-%m-%d"
do_deletion = False


files_to_delete = []
files_to_save = []
today = datetime.date.today()
two_weeks_ago = today - datetime.timedelta(14)
two_months_ago = today - datetime.timedelta(60)
one_week = datetime.timedelta(7)
one_month = datetime.timedelta(30)


def date_from_filename(fn):
    return datetime.datetime.strptime(fn[-14:-4], date_format).date()


for filename in os.listdir(backup_dir):
    # Get a list of all .tgz files in directory
    if filename.endswith(".tgz"):
        d = date_from_filename(filename)
        if not(today >= d > two_weeks_ago):
            # If the file is within the last two weeks ignore it
            # Else add it to the list
            files_to_delete.append(filename)
        else:
            files_to_save.append(filename)
files_to_delete.sort(reverse=True)  # sort

# ---WEEK---
# Loop through dates from 2 weeks to 2 months ago decrementing by week
newer_date = two_weeks_ago

file_index = 0
while newer_date > two_months_ago:
    # Generate the week boundaries
    older_date = newer_date - one_week

    # Get list of files that are within those boundaries
    range_files = []
    while len(files_to_delete) != file_index and date_from_filename(files_to_delete[file_index]) > older_date:
        range_files.append(file_index)
        print(file_index, files_to_delete[file_index], date_from_filename(files_to_delete[file_index]), older_date)
        file_index += 1

    # print(newer_date, older_date, range_files)
    # Remove the most recent one from the deletion scope
    if len(range_files) > 0:
        files_to_save.append(files_to_delete[range_files[0]])
        files_to_delete.pop(range_files[0])
        file_index -= 1

    newer_date = older_date

# ---MONTH---
# Loop through dates from 2 weeks to the earliest backup decrementing by month
newer_date = two_months_ago
while len(files_to_delete) > 0 and newer_date >= date_from_filename(sorted(files_to_delete)[0]):
    # print(newer_date, ",", date_from_filename(sorted(files_to_delete)[0]))
    # Generate the month boundaries
    older_date = newer_date - one_month

    # Get list of files that are within those boundaries
    range_files = []
    while len(files_to_delete) != file_index and date_from_filename(files_to_delete[file_index]) > older_date:
        range_files.append(file_index)
        print(file_index, files_to_delete[file_index], date_from_filename(files_to_delete[file_index]), older_date)
        file_index += 1

    # print(newer_date, older_date, range_files)
    # Remove the most recent one from the deletion scope
    if len(range_files) > 0:
        print(range_files)
        files_to_save.append(files_to_delete[range_files[0]])
        files_to_delete.pop(range_files[0])
        file_index -= 1

    newer_date = older_date

# Delete all files remaining in the deletion scope
print(today, " Save (", len(files_to_save), "): ", files_to_save, sep='')
print(today, " Delete (", len(files_to_delete), "): ",  files_to_delete, sep='')
log_file = open(backup_dir + log_file_name, "ab+")
log_file.write(bytes((today.strftime(date_format) + " Saved (" + str(len(files_to_save)) + "): " + ", ".join(files_to_save) + "\n"), "UTF-8"))
log_file.write(bytes((today.strftime(date_format) + " Deleted (" + str(len(files_to_delete)) + "): " + ", ".join(files_to_delete) + "\n"), "UTF-8"))
if do_deletion:
    for filename in files_to_delete:
        os.remove(backup_dir + filename)

log_file.close()


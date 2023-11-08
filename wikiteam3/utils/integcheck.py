import re

file_path = 'blobbb/history.xml'

# Read the file
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()

# Count occurrences using regex
title_count = len(re.findall(r"<title.*?>", file_content))
page_open_count = len(re.findall(r"<page.*?>", file_content))
page_close_count = len(re.findall(r"</page>", file_content))
revision_open_count = len(re.findall(r"<revision.*?>", file_content))
revision_close_count = len(re.findall(r"</revision>", file_content))

print("Title count:", title_count)
print("Page open count:", page_open_count)
print("Page close count:", page_close_count)
print("Revision open count:", revision_open_count)
print("Revision close count:", revision_close_count)

# Check conditions
if (
    title_count == page_open_count == page_close_count
    and revision_open_count == revision_close_count
    and file_content.strip().endswith('</mediawiki>')
):
    filestatus = "okay"
else:
    filestatus = "not okay"

print(f"File status: {filestatus}")

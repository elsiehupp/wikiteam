import re


def check_xml_integrity(file_path):
    with open(file_path, encoding="utf-8") as file:
        file_content = file.read()

    title_count = len(re.findall(r"<title.*?>", file_content))
    page_open_count = len(re.findall(r"<page.*?>", file_content))
    page_close_count = len(re.findall(r"</page>", file_content))

    revision_open_count = len(re.findall(r"<revision.*?>", file_content))
    revision_close_count = len(re.findall(r"</revision>", file_content))

    check_1 = title_count == page_open_count == page_close_count
    check_2 = revision_open_count == revision_close_count

    checktags = check_1 and check_2

    checkends = file_content.strip().endswith("</mediawiki>")

    # Extracting the last line of text  - just for info, delete later
    lines = file_content.rstrip().split("\n")
    last_line = lines[-1].strip() if lines[-1].strip() else lines[-2].strip()

    # Only checktags and checkends are useful - the rest are just for info, delete later
    return (
        checktags,
        checkends,
        {
            "title_count": title_count,
            "page_open_count": page_open_count,
            "page_close_count": page_close_count,
            "revision_open_count": revision_open_count,
            "revision_close_count": revision_close_count,
            "last_line": last_line,
        },
    )

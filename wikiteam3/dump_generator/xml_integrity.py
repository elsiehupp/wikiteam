from domain import Domain
from xml_dump import generate_xml_dump


def check_xml_integrity(config: dict, titles: str):
    """Check XML dump integrity, to detect broken XML chunks"""

    print("")
    print("Verifying dump...")
    checktitles = 0
    checkpageopen = 0
    checkpageclose = 0
    checkrevisionopen = 0
    checkrevisionclose = 0
    with open(
        "%s/%s-%s-%s.xml"
        % (
            config["path"],
            Domain(config).to_prefix(),
            config["date"],
            config["current-only"] and "current-only" or "history",
        ),
    ) as xml_dump_file:
        lines = xml_dump_file.read().splitlines()
    for line in lines:
        if "<revision>" in line:
            checkrevisionopen += 1
        elif "</revision>" in line:
            checkrevisionclose += 1
        elif "<page>" in line:
            checkpageopen += 1
        elif "</page>" in line:
            checkpageclose += 1
        elif "<title>" in line:
            checktitles += 1
        else:
            continue
    try:
        assert checktitles == checkpageopen
        assert checktitles == checkpageclose
        assert checkrevisionopen == checkrevisionclose
    except AssertionError as assertion_error:
        print("XML dump seems to be corrupted: %s" % assertion_error)
        reply = ""
        if config["failfast"]:
            reply = "yes"
        while reply.lower() not in ["yes", "y", "no", "n"]:
            reply = input("Regenerate a new dump ([yes, y], [no, n])? ")
        if reply.lower() in ["yes", "y"]:
            generate_xml_dump(config=config, titles=titles)
        elif reply.lower() in ["no", "n"]:
            print("Not generating a new dump.")

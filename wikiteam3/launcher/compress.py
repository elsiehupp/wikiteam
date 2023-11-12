import os
import time
from pathlib import Path

from py7zr import SevenZipFile


# Compress history, titles, index, SpecialVersion, errors log, and siteinfo into an archive
# You can also add config.txt if you don't care about your computer and user names being published or you don't use full paths so that they're not stored in it.
def compress_history(prefix):
    pathHistoryTmp = Path("..", f"{prefix}-history.xml.7z.tmp")
    pathHistoryFinal = Path("..", f"{prefix}-history.xml.7z")

    with SevenZipFile(str(pathHistoryTmp), "w") as archive:
        archive.write(f"{prefix}-history.xml")
        archive.write(f"{prefix}-titles.txt")
        archive.write("index.html")
        archive.write("SpecialVersion.html")
        archive.write("siteinfo.json")
        # Check if errors.log file exists and add it to the archive if it does
        if os.path.exists("errors.log"):
            archive.write("errors.log")
            print("errors.log exists and has been added to the archive.")
        else:  # - just for info, delete later
            print("no errors.log")  #

    pathHistoryTmp.rename(pathHistoryFinal)
    # End of compress history section


# Compress any images and other media files into another archive
def compress_images(prefix):
    pathFullTmp = Path("..", f"{prefix}-wikidump.7z.tmp")
    pathFullFinal = Path("..", f"{prefix}-wikidump.7z")

    with SevenZipFile(str(pathFullTmp), "w") as archive:
        archive.write(f"{prefix}-images.txt")
        archive.writeall("images/")

    pathFullTmp.rename(pathFullFinal)
    # End of compress images section
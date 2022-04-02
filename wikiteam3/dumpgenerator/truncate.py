from hashlib import md5


def truncateFilename(filename: str, filename_limit: int = 100):
    """Truncate filenames when downloading images with large filenames"""
    return (
        filename[:filename_limit]
        + md5(str(filename).encode("utf-8")).hexdigest()
        + "."
        + filename.split(".")[-1]
    )

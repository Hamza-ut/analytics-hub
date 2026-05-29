# uploads/utils.py
import hashlib


def calculate_md5(file_obj):
    """
    Calculates MD5 hash of an uploaded file object.
    """
    md5_hash = hashlib.md5()
    for chunk in file_obj.chunks():
        md5_hash.update(chunk)
    return md5_hash.hexdigest()


ALLOWED_EXTENSIONS = [
    "csv",
    "fastq",
    "fastq.gz",
    "fq",
    "fq.gz",
    "fasta",
    "fna",
    "fa",
    "gbk",
    "gb",
    "genbank",
]
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10 GB


def get_file_extension(file_obj):
    # Use the 'name' attribute of the uploaded file
    filename = getattr(file_obj, "name", None)
    if not filename:
        return ""  # fallback if name is missing
    # Extract the extension
    ext = filename.split(".")[-1].lower()  # simple split, robust even if multiple dots
    return ext


# uploads/utils.py
def human_readable_size(size_bytes: int) -> str:
    """
    Convert a file size in bytes to a human-readable string. Automatically chooses B, KB, MB, GB, TB.
    """
    if size_bytes == 0:
        return "0B"
    units = ["B", "KB", "MB", "GB", "TB"]
    index = 0
    size = float(size_bytes)
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"


def validate_file(
    file_obj, max_size=MAX_FILE_SIZE, allowed_extensions=ALLOWED_EXTENSIONS
):
    # Check file size
    if file_obj.size > max_size:
        return False, f"File is too large. Max size is {human_readable_size(max_size)}."

    # Check extension
    ext = get_file_extension(file_obj)
    if ext not in allowed_extensions:
        return (
            False,
            f"File type .{ext} is not allowed. Allowed: {', '.join(allowed_extensions)}",
        )

    return True, None

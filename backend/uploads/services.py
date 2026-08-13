import logging

logger = logging.getLogger(__name__)


def stream_file(file_obj):
    return open(file_obj.file.path, "rb")


def delete_file(file_obj):
    file_obj.delete()  # post_delete signal handles disk cleanup

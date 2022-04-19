import logging
import os
import shutil
import tarfile
import tempfile

from django.conf import settings

__all__ = [
    "ExportError",
    "ExportFileContext"
]

logger = logging.getLogger(__name__)

EXPORT_DIR = 'export'


class ExportError(Exception):
    pass


class ExportFileContext:
    """
    File context manager around a tmp export directory for a given study
    identifier.
    When no temp directory is provided, this context takes care of removing the
    temp directories created with their contents.

    Attributes:
        tmp_dir: path to the directory where the exported files are written.
            Can be None. In that case the files are written to a tmp directory
            on the system and cleaned once the context manager finishes.
        project_id: name that will be used to namespace the export directory.
            This is also used for the archive filename by the writeTar() method
    """
    path = ""
    should_del = False
    base_path = ""
    project_id = ''

    def __init__(self, tmp_dir: str, project_id: str):
        tmp_dir = tmp_dir or settings.SERVICE_TEMP

        if tmp_dir is None:
            tmp_dir = tempfile.mkdtemp()
            self.should_del = True

        if not os.access(tmp_dir, os.W_OK):
            raise ExportError(f"Directory does not exist or is not writable: {tmp_dir}")

        self.base_path = tmp_dir
        self.project_id = project_id

        try:
            self.path = os.path.join(tmp_dir, EXPORT_DIR, project_id)

            # clean pre-existing export dir
            isExistant = os.path.exists(self.path)
            if isExistant:
                shutil.rmtree(self.path)

            original_umask = os.umask(0)    # fix issue with non-writable dir due to OS based mask
            os.makedirs(self.path, 0o777)

        except OSError:
            raise ExportError

        finally:
            os.umask(original_umask)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.should_del and self.path:
            shutil.rmtree(self.path)

    def get_path(self, filename: str = ''):
        """Returns a path within the export directory

        Attributes:
            filename: optional filename to use
        """
        return os.path.join(self.path, filename)

    def write_tar(self):
        """Creates a tar gzipped archive from the export directory content

        Note that the tar file is created inside the context of this ExportFileContext
        class. If no path was provided at the time of the context creation,
        then the generated tar file will be deleted along with the tmp directory

        Return: path to the generated tar file
        """
        tar_path = os.path.join(self.base_path, EXPORT_DIR, self.project_id + '.tar.gz')
        with tarfile.open(tar_path, 'w:gz') as tar:
            output_dir = self.get_path()
            tar.add(output_dir, filter=reset_tar_info)
        return tar_path


def reset_tar_info(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.gid = 0
    info.uid = 0
    info.uname = 'root'
    info.gname = 'root'
    return info

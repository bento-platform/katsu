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
    Context manager around the tmp export directory for a given study
    identifier.
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

            #clean pre-existing export dir
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

    def getPath (self, filename: str = ''):
        return os.path.join(self.path, filename)

    def writeTar (self):
        tar_path = os.path.join(self.base_path, EXPORT_DIR, self.project_id + '.tar.gz')
        with tarfile.open(tar_path, 'w:gz') as tar:
            output_dir = self.getPath()
            tar.add(output_dir, filter=resetTarInfo)
        return tar_path

def resetTarInfo(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.gid = 0
    info.uid = 0
    info.uname = 'root'
    info.gname = 'root'
    return info
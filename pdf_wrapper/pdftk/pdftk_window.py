import shutil
from overrides import overrides

from os_enum.os import OSEnum
from pdftk.pdftk_base import PDFTKBase
from os_enum.os import OSEnum

class PDFTKWindow(PDFTKBase):

    def __init__(self) -> None:
        self.os = OSEnum.WINDOW
        super()._initialize(self)
    
    @overrides
    def _check_installed_pdftk(self) -> bool:
        if shutil.which('pdftk') is not None:
            return True
        return False
    
    @overrides
    def merge_pdf(self, tmp_pdf_directory: str, target_pdf_files: str):
        import subprocess
        _tmp_pdf_files = super()._get_tmp_pdf_files(tmp_pdf_directory)
        subprocess.call(['pdftk'] + _tmp_pdf_files + ['cat', 'output', target_pdf_files])    
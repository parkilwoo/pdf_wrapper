from os_enum.os import OSEnum
from pdftk.pdftk_base import PDFTKBase
import subprocess

class PDFTKLinux(PDFTKBase):

    def __init__(self) -> None:
        self.os = OSEnum.LINUX
        super()._initialize(self)
    
    def _check_installed_pdftk(self) -> bool:
        try:
            subprocess.run(["pdftk", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False        

    def merge_pdf(self, tmp_pdf_directory: str, target_pdf_files: str):
        _tmp_pdf_files = super()._get_tmp_pdf_files(tmp_pdf_directory)
        subprocess.call(['pdftk'] + _tmp_pdf_files + ['cat', 'output', target_pdf_files])
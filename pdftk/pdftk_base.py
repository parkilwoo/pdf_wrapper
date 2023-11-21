from abc import ABC, abstractmethod
import os

class PDFTKBase(ABC):
    __PDF_EXTENSION = '.pdf'

    def _initialize(self, child_instance):
        if not self._check_installed_pdftk():
            raise FileNotFoundError(f"Pdftk not found in {child_instance.os.value}. Please install pdftk first")
    
    def _get_tmp_pdf_files(self, mereged_pdf_file: str):
        pdf_files = [f for f in os.listdir(mereged_pdf_file) if f.endswith(self.__PDF_EXTENSION)]
        pdf_files.sort()
        return [os.path.join(mereged_pdf_file, f) for f in pdf_files]

    @abstractmethod
    def _check_installed_pdftk(self) -> bool:
        pass

    @abstractmethod
    def merge_pdf(self, tmp_pdf_directory: str, target_pdf_files: str):
        pass  
from abc import ABC, abstractmethod
import os

class PDFTKBase(ABC):
    __PDF_EXTENSION = '.pdf'

    def _initialize(self, child_instance):
        """
        Check pdftk installation when creating instance
        Args:
            child_instance (PDFTKLinux | PDFTKMacos | PDFTKWindow): Subclass instance

        Raises:
            FileNotFoundError: Not installed pdftk
        """
        if not self._check_installed_pdftk():
            raise FileNotFoundError(f"Pdftk not found in {child_instance.os.value}. Please install pdftk first")
    
    def _get_tmp_pdf_files(self, mereged_pdf_file: str) -> list:
        """
        Sort the PDF files in the tmp folder and import a list containing the file names including the path.
        Args:
            mereged_pdf_file (str): Tmp folder path

        Returns:
            list: List containing the paths of sorted PDF files
        """
        pdf_files = [f for f in os.listdir(mereged_pdf_file) if f.endswith(self.__PDF_EXTENSION)]
        pdf_files.sort()
        return [os.path.join(mereged_pdf_file, f) for f in pdf_files]

    @abstractmethod
    def _check_installed_pdftk(self) -> bool:
        """
        Check if pdftk is installed on the OS
        Returns:
            bool: Installed or not
        """
        pass

    @abstractmethod
    def merge_pdf(self, tmp_pdf_directory: str, target_pdf_files: str):
        """
        Combine PDFs in the tmp folder to create final PDF
        Args:
            tmp_pdf_directory (str): tmp pdf directory
            target_pdf_files (str): final pdf file name including path
        """
        pass  
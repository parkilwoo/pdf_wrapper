import platform
from queue import SimpleQueue
import uuid
import os

from overrides import overrides
from reportlab.pdfbase import pdfdoc
from reportlab.pdfgen.canvas import Canvas

from pdftk.pdftk_base import PDFTKBase
from pdftk.pdftk_linux import PDFTKLinux
from pdftk.pdftk_window import PDFTKWindow
from pdftk.pdftk_macos import PDFTKMacos
from os_enum.os import OSEnum


class PDFGenerator(Canvas):

    def __init__(self, filename, pagesize=None, bottomup=1, pageCompression=None, invariant=None, verbosity=0, encrypt=None, cropMarks=None, pdfVersion=None, enforceColorSpace=None, initialFontName=None, initialFontSize=None, initialLeading=None, cropBox=None, artBox=None, trimBox=None, bleedBox=None, lang=None, batchSize=20):
        super().__init__(filename, pagesize, bottomup, pageCompression, invariant, verbosity, encrypt, cropMarks, pdfVersion, enforceColorSpace, initialFontName, initialFontSize, initialLeading, cropBox, artBox, trimBox, bleedBox, lang)
        self.invariant = invariant
        self.pdfVersion = pdfVersion
        self.lang = lang
        self._doc_queue = SimpleQueue()
        self.batch_size = batchSize
        self.pdftk = self._set_pdftK()
        self.tmp_folder_path = self._make_tmp_folder(filename)

    def _set_pdftK(self) -> PDFTKBase:
        """
        Create an instance to use PDFTK suitable for OS
        Returns:
            PDFTKBase: PDFTK subclass instance
        """
        os_ = platform.system()
        if os_ == OSEnum.LINUX.value:
            return PDFTKLinux()
        elif os_ == OSEnum.WINDOW.value:
            return PDFTKWindow()
        return PDFTKMacos()
    
    def _make_tmp_folder(self, filename: str) -> str:
        """
        Create tmp folder for temporary storage
        Args:
            filename (str): input filename

        Raises:
            FileExistsError: Error when there is a duplicate tmp folder
            
        Returns:
            str: Created tmp folder path
        """
        parent_directory = os.path.dirname(filename)
        tmp_folder_nm = f"{str(uuid.uuid4())}_tmp"
        tmp_path = os.path.join(parent_directory, tmp_folder_nm)
        try:
            os.makedirs(tmp_path)
            return tmp_path
        except FileExistsError:
            raise FileExistsError(f"{tmp_path} alreay exists!")
    
    @overrides
    def showPage(self):
        doc_page_count = self._doc.pageCounter
        if doc_page_count-1 == self.batch_size:
            self._doc_queue.put(self._doc)
            self._doc = pdfdoc.PDFDocument(compression=self._pageCompression,
                                        invariant=self.invariant, filename=self._filename,
                                        pdfVersion=self.pdfVersion or pdfdoc.PDF_VERSION_DEFAULT,
                                        lang=self.lang
                                        )
            self._make_preamble()   
        super().showPage()

    @overrides
    def save(self):
        try:
            if len(self._code): self.showPage()
            if self._doc.pageCounter != 1:
                self._doc_queue.put(self._doc)
            
            _count = 1
            while(not self._doc_queue.empty()):
                _doc:pdfdoc.PDFDocument = self._doc_queue.get()
                _index_file_nm = os.path.join(self.tmp_folder_path, f"{_count}.pdf")
                _doc.SaveToFile(_index_file_nm, self)
                _count += 1
            self.pdftk.merge_pdf(self.tmp_folder_path, self._filename)
        except Exception as e:
            raise e
        finally:
            import shutil
            shutil.rmtree(self.tmp_folder_path)

if __name__ == '__main__':
    pdfgen = PDFGenerator(filename="/CAMS/test.pdf")

    # 첫 번째 페이지
    pdfgen.drawString(100, 750, "Page 1")
    pdfgen.line(100, 740, 500, 740)

    for i in range(2, 15):
        # 두 번째 페이지
        pdfgen.showPage()
        pdfgen.drawString(100, 750, f"Page {i}")
        pdfgen.line(100, 740, 500, 740)    

    pdfgen.save()
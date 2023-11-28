from overrides import overrides

from reportlab import rl_config
from reportlab.pdfbase.pdfdoc import PDFFile, PDFDocument, PDFIndirectObject, PDFCrossReferenceTable, PDFTrailer
from reportlab.lib.utils import makeFileName, isStr
from chunk_pdf.pdfbase.chunk_file import ChunkedFileIO

PDF_VERSION_DEFAULT = (1, 3)

def pdfdocEnc(x):
    return x.encode('extpdfdoc') if isinstance(x,str) else x
class PDFFileWrapper(PDFFile):

    ### just accumulates strings: keeps track of current offset
    def __init__(self,pdfVersion=PDF_VERSION_DEFAULT):
        self.bytes = bytearray()
        self.write = self.bytes.extend
        self.offset = 0
        ### chapter 5
        # Following Ken Lunde's advice and the PDF spec, this includes
        # some high-order bytes.  I chose the characters for Tokyo
        # in Shift-JIS encoding, as these cannot be mistaken for
        # any other encoding, and we'll be able to tell if something
        # has run our PDF files through a dodgy Unicode conversion.
        self.add((pdfdocEnc("%%PDF-%s.%s" % pdfVersion) +
            b'\n%\223\214\213\236 ReportLab Generated PDF document http://www.reportlab.com\n'
            ))

    @overrides
    def format(self, document):
        return self.bytes


class PDFDocumentWrapper(PDFDocument):

    def __init__(self, dummyoutline=0, compression=rl_config.pageCompression, invariant=rl_config.invariant, filename=None, pdfVersion=..., lang=None, chunk_size = None):
        super().__init__(dummyoutline, compression, invariant, filename, pdfVersion, lang)
        self.chunk_size = chunk_size

    @overrides
    def format(self):
        # register the Catalog/INfo and then format the objects one by one until exhausted
        # (possible infinite loop if there is a bug that continually makes new objects/refs...)
        # Prepare encryption
        self.encrypt.prepare(self)
        cat = self.Catalog
        info = self.info
        self.Reference(cat)
        self.Reference(info)
        # register the encryption dictionary if present
        encryptref = None
        encryptinfo = self.encrypt.info()
        if encryptinfo:
            encryptref = self.Reference(encryptinfo)
        # make std fonts (this could be made optional
        counter = 0 # start at first object (object 1 after preincrement)
        ids = [] # the collection of object ids in object number order
        numbertoid = self.numberToId
        idToOb = self.idToObject
        idToOf = self.idToOffset
        ### note that new entries may be "appended" DURING FORMATTING
        # __accum__ allows objects to know where they are in the file etc etc
        self.__accum__ = File = PDFFileWrapper(self._pdfVersion) # output collector
        while True:
            counter += 1 # do next object...
            if counter not in numbertoid: break
            oid = numbertoid[counter]
            #printidToOb
            obj = idToOb[oid]
            IO = PDFIndirectObject(oid, obj)
            # register object number and version
            IOf = IO.format(self)
            # add a comment to the PDF output
            if not rl_config.invariant and rl_config.pdfComments:
                try:
                    classname = obj.__class__.__name__
                except:
                    classname = ascii(obj)
                File.add("%% %s: class %s \n" % (ascii(oid), classname[:50]))
            offset = File.add(IOf)
            idToOf[oid] = offset
            ids.append(oid)
        del self.__accum__
        # sanity checks (must happen AFTER formatting)
        lno = len(numbertoid)
        if counter-1!=lno:
            raise ValueError("counter %s doesn't match number to id dictionary %s" %(counter, lno))
        # now add the xref
        xref = PDFCrossReferenceTable()
        xref.addsection(0, ids)
        xreff = xref.format(self)
        xrefoffset = File.add(xreff)
        # now add the trailer
        trailer = PDFTrailer(
            startxref = xrefoffset,
            Size = lno+1,
            Root = self.Reference(cat),
            Info = self.Reference(info),
            Encrypt = encryptref,
            ID = self.ID(),
            )
        trailerf = trailer.format(self)
        File.add(trailerf)
        for ds in getattr(self,'_digiSigs',[]):
            ds.sign(File)
        # return string format for pdf file
        return File.format(self)
    
    @overrides
    def SaveToFile(self, filename, canvas):
        if getattr(self,'_savedToFile',False):
            raise RuntimeError("class %s instances can only be saved once" % self.__class__.__name__)
        self._savedToFile = True
        if hasattr(getattr(filename, "write",None),'__call__'):
            myfile = 0
            f = filename
            filename = getattr(f,'name',None)
            if isinstance(filename,int):
                filename = '<os fd:%d>'% filename
            elif not isStr(filename): #try to fix bug reported by Robert Schroll <rschroll at gmail.com> 
                filename = '<%s@0X%8.8X>' % (f.__class__.__name__,id(f))
            filename = makeFileName(filename)
        elif isStr(filename):
            myfile = 1
            filename = makeFileName(filename)
            f = open(filename, "wb")
        else:
            raise TypeError('Cannot use %s as a filename or file' % repr(filename)) 

        data = self.GetPDFData(canvas)
        chunk_file_io = ChunkedFileIO(chunk_size=self.chunk_size)
        chunk_file_io.file_write(data, f)

        if myfile:
            f.close()
            import os
            if os.name=='mac':
                from reportlab.lib.utils import markfilename
                markfilename(filename) # do platform specific file junk
        if getattr(canvas,'_verbosity',None): print('saved %s' % (filename,))
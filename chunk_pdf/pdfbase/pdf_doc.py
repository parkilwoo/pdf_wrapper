from overrides import overrides

from reportlab import rl_config
from reportlab.pdfbase.pdfdoc import PDFFile, PDFDocument, PDFIndirectObject, PDFCrossReferenceTable, PDFTrailer
from reportlab.lib.utils import makeFileName, isUnicode, isStr
from chunk_pdf.pdfbase.chunk_list import ChukedList, ListFull

class PDFFileWrapper(PDFFile):

    @overrides
    def format(self, document):
        yield from self.strings


class PDFDocumentWrapper(PDFDocument):

    def __init__(self, dummyoutline=0, compression=rl_config.pageCompression, invariant=rl_config.invariant, filename=None, pdfVersion=..., lang=None, chunkSize = 10):
        super().__init__(dummyoutline, compression, invariant, filename, pdfVersion, lang)
        self.chunkedList = ChukedList(chunkSize)

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

        data_generator = self.GetPDFData(canvas)
        self._saveFileUseChunkSize(data_generator, f)

        if myfile:
            f.close()
            import os
            if os.name=='mac':
                from reportlab.lib.utils import markfilename
                markfilename(filename) # do platform specific file junk
        if getattr(canvas,'_verbosity',None): print('saved %s' % (filename,))

    def _saveFileUseChunkSize(self, data_generator, file_io):
        for data in data_generator:        
            try:
                self.chunkedList.append(data)
            except ListFull:
                file_data = self.chunkedList.convertBytes()
                self._fileWrite(file_data, file_io)
                self.chunkedList.append(data)
        
        if not self.chunkedList.is_empty():
            file_data = self.chunkedList.convertBytes()
            self._fileWrite(file_data, file_io)

    def _fileWrite(self, data: bytes, file_io):
        if isUnicode(data):
            data = data.encode('latin1')
        file_io.write(data)
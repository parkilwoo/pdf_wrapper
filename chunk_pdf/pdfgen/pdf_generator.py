from reportlab.pdfbase import pdfdoc
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import _chooseEnforceColorSpace
from reportlab import rl_config

from chunk_pdf.pdfbase.pdf_doc import PDFDocumentWrapper

class PDFGenerator(Canvas):

    def __init__(self,filename,
                 pagesize=None,
                 bottomup = 1,
                 pageCompression=None,
                 invariant = None,
                 verbosity=0,
                 encrypt=None,
                 cropMarks=None,
                 pdfVersion=None,
                 enforceColorSpace=None,
                 initialFontName=None,
                 initialFontSize=None,
                 initialLeading=None,
                 cropBox=None,
                 artBox=None,
                 trimBox=None,
                 bleedBox=None,
                 lang=None,
                 chunkSize = 10
                 ):
        """Create a canvas of a given size. etc.

        You may pass a file-like object to filename as an alternative to
        a string.
        For more information about the encrypt parameter refer to the setEncrypt method.
        
        Most of the attributes are private - we will use set/get methods
        as the preferred interface.  Default page size is A4.
        cropMarks may be True/False or an object with parameters borderWidth, markColor, markWidth
        and markLength
    
        if enforceColorSpace is in ('cmyk', 'rgb', 'sep','sep_black','sep_cmyk') then one of
        the standard _PDFColorSetter callables will be used to enforce appropriate color settings.
        If it is a callable then that will be used.
        """
        if pagesize is None: pagesize = rl_config.defaultPageSize
        if invariant is None: invariant = rl_config.invariant

        self._initialFontName = initialFontName if initialFontName else rl_config.canvas_basefontname
        self._initialFontSize = initialFontSize if initialFontSize is not None else 12
        self._initialLeading = initialLeading if initialLeading is not None else self._initialFontSize*1.2

        self._filename = filename

        self._doc = PDFDocumentWrapper(compression=pageCompression,
                                       invariant=invariant, filename=filename,
                                       pdfVersion=pdfVersion or pdfdoc.PDF_VERSION_DEFAULT,
                                       lang=lang
                                       )

        self._enforceColorSpace = _chooseEnforceColorSpace(enforceColorSpace)

        #this only controls whether it prints 'saved ...' - 0 disables
        self._verbosity = verbosity

        #this is called each time a page is output if non-null
        self._onPage = None
        self._cropMarks = cropMarks

        self._pagesize = pagesize
        self._hanging_pagesize = None
        self._pageRotation = 0
        #self._currentPageHasImages = 0
        self._pageTransition = None
        self._pageDuration = None
        self._destinations = {} # dictionary of destinations for cross indexing.

        self.setPageCompression(pageCompression)
        self._pageNumber = 1   # keep a count
        # when we create a form we need to save operations not in the form
        self._codeStack = []
        self._restartAccumulators()  # restart all accumulation state (generalized, arw)
        self._annotationCount = 0

        self._outlines = [] # list for a name tree
        self._psCommandsBeforePage = [] #for postscript tray/font commands
        self._psCommandsAfterPage = [] #for postscript tray/font commands

        #PostScript has the origin at bottom left. It is easy to achieve a top-
        #down coord system by translating to the top of the page and setting y
        #scale to -1, but then text is inverted.  So self.bottomup is used
        #to also set the text matrix accordingly.  You can now choose your
        #drawing coordinates.
        self.bottomup = bottomup
        self.imageCaching = rl_config.defaultImageCaching

        self._cropBox = cropBox     #we don't do semantics for these at all
        self._artBox = artBox
        self._trimBox = trimBox
        self._bleedBox = bleedBox

        self.init_graphics_state()
        self._make_preamble()
        self.state_stack = []

        self.setEncrypt(encrypt)
        self.chunkSize = chunkSize
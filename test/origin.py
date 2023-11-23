from reportlab.pdfgen.canvas import Canvas
from datetime import datetime
from reportlab.lib.units import mm
from memory_profiler import profile

@profile
def create_pdf():
    start_time = datetime.now()
    pdfgen = Canvas(filename="/CAMS/origin.pdf")


    for i in range(1, 3001):
        pdfgen.drawImage("sample/test.png", 0, 0, 210.82 * mm, 297.18 * mm)
        pdfgen.drawString(100, 750, f"Page {i}")
        pdfgen.line(100, 740, 500, 740)    
        pdfgen.showPage()

    pdfgen.save()
    print(f"elapsed time : {datetime.now() - start_time}")

if __name__ == '__main__':
    create_pdf()
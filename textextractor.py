import PyPDF2
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)

        # Convert each page to an image
        images = convert_from_path(pdf_path)

        # Perform OCR on each image
        text = ""
        for i in range(len(images)):
            text += pytesseract.image_to_string(images[i])

        return text

# Use the function
i=extract_text_from_pdf('data/atomic.pdf')
with open('data/atomic.txt','w') as f:
    f.write(i)
print(i)

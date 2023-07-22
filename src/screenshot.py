import ctypes
import os


class Screenshot:

    def __init__(self, tesserocr=None):
        tesseract_path = os.path.join(os.getcwd(), 'Tesseract-OCR')
        tessdata_path = os.path.join(tesseract_path, 'tessdata')
        tesseract_library = os.path.join(tesseract_path, 'libtesseract-5.dll')
        # Set the Tesseract OCR path for tesserocr
        tesserocr.tesseract_cmd = tessdata_path
        ctypes.cdll.LoadLibrary(tesseract_library)
        self.api = tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_WORD, lang='train', path=tesserocr.tesseract_cmd)

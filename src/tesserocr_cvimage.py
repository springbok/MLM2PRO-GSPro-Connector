import cv2
import numpy as np
from tesserocr import PyTessBaseAPI

class TesserocrCVImage(PyTessBaseAPI):

    def SetCVImage(self, image, color='RGB'):
        """ Sets an OpenCV-style image for recognition.

        'image' is a numpy ndarray in color, grayscale, or binary (boolean)
            format.
        'color' is a string representing the current color of the image,
            for conversion using OpenCV into an RGB array image. By default
            color images in OpenCV use BGR, but any valid channel
            specification can be used (e.g. 'BGRA', 'XYZ', 'YCrCb', 'HSV', 'HLS',
            'Lab', 'Luv', 'BayerBG', 'BayerGB', 'BayerRG', 'BayerGR').
            Conversion only occurs if the third dimension of the array is
            not 1, else 'color' is ignored.

        """
        bytes_per_pixel = image.shape[2] if len(image.shape) == 3 else 1
        height, width = image.shape[:2]
        bytes_per_line = bytes_per_pixel * width

        if bytes_per_pixel != 1 and color != 'RGB':
            # non-RGB color image -> convert to RGB
            image = cv2.cvtColor(image, getattr(cv2, f'COLOR_{color}2RGB'))
        elif bytes_per_pixel == 1 and image.dtype == bool:
            # binary image -> convert to bitstream
            image = np.packbits(image, axis=1)
            bytes_per_line = image.shape[1]
            width = bytes_per_line * 8
            bytes_per_pixel = 0
        # else image already RGB or grayscale

        self.SetImageBytes(image.tobytes(), width, height,
                           bytes_per_pixel, bytes_per_line)

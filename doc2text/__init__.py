# coding=utf-8

# coding=utf-8

import os
import mimetypes

import PyPDF2 as pyPdf
import PythonMagick
import cv2
import img2pdf
import numpy
import pdf2image
from pdf2image import convert_from_path

from .page import Page


acceptable_mime = ["image/bmp", "image/png",  "image/jpeg",
                   "image/jpg", "video/JPEG", "video/jpeg2000"]


FileNotAcceptedException = Exception(
    'The filetype is not acceptable. We accept bmp, png, tiff, jpg, jpeg, jpeg2000, and PDF.'
)


class Document(object):
    def __init__(self, lang=None):
        self.lang = lang
        self.pages = []
        self.processed_pages = []
        self.page_content = []
        self.prepared = False
        self.error = None

    def read(self, path):

        self.filename = os.path.basename(path)
        self.file_basename, self.file_extension = os.path.splitext(self.filename)
        self.path = path
        self.mime_type = mimetypes.guess_type(path)
        self.file_basepath = os.path.dirname(path)

        # If the file is a pdf, split the pdf and prep the pages.
        if self.mime_type[0] == "application/pdf":
            file_temp = open(self.path, 'rb')
            pdf_reader = pyPdf.PdfFileReader(file_temp)


            self.num_pages = pdf_reader.numPages
            try:
                #for i in range(self.num_pages):


                    # im = PythonMagick.Image()
                    # im.density("300")
                    # im.read(path)
                    # im.write(im_path)

                images = convert_from_path(self.path)
                i=0
                for image in images:
                    output = pyPdf.PdfFileWriter()
                    output.addPage(pdf_reader.getPage(i))
                    path = 'temp.pdf'
                    im_path = 'temp.png'
                    with open(path, 'wb') as f:
                        output.write(f)
                    #orig_im = cv2.imread(im_path, 0)

                    # Convert RGB to BGR
                    image = image.save(im_path)
                    i=i+1

                    orig_im = cv2.imread(im_path, 0)
                    page = Page(orig_im, i, self.lang)
                    self.pages.append(page)
                        # os.remove(path)
                        # os.remove(im_path)
                self.prepared = True
            except Exception as e:
                self.error = e
                raise
        elif self.mime_type[0]=="image/tiff" or self.mime_type[0]=="image/tif" or self.mime_type[0]=="image/TIFF":
            pass

        # If the file is an image, think of it as a 1-page pdf.
        elif self.mime_type[0] in acceptable_mime:
            self.num_pages = 1


            im = PythonMagick.Image()
            im.density("300")
            im.read(path)
            temp_path = os.path.normpath(os.path.join(
                self.file_basepath, self.file_basename + '_temp.png'
            ))
            im.write(temp_path)
            orig_im = cv2.imread(temp_path, 0)
            os.remove(temp_path)
            page = Page(orig_im, 0)
            self.pages.append(page)

        # Otherwise, out of luck.
        else:
            print(self.mime_type[0])
            raise FileNotAcceptedException

    def process(self):
        for page in self.pages:
            new = page
            new.crop()
            new.deskew()
            self.processed_pages.append(new)

    def extract_text(self):
        if len(self.processed_pages) > 0:
            for page in self.processed_pages:
                new = page
                text = new.extract_text()
                self.page_content.append(text)
        else:
            raise Exception('You must run `process()` first.')

    def get_text(self):
        if len(self.page_content) > 0:
            return "\n".join(self.page_content)
        else:
            raise Exception('You must run `extract_text()` first.')

    def save_pages(self):
        # TODO

        stuff = stuff

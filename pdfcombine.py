"""
    Combine (merge) two pdf files.

    Usage:

    python pdfreorder.py --inpath1 "path/file1" --inpath2 "path/file2" \
                         [--rotate1 CW|CCW|FV]  [--rotate2 CW|CCW|FV]  \
                         [--clobber]

    Command line options:

        --inpath1     Path and file name of first input PDF file

        --inpath2     Path and file name of second input PDF file

        --rotate1     Optional rotation applied to all pages of file1
                      CW = 90 degrees clockwise
                      CCW = 90 degrees counter-clockwise
                      FV = 180 degrees flip vertically

        --rotate2     Optional rotation applied to all pages of file2

        --clobber     Optional, if provided output overwrites file1

    If the --clobber option is not provided, then the output file name is
    formed as file1_file2.pdf where file1 and file2 are the names of the
    input files without extension. The output file is placed in the same
    directory as the input file.

    Examples: 

      Combine doc1.pdf and doc2.pdf

         python pdfcombine.py --inpath1 doc1.pdf --inpath2 doc2.pdf


      Combine doc1.pdf and doc2.pdf. Rotate doc1.pdf 90 degrees clockwise

         python pdfcombine.py --inpath1 doc.pdf --inpath2 doc2.pdf -rotate1 CW

"""
import argparse
import PyPDF2
import os
import uuid
import pdftools_utils as pu


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inpath1',  help='First input file',  type=str, default = '')
    parser.add_argument('-j', '--inpath2',  help='Second input file', type=str, default = '')
    parser.add_argument('-r', '--rotate1',  help='File 1 rotation',   type=str, default = '')
    parser.add_argument('-s', '--rotate2',  help='File 1 rotation',   type=str, default = '')
    parser.add_argument('-c', '--clobber',  help='Overwrite file 1', action='store_true')
    return parser.parse_args()


class PdfCombiner():
    def __init__(self, **kwargs):
        self.msg = ''
        degree_sign= u'\N{DEGREE SIGN}'
        self.rotOptionList = ('None'
                             , '90' + degree_sign + ' CW'
                             , '90' + degree_sign + ' CCW'
                             , 'Flip Vertical')
        self.ofile = None

    def validate_inputs(self, **kwargs):
        self.args_d = kwargs
        for infile in ['inpath1', 'inpath2']:
            if not os.path.isfile(self.args_d[infile]):
                ok = False
                self.msg = 'Cannot find input file {0}'.format(self.args_d[infile])
            elif not pu.ispdf(self.args_d[infile]):
                ok = False
                self.msg = '{0} does not look like a valid PDF.'.format(self.args_d[infile])
            elif pu.isRestricted(self.args_d[infile]):
                ok = False
                self.msg = 'File is restricted:\n {0}'.format(self.args_d[infile])
            else:
                ok = True
                self.msg = 'Inputs validated'
            if not ok:
                break
        self.rotate1  = self.args_d['rotate1'].upper()
        self.rotate2  = self.args_d['rotate2'].upper()
        self.file1    = self.args_d['inpath1']
        self.file2    = self.args_d['inpath2']
        self.clobber  = self.args_d['clobber']
        return ok

    def status(self):
        return self.msg

    def get_ofile(self):
        return self.ofile

    def process(self):
        # Form outout file path/name
        pdir1,pfile1 = os.path.split(self.file1)
        pdir2,pfile2 = os.path.split(self.file2)
        if not pdir1:
            pdir1 = '.'
        if not pdir2:
            pdir2 = '.'
        if self.clobber:
            self.ofile = os.path.join(pdir1,pfile1)
            tempfile = os.path.join(pdir1, str(uuid.uuid4()) + '.pdf')
            os.rename(self.file1, tempfile)
            self.file1 = tempfile
        else:
            self.ofile = pdir1 + '/' + os.path.splitext(pfile1)[0] 
            self.ofile += '_' + os.path.splitext(pfile2)[0] + '.pdf'
            tempfile = '' 

        # Open each file to be merged
        with open(self.file1, 'rb') as pdf1File:
            with open(self.file2, 'rb') as pdf2File:
   
                # Read files
                pdf1Reader = PyPDF2.PdfFileReader(pdf1File)
                pdf2Reader = PyPDF2.PdfFileReader(pdf2File)

                # Create a new PdfFileWriter object which represents a blank PDF document
                pdfWriter = PyPDF2.PdfFileWriter()
           
                # Loop through all pages of the first document
                for pageNum in range(pdf1Reader.numPages):
                    pageObj = pdf1Reader.getPage(pageNum)
                    if self.rotate1 == 'CW':
                        pageObj.rotateClockwise(90)
                    elif self.rotate1 == 'CCW':
                        pageObj.rotateCounterClockwise(90)
                    elif self.rotate1 == 'FV':
                        pageObj.rotateCounterClockwise(180)
                    pdfWriter.addPage(pageObj)
           
                # Loop through all pages of the second document
                for pageNum in range(pdf2Reader.numPages):
                    pageObj = pdf2Reader.getPage(pageNum)
                    if self.rotate2 == 'CW':
                        pageObj.rotateClockwise(90)
                    elif self.rotate2 == 'CCW':
                        pageObj.rotateCounterClockwise(90)
                    elif self.rotate2 == 'FV':
                        pageObj.rotateCounterClockwise(180)
                    pdfWriter.addPage(pageObj)
           
                # Write combined document
                with open(self.ofile, 'wb') as pdfOutputFile:
                    pdfWriter.write(pdfOutputFile)
   
        # Housekeeping
        if self.clobber:
            self.file1 = self.ofile
        if os.path.isfile(tempfile):
            os.remove(tempfile)
        return True

if __name__ == "__main__":
    args = parse_args()
    C = PdfCombiner()
    if not (C.validate_inputs(**vars(args)) and C.process()):
        print(C.status())

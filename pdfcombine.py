import argparse
import PyPDF2
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inpath1',  help='First input file',  type=str, default = '')
    parser.add_argument('-j', '--inpath2',  help='Second input file', type=str, default = '')
    parser.add_argument('-r', '--rotate1',  help='File 1 rotation',   type=str, default = '')
    parser.add_argument('-s', '--rotate2',  help='File 1 rotation',   type=str, default = '')
    parser.add_argument('-c', '--clobber',  help='Overwrite file 1', action='store_true')
    return parser.parse_args()

def ispdf(pathfile):
    try:
        reader = PyPDF2.PdfFileReader(open(pathfile, "rb"))
        return True  # PDF file
    except PyPDF2.utils.PdfReadError:
        return False  # not a PDF file


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
        if not os.path.isfile(self.args_d['inpath1']):
            ok = False
            self.msg = 'Cannot find input file {0}'.format(self.args_d['inpath1'])
        elif not ispdf(self.args_d['inpath1']):
            ok = False
            self.msg = '{0} does not look like a valid PDF.'.format(self.args_d['inpath1'])
        elif not os.path.isfile(self.args_d['inpath2']):
            ok = False
            self.msg = 'Cannot find input file {0}'.format(self.args_d['inpath2'])
        elif not ispdf(self.args_d['inpath2']):
            ok = False
            self.msg = '{0} does not look like a valid PDF.'.format(self.args_d['inpath2'])
        else:
            ok = True
            self.msg = 'Inputs validated'
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

    def combine(self):
        # Form outout file path/name
        pdir1,pfile1 = os.path.split(self.file1)
        pdir2,pfile2 = os.path.split(self.file2)
        if not pdir1:
            pdir1 = '.'
        if not pdir2:
            pdir2 = '.'
        if self.clobber:
            self.ofile = os.path.join(pdir1,pfile1)
            tempfile = os.path.join(pdir1, os.path.splitext(pfile1)[0] + '_old.pdf')
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
    P = PdfCombiner()
    args = parse_args()
    if P.validate_inputs(**vars(args)):
        P.combine()
    else:
        print(P.status())

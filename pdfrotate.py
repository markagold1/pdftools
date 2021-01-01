"""
    Rotate spefiied pages of a PDF file.

    Usage:

    python pdfrotate.py --pages "page-spec" --rotation CW|CC|FV  --inpath "path/file"

    Command line options:

        --pages       Comma separated list of pages and page ranges to rotate
                      Pages not in the list will appear in the output unrotated
                      Example: "1-3, 7, 10"  rotates pages 1,2,3,7, and 10
                      Note: this option must be quoted

        --rotation    One of the following
                      CW:   Clockwise rotation by 90 degrees (default)
                      CCW:  Counter-clockwise rotation by 90 degrees
                      FV:   Flip verical (rotate 180 degrees)

        --inpath      Path and file name of input PDF file

    The output file name is derived from the input file name by appending the
    string "_rot" to the input file name before the extension. The output
    file is placed in the same directory as the input file.

    Example: Rotate the first four pages of doc.pdf

              python pdfrotate.py --pages "1-4" --inpath doc.pdf

"""
import argparse
import PyPDF2 
import os
import pdftools_utils as pu

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pages',    help='Pages to rotate',  type=str, default = '1')
    parser.add_argument('-r', '--rotation', help='Type of rotation', type=str, default = 'CW')
    parser.add_argument('-i', '--inpath',   help='Input path/file',  type=str, default = '')
    return parser.parse_args()


class PdfRotator:
    def __init__(self):
        self.ofile = None
        self.msg = ''
        degree_sign= u'\N{DEGREE SIGN}'
        self.rotOptionList = ('Select Rotation'
                             , '90' + degree_sign + ' Clockwise'
                             , '90' + degree_sign + ' Counter-Clockwise'
                             , '180' + degree_sign + ' (Flip Vertical)')

    def validate_inputs(self, **kwargs):
        """
        Test for valid inputs and return status.
        Check for existence and validity of PDF input file.
        Ensure proper format of rotation input.
        """
        self.args_d = kwargs
        if not os.path.isfile(self.args_d['inpath']):
            ok = False
            self.msg = 'Cannot find input file {0}'.format(self.args_d['inpath'])
        elif not pu.ispdf(self.args_d['inpath']):
            ok = False
            self.msg = '{0} does not look like a valid PDF.'.format(self.args_d['inpath'])
        elif pu.isRestricted(self.args_d['inpath']):
            ok = False
            self.msg = 'File is restricted:\n {0}'.format(self.args_d['inpath'])
        else:
            ok = True
            self.args_d['rotation'] = self.args_d['rotation'].upper()
            self.msg = 'Inputs validated'
        return ok

    def status(self):
        return self.msg

    def get_ofile(self):
        return self.ofile

    def process(self):
        """
        Main processing core.
        Read pages from input PDF, rotate specified pages, write to output.
        """
        with open(self.args_d['inpath'], 'rb') as fr:
            Reader = PyPDF2.PdfFileReader(fr)
            Writer = PyPDF2.PdfFileWriter()
            pagesToRotate = pu.pages(self.args_d['pages'], Reader.numPages)
            indir,infile = os.path.split(self.args_d['inpath'])
            tmpfi = os.path.splitext(infile)[0] + '_rot.pdf'
            self.ofile = os.path.join(indir, tmpfi)
            for pageNum in range(Reader.numPages):
                pageObj = Reader.getPage(pageNum)
                if pageNum in pagesToRotate:
                    if self.args_d['rotation'] == 'CW':
                        pageObj.rotateClockwise(90)
                    elif self.args_d['rotation'] == 'CCW': 
                        pageObj.rotateCounterClockwise(90)
                    elif self.args_d['rotation'] == 'FV': 
                        pageObj.rotateClockwise(180)
                Writer.addPage(pageObj)
            with open(self.ofile, 'wb') as fw:
                Writer.write(fw)
        return True


if __name__ == "__main__":
    args = parse_args()
    R = PdfRotator()
    if not (R.validate_inputs(**vars(args)) and R.process()):
        print(R.status())

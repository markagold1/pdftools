"""
    Retrieve document info from  a PDF file.

    Usage:

    python pdfinfo.py --inpath "path/file"

    Command line options:

        --inpath      Path and file name of input PDF file

    Example: Retrieve and display document info for doc.pdf

              python pdfinfo.py --inpath doc.pdf

"""
import argparse
import PyPDF2 
import os
import pdftools_utils as pu

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inpath',   help='Input path/file',  type=str, default = '')
    return parser.parse_args()


class PdfInfo:
    def __init__(self):
        self.doc_info = str()
        self.msg = ''

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
        else:
            ok = True
            self.msg = 'Inputs validated'
        return ok

    def status(self):
        return self.msg

    def get_doc_info(self):
        return self.doc_info

    def process(self):
        """
        Main processing core.
        Retrieve document info
        """
        with open(self.args_d['inpath'], 'rb') as fr:
            Reader = PyPDF2.PdfFileReader(fr)
            info = Reader.getDocumentInfo()
            self.doc_info = 'Pages: {0}'.format(Reader.numPages) + '\n'
            for item in info:
                self.doc_info += '{0} = {1}'.format(item[1:], info[item]) + '\n'
            self.doc_info = self.doc_info[:-1]
        return True


if __name__ == "__main__":
    args = parse_args()
    P = PdfInfo()
    if not (P.validate_inputs(**vars(args)) and P.process()):
        print(P.status())
    else:
        print(P.doc_info)


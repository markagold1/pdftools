"""
    Reorder spefiied pages of a PDF file.

    Usage:

    python pdfreorder.py --pages "page-spec" --inpath "path/file"

    Command line options:

        --pages       Comma separated ordered list of pages and page ranges
                      Pages not in the list will not be written to the output
                      Thus pdfreorder can be used to extract pages
                      Note: this option must be quoted

        --inpath      Path and file name of input PDF file

    The string "_reoder" is appended to the output file name before the extension.
    The output file is placed in the same directory as the input file

    Examples: 

          Swap the first two pages of 10 page document doc.pdf

              python pdfreorder.py --pages "2, 1, 3-10" doc.pdf


          Reverse the order of pages in 10 page document doc.pdf

              python pdfreorder.py --pages "10-1" doc.pdf


          Extract page 5 of doc.pdf, which has at least 5 pages

              python pdfreorder.py --pages "5" doc.pdf

"""
import argparse
import PyPDF2 
import os
import pdftools_utils as pu

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pages',    help='Pages to rotate',  type=str, default = '1')
    parser.add_argument('-i', '--inpath',   help='Input path/file',  type=str, default = '')
    return parser.parse_args()


class PdfReorderer:
    def __init__(self, **kwargs):
        self.ofile = None
        self.msg = ''

    def validate_inputs(self, **kwargs):
        """
        Test for valid inputs and return status.
        Check for existence and validity of PDF input file.
        """
        self.args_d = kwargs
        if not os.path.isfile(self.args_d['inpath']):
            ok = False
            s = 'Cannot find input file {0}'
            self.msg = s.format(self.args_d['inpath'])
        elif not pu.ispdf(self.args_d['inpath']):
            ok = False
            s = '{0} does not look like a valid PDF.'
            self.msg = s.format(self.args_d['inpath'])
        elif not pu.pages(self.args_d['pages']
                        , pu.getNumPages(self.args_d['inpath'])):
            ok = False
            self.msg = 'No pages to process. Check pages specification.'
        else:
            ok = True
            self.msg = 'Inputs validated'
        return ok

    def status(self):
        return self.msg

    def get_ofile(self):
        return self.ofile

    def process(self):
        """
        Main processing core.
        Read pages from input, reorder, and write specified pages to output.
        """
        ok = True
        with open(self.args_d['inpath'], 'rb') as fr:
            Reader = PyPDF2.PdfFileReader(fr)
            Writer = PyPDF2.PdfFileWriter()
            pagesToReorder = pu.pages(self.args_d['pages'], Reader.numPages)
            if pagesToReorder:
                indir,infile = os.path.split(self.args_d['inpath'])
                tmpfi = os.path.splitext(infile)[0] + '_reorder.pdf'
                self.ofile = os.path.join(indir, tmpfi)
                for pageNum in pagesToReorder:
                    pageObj = Reader.getPage(pageNum)
                    Writer.addPage(pageObj)
                with open(self.ofile, 'wb') as fw:
                    Writer.write(fw)
            else:
                ok = False
                self.msg = 'No pages to process'
        return ok

if __name__ == "__main__":
    args = parse_args()
    R = PdfReorderer(**vars(args))
    if R.validate_inputs(**vars(args)):
        if not R.process():
            print(R.status())
    else:
        print(R.status())

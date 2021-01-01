"""
    Helper utilities for PDFtools
"""
import PyPDF2 

def ispdf(pathfile):
    try:
        with open(pathfile, "rb") as fh:
            Reader = PyPDF2.PdfFileReader(fh)
        return True  # PDF file
    except PyPDF2.utils.PdfReadError:
        return False  # not a PDF file

def getNumPages(pathfile):
    N = 0
    if ispdf(pathfile) and not isRestricted(pathfile):
        with open(pathfile, "rb") as fh:
            Reader = PyPDF2.PdfFileReader(fh)
            N = Reader.numPages
    return N

def pages(pageString, N):
    '''
    Convert page specification into a list of pages
    pageString - comma separated string of pages and page ranges
    N - total number of pages in the document
    '''
    s_l = [item.strip() for item in pageString.split(',')]
    pageRange = list()
    for item in s_l:
        if '-' in item:
            l = item.split('-')
            if len(l) > 2:
                print('More than 1 dash not allowed in page range')
                continue
            if (not l[0].isnumeric()) or (not l[1].isnumeric()):
                print('Non-numeric page not allowed')
                continue
            be = int(l[0]) - 1 # zero-based
            ed = int(l[1]) - 1
            if be <= ed:
                while be <= ed:
                    if be in range(0, N):
                        pageRange.append(be)
                    be += 1
            else:
                while be >= ed:
                    if be in range(0, N):
                        pageRange.append(be)
                    be -= 1
        else:
            if not item.isnumeric():
                print('Non-numeric page not allowed')
                continue
            pg = int(item) - 1 # zero-based
            if pg in range(0, N):
                pageRange.append(pg)
    return pageRange

def isRestricted(pathfile):
    '''
    Return true if file is not decryptable (eg. file is restricted).
    '''
    restricted = False
    with open(pathfile, "rb") as fh:
        Reader = PyPDF2.PdfFileReader(fh)
        if Reader.isEncrypted:
            try:
                Reader.decrypt('')
            except NotImplementedError:
                restricted = True
            except Exception:
                restricted = True
    return restricted

"""
    Tkinter GUI for pdftools

    Usage:   python pdftools.py

    - Combine pdf files
    - Reorder, Rotate, and Extract pages of a pdf file

    Requires:
    1. PyPDF2 version 1.26.0 or newer (pip install PyPDF2)
    2. python version 3.6 or newer (includes tkinter)

"""
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd 
from tkinter import messagebox as mb
from tkinter import scrolledtext as st
import PyPDF2 
import os
import pdfcombine as comb
import pdfreorder as reorder
import pdfrotate as rotator
import pdfinfo as pdfinfo
import pdftools_utils as pu

openString = 'Click to open file '

def get_default_dir():
    ''' 
    Return default directory for file open operations
    First try ~/Downloads
    Else try ~/Documents
    Else try ~
    Else return None
    '''
    if os.name == 'nt':
        # Windows
        import ctypes.wintypes
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value
        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None
                                             , CSIDL_PERSONAL
                                             , None,
                                              SHGFP_TYPE_CURRENT, buf)
        docs = buf.value
        home = os.path.split(docs)[0]
    else:
        # Linux
        home = os.path.expanduser('~')
        docs= os.path.join(home, 'Documents')
    dlds = os.path.join(home, 'Downloads')
    if os.path.isdir(dlds):
        default_dir = dlds
    elif os.path.isdir(docs):
        default_dir = docs
    elif os.path.isdir(home):
        default_dir = home
    else:
        default_dir = None
    return default_dir
      

class PdfTools(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        master.title("PDF Tools")
        self.init_combiner_gui()
        self.init_reorderer_gui()
        self.init_rotator_gui()
        self.init_info_gui()
        self.Co = comb.PdfCombiner()
        self.Re = reorder.PdfReorderer()
        self.Ro = rotator.PdfRotator()
        self.Pi = pdfinfo.PdfInfo()

        # Setup notebook, style
        customed_style = ttk.Style()
        customed_style.configure('PDFtools.TNotebook.Tab'
                                , padding=[2, 2]
                                , font=('TkDefaultFont', 10, "bold"))
        self.notebook = ttk.Notebook(master, style='PDFtools.TNotebook')
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Combine")
        self.notebook.add(self.tab2, text="Reorder")
        self.notebook.add(self.tab3, text="Rotate")
        self.notebook.add(self.tab4, text="Info")
        self.notebook.grid(row=0, column=0)

        # Populate widgets
        self.create_widgets_tab1()
        self.create_widgets_tab2()
        self.create_widgets_tab3()
        self.create_widgets_tab4()

    def create_widgets_tab1(self):
        ''''
        Place widgets for Combiner applet
        '''
        self.mainframe = tk.Frame(self.tab1)
        self.mainframe.grid(row=3, column=0, ipadx=40)

        # File selection buttons
        self.FileButton1 = tk.Button(self.tab1
                                    , text=openString + '1'
                                    , activebackground='red'
                                    , command=self.setfile1)
        self.FileButton1.config(font=("TkDefaultFont", 10))
        self.FileButton1.grid(row=0, column=0, sticky='NSEW')
        self.FileButton2 = tk.Button(self.tab1
                                    , text=openString + '2'
                                    , activebackground='red'
                                    , command=self.setfile2)
        self.FileButton2.config(font=("TkDefaultFont", 10))
        self.FileButton2.grid(row=1, column=0, sticky='NSEW')

        # Overwrite checkbox
        self.ClobberButton = tk.Checkbutton(self.tab1
                                          , text="Overwrite File 1"
                                          , variable=self.overwrite1)
        self.ClobberButton.grid(row=2, column=0)

        # Rotation labels and dropdowns
        self.rotlabel1 = tk.Label(self.mainframe,text = 'Rotate file 1: ')
        self.rotlabel1.config(font=("TkDefaultFont", 10))
        self.rotlabel1.grid(row=3, column=0, ipadx=10, sticky="W")
        self.rotlabel2 = tk.Label(self.mainframe,text = 'Rotate file 2: ')
        self.rotlabel2.config(font=("TkDefaultFont", 10))
        self.rotlabel2.grid(row=4, column=0, ipadx=10, sticky="W")

        self.v1 = tk.StringVar()
        self.v1.set(self.Co.rotOptionList[0])
        self.v2 = tk.StringVar()
        self.v2.set(self.Co.rotOptionList[0])
        self.om1 = tk.OptionMenu(self.mainframe
                               , self.v1
                               , *self.Co.rotOptionList
                               , command=lambda value: self.setrot(value, 0))
        self.om1.grid(row=3, column=1, ipadx=10)
        self.om2 = tk.OptionMenu(self.mainframe
                               , self.v2
                               , *self.Co.rotOptionList
                               , command=lambda value: self.setrot(value, 1))
        self.om2.grid(row=4, column=1, ipadx=10)

        # Combine! button
        self.CombineButton = tk.Button(self.tab1
                                     , text='Combine!'
                                     , activebackground='red'
                                     , bg='green', fg='white'
                                     , command=self.do_combine)
        self.CombineButton.config(font=("TkDefaultFont", 12, "bold"))
        self.CombineButton.grid(row=5, column=0, sticky='NESW', columnspan=5)

    def create_widgets_tab2(self):
        ''''
        Place widgets for Reorder applet
        '''
        # File selection button
        self.FileButton3 = tk.Button(self.tab2
                                   , text=openString
                                   , activebackground='red'
                                   , command=self.setfile3)
        self.FileButton3.config(font=("TkDefaultFont", 12))
        self.FileButton3.pack(side='top', fill=tk.X, expand=True)

        # Label to dispay number of pages in document
        self.npagelabel1 = tk.Label(self.tab2, text = ' ')
        self.npagelabel1.config(font=("TkDefaultFont", 10))
        self.npagelabel1.pack(side='top', fill=tk.X, expand=True)

        # Label the text enty box
        self.rotlabel4 = tk.Label(self.tab2
                                , text = 'Pages to reorder (eg. 1-3,5,9,...):')
        self.rotlabel4.config(font=("TkDefaultFont", 12))
        self.rotlabel4.pack(fill="both", expand=True)

        # Text enty box
        self.reorder_pages = ''
        self.entry1 = tk.Entry(self.tab2, textvariable=self.reorder_pages)
        self.entry1.config(font=("TkDefaultFont", 12))
        self.entry1.pack(fill=tk.X, expand=True)

        # Reorder! button
        self.ReorderButton = tk.Button(self.tab2
                                     , text='Reorder!'
                                     , activebackground='red'
                                     , bg='green', fg='white'
                                     , command=self.do_reorder)
        self.ReorderButton.config(font=("TkDefaultFont", 12, "bold"))
        self.ReorderButton.pack(side="bottom"
                              , fill=tk.X
                              , expand=True)

    def create_widgets_tab3(self):
        ''''
        Place widgets for Rotator applet
        '''
        # File selection button
        self.FileButton4 = tk.Button(self.tab3
                                   , text=openString
                                   , activebackground='red'
                                   , command=self.setfile4)
        self.FileButton4.config(font=("TkDefaultFont", 12))
        self.FileButton4.pack(side='top', fill='both', expand=True)

        # Label to dispay number of pages in document
        self.npagelabel2 = tk.Label(self.tab3, text = ' ')
        self.npagelabel2.config(font=("TkDefaultFont", 10))
        self.npagelabel2.pack(fill='both', expand=True)

        # Label for the text enty box
        self.rotlabel5 = tk.Label(self.tab3
                                , text = 'Pages to rotate (eg. 1-3,5,9,...):')
        self.rotlabel5.config(font=("TkDefaultFont", 12))
        self.rotlabel5.pack(fill="both", expand=True)

        # Text enty box
        self.rotate_pages = ''
        self.entry2 = tk.Entry(self.tab3, textvariable=self.rotate_pages)
        self.entry2.config(font=("TkDefaultFont", 12))
        self.entry2.pack(fill='both', expand=True)

        # Rotation dropdown
        self.v3 = tk.StringVar()
        self.v3.set(self.Ro.rotOptionList[0])
        self.om3 = tk.OptionMenu(self.tab3
                               , self.v3
                               , *self.Ro.rotOptionList
                               , command=self.setpagerot)
        self.om3.config(font=("TkDefaultFont", 12))
        self.om3.pack(side='top', fill=tk.X, expand=True)

        # Rotate! button
        self.RotateButton = tk.Button(self.tab3
                                    , text='Rotate!'
                                    , activebackground='red'
                                    , bg='green', fg='white'
                                    , command=self.do_rotate)
        self.RotateButton.config(font=("TkDefaultFont", 12, "bold"))
        self.RotateButton.pack(side="bottom"
                             , fill=tk.X
                             , expand=True)

    def create_widgets_tab4(self):
        ''''
        Place widgets for Info applet
        '''
        # File selection button
        self.FileButton5 = tk.Button(self.tab4
                                   , text=openString
                                   , activebackground='red'
                                   , command=self.setfile5)
        self.FileButton5.config(font=("TkDefaultFont", 10))
        self.FileButton5.pack(side='top', fill='both', expand=True)

        # Scrolled text box
        self.textArea1 = st.ScrolledText(self.tab4
                                       , wrap = tk.WORD
                                       , width = 27
                                       , height = 9
                                       , font = ("TkDefaultFont", 10))
        self.textArea1.pack(side='top', fill=tk.X, expand=True)

    def init_combiner_gui(self):
        self.file1 = None
        self.file2 = None
        self.ofile = None
        self.defdir1 = get_default_dir()
        self.defdir2 = get_default_dir()
        self.overwrite1 = tk.BooleanVar()
        self.rotation = ['NONE', 'NONE']   # rotation flag for file1, file2

    def init_reorderer_gui(self):
        self.defdir3 = get_default_dir()

    def init_rotator_gui(self):
        self.defdir4 = get_default_dir()
        self.rotate = 'NONE'

    def init_info_gui(self):
        self.defdir5 = get_default_dir()
        self.mru_file = None
        self.mru_dir = self.defdir5

    def setrot(self, choice, value):
        '''
        Configure rotation used by PDF combiner
        '''
        if choice == self.Co.rotOptionList[1]:
            self.rotation[value] = 'CW' 
        elif choice == self.Co.rotOptionList[2]:
            self.rotation[value] = 'CCW'
        elif choice == self.Co.rotOptionList[3]:
            self.rotation[value] = 'FV'
        else:
            self.rotation[value] = 'NONE'

    def setpagerot(self, choice):
        '''
        Configure rotation used by PDF rotator
        '''
        if choice == self.Ro.rotOptionList[1]:
            self.rotate = 'CW' 
        elif choice == self.Ro.rotOptionList[2]:
            self.rotate = 'CCW'
        elif choice == self.Ro.rotOptionList[3]:
            self.rotate = 'FV'
        else:
            self.rotate = 'NONE'

    def setfile1(self):
        '''
        Setup file 1 input for PDF combiner
        '''
        self.file1= fd.askopenfilename(initialdir=self.defdir1, 
          filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if self.file1:
            self.FileButton1["text"] = self.file1
            self.FileButton1["bg"] = "yellow"
            self.defdir1 = os.path.split(self.file1)[0]
            self.updateMostRecentFile(self.file1)
            print("file 1 is " + self.file1)

    def setfile2(self):
        '''
        Setup file 2 input for PDF combiner
        '''
        self.file2= fd.askopenfilename(initialdir=self.defdir2,
          filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if self.file2:
            self.FileButton2["text"] = self.file2
            self.FileButton2["bg"] = "yellow"
            self.defdir2 = os.path.split(self.file2)[0]
            self.updateMostRecentFile(self.file2)
            print("file 2 is " + self.file2)

    def setfile3(self):
        '''
        Setup file input for PDF reorderer
        '''
        self.file3= fd.askopenfilename(initialdir=self.defdir3,
          filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if self.file3:
            self.FileButton3["text"] = self.file3
            self.FileButton3["bg"] = "yellow"
            self.defdir3 = os.path.split(self.file3)[0]
            N = pu.getNumPages(self.file3)
            displayPages= 'Document contains {0} pages'.format(N)
            self.npagelabel1["text"] = displayPages
            self.updateMostRecentFile(self.file2)
            print("file 3 is " + self.file3)

    def setfile4(self):
        '''
        Setup file input for PDF rotator
        '''
        self.file4= fd.askopenfilename(initialdir=self.defdir4,
          filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if self.file4:
            self.FileButton4["text"] = self.file4
            self.FileButton4["bg"] = "yellow"
            self.defdir4 = os.path.split(self.file4)[0]
            N = pu.getNumPages(self.file4)
            displayPages= 'Document contains {0} pages'.format(N)
            self.npagelabel2["text"] = displayPages
            self.updateMostRecentFile(self.file4)
            print("file 4 is " + self.file4)

    def setfile5(self):
        '''
        Setup file input for PDF info
        '''
        self.file5= fd.askopenfilename(initialdir=self.mru_dir,
          filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if self.file5:
            self.updateMostRecentFile(self.file5)
            print("file 5 is " + self.file5)

    def updateMostRecentFile(self, pathfilename):
        '''
        Update the most recently selected file
        for displaying file info
        '''
        self.mru_file = pathfilename
        self.mru_dir = os.path.split(self.mru_file)[0]
        # Update button label on the Info tab
        self.FileButton5["text"] = pathfilename
        self.FileButton5["bg"] = "yellow"
        self.defdir5 = os.path.split(pathfilename)[0]
        self.do_info()

    def set_reorder_text(self, dummy):
        '''
        Read pages text box in the PDF reorderer
        '''
        self.reorder_pages = self.entry1.get()
        print("entry1: entered text is " + self.reorder_pages)

    def set_rotate_text(self, dummy):
        '''
        Read pages text box in the PDF rotator
        '''
        self.rotate_pages = self.entry2.get()
        print("entry2: entered text is " + self.rotate_pages)

    def do_combine(self):
        '''
        Setup inputs and call PDF combiner
        '''
        args = {'inpath1' : self.file1
              , 'inpath2' : self.file2
              , 'rotate1' : self.rotation[0]
              , 'rotate2' : self.rotation[1]
              , 'clobber' : self.overwrite1.get()}
        if self.Co.validate_inputs(**args) and self.Co.process():
            mb.showinfo(title=None, message="Created " + self.Co.get_ofile())
        else:
            mb.showinfo(title=None, message=self.Co.status())
            print(self.Co.status())

    def do_reorder(self):
        '''
        Setup inputs and call PDF reorderer
        '''
        self.set_reorder_text('')
        args = {'inpath' : self.file3,
                'pages'  : self.reorder_pages}
        if self.Re.validate_inputs(**args) and self.Re.process():
            mb.showinfo(title=None, message="Created " + self.Re.get_ofile())
        else:
            mb.showinfo(title=None, message=self.Re.status())
            print(self.Re.status())

    def do_rotate(self):
        '''
        Setup inputs and call PDF rotator
        '''
        self.set_rotate_text('')
        args = {'inpath'   : self.file4,
                'pages'    : self.rotate_pages,
                'rotation' : self.rotate}
        if self.Ro.validate_inputs(**args) and self.Ro.process():
            mb.showinfo(title=None, message="Created " + self.Ro.get_ofile())
        else:
            mb.showinfo(title=None, message=self.Ro.status())
            print(self.Ro.status())

    def do_info(self):
        '''
        Setup inputs and call PDF file info
        '''
        args = {'inpath' : self.mru_file,}
        if self.Pi.validate_inputs(**args) and self.Pi.process():
            self.textArea1.configure(state ='normal')
            self.textArea1.delete('1.0', tk.END)
            self.textArea1.insert(tk.INSERT, self.Pi.get_doc_info())
            self.textArea1.configure(state ='disabled')
        else:
            mb.showinfo(title=None, message=self.Pi.status())
            print(self.Pi.status())


root = tk.Tk()
P = PdfTools(master=root)
P.mainloop()

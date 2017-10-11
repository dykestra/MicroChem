"""
Main Script to launch Teacher Interface GUI
"""

import os
from tkinter import PhotoImage, ttk, LEFT, RIGHT
from tkinter.ttk import *
from ttkthemes import themed_tk as tk


class TeacherInterfaceGUI:
    """ Main GUI class """

    CURRENT_DIR = os.path.dirname(__file__)
    IMAGE_DIR = os.path.join(CURRENT_DIR,'images')

    def __init__(self, master):
        self.master = master
        master.title("Micro:Chem")

        self.add_styling()

        self.add_heading_area(master)

        nb = ttk.Notebook(master)
        self.add_main_page(nb)
        self.add_options_page(nb)
        self.add_scenarios_page(nb)
        nb.pack(expand=1, fill="both")

    def add_styling(self):
        """Add custom styling here"""
        style = ttk.Style()
        style.configure("BW.TLabel", foreground="white", background="black") #random example
        style.configure("Color.TFrame", background="#334353")
        style.configure("Black.TFrame", background="black")

    def add_heading_area(self, master):
        """Header area with logo"""
        self.header_im = PhotoImage(file=os.path.join(self.IMAGE_DIR, 'microchem_logo.png'))
        self.header_im = self.header_im.subsample(4,4)
        self.heading = ttk.Label(master, image=self.header_im)
        self.heading.pack()

    def add_main_page(self, nb):   
        """ Main tab has 
                - list of ElementBits and current element/compounds
                - information panel about selected elementbit
                - panel showing current reaction(s) 
                - panel with description for current scenario? """

        self.main_page = ttk.Frame(nb)

        self.add_element_bit_list_frame()
        self.add_info_frame()

        nb.add(self.main_page, text='Main')
   
    def add_element_bit_list_frame(self):
        """ Frame has list of ElementBits and their current element/compounds """
        element_bit_list_frame = ttk.Frame(self.main_page, style="Color.TFrame")
        element_bit_list_frame.pack(side=LEFT, fill="both", expand="true")

    def add_info_frame(self):
        """ Frame contains information about the element/compound on whichever ElementBit has been selected in the list """
        info_frame = ttk.Frame(self.main_page, style="Black.TFrame")
        info_frame.pack(side=RIGHT, fill="both", expand="true")

    def add_options_page(self, nb):
        """ Options tab has
                - list of fields to include in information panel """

        self.options_page = ttk.Frame(nb, width=1000, height=600)
        nb.add(self.options_page, text='Options')

    def add_scenarios_page(self, nb):
        """ Load Scenarios tab has
                - list of scenarios to choose from
                - description panel for selected scenario
                - button to load selected scenario """

        self.scenarios_page = ttk.Frame(nb, width=1000, height=600)
        nb.add(self.scenarios_page, text="Load Scenario")


root = tk.ThemedTk()
root.set_theme("arc")
root.minsize(1024,648)
gui = TeacherInterfaceGUI(root)
root.mainloop()

"""
Main Script to launch Teacher Interface GUI
"""

import os
from tkinter import PhotoImage, ttk, LEFT, RIGHT, TOP, BOTTOM, CENTER, StringVar
from ttkthemes import themed_tk as tk


class TeacherInterfaceGUI:
    """ Main GUI class """

    CURRENT_DIR = os.path.dirname(__file__)
    IMAGE_DIR = os.path.join(CURRENT_DIR, 'images')

    def __init__(self, master):
        # customize root object
        master.title("Micro:Chem")
        master.set_theme("arc")
        master.minsize(1024, 648)
        master.configure(background='#f5f6f7')
        self.master = master

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
        style.configure("Groove.TFrame", relief="groove")

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
        self.add_reaction_frame()
        self.add_info_frame()

        nb.add(self.main_page, text='Main')
   
    def add_element_bit_list_frame(self):
        """ Frame contains
            - list of ElementBits and their current element/compounds """
        self.element_bit_list_frame = ttk.Frame(self.main_page, style="Groove.TFrame")

        self.element_bit_list_frame_label = ttk.Label(self.element_bit_list_frame, text="ElementBit List")
        self.element_bit_list_frame_label.pack(pady=10)

        self.element_bit_tree = ttk.Treeview(self.element_bit_list_frame, selectmode="browse")
        self.element_bit_tree['show'] = 'headings' # hide empty first column
        self.element_bit_tree['columns'] = ('id', 'element')
        
        self.element_bit_tree.column('id', width=100)
        self.element_bit_tree.heading('id', text='ElementBit ID')
        self.element_bit_tree.column('element', width=150)
        self.element_bit_tree.heading('element', text='Element/Compound')

        for x in range(0,10):
            self.element_bit_tree.insert('','end', values=(str(x) + ' blah'))

        self.element_bit_tree.pack()
        self.element_bit_tree.bind("<<TreeviewSelect>>", self.on_element_bit_tree_select)

        self.element_bit_list_frame.pack(side=LEFT,ipadx=10, fill="both", expand="false")

    def update_element_bit_list(self, new_list):
        """ update element bit list with new values """
        # self.element_bit_tree.insert()

    def on_element_bit_tree_select(self, event):
        """ Get values from selection and update info frame """
        selection = self.element_bit_tree.selection()[0]
        item = self.element_bit_tree.item(selection)
        self.info_frame_update(item['values'])

    def add_reaction_frame(self):
        """ Frame contains 
            - information about the current ongoing reaction(s)
            - log of past reactions? """
        self.reaction_frame = ttk.Frame(self.main_page, style="Groove.TFrame")

        self.reaction_frame_label = ttk.Label(self.reaction_frame, text="Reaction Panel")
        self.reaction_frame_label.pack(pady=10)

        self.current_reactions_frame = ttk.Frame(self.reaction_frame)
        self.current_reactions_frame.pack(padx=5, side=TOP, fill="both", expand="true")

        self.reaction_log_frame = ttk.Frame(self.reaction_frame, height="250", style="Groove.TFrame")
        self.reaction_log_frame_label = ttk.Label(self.reaction_log_frame, text="Reaction Log")
        self.reaction_log_frame_label.pack(pady=10)
        self.reaction_log_frame.pack(padx=5, pady=5, side=BOTTOM, fill="both", expand="false")
        self.reaction_log_frame.pack_propagate(0)

        self.reaction_frame.pack(side=LEFT, fill="both", expand="true")

    def add_info_frame(self):
        """ Frame contains 
            - information about the element/compound on whichever ElementBit has been selected in the list
            - description of current scenario? """
        self.info_frame = ttk.Frame(self.main_page, style="Groove.TFrame")

        self.info_frame_label = ttk.Label(self.info_frame, text="Information Panel")
        self.info_frame_label.pack(pady=10)

        selected_element_label = ttk.Label(self.info_frame, text="Selected Element")
        selected_element_label.pack()

        self.selected_element_string = StringVar()
        selected_element_box = ttk.Entry(self.info_frame, textvariable=self.selected_element_string, state="readonly")
        selected_element_box.pack()

        self.info_frame.pack(side=RIGHT, fill="both", expand="true")

    def info_frame_update(self, selection):
        self.selected_element_string.set(selection)

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
gui = TeacherInterfaceGUI(root)
root.mainloop()

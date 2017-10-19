"""
Main Script to launch Teacher Interface GUI
"""

import os
from tkinter import PhotoImage, ttk, LEFT, RIGHT, TOP, BOTTOM, CENTER, E, Message, StringVar
from ttkthemes import themed_tk as tk
import csv
from collections import OrderedDict
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from desktop import Scenario as sc
from threading import Thread


class TeacherInterfaceGUI:
    """ Main GUI class """

    CURRENT_DIR = os.path.dirname(__file__)
    IMAGE_DIR = os.path.join(CURRENT_DIR, 'images')
    SCENARIOS_DIR = os.path.join(CURRENT_DIR, 'scenarios')

    INFORMATION_FILE = os.path.join(CURRENT_DIR, 'informationDBv2.csv')
    SCENARIOS_FILE = os.path.join(SCENARIOS_DIR, 'scenarios.csv')

    scenario_obj = None

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
        style.configure('Log.Treeview', rowheight=30)

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
        self.element_bit_tree['columns'] = ('id', 'element', 'valence')
        
        self.element_bit_tree.column('id', width=100)
        self.element_bit_tree.heading('id', text='ElementBit ID')
        self.element_bit_tree.column('element', width=150)
        self.element_bit_tree.heading('element', text='Element/Compound')
        self.element_bit_tree.column('valence', width=50)
        self.element_bit_tree.heading('valence', text='Valence')

        self.element_bit_tree.pack()
        self.element_bit_tree.bind("<<TreeviewSelect>>", self.on_element_bit_tree_select)

        self.element_bit_list_frame.pack(side=LEFT,ipadx=10, fill="both", expand="false")

    def update_element_bit_list(self, new_list):
        """ update element bit list with new values stored in numpy ndarray
            array items are expected to have 'aliasID', 'chem_symbol' and 'valence' """

        # clear current tree
        for row in self.element_bit_tree.get_children():
            self.element_bit_tree.delete(row)

        # repopulate tree
        for item in new_list:
            item_values = " ".join([item['aliasID'].decode('UTF-8'), item['chem_symbol'].decode('UTF-8'),
                                    item['valence'].decode('UTF-8')])
            self.element_bit_tree.insert('', 'end', values=item_values)

    def on_element_bit_tree_select(self, event):
        """ Get values from selection and update info frame """
        selection = self.element_bit_tree.selection()[0]
        item = self.element_bit_tree.item(selection)
        self.info_frame_update(item['values'][1])  # send chemical symbol to info panel

    def add_reaction_frame(self):
        """ Frame contains 
            - information about the current ongoing reaction(s)
            - log of past reactions? """
        self.reaction_frame = ttk.Frame(self.main_page, width=400, style="Groove.TFrame")

        self.reaction_frame_label = ttk.Label(self.reaction_frame, text="Reaction Panel")
        self.reaction_frame_label.pack(pady=10)

        self.current_reactions_frame = ttk.Frame(self.reaction_frame)
        self.current_reaction_label_string = StringVar()
        self.current_reaction_label_string.set('')
        self.current_reaction_label = Message(self.current_reactions_frame,
                                                  textvariable=self.current_reaction_label_string,
                                                  background="white", relief="raised", foreground="#535d6d", aspect=700)
        self.current_reaction_label.pack(ipady=10, padx=1, fill="x")
        self.current_reactions_frame.pack(padx=5, side=TOP, fill="both", expand="true")

        self.reaction_log_frame = ttk.Frame(self.reaction_frame, height="250", style="Groove.TFrame")
        self.reaction_log_frame_label = ttk.Label(self.reaction_log_frame, text="Reaction Log")
        self.reaction_log_frame_label.pack(pady=10)

        self.reaction_log_tree = ttk.Treeview(self.reaction_log_frame, selectmode="browse", style="Log.Treeview")
        self.reaction_log_tree.pack(fill="x", padx=10, ipady=15)

        self.reaction_log_frame.pack(padx=5, pady=5, side=BOTTOM, fill="both", expand="false")
        self.reaction_log_frame.pack_propagate(0)

        self.reaction_frame.pack(side=LEFT, fill="both", expand="false")
        self.reaction_frame.pack_propagate(0)

    def trigger_reaction(self, elements):
        """ Triggers a reaction which is displayed in the reaction frame """

        # add previous reaction to log
        old_reaction = self.current_reaction_label_string.get()
        if old_reaction != '':
            self.add_to_log(old_reaction)

        # update label to current reaction
        reaction_str = " + ".join([e['prev_symbol'].decode('UTF-8') for e in elements])
        reaction_str += " => "
        reaction_str += elements[0]['chem_symbol'].decode('UTF-8')

        print(reaction_str)
        self.current_reaction_label_string.set(reaction_str)

    def add_to_log(self, old_reaction):
        """ add old_reaction to the reaction log """

        self.reaction_log_tree.insert('', '0', text=old_reaction)


    def add_info_frame(self):
        """ Frame contains 
            - information about the element/compound on whichever ElementBit has been selected in the list
            - description of current scenario? """
        self.info_frame = ttk.Frame(self.main_page, style="Groove.TFrame")

        self.info_frame_label = ttk.Label(self.info_frame, text="Information Panel")
        self.info_frame_label.pack(pady=10)

        self.read_info_from_file()

        self.info_labels = []
        self.info_entries = []
        self.info_vars = []

        self.info_frame.pack(side=RIGHT, fill="both", expand="true")

    def read_info_from_file(self):
        """ reads the whole information table from file into memory"""
        self.info_table = []
        with open(self.INFORMATION_FILE, 'rt') as info_File:
            reader = csv.DictReader(info_File)

            for row in reader:
                self.info_table.append(OrderedDict(sorted(row.items(),
                                                key=lambda item: reader.fieldnames.index(item[0]))))

    def info_frame_update(self, selected_symbol):
        """ update info frame to display info about selected element/compound """

        # get relevant info from table
        info_results = [x for x in self.info_table if x['Symbol']==selected_symbol]
        res = info_results[0]

        # clear info from previous selection
        for j in range(0,len(self.info_labels)):
            self.info_labels[j].pack_forget()
            self.info_entries[j].pack_forget()

        self.info_labels.clear()
        self.info_entries.clear()

        # make labels and entries for new info
        for key, value in res.items():
            label = ttk.Label(self.info_frame, text=key)
            self.info_labels.append(label)
            label.pack()

            info = Message(self.info_frame, text=value, aspect=500, background="white", relief="raised", fg="#535d6d")
            self.info_entries.append(info)
            info.pack(ipadx=5, ipady=5, pady=10)

    def add_options_page(self, nb):
        """ Options tab has
                - list of fields to include in information panel """

        self.options_page = ttk.Frame(nb, width=1000, height=600)
        nb.add(self.options_page, text='Options')

    def add_scenarios_page(self, nb):
        """ Load Scenarios tab has
                - list of scenarios to choose from
                - button to load selected scenario """

        self.scenarios_page = ttk.Frame(nb, width=1000, height=600)

        self.scenarios_tree = ttk.Treeview(self.scenarios_page, show='headings', columns=('name', 'desc', 'nbits'),
                                           selectmode="browse")

        self.scenarios_tree.column('name', width=100)
        self.scenarios_tree.heading('name', text='Scenario')
        self.scenarios_tree.column('desc', width=400)
        self.scenarios_tree.heading('desc', text='Description')
        self.scenarios_tree.column('nbits', width=120)
        self.scenarios_tree.heading('nbits', text='No. ElementBits')

        self.read_scenarios_from_file()

        self.scenarios_tree.pack(pady=20)
        self.scenarios_tree.bind("<<TreeviewSelect>>", self.on_scenario_tree_select)

        self.load_scenario_button = ttk.Button(self.scenarios_page, command=self.load_scenario, text="Load Scenario",
                                               state="disabled")
        self.load_scenario_button.pack()

        nb.add(self.scenarios_page, text="Load Scenario")

    def read_scenarios_from_file(self):
        """ reads the list of scenarios from file into a list of ordered dicts"""
        self.scenarios_list = []
        with open(self.SCENARIOS_FILE, 'rt') as scenarios_file:
            reader = csv.DictReader(scenarios_file)

            for row in reader:
                self.scenarios_list.append(OrderedDict(sorted(row.items(),
                                                key=lambda item: reader.fieldnames.index(item[0]))))

        for s in self.scenarios_list:
            self.scenarios_tree.insert('', 'end', text=s['File'],
                                       values=([s['Name'], s['Description'], s['No. ElementBits']]))

    def on_scenario_tree_select(self, event):
        """ set currently selected scenario and enable load scenario button"""

        selection = self.scenarios_tree.selection()[0]
        self.scenario_file = os.path.join(self.SCENARIOS_DIR, self.scenarios_tree.item(selection)['text'])
        self.load_scenario_button.state(['!disabled'])

    def load_scenario(self):
        """ load scenario from file """
        if self.scenario_obj:
            self.scenario_obj.force_quit_main_loop()
            self.thread.join()
        print(self.scenario_file)
        self.scenario_obj = sc.Scenario(self, scenario_file=self.scenario_file)
        self.thread = Thread(target=self.scenario_obj.main_loop, kwargs=dict(master=self))
        self.thread.setDaemon(True)
        self.thread.start()




root = tk.ThemedTk()
gui = TeacherInterfaceGUI(root)
root.mainloop()

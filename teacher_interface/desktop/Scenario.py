import serial
import numpy as np
from pathlib import Path
import os
import time


class Scenario:
    
    # the port will depend on your computer
    # for a raspberry pi it will probably be /dev/ttyACM0
    PORT = "NO PORT"
    if (os.name == "posix"):
        PORT = "/dev/ttyACM0"
    if (os.name == "nt"):
        PORT = "COM3"

    BAUD = 115200

    s = serial.Serial(PORT)
    s.baudrate = BAUD
    s.timeout = 0.2 # read timeout of 0.5 seconds
    s.parity = serial.PARITY_NONE
    s.databits = serial.EIGHTBITS
    s.stopbits = serial.STOPBITS_ONE

    # "MACROS"
    IDALIAS = 0
    ELEMENTREQ = 1
    REACTION_CHECK = 2

    next_ele = b'H'  # TEMP DEF - make it relative to the self.master_table
    next_val = b'+1'  # TEMP

    break_loop = False

    n_elements = 10
    max_ttl = 500 #Was 100

    def __init__(self, master, scenario_file):

        # DATA SETUP
        # --------------------------------------------------
        ## Create master table
        # load a scenario file, if any
        # CURRENT_DIR = Path('.')
        CURRENT_DIR = os.path.dirname(__file__)
        print (CURRENT_DIR)
        scen_file = Path(scenario_file)
        # Create master table
        if scen_file.exists():
            self.master_table = np.genfromtxt(scenario_file, delimiter=",", \
                                         dtype=[('aliasID', 'S2'),('serialNo', 'i4'),\
                                                ('chem_symbol', 'S10'), ('valence', 'S2'), ('prev_symbol', 'S10'), ('prev_valence', 'S2')])
        else:
            self.master_table = np.array([(b'aa',-1,b'',b'')],\
                                     dtype=[('aliasID', 'S2'),('serialNo', 'i4'),\
                                            ('chem_symbol', 'S10'), ('valence', 'S2'), ('prev_symbol', 'S10'), ('prev_valence', 'S2')])

        master.update_element_bit_list(self.master_table)

        ## Create the reaction table
        self.reaction_table = np.genfromtxt(os.path.join(CURRENT_DIR, 'elementsDB-v3.1.csv'), delimiter=";", dtype=None)
        #self.reaction_table = np.genfromtxt(os.path.join(CURRENT_DIR, 'elementsDB-v4final.csv'), delimiter=",", dtype=None)
        
        # Collision list setup
        # --------------------------------------------------
        self.MB_collision_list = [[] for x in range(self.n_elements)]
        
        ## Ready message
        print("Ready.")

        """        
        #TESTING
        SERIAL = b'ad'
        if SERIAL in self.master_table["aliasID"]:
            i, = np.where(self.master_table["aliasID"]==SERIAL)
            send_alias = self.master_table["chem_symbol"][i][0]
        else:
            i, = np.where(self.master_table["serialNo"] == -1)
            send_alias = self.master_table["aliasID"][i][0]
        print("Alias is", send_alias)

        #new_alias = bytes([self.master_table["aliasID"][-1][0],self.master_table["aliasID"][-1][1]+1])
        #print("Last alias is", new_alias)

        ##STRING TO BYTES SAMPLE -> "str.encode()" and ".decode()"
        #string = "text"
        #print(string)
        #bytestr = str.encode(string)
        #print(bytestr)
        #print(bytestr.decode())
        """
        
    # --------------------------------------------------
    # Function to exit the main loop
    # --------------------------------------------------
    def force_quit_main_loop(self):
        self.break_loop = True
        print("BREAKING LOOP")

    # --------------------------------------------------
    # Function to add to the list of collisions
    # --------------------------------------------------
    def add_to_collision_list(self,  to_be_added  ):
        for i in range(len(self.MB_collision_list)):
            if not self.MB_collision_list[i]:
                self.MB_collision_list[i] = [to_be_added, 0]
                break
            else:
                if i == len(self.MB_collision_list)-1:
                    self.MB_collision_list.append([to_be_added, 0])

    # --------------------------------------------------
    # Function to search the collision list
    # --------------------------------------------------
    def search_collision_list(self, searchable ):
        for sublist in self.MB_collision_list:
            if sublist: # if sublist is not empty
                if sublist[0] == searchable:
                    return True

    # --------------------------------------------------
    # Function to search for "reverse message" in the collision list
    # returns true if exists in the list
    # --------------------------------------------------
    def is_reverse_in_collision_list(self, searchable ):
        reverse = searchable[2:4] + searchable[0:2]
        for sublist in self.MB_collision_list:
            if sublist: # if sublist is not empty
                if sublist[0] == reverse:
                    return True


    # --------------------------------------------------
    # Function to iterate time alive in all messages
    # and remove messages that have exceeded max time
    # --------------------------------------------------
    def iterate_time_in_collision_list(self, max_ttl = 1024 ):
        for sublist in self.MB_collision_list:
            if sublist: # if sublist is not empty
                if sublist[1] == max_ttl:
                    del sublist[:]
                else:
                    sublist[1] = sublist[1] + 1

    
    #==================================================
    # The main loop
    #==================================================
    def main_loop(self, master):
        if not self.s.is_open:
            self.s.open()
                
        while not self.break_loop:
            try:
                #read a line from the microbit, decode it and
                # strip the whitespace at the end
                data = self.s.readline().rstrip()
                if data:
                    #data_str = data.decode()
                    print(data)

                    #split the data
                    data_s = data.split(b":")

                    # Split the data to comm_type, ID, and message
                    # data_s[0] is comm_type, data_s[1] is ID, data_s[2] is the message
                    comm_type = int((data_s[0]).decode())
                    print("Comm type is:", comm_type)
                    id_in = data_s[1]
                    print("id_in", id_in)
                    message = data_s[2] ##SPLIT this message to parts with message.split(b"#")

                    # Message handler
                    # ID alias creation
                    if comm_type == self.IDALIAS:
                        SERIAL = id_in
                        # Check the table for the serial, and allocate an ID number
                        if SERIAL in self.master_table["serialNo"]:
                            i, = np.where(self.master_table["serialNo"] == SERIAL)
                            send_alias = self.master_table["aliasID"][i][0]
                        else:
                            if -1 in self.master_table["serialNo"]:
                                i, = np.where(self.master_table["serialNo"] == -1)
                                send_alias = self.master_table["aliasID"][i][0]
                            else: # if no available row exists
                                new_alias = bytes([self.master_table["aliasID"][-1][0],
                                                   self.master_table["aliasID"][-1][1]+1])
                                np.append(self.master_table, [new_alias, SERIAL, self.next_ele, self.next_val])
                                # HAVE TO KEEP TRACK OF HOW MANY ELEMENTS HAVE BEEN RECYCLED!
                        print(send_alias)
                        self.s.write(b'#'+SERIAL+b'#'+send_alias+b'#\n')
                        # HAVE TO SEND THE SERIAL NUMBER AS WELL

                    # Element requests
                    elif comm_type == self.ELEMENTREQ:
                        # Find "id_in" in the master table, and pick the element given to it, if any
                        i, = np.where(self.master_table["aliasID"] == id_in)
                        if i.size:
                            send_symbol = self.master_table["chem_symbol"][i][0]
                            send_valence = self.master_table["valence"][i][0]
                            print(send_valence + send_symbol + b'\n')
                            self.s.write(send_valence + send_symbol + b'\n')
                    # Reaction messages (collisions)
                    elif comm_type == self.REACTION_CHECK:
                        message_s = message.split(b"#")
                        id_a = id_in
                        id_b = message#_s[0]#message_s[1]
                        print("id_a:", id_a)
                        print("id_b:", id_b)
                        pair = id_a + id_b
                        pair_str = pair.decode()
                        # Add to collision list
                        self.add_to_collision_list( pair_str )

                        # Only process if reverse is already in collision list
                        if self.is_reverse_in_collision_list( pair_str ):
                            print("Both collided")
                            x, = np.where(self.master_table["aliasID"] == id_a)
                            symb_a = self.master_table["chem_symbol"][x][0] + self.master_table["valence"][x][0]
                            print("Symb_a is:", symb_a)
                            y, = np.where(self.master_table["aliasID"] == id_b)
                            symb_b = self.master_table["chem_symbol"][y][0] + self.master_table["valence"][y][0]
                            print("Symb_b is:", symb_b)
                            # Get the indices of the elements, then check if the location is empty
                            i, = np.where(self.reaction_table[0,:] == symb_a)
                            j, = np.where(self.reaction_table[:,0] == symb_b)
                            if self.reaction_table[j,i] != b"":
                                print("Reaction accepted")
                                #Update the master table, and send OK message
                                self.master_table["prev_symbol"][x] = self.master_table["chem_symbol"][x]
                                self.master_table["prev_symbol"][y] = self.master_table["chem_symbol"][y]
                                self.master_table["prev_valence"][x] = self.master_table["valence"][x]
                                self.master_table["prev_valence"][y] = self.master_table["valence"][y]
                                self.master_table["chem_symbol"][x] = self.reaction_table[j,i]
                                self.master_table["chem_symbol"][y] = self.reaction_table[j,i]
                                self.master_table["valence"][x] = b'+0'
                                self.master_table["valence"][y] = b'+0'
                                
                                # Send message about reaction
                                i, = np.where(self.master_table["aliasID"] == id_a)
                                #send_symbol = self.master_table["chem_symbol"][i][0]
                                #send_valence = self.master_table["valence"][i][0]

                                #print(b'$1' + id_a + send_valence + send_symbol +b'\n')
                                #s.write(b'$1' + id_a + send_valence + send_symbol +b'\n')
                                print(b'$1' + id_a  +b'\n')
                                self.s.write(b'$1' + id_a  +b'\n')

                                """
                                time.sleep(0.5) #TEST

                                # Send message to id_b
                                i, = np.where(self.master_table["aliasID"] == id_b)
                                #send_symbol = self.master_table["chem_symbol"][i][0]
                                #send_valence = self.master_table["valence"][i][0]

                                #print(b'$1' + id_b + send_valence + send_symbol +b'\n')
                                #s.write(b'$1' + id_b + send_valence + send_symbol +b'\n')
                                print(b'$1' + id_b +b'\n')a
                                self.s.write(b'$1' + id_b +b'\n')
                                """
                                master.update_element_bit_list(self.master_table)
                                subtable = [e for e in self.master_table if (e["aliasID"] == id_a or e["aliasID"] == id_b)]
                                print(subtable)
                                master.trigger_reaction(elements=subtable)
                            #else:
                                #print("Reaction not allowed")
                                #s.write(b'$0'+ id_a + b'\n') # 'NOT OK' message
                                #s.write(b'$0'+ id_b + b'\n') # 'NOT OK' message
                        else:
                            print("Both not reported collision yet.")
                    else: #other case or broken message, drop message and request resend?
                        print("STUB - BROKEN MESSAGE?")
                        #  DROP
    
                # Iterating collision table times
                self.iterate_time_in_collision_list( max_ttl = self.max_ttl )
    
            except (KeyboardInterrupt, SystemExit):
                self.s.close()
                print("EXIT")
                try:
                    exit(0)
                except SystemExit:
                    os._exit(0)
        self.s.close() # Close the serial port
        print("Out of loop")

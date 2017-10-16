import serial
import numpy as np
from pathlib import Path
import time

#import csv

#the port will depend on your computer
#for a raspberry pi it will probably be /dev/ttyACM0
#PORT = "/dev/ttyACM0"
#for windows it will be COM(something)
PORT = "COM3"

BAUD = 115200

s = serial.Serial(PORT)
s.baudrate = BAUD
s.parity   = serial.PARITY_NONE
s.databits = serial.EIGHTBITS
s.stopbits = serial.STOPBITS_ONE


# DATA SETUP
#element_data = np.genfromtxt('data.csv', delimiter=",", dtype=None, names="element, val1, val2")

#print(element_data['element'][0])
#print(element_data['val1'][0])
#print(element_data)

# Create master table
# load a scenario file, if any
scenario_path = Path('.')
scen_file = scenario_path / 'scenario.csv'
# Create master table
if scen_file.exists():
    master_table = np.genfromtxt('scenario.csv', delimiter=",", \
                                 dtype=[('aliasID', 'S2'),('serialNo', 'i4'),\
                                        ('chem_symbol', 'S10'), ('valence', 'S2')])
else:
    master_table = np.array([(b'aa',-1,b'',b'')],\
                             dtype=[('aliasID', 'S2'),('serialNo', 'i4'),\
                                    ('chem_symbol', 'S10'), ('valence', 'S2')])

#print(master_table)
print("Valences are", master_table["valence"])



#TESTING
SERIAL = b'ad'

if SERIAL in master_table["aliasID"]:
    i, = np.where(master_table["aliasID"]==SERIAL)
    send_alias = master_table["chem_symbol"][i][0]
else:
    i, = np.where(master_table["serialNo"] == -1)
    send_alias = master_table["aliasID"][i][0]
print("Thingy is", send_alias)
new_alias = bytes([master_table["aliasID"][-1][0],master_table["aliasID"][-1][1]+1])
print("Last alias is", new_alias)

##STRING TO BYTES SAMPLE -> "str.encode()" and ".decode()"
#string = "text"
#print(string)
#bytestr = str.encode(string)
#print(bytestr)
#print(bytestr.decode())

#exit()

#with open('data.csv', newline='') as csvfile:
#    symbols = csv.reader(csvfile, dialect='excel', delimiter=' ', quotechar='|')
#    for row in spamreader:
#        print(', '.join(row))



# NEED:
# 1. Send the ID numbers for the MBs
#    -> need to have an if loop for this 
# 2. Send the element numbers
#    - either due to request for element, OR as push for elements
#      -> either could be done using the same element int system as used,
#         as when pushing, whatever int the ID (alias) asks for, it can be
#         overriden based on the table that has the alias 
# 3. Check data tables for acceptable combinations
#    -> Send the combinations
# -> need to make a handler if loop for determining which case should run!
# 4. OTHER - drop message and request resend?

# Master table (ID table) sample:
# AT START:
#   aliasID  serialNo    chem_symbol   valence
#   aa       1234567890  H             +1
#   ab       1234567891  O             -2
#   ac       1234567892  H             +1
# AFTER MATCH:
#   aliasID  serialNo    chem_symbol   valence
#   aa       1234567890  H2O           0
#   ab       1234567891  H2O           0
#   ac       1234567892  H2O           0



# "MACROS"
IDALIAS = 0
ELEMENTREQ = 1
REACTION_CHECK = 2


next_ele = b'H' # TEMP DEF - make it relative to the master_table
next_val = b'+1'

try:
    while True:
        #read a line from the microbit, decode it and
        # strip the whitespace at the end
        data = s.readline().rstrip()

        print(data)
        
        #split the data
        data_s = data.split(b":")
        #symbol_int = int(data_s[1])
        symbol_int=2
        
        print("Symbol int is:",symbol_int)

        # Strip off the first elements to get the data type
        # data_s[0] is comm_type, data_s[1] is ID, data_s[2] is
        comm_type = data_s[0]
        id_in = data_s[1]
        message = data_s[2] ##SPLIT this message to parts with data.split(b"#")
        if comm_type == 5:#IDALIAS:
        # - CHECK THE TABLE FOR THE SERIAL, AND ALLOCATE ID NUMBER
        #   #if SERIAL in master_table[:, 1]:
            if SERIAL in master_table["serialNo"]:
                i, = np.where(master_table["serialNo"] == SERIAL)
                send_alias = master_table["aliasID"][i][0]
            else:
                if -1 in master_table["serialNo"]:
                    i, = np.where(master_table["serialNo"] == -1)
                    send_alias = master_table["aliasID"][i][0]
                else: # IF NO AVAILABLE ROW EXISTS
                    new_alias = bytes([master_table["aliasID"][-1][0], \
                                       master_table["aliasID"][-1][1]+1])
                    np.append(master_table, [new_alias, SERIAL, next_ele, next_val])
                    # HAVE TO KEEP TRACK OF HOW MANY ELEMENTS HAVE BEEN RECYCLED!
            print(send_alias)
            s.write(b'#'+str.encode(SERIAL)+b'#'+send_alias+b'#\n')
            # HAVE TO SEND THE SERIAL NUMBER AS WELL
        #   if SERIAL not in table, do
        #      add_to_table, pick a 2-char alias
        #   else:
        #      take the 2-char alias already allocated to the SERIAL
        # - send back the alias for the serial given
        #   s.write(b'#'+alias+b'#\n')
        #elif comm_type == ELEMENTREQ:
        #  find "id_in" in the master table, and pick the element given to it, if any 
        #elif comm_type == REACTION_CHECK:
        #else: #other case or broken message, drop message and request resend?
        #  #DROP

        
        # FAKE DATA, FOR TESTING
        symbols =      [b'H' ,b'He',b'Li',b'Be',b'B' ,b'C' ,b'N' ,b'O' ,b'F' ,b'Ne']
        electron_bal = [b'-1',b'-0' ,b'-5',b'-5',b'-5',b'-4',b'-5',b'-2',b'-5',b'-0'] 

        #print("Writing in: ", str(symbols[symbol_int]))
        #print("Writing in: ", str(electron_bal[symbol_int]))

        #for x in range(0, 3): #HACK to ensure the message gets through
        #   s.write(b'#'+symbols[symbol_int]+b'#\n')
        #print(b'#'+symbols[symbol_int]+b'#\n')

        #s.write(b'#'+electron_bal[symbol_int]+b'\n')
        #for x in range(0, 10): #HACK to ensure the message gets through
        s.write(electron_bal[symbol_int]+symbols[symbol_int]+b'\n')
        #s.write(b'#'+electron_bal[symbol_int]+b'\n')
        #for x in range(0, 10): #HACK to ensure the message gets through
        #   s.write(b'#'+electron_bal[symbol_int] + b'#'+symbols[symbol_int]+b'#' +b'\n')
        print(b'#'+electron_bal[symbol_int] + b'#'+symbols[symbol_int]+b'#\n')

        #for x in range(0, 5): #HACK to ensure the message gets through
        #    s.write(b'#'+electron_bal[symbol_int]+b'\n')
        #print(b'#'+electron_bal[symbol_int]+b'\n')


        
finally:
    s.close()

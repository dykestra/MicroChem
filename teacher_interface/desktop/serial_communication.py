import serial
import numpy as np
from pathlib import Path
import os

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
# --------------------------------------------------
## Create master table
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

## Create the reaction table
reaction_table = np.genfromtxt('elementsDB-v3.csv', delimiter=";", dtype=None)

## TESTING REACTIONS
#message = b"ot#iz"
#message_s = message.split(b"#")
#id_a = message_s[0]
#id_b = message_s[1]
#x, = np.where(master_table["aliasID"] == id_a)
#symb_a = master_table["chem_symbol"][x][0] + master_table["valence"][x][0]
#y, = np.where(master_table["aliasID"] == id_b)
#symb_b = master_table["chem_symbol"][y][0] + master_table["valence"][y][0]
#print(symb_b)

##GET INDEX OF symb_a, then check if reaction_table[symb_b][symb_a] is empty or not
## -> NOT SURE how to find the index for id_a...
#i, = np.where(reaction_table[0,:] == symb_a)
#j, = np.where(reaction_table[:,0] == symb_b)
#print(i,j)
#print(reaction_table[j,i])
#if reaction_table[j,i] != b"":
#    print("Reaction accepted")
#    ##UPDATE THE MASTER TABLE, and send OK message
#    master_table["chem_symbol"][x] = reaction_table[j,i]
#    master_table["chem_symbol"][y] = reaction_table[j,i]
#    master_table["valence"][x] = b'+0'
#    master_table["valence"][y] = b'+0'
#    print(master_table)
#else:
#    print("Reaction not allowed")


#exit()

#TESTING
SERIAL = b'ad'

if SERIAL in master_table["aliasID"]:
    i, = np.where(master_table["aliasID"]==SERIAL)
    send_alias = master_table["chem_symbol"][i][0]
else:
    i, = np.where(master_table["serialNo"] == -1)
    send_alias = master_table["aliasID"][i][0]
print("Alias is", send_alias)
#new_alias = bytes([master_table["aliasID"][-1][0],master_table["aliasID"][-1][1]+1])
#print("Last alias is", new_alias)


##STRING TO BYTES SAMPLE -> "str.encode()" and ".decode()"
#string = "text"
#print(string)
#bytestr = str.encode(string)
#print(bytestr)
#print(bytestr.decode())


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
next_val = b'+1' # TEMP

break_loop = False

n_elements = 10
max_ttl = 1024
MB_collision_list = [[] for x in range(n_elements)]
#print(MB_collision_list)



# --------------------------------------------------
# Function to add to the list of collisions
# --------------------------------------------------
def add_to_collision_list( to_be_added  ):
    for i in range(len(MB_collision_list)):
        if not MB_collision_list[i]:
            print("Empty list at position", i)
            MB_collision_list[i] = [to_be_added, 0]
            break
        else:
            if i == len(MB_collision_list)-1:
                MB_collision_list.append([to_be_added, 0])

# --------------------------------------------------        
# Function to search the collision list
# --------------------------------------------------
def search_collision_list( searchable ):
    for sublist in MB_collision_list:
        if sublist: # if sublist is not empty
            if sublist[0] == searchable:
                print("Found it!", sublist)
                return True

# --------------------------------------------------        
# Function to search for "reverse message" in the collision list
# returns true if exists in the list
# --------------------------------------------------
def is_reverse_in_collision_list( searchable ):
    #reverse = searchable[0:2] + searchable[5:] + searchable[4] + searchable[2:4]
    reverse = searchable[2:4] + searchable[0:2]
    print("The reverse of ", searchable)
    print("is", reverse)
    for sublist in MB_collision_list:
        if sublist: # if sublist is not empty
            if sublist[0] == reverse:
                print("Found the reverse!", sublist)
                return True

        
# --------------------------------------------------        
# Function to iterate time alive in all messages
# and remove messages that have exceeded max time
# --------------------------------------------------
def iterate_time_in_collision_list( max_ttl = 1024 ):
    for sublist in MB_collision_list:
        if sublist: # if sublist is not empty
            if sublist[1] == max_ttl:
                del sublist[:]
            else:
                sublist[1] = sublist[1] + 1

                
#TESTING THE LIST ============================ REMOVE
# Add things to the list
str_to_be_added = "1av3op"
add_to_collision_list( str_to_be_added )
print(MB_collision_list)

# Search the list
searchable = "1av3op"
search_collision_list( searchable )


# FILL LIST
for i in range(len(MB_collision_list)):
    if not MB_collision_list[i]:
        print("Filling position", i)
        MB_collision_list[i] = [str_to_be_added, 0]

# Adding to a full list
str_to_be_added = "1ad3ed"
add_to_collision_list( str_to_be_added )
print(len(MB_collision_list))
print(MB_collision_list)

# Iterate time in list
iterate_time_in_collision_list()
print(MB_collision_list)

if is_reverse_in_collision_list( "2:op:av" ):
    print("Yeah man")

# Clearing parts of the list
iterate_time_in_collision_list(max_ttl=1)
#rm_old_messages_from_list(1)
print(MB_collision_list)


iterate_time_in_collision_list(max_ttl=1)

# ============================ REMOVE

#exit()

while not break_loop:
    try:
        #read a line from the microbit, decode it and
        # strip the whitespace at the end
        data = s.readline().rstrip()
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
        if comm_type == IDALIAS:
            SERIAL = id_in
            # Check the table for the serial, and allocate an ID number
            if SERIAL in master_table["serialNo"]:
                i, = np.where(master_table["serialNo"] == SERIAL)
                send_alias = master_table["aliasID"][i][0]
            else:
                if -1 in master_table["serialNo"]:
                    i, = np.where(master_table["serialNo"] == -1)
                    send_alias = master_table["aliasID"][i][0]
                else: # if no available row exists
                    new_alias = bytes([master_table["aliasID"][-1][0], \
                                       master_table["aliasID"][-1][1]+1])
                    np.append(master_table, [new_alias, SERIAL, next_ele, next_val])
                    # HAVE TO KEEP TRACK OF HOW MANY ELEMENTS HAVE BEEN RECYCLED!
            print(send_alias)
            s.write(b'#'+SERIAL+b'#'+send_alias+b'#\n')
            # HAVE TO SEND THE SERIAL NUMBER AS WELL

        # Element requests
        elif comm_type == ELEMENTREQ:
            i, = np.where(master_table["aliasID"] == id_in)
            send_symbol = master_table["chem_symbol"][i][0]
            send_valence = master_table["valence"][i][0]
            print(send_valence + send_symbol + b'\n')
            s.write(send_valence + send_symbol + b'\n')
            #  find "id_in" in the master table, and pick the element given to it, if any
        # Reaction messages (collisions)
        elif comm_type == REACTION_CHECK:
            message_s = message.split(b"#")
            id_a = id_in
            id_b = message#_s[0]#message_s[1]
            print("id_a:", id_a)
            print("id_b:", id_b)
            pair = id_a + id_b
            pair_str = pair.decode()
            # Add to collision list
            add_to_collision_list( pair_str )
            
            # Only process if reverse is already in collision list
            if is_reverse_in_collision_list( pair_str ):
                print("Both collided")
                x, = np.where(master_table["aliasID"] == id_a)
                symb_a = master_table["chem_symbol"][x][0] + master_table["valence"][x][0]
                print("Symb_a is:", symb_a)
                y, = np.where(master_table["aliasID"] == id_b)
                symb_b = master_table["chem_symbol"][y][0] + master_table["valence"][y][0]
                print("Symb_b is:", symb_b)
                # Get the indices of the elements, then check if the location is empty
                i, = np.where(reaction_table[0,:] == symb_a)
                j, = np.where(reaction_table[:,0] == symb_b)
                if reaction_table[j,i] != b"":
                    print("Reaction accepted")
                    #Update the master table, and send OK message
                    master_table["chem_symbol"][x] = reaction_table[j,i]
                    master_table["chem_symbol"][y] = reaction_table[j,i]
                    master_table["valence"][x] = b'+0'
                    master_table["valence"][y] = b'+0'

                    # Send message to id_a
                    i, = np.where(master_table["aliasID"] == id_a)
                    send_symbol = master_table["chem_symbol"][i][0]
                    send_valence = master_table["valence"][i][0]
    
                    print(b'$1' + id_a + send_valence + send_symbol +b'\n')
                    s.write(b'$1' + id_a + send_valence + send_symbol +b'\n') #OK message
                    # Send message to id_b
                    i, = np.where(master_table["aliasID"] == id_b)
                    send_symbol = master_table["chem_symbol"][i][0]
                    send_valence = master_table["valence"][i][0]
    
                    print(b'$1' + id_b + send_valence + send_symbol +b'\n')
                    s.write(b'$1' + id_b + send_valence + send_symbol +b'\n') #OK messag
                else:
                    print("Reaction not allowed")
                    s.write(b'$0'+b'\n') # 'NOT OK' message
            else:
                print("Both not reported collision yet.")
        else: #other case or broken message, drop message and request resend?
            print("STUB - BROKEN MESSAGE?")
            #  DROP

        # Iterating collision table times
        iterate_time_in_collision_list( max_ttl = 1024 )
                        
        #IF THE MASTER_TABLE UPDATED:
        ##   UPDATE THE GUI WITH THE MASTER_TABLE DATA!

        # Make an event to update the GUI with this table every time this table gets updated
        #  - a check in the while loop that sends the info conditional on it being OK
        #   - the other code would be imported as a module for this
    except (KeyboardInterrupt, SystemExit):
        s.close()
        print("EXIT")
        try:
            exit(0)
        except SystemExit:
            os._exit(0)

        
    #finally:
    #    s.close()

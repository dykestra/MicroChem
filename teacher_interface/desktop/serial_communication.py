import serial

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

try:
    while True:
        #read a line from the microbit, decode it and
        # strip the whitespace at the end
        data = s.readline().rstrip()

        #print(data)
        
        #split the data into x, y, z
        data_s = data.split(b":")
        symbol_int = int(data_s[1])

        print("Symbol int is:",symbol_int)

        # FAKE DATA, FOR TESTING
        symbols =      [b'H' ,b'He',b'Li',b'Be',b'B' ,b'C' ,b'N' ,b'O' ,b'F' ,b'Ne']
        electron_bal = [b'-1',b'-0' ,b'-5',b'-5',b'-5',b'-4',b'-5',b'-2',b'-5',b'-0'] 

        print("Writing in: ", str(symbols[symbol_int]))
        print("Writing in: ", str(electron_bal[symbol_int]))
        
        s.write(symbols[symbol_int]+b'\n')
        print(symbols[symbol_int]+b'\n')
        s.write(electron_bal[symbol_int]+b'\n')
        print(electron_bal[symbol_int]+b'\n')

        #NOTE: There is some annoying bug in which:
        # a) things don't always change as they should in the element MB
        # b) The hub MB doesn't seem to get to the "processing..." stage, so
        #    doesn't update the element
    # COULD IT BE MESSAGE CORRUPTION? SHOULD HAVE SOME CHECKS, ACKS,
    # AND BUFFERING OF THE MESSAGES
        #s.write(b'C\n')
        #s.write(b'-4\n')


        
        #split the accelerometer data into x, y, z
        #data_s = data.split(b" ")
        #x, y, z = data_s[0], data_s[1], data_s[2]
        #a, b = data_s[3], data_s[4]
        #print(x,y,z)
        #print(a,b)

finally:
    s.close()

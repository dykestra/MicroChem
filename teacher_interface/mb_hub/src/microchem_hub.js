// Packet length defitions
let check_len = 0
let comm_type_len = 1
let serial_len = 10
let ID_len = 2
let msg_type_len = 1

// "Macros" for sending messages
let MBHUB = 0
let HUBMB = 1
let MBMB = 2
let STORE_ID = 0
let NEED_ELEMENT = 1
let CONFIRM_ELEMENT = 2
let COLLISION = 3
let CONFIRM_REACTION = 4
let OK_STORE_ID = 0
let NEW_ELEMENT = 1
let REACT = 2
let NO_REACT = 3

// Other definitions
let message = ""
let msg_type = 0
let id_in = ""
let curr_symbol_int = 0
let send_str = ""
let comm_type = 0
let str_electron_bal = ""
let msg_len = 0
let curr_symbol = ""

function get_chem_data() {
    led_breathe()
    serial.writeValue(id_in, curr_symbol_int)
    curr_symbol = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    str_electron_bal = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    //send_str = "" + str_electron_bal + curr_symbol
    basic.showString("S:")
    //basic.showString(send_str)
}

radio.onDataPacketReceived(({ receivedString: msg_in, receivedNumber: value }) => {
    msg_len = msg_in.length
    comm_type = parseInt(msg_in.substr(check_len, comm_type_len))
    id_in = msg_in.substr(check_len + comm_type_len, ID_len)
    msg_type = parseInt(msg_in.substr(check_len + comm_type_len + ID_len, msg_type_len))
    message = msg_in.substr(check_len + comm_type_len + ID_len + msg_type_len, msg_len - check_len - comm_type_len - ID_len - msg_type_len)
    if (comm_type == MBHUB) {
        curr_symbol_int = value
        get_chem_data()
        send_chem_data()
    }
    show_S()
})

function show_S() {
    basic.showLeds(`
        . # # # .
        . # . . .
        . # # # .
        . . . # .
        . # # # .
        `)
}

function send_chem_data() {
    send_str = HUBMB.toString() + id_in + NEW_ELEMENT.toString() + str_electron_bal + curr_symbol
    basic.showString(send_str)
    radio.sendValue(send_str, curr_symbol_int)
}

function get_compound_data() {
    led_breathe()
    basic.showString("STUB")
}

function led_breathe() {
    led.setBrightness(255)
    basic.pause(100)
    led.setBrightness(192)
    basic.pause(100)
    led.setBrightness(127)
    basic.pause(100)
    led.setBrightness(61)
    basic.pause(100)
    led.setBrightness(127)
    basic.pause(100)
    led.setBrightness(192)
    basic.pause(100)
    led.setBrightness(255)
}

radio.setGroup(83)
radio.setTransmitPower(7)
curr_symbol_int = 0
curr_symbol = "H"
show_S() 

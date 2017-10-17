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
let serial_in = ""
let send_str = ""
let comm_type = 0
let str_electron_bal = ""
let msg_len = 0
let curr_symbol = ""

function get_id_alias() {
    led_breathe()
    serial.writeValue("0:" + serial_in, 0)
    //serial.writeString("0:"+id_in+":TEST")
    send_str = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    send_str = "#" + serial_in + "#" + send_str + "#"
    basic.showString("S:")
}

function get_chem_data() {
    led_breathe()
    serial.writeValue("1:" + id_in + ":TEST", 0)
    //serial.writeString("0:"+id_in+":TEST")
    send_str = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    str_electron_bal = send_str.substr(0, 2)
    curr_symbol = send_str.substr(2, send_str.length - 2)
    send_str = "#" + str_electron_bal + "#" + curr_symbol + "#"
    basic.showString("S:")
}

radio.onDataPacketReceived(({ receivedString: msg_in }) => {
    //basic.showString(msg_in) //TEMP for testing
    msg_len = msg_in.length
    comm_type = parseInt(msg_in.substr(check_len, comm_type_len))
    id_in = msg_in.substr(check_len + comm_type_len, ID_len)
    msg_type = parseInt(msg_in.substr(check_len + comm_type_len + ID_len, msg_type_len))
    message = msg_in.substr(check_len + comm_type_len + ID_len + msg_type_len, msg_len - check_len - comm_type_len - ID_len - msg_type_len)
    if (comm_type == MBHUB) {
	if (msg_type == STORE_ID) {
	    serial_in = msg_in.substr(check_len + comm_type_len, serial_len)
            get_id_alias()
            send_id_alias()
	} else if (msg_type == NEED_ELEMENT) {
            get_chem_data()
            send_chem_data()
	}
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

function send_id_alias() {
    send_str = HUBMB.toString() + serial_in + OK_STORE_ID.toString() + send_str
    basic.showString(send_str)
    radio.sendString(send_str)
}

function send_chem_data() {
    send_str = HUBMB.toString() + id_in + NEW_ELEMENT.toString() + send_str
    basic.showString(send_str)
    radio.sendString(send_str)
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
show_S() 

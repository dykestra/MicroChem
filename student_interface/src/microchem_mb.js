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
let comm_type = 0
let own_ID = ""
let id_in = ""
let msg_type = 0
let message = ""
let msg_len = 0

let symbol_len = 0
let str_elect_bal = ""
let packet_ok = 0
let chk_chars: number[] = []
let electron_balance = 0
let chem_symbol = ""
let sym_num = 0
let curr_page = 0
let send_str = ""


input.onButtonPressed(Button.A, () => {
    curr_page += -1
    show_page()
})

input.onButtonPressed(Button.B, () => {
    curr_page += 1
    show_page()
})

function show_page() {
    if (curr_page == 0) {
        basic.showString(chem_symbol)
    } else {
        curr_page = 1
        basic.showNumber(electron_balance)
    }
}

radio.onDataPacketReceived(({ receivedNumber, receivedString: msg_in }) => {
    basic.showString(msg_in)
    msg_len = msg_in.length
    comm_type = parseInt(msg_in.substr(check_len, comm_type_len))
    id_in = msg_in.substr(check_len + comm_type_len, ID_len)
    msg_type = parseInt(msg_in.substr(check_len + comm_type_len + ID_len, msg_type_len))
    message = msg_in.substr(check_len + comm_type_len + ID_len + msg_type_len, msg_len - check_len - comm_type_len - ID_len - msg_type_len)
    if (comm_type == HUBMB) {
        if (id_in == own_ID) {
            basic.showString(message)
            chk_chars = [0, 3, message.length - 1]
            for (let ch of chk_chars) {
                if (message.charAt(ch) == "#") {
                    packet_ok = 1
                } else {
                    packet_ok = 0
                    basic.showString("F:")
                    basic.showNumber(ch)
                }
            }
            if (packet_ok == 1) {
                str_elect_bal = message.substr(1, 2)
                symbol_len = message.length - 5
                chem_symbol = message.substr(4, symbol_len)
                electron_balance = parseInt(str_elect_bal)
            } else {
                radio.sendValue(send_str, sym_num)
            }
        } else {
            if (receivedNumber == -1) {
                sym_num = parseInt(message)
                initialise_element()
            }
        }
    }
    basic.showString(chem_symbol)
})

function set_symbol() {
    sym_num = Math.random(6)
    initialise_element()
}

function attempt_compound() {
    basic.showString("STUB")
}

function initialise_element() {
    basic.showLeds(`
        . # . . .
        . . # . .
        . # # # .
        . . # . .
        . . . # .
        `)
    send_str = MBHUB.toString() + own_ID + NEED_ELEMENT.toString() + "TEST" //REMOVE "TEST" LATER
    radio.sendValue(send_str, sym_num)
}

function check_packet() {
    basic.showString("STUB")
}

input.onButtonPressed(Button.AB, () => {
    attempt_compound()
    basic.showLeds(`
        . . . . .
        # . . # .
        . # . . #
        # . . # .
        . . . . .
        `)
})

own_ID = control.deviceName().substr(3, ID_len) //TEMP - CHANGE TO ALIAS ID QUERIED FROM HUB!
//basic.showString(own_ID)
radio.setGroup(83)
chem_symbol = "H"
electron_balance = -1
radio.setTransmitPower(7)
set_symbol()
radio.setTransmitPower(1)
curr_page = 0

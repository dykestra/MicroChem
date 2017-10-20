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

let REACT_STATE = 0

function get_id_alias() {
    led_flicker()
    serial.writeValue("0:" + serial_in, 0)
    send_str = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    send_str = "#" + serial_in + "#" + send_str + "#"
    basic.showString("S:")
}

function get_chem_data(send_str: string, id_a: string, comm: number) {
    let str_valence = ""
    let symbol = ""
    led_flicker()
    while (str_valence == "" || symbol == "") {
        serial.writeValue("1:" + id_a + ":TEST", 0)
        send_str = serial.readUntil(serial.delimiters(Delimiters.NewLine))
        str_valence = send_str.substr(0, 2)
        symbol = send_str.substr(2, send_str.length - 2)
    }
    send_str = "#" + str_valence + "#" + symbol + "#"
    send_chem_data(send_str, id_a, comm)
    if (REACT_STATE == 1) {
        REACT_STATE = 0
    }
}

// Collision data
// Fire serial when data with a "$" is received
serial.onDataReceived(serial.delimiters(Delimiters.Dollar), () => {
    radio.setGroup(82) //change channel to stop interference
    let db_response = ""
    db_response = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    if (db_response.substr(0,2) == '$1') { //TEST
	REACT_STATE = 1
	let id_a = ""
	id_a = db_response.substr(2, 2)
	let response = ""
	led_flicker( 20, 25 ) //TEST
	response = HUBMB.toString() + "22" + REACT.toString()
	radio.sendString(response)
    }
    radio.setGroup(83) //change channel back
})


function send_collision_data(id_a: string, id_b: string) {
    led_flicker()
    serial.writeValue("2:" + id_a + ":" + id_b, 0)
}


radio.onDataPacketReceived(({ receivedString: msg_in }) => {
    msg_len = msg_in.length
    comm_type = parseInt(msg_in.substr(check_len, comm_type_len))
    id_in = msg_in.substr(check_len + comm_type_len, ID_len)
    msg_type = parseInt(msg_in.substr(check_len + comm_type_len + ID_len, msg_type_len))
    message = msg_in.substr(check_len + comm_type_len + ID_len + msg_type_len, msg_len - check_len - comm_type_len - ID_len - msg_type_len)
    if (comm_type == MBHUB) {
        if (msg_type == NEED_ELEMENT || REACT_STATE == 0) {
            if (msg_type == STORE_ID) {
                serial_in = msg_in.substr(check_len + comm_type_len, serial_len)
                get_id_alias()
                send_id_alias()
            } else if (msg_type == NEED_ELEMENT) {
                let send_string = ""
                get_chem_data(send_string, id_in, NEW_ELEMENT)
            } else if (msg_type == COLLISION) {
                let id_b = ""
                id_b = message
                send_collision_data(id_in, id_b)
            }
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

function send_chem_data(send_str: string, id_a: string, comm: number) {
    if (comm == NEW_ELEMENT) {
        send_str = HUBMB.toString() + id_a + NEW_ELEMENT.toString() + send_str
    } else if (comm == REACT) { //REMOVE? - unnecessary if keep current REACT messages
        send_str = HUBMB.toString() + id_a + REACT.toString() + send_str
    }
    radio.sendString(send_str)
}


// Flicker the LEDs to show message received
function led_flicker( low_bright = 61, pause_time = 50 ) {
    led.setBrightness(low_bright)
    basic.pause(50)
    led.setBrightness(255)
}


//--------------------------------------------------
//     Forever loop to re-broadcast REACT command
//--------------------------------------------------
basic.forever(() => {
    if (REACT_STATE == 1) {
	//Rebroadcast the REACT command
	let response = ""
	led_flicker( 20, 25 )
	response = HUBMB.toString() + "22" + REACT.toString()
	radio.sendString(response)
    }
})


//--------------------------------------------------
//     Start receiving only when A pressed
//--------------------------------------------------
input.onButtonPressed(Button.A, () => {
    radio.setGroup(83) //Set group to same with MB elements
    show_S()
})

radio.setGroup(82) //TEST - may be unnecessary
radio.setTransmitPower(7)
    basic.showLeds(`
        . # # # .
        . . . . .
        . # # # .
        . . . . .
        . # # # .
        `)


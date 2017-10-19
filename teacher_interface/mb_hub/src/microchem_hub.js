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
    led_breathe()
    serial.writeValue("0:" + serial_in, 0)
    //serial.writeString("0:"+id_in+":TEST")
    send_str = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    send_str = "#" + serial_in + "#" + send_str + "#"
    basic.showString("S:")
}

function get_chem_data(send_str: string, id_a: string, comm: number) {
    let str_valence = ""
    let symbol = ""
    led_breathe()
    while (str_valence == "" || symbol == "") {
        serial.writeValue("1:" + id_a + ":TEST", 0) //TEMP
        //serial.writeString("0:"+id_a+":TEST")
        send_str = serial.readUntil(serial.delimiters(Delimiters.NewLine))
        str_valence = send_str.substr(0, 2)
        symbol = send_str.substr(2, send_str.length - 2)
    }
    send_str = "#" + str_valence + "#" + symbol + "#"
    //basic.showString("S:")
    send_chem_data(send_str, id_a, comm)
    if (REACT_STATE == 1) {
        REACT_STATE = 0
    }
}

// Collision data
// Fire serial when data with a "$" is received
serial.onDataReceived(serial.delimiters(Delimiters.Dollar), () => {
    radio.setGroup(82) //change channel to stop interference
    REACT_STATE = 1
    let db_response = ""
    let id_a = ""
    db_response = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    id_a = db_response.substr(2, 2)
    let response = "" //TEST
    basic.showString("RE") //TEST
    response = HUBMB.toString() + "22" + REACT.toString()  //TEST
    radio.setGroup(83) //change channel to stop interference //TEST
    basic.showString(response) //TEST
    radio.sendString(response) //TEST
    /*
    if (db_response.substr(0,2) == "$0") {
	basic.showString("x") // TEMP
	//  SEND NO_REACT to the microbit id_a
	//response = HUBMB.toString() + id_a + NO_REACT.toString()// + id_b
	//basic.showString(response)
	//radio.sendString(response)
    } else {
	//basic.showString("U:" + id_a)
	//get_chem_data( "", id_a, REACT ) //TEST
	let response = ""
	basic.showString("R")
	response = HUBMB.toString() + "00" + REACT.toString()  //TEST
	radio.sendString(response)
	//*let response = ""
	let valence = ""
	let smbl = ""
	valence = db_response.substr(4, 2)
	basic.showString("V:" + valence)
	smbl = db_response.substr(6, send_str.length - 6)
	if (valence != "" && smbl != "") {
	//symbol = db_response.substr(3, send_str.length - 3)
	//response = "#" + str_electron_bal + "#" + symbol + "#"
	//response = HUBMB.toString() + id_a + REACT.toString() + response
	    response = HUBMB.toString() + id_a + REACT.toString() + "#" + valence + "#" + smbl + "#"
	    basic.showString("R:" + response)
	    radio.sendString(response)
	} else {
	    basic.showString("F")
	}
	///
    }*/
    //radio.setGroup(83) //change channel back //TEST
})


function send_collision_data(id_a: string, id_b: string) {
    led_breathe()
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
                //get_chem_data()
                //send_chem_data()
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
    } else if (comm == REACT) {
        basic.showString("R")
        send_str = HUBMB.toString() + id_a + REACT.toString() + send_str
    }
    //basic.showString(send_str)
    radio.sendString(send_str)
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

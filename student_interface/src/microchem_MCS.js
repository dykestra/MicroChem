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
let full_formula = ""

let Threshold_Power = 0
let CmdProcess = 0
let CommsBuffer: string[] = []
let value = ""
let ActiveIDState: string[] = []
let ActiveIDFlag: number[] = []
let ActiveIDList: string[] = []
let MBState = "Start-Up"
let AnimationStage = 0
let ClockSpeed = 500


/********************************************* */
/**     Controls the component on screen       */
/********************************************* */
input.onButtonPressed(Button.A, () => {
    curr_page += -1
    if (curr_page < 0) { curr_page = 0 }
})

input.onButtonPressed(Button.B, () => {
    curr_page += 1
    if (curr_page > (full_formula.length - 1)) { curr_page = (full_formula.length - 1) }
})

radio.onDataPacketReceived(({ receivedString, signal }) => {
    switch (MBState) {
        case "Start-Up":
            process_startup_messages(receivedString)
            break
        case "Ready":
            if (signal >= Threshold_Power) {
                CommsBuffer.push(receivedString)
            }
            break
        default:
    }
})

basic.forever(() => {
    switch (MBState) {
        case "Start-Up":
	    ClockSpeed = 500
            basic.showLeds(`
			   . # . . .
			   . . # . .
			   . # # # .
			   . . # . .
			   . . . # .
			   `)
            if (chem_symbol != "") {
                radio.setTransmitPower(0)
		if (electron_balance > 0) {
                    full_formula = chem_symbol + "+" + electron_balance.toString()
                } else {
                    full_formula = chem_symbol + electron_balance.toString()
                }
                MBState = "Ready"
            }
            break
        case "Ready":
	    ClockSpeed = 500	
            basic.showString(full_formula[curr_page])
            radio.sendString(MBMB.toString() + own_ID)
            BufferProcessing()
            break
        case "Reaction":
	    ClockSpeed = 50	
            // Need a function that:
            // -> Create screen animation for reaction
            // -> Clean all matrices
	    ReactionAnimation()
            MBState = "Ready"
            break
        default:
            MBState = "Start-Up"
    }

    basic.pause(ClockSpeed)
})

/********************************************* */
/**Read all messages received every 500ms      */
/********************************************* */
function BufferProcessing() {
    for (let value of CommsBuffer) {
        CmdProcess = parseInt(value.substr(0, comm_type_len))
        if (CmdProcess == MBMB) {
            MBMBProcessing(value.substr(comm_type_len, value.length))
        } else if (CmdProcess == MBHUB) {
            serial.writeLine(value)
        } else if (CmdProcess == HUBMB) {
            HBMBProcessing(value.substr(comm_type_len, value.length))
        } else {
            serial.writeLine("Someone is drunk")
        }
    }
    CommsBuffer = []
    CleanIDs()
}

/*********************************** */
/**Clean list of Active devices      */
/*********************************** */
function CleanIDs() {

    let ActiveIDListAux: string[] = []
    let ActiveIDFlagAux: number[] = []
    let ActiveIDStateAux: string[] = []

    // Eliminate all elements not present
    for (let i = 0; i < ActiveIDFlag.length; i++) {
        if (ActiveIDFlag[i] == 1) {
            ActiveIDListAux.push(ActiveIDList[i])
            ActiveIDFlagAux.push(0)
            ActiveIDStateAux.push(ActiveIDState[i])
        }
    }

    ActiveIDList = []
    ActiveIDFlag = []
    ActiveIDState = []
    ActiveIDList = ActiveIDListAux
    ActiveIDFlag = ActiveIDFlagAux
    ActiveIDState = ActiveIDStateAux

}

/*********************************** */
/**Function processing MBMB messages */
/*********************************** */
function MBMBProcessing(ID: string) {
    let IDIndex = 0
    if (isInArray(ID, ActiveIDList)) {
        IDIndex = ActiveIDList.indexOf(ID)
        ActiveIDFlag[IDIndex] = 1
        switch (ActiveIDState[IDIndex]) {
            case "Initial State":
                ActiveIDState[IDIndex] = "Wait 1"
                break
            case "Wait 1": // hysteresis case
                ActiveIDState[IDIndex] = "Send Hub"
                break
            case "Send Hub":
                ActiveIDState[IDIndex] = "Waiting Hub"
                radio.setTransmitPower(7)
                radio.sendString(MBHUB.toString() + own_ID + COLLISION.toString() + ID)
                radio.setTransmitPower(0)
                break
            case "Waiting Hub":
                ActiveIDState[IDIndex] = "Send Hub"
                break
            default:
                break
        }

    } else {
        ActiveIDList.push(ID)
        ActiveIDFlag.push(1)
        ActiveIDState.push("Initial State")
    }
}

/*********************************** */
/**Function processing HBMB messages */
/*********************************** */
function HBMBProcessing(message: string) {
    id_in = message.substr(0, ID_len)
    msg_type = parseInt(message.substr(ID_len, msg_type_len))
    message = message.substr(ID_len + msg_type_len, msg_len - ID_len - msg_type_len)
    if (id_in == own_ID) {
        if (msg_type == OK_STORE_ID) {
            chk_chars = [0, 3]
        } else {
            chk_chars = [0, 3, message.length - 1]
        }
        for (let ch of chk_chars) {
            if (message.charAt(ch) == "#") {
                packet_ok = 1
            } else {
                packet_ok = 0
            }
        }
        if (packet_ok == 1) {
            if (msg_type == OK_STORE_ID) {
                own_ID = message.substr(1, 2)
            } else { //(msg_type == NEW_ELEMENT) {
                str_elect_bal = message.substr(1, 2)
                symbol_len = message.length - 5
                chem_symbol = message.substr(4, symbol_len)
                electron_balance = parseInt(str_elect_bal)
            }
        } else {
            // Packet failed, request resend
            radio.sendString(send_str)
        }
    }
}



/*********************************** */
/**Function processing messages at startup */
/*********************************** */
function process_startup_messages(msg_in: string) {
    msg_len = msg_in.length
    comm_type = parseInt(msg_in.substr(check_len, comm_type_len))
    id_in = msg_in.substr(check_len + comm_type_len, ID_len)
    msg_type = parseInt(msg_in.substr(check_len + comm_type_len + ID_len, msg_type_len))
    message = msg_in.substr(check_len + comm_type_len + ID_len + msg_type_len, msg_len - check_len - comm_type_len - ID_len - msg_type_len)
    if (comm_type == HUBMB) {
        if (id_in == own_ID) {
            if (msg_type == OK_STORE_ID) {
                chk_chars = [0, 3]
            } else {
                chk_chars = [0, 3, message.length - 1]
            }
            for (let ch of chk_chars) {
                if (message.charAt(ch) == "#") {
                    packet_ok = 1
                } else {
                    packet_ok = 0
                }
            }
            if (packet_ok == 1) {
                if (msg_type == OK_STORE_ID) {
                    own_ID = message.substr(1, 2)
                } else { //(msg_type == NEW_ELEMENT) {
                    str_elect_bal = message.substr(1, 2)
                    symbol_len = message.length - 5
                    chem_symbol = message.substr(4, symbol_len)
                    electron_balance = parseInt(str_elect_bal)
                }
            } else {
                // Packet failed, request resend
                radio.sendString(send_str)
            }
        }
    }
}


function isInArray(value: string, array: string[]) {
    return array.indexOf(value) > -1;
}

function initialise_element() {
    send_str = MBHUB.toString() + own_ID + NEED_ELEMENT.toString() + "TEST" //REMOVE "TEST" LATER
    radio.sendString(send_str)
}

function ReactionAnimation() {
    switch (AnimationStage) {
        case 0:
            basic.showLeds(`
                . . . . .
                . . . . .
                . . # . .
                . . . . .
                . . . . .
                `)
            AnimationStage++
            break
        case 1:
            basic.showLeds(`
                . . . . .
                . . # . .
                . # # # .
                . . # . .
                . . . . .
                `)
            AnimationStage++
            break
        case 2:
            basic.showLeds(`
                . . . . .
                . # # # .
                . # # # .
                . # # # .
                . . . . .
                `)
            AnimationStage++
            break
        case 3:
            basic.showLeds(`
                . . # . .
                . # # # .
                # # # # #
                . # # # .
                . . # . .
                `)
            AnimationStage++
            break
        case 4:
            basic.showLeds(`
                # . # . #
                . # # # .
                # # # # #
                . # # # .
                # . # . #
                `)
            AnimationStage++
            break
        case 5:
            basic.showLeds(`
                # . # . #
                . # # # .
                # # . # #
                . # # # .
                # . # . #
                `)
            AnimationStage++
            break
        case 6:
            basic.showLeds(`
                # . # . #
                . # . # .
                # . . . #
                . # . # .
                # . # . #
                `)
            AnimationStage++
            break
        case 7:
            basic.showLeds(`
                # . # . #
                . . . . .
                # . . . #
                . . . . .
                # . # . #
                `)
            AnimationStage++
            break
        case 8:
            basic.showLeds(`
                # . . . #
                . . . . .
                . . . . .
                . . . . .
                # . . . #
                `)
            AnimationStage++
            break
        case 9:
            basic.showLeds(`
                . . . . .
                . . . . .
                . . . . .
                . . . . .
                . . . . .
                `)
            AnimationStage = 0
            CommsBuffer = []
            ActiveIDList = []
            ActiveIDFlag = []
            ActiveIDState = []
            MBState = "Ready"
            break
    }
}


own_ID = control.deviceName().substr(3, ID_len)
radio.setGroup(83)
radio.setTransmitPower(7) //for initialisation
initialise_element()
Threshold_Power = -63
CommsBuffer = []
CmdProcess = 0
ActiveIDList = []
ActiveIDFlag = []
ActiveIDState = []
curr_page = 0
full_formula = ""
AnimationStage = 0
ClockSpeed = 500

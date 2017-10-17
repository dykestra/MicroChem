let Threshold_Power = 0
let CmdProcess = ""
let CommsBuffer: string[] = []
let Loading_Bar = 0
let value = ""
let ActiveIDState: string[] = []
let ActiveIDFlag: number[] = []
let ActiveIDList: string[] = []
let MBState = "Start-Up"

radio.onDataPacketReceived(({ receivedString, signal }) => {
    if (signal >= Threshold_Power) {
        CommsBuffer.push(receivedString)
        basic.showLeds(`
            . . . . .
            . . . . #
            . . . # .
            # . # . .
            . # . . .
            `)
    } else {
        Loading_Screen()
    }
})
function Loading_Screen() {
    Loading_Bar += 1
    if (Loading_Bar == 1) {
        basic.showLeds(`
            . . # . .
            . . . . .
            . . . . .
            . . . . .
            . . . . .
            `)
    } else if (Loading_Bar == 2) {
        basic.showLeds(`
            . . . . .
            . . . # .
            . . . . .
            . . . . .
            . . . . .
            `)
    } else if (Loading_Bar == 3) {
        basic.showLeds(`
            . . . . .
            . . . . .
            . . . . #
            . . . . .
            . . . . .
            `)
    } else if (Loading_Bar == 4) {
        basic.showLeds(`
            . . . . .
            . . . . .
            . . . . .
            . . . # .
            . . . . .
            `)
    } else if (Loading_Bar == 5) {
        basic.showLeds(`
            . . . . .
            . . . . .
            . . . . .
            . . . . .
            . . # . .
            `)
    } else if (Loading_Bar == 6) {
        basic.showLeds(`
            . . . . .
            . . . . .
            . . . . .
            . # . . .
            . . . . .
            `)
    } else if (Loading_Bar == 7) {
        basic.showLeds(`
            . . . . .
            . . . . .
            # . . . .
            . . . . .
            . . . . .
            `)
    } else {
        basic.showLeds(`
            . . . . .
            . # . . .
            . . . . .
            . . . . .
            . . . . .
            `)
        Loading_Bar = 0
    }
}

basic.forever(() => {
    switch (MBState) {
        case "Start_Up":
            // Need to include some kind of start-up process with HUB
            // If start-up is ready, move to ready
            MBState = "Ready"
            break
        case "Ready":
            radio.sendString("MBMB " + control.deviceSerialNumber())
            BufferProcessing()
            break
        case "Reaction":
            // Need a function that:
            // -> Create screen animation for reaction
            // -> Clean all matrices
            MBState = "Ready"
            break
        default:
            MBState = "Start_Up"
    }

    basic.pause(500)
})

/********************************************* */
/**Read all messages received every 500ms      */
/********************************************* */
function BufferProcessing() {
    for (let value of CommsBuffer) {
        CmdProcess = value.substr(0, 4)
        if (CmdProcess == "MBMB") {
            MBMBProcessing(value.substr(5, value.length))
        } else if (CmdProcess == "MBHB") {
            serial.writeLine(value)
        } else if (CmdProcess == "HBMB") {
            HBMBProcessing(value.substr(5, value.length))
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
                radio.sendString("MBHB " + control.deviceSerialNumber() + "COLISSION" + ID)
                radio.setTransmitPower(0)
                break
            case "Waiting Hub":
                ActiveIDState[IDIndex] = "Send Hub"
                break
            default:
                break
        }

    } else {
        //serial.writeLine("ID: " + ID + " not in array. Inserting...")
        ActiveIDList.push(ID)
        ActiveIDFlag.push(1)
        ActiveIDState.push("Initial State")
    }
}

/*********************************** */
/**Function processing HBMB messages */
/*********************************** */
function HBMBProcessing(message: string) {
    // integration with Jukka
}

function isInArray(value: string, array: string[]) {
    return array.indexOf(value) > -1;
}

radio.setGroup(66)
radio.setTransmitPower(0)
Loading_Bar = 0
Threshold_Power = -63
CommsBuffer = []
CmdProcess = ""
ActiveIDList = []
ActiveIDFlag = []
ActiveIDState = []

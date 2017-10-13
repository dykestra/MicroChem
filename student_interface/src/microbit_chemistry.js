let symbol_len = 0
let str_elect_bal = ""
let packet_ok = 0
let chk_chars: number[] = []
let electron_balance = 0
let chem_symbol = ""
let sym_num = 0
let curr_page = 0
input.onButtonPressed(Button.A, () => {
    curr_page += -1
    show_page()
})
input.onButtonPressed(Button.B, () => {
    curr_page += 1
    show_page()
})
function show_page()  {
    if (curr_page == 0) {
        basic.showString(chem_symbol)
    } else {
        curr_page = 1
        basic.showNumber(electron_balance)
    }
}
radio.onDataPacketReceived( ({ receivedNumber, receivedString }) =>  {
    if (receivedNumber == sym_num) {
        basic.showString(receivedString)
        chk_chars = [0, 3, 5, receivedString.length - 1]
        for (let ch of chk_chars) {
            if (receivedString.charAt(ch) == "#") {
                packet_ok = 1
            } else {
                packet_ok = 0
                basic.showString("F:")
                basic.showNumber(ch)
            }
        }
        if (packet_ok == 1) {
            str_elect_bal = receivedString.substr(1, 2)
            symbol_len = receivedString.length - 7
            chem_symbol = receivedString.substr(6, symbol_len)
            electron_balance = parseInt(str_elect_bal)
        } else {
            radio.sendValue("symbol_num", sym_num)
        }
    } else {
        if (receivedNumber == -1) {
            sym_num = parseInt(receivedString)
            initialise_element()
        }
    }
    basic.showString(chem_symbol)
})
function set_symbol()  {
    sym_num = Math.random(6)
    initialise_element()
}
function attempt_compound()  {
    basic.showString("STUB")
}
function initialise_element()  {
    basic.showLeds(`
        . # . . .
        . . # . .
        . # # # .
        . . # . .
        . . . # .
        `)
    radio.sendValue("symbol_num", sym_num)
}
function check_packet()  {
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
radio.setGroup(83)
chem_symbol = "H"
electron_balance = -1
radio.setTransmitPower(7)
set_symbol()
radio.setTransmitPower(1)
curr_page = 0

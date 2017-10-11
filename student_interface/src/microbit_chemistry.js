let symbol_len = 0
let str_elect_bal = ""
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
function set_symbol()  {
    sym_num = Math.random(6)
    initialise_element()
}
function attempt_compound()  {
    basic.showString("STUB")
}
function initialise_element()  {
    basic.showString("SETUP")
    radio.sendValue("symbol_num", sym_num)
}
radio.onDataPacketReceived( ({ receivedNumber, receivedString }) =>  {
    if (receivedNumber == sym_num) {
        basic.showString(receivedString)
        str_elect_bal = receivedString.substr(0, 2)
        symbol_len = receivedString.length - 3
        chem_symbol = receivedString.substr(3, symbol_len)
        electron_balance = parseInt(str_elect_bal)
    } else {
        if (receivedNumber == -1) {
            sym_num = parseInt(receivedString)
            initialise_element()
        }
    }
    basic.showString(chem_symbol)
})
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

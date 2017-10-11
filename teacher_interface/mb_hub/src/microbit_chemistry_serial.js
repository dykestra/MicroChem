let curr_electron_bal = 0
let send_str = ""
let curr_symbol_int = 0
let str_electron_bal = ""
let curr_symbol = ""

function get_chem_data()  {
    led_breathe()
    serial.writeValue("symbol_int", curr_symbol_int)
    curr_symbol = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    str_electron_bal = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    curr_electron_bal = parseInt(str_electron_bal)
    send_str = "" + str_electron_bal + "_" + curr_symbol
    basic.showString("S:")
    basic.showString(send_str)
}

function chem_data_TEST()  {
    curr_symbol = "O"
    str_electron_bal = "-2"
    send_str = "" + str_electron_bal + "_" + curr_symbol
}

radio.onDataPacketReceived( ({ receivedString: name, receivedNumber: value }) =>  {
    if (name == "symbol_num") {
        curr_symbol_int = value
        get_chem_data()
        send_chem_data()
    } else {
        get_compound_data()
    }
    show_S()
})

function show_S()  {
    basic.showLeds(`
        . # # # .
        . # . . .
        . # # # .
        . . . # .
        . # # # .
        `)
}

function send_chem_data()  {
    radio.sendValue(send_str, curr_symbol_int)
}

function get_compound_data()  {
    led_breathe()
    basic.showString("STUB")
}

function led_breathe()  {
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
curr_electron_bal = -1
show_S()

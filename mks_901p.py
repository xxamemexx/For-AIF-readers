import serial
import time

kRESPONSE_SIZE = 100

class MKS_901p:
    
    def __init__(self):
        self.spinner = '|'
        self.pressure = "Comm!"
        self.units = "torr"
        self.pressureSciNote = "Comm!"

        try:

            #self.serialPort = serial.Serial(port = '/dev/tty.usbserial',
            self.serialPort = serial.Serial(port = 'COM7',
                                            baudrate = 9600,
                                            bytesize = serial.EIGHTBITS,
                                            parity = serial.PARITY_NONE,
                                            stopbits = serial.STOPBITS_ONE,
                                            timeout = 0.250,
                                        )
            
        except Exception as e:
            print(repr(e))
            raise  #re-raise the exception the the GUI can notify the user
            return

        # Give the serial port time to open because it's been reported pyserial
        # can crash if writing driectly after opening
        time.sleep(0.2)

        serial.Serial.write_timeout = 1.0
        self.setTorrMode()

    def setTorrMode(self):
      self.serialPort.write("@253U!TORR;FF".encode("utf-8"))
      buffer = self.serialPort.read(kRESPONSE_SIZE).decode("utf-8")

      # TODO check the response and raise an error if incorrect
      # print(buffer.decode("utf-8"))

    def getPressure(self):

        try:
            self.serialPort.write("@254PR3?;FF".encode("utf-8"))
        except Exception as e:
            print("Exception = " + repr(e))
            time.sleep(1)
            raise  #re-raise the exception the the GUI can notify the user
            return

        response = "1234"
        try:
            response = self.serialPort.read(kRESPONSE_SIZE).decode("utf-8")
        except Exception as e:
            print("Exception = " + repr(e))
            time.sleep(1)
            raise  #re-raise the exception the the GUI can notify the user
            return
           
        # Error communicating with sensor if less that 14 characters returned
        if (len(response) < 14):
            print("respones length < 14; = " + str(len(response)))
            time.sleep(1)

            self.pressure = "!Comm"
            self.pressureSciNote = "!Comm"

            self.serialPort.reset_input_buffer()
            self.serialPort.reset_output_buffer()
            self.setTorrMode()

        elif (response[0] != '@'):
            print("respone[0] != @, = ", response)
            time.sleep(1)

            self.pressure = "!Fmt"
            self.pressureSciNote = "!Fmt"
            self.serialPort.reset_input_buffer()
            self.serialPort.reset_output_buffer()

        else:
            
            # Get the 7 characters that make up the pressure from @253ACK7.61E+2;FF
            # to get 7.61E+2
            self.pressureSciNote = response[7:14]
            self.formatPressure(response[7:14])

        return self.pressure

    def formatPressure(self, pressureBuf):

        exponent = pressureBuf[6];      # Grab the exponent 2, 1, 0
        exponentSign = pressureBuf[5];  # Grab the exponent sign +/-

        millitorr = [ "-1", "-2", "-3" ]
        if pressureBuf[5:] in millitorr:
            self.units = "millitorr"
            
        else:
            self.units = "torr"

        # Display pressure as xxx.0
        if (((exponent == '2') and (exponentSign == '+')) or ((exponent == '1') and (exponentSign == '-'))):
            self.pressure = pressureBuf[0:1] + pressureBuf[2:4] + ".0"

        # Display pressure as xx.x
        elif (((exponent == '1') and (exponentSign == '+')) or ((exponent == '2') and (exponentSign == '-'))):
            self.pressure = pressureBuf[0:1] + pressureBuf[2:3] + "." + pressureBuf[3:4]

        # Display pressure as x.xx
        elif ((exponent == '0') or ((exponent == '3') and (exponentSign == '-'))):
            # Remove the exponent E+0 or E-3
            self.pressure = pressureBuf[0:4]

        # Display pressure as x.xxE-4 
        else:
            self.pressure = pressureBuf

    def dumpConfig(self):
        commands = ["@254PR1?;FF",
                    "@254PR2?;FF",
                    "@254PR3?;FF",
                    "@254PR4?;FF",
                    "@254BR?;FF",
                    "@254AD?;FF",
                    "@254RSD?;FF",
                    "@254MD?;FF",
                    "@254PN?;FF",
                    "@254DT?;FF",
                    "@254MF?;FF",
                    "@254HV?;FF",
                    "@254FV?;FF",
                    "@254SN?;FF",
                    "@254SW?;FF",
                    "@254TIM?;FF",
                    "@254TEM?;FF",
                    "@254UT?;FF",
                    "@254T?;FF",
                    "@254U?;FF",
                    "@254GT?;FF",
                    "@254VAC?;FF",
                    "@254ATM?;FF",
                    "@254AO1?;FF",
                    "@254AO2?;FF" ]

        for cmd in commands:
            self.serialPort.write(cmd.encode("utf-8"))
            buffer = self.serialPort.read(kRESPONSE_SIZE)
            print(cmd + " " + buffer.decode("utf-8")) 

        
    def nextSpinner(self):
        if self.spinner == '|':
            self.spinner = '/'
        elif self.spinner == '/':
            self.spinner = '-'
        elif self.spinner == '-':
            self.spinner = '\\'            
        else:
            self.spinner = '|'
        return self.spinner


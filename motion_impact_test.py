import serial
import time
import keyboard
import random
import math
import trig

class Irobot():
    pass

    def __init__(self, port, baudrate):
        # Defaults set to COM6 and 57600 baud. 
        # The robot should always be run from 57600 baud unless not possible with the hardware.
        # COM6 would be a default on windows. Linux will require some '/dev/ttyUSB[port]'.
        self.ser = serial.Serial(port='/dev/ttyUSB0', baudrate=57600)
        self.safe_start()
        
    # Starts the robot up in safe mode to prevent overheating, crashes, etc. Gives the robot time to sleep before operation.
    # As you may notice, the way all of these methods work is through sending serial over UART to the robot.
    def safe_start(self):
        self.ser.write(b'\x80')
        self.ser.write(b'\x84')
        time.sleep(3)

    #Takes in a distance and a speed to move the robot. Distance can be positive or negative. Speed should be positive.
    def move(self, distance, speed):
        array = bytearray()
        # Start code for movement.
        start_code = 145

        # These lines of code determine how long the robot will run for based on its speed and distance.
        seconds = 0.0
        seconds = distance/speed
        seconds = abs(seconds)

        # A check for whether or not the speed is positive or negative.
        # Because of the way these robots function with serial commands, there has to be a 
        # two's complement transformation done to reverse the robot.
        if (distance > 0):
            speed = speed
            low_byte = 0
            high_byte = speed

        if (distance < 0):
            temp1 = 0xFF
            temp2 = speed
            temp3 = temp2 ^ temp1 
            temp3 = temp3 + 0x01
            low_byte = 255
            high_byte = int(temp3)
        
        # Appends all required data to the array to be sent to the robot.
        array.append(start_code)
        array.append(low_byte)
        array.append(high_byte)
        array.append(low_byte)
        array.append(high_byte)

        # print(array)
        self.ser.write(array)
        # print (seconds)
        time.sleep(seconds)
        self.ser.write(b'\x89\x00\x00\x00\x00')

    def turn(self, degrees):
        array = bytearray()
        array.append(137)
        if (degrees < 0):
            newDeg = int((255+56) / (90/degrees))
            lowByte = int(newDeg - 255)
            array.append(255)
            degrees = abs(degrees)
            array.append(lowByte)            
        else:
            newDeg = int(200 / (90/degrees))
            if newDeg < 255 and newDeg >= 0:
                array.append(0)
                array.append(newDeg)
            else:
                temp = newDeg % 255
                array.append(temp)
                array.append(255)

        # if (left_right):
        #     array.append(0)
        #     array.append(200)
        # else:
        #     array.append(255)
        #     array.append(55)
        array.append(0)
        array.append(0)

        self.ser.write(array)
        time.sleep(1.1)
        self.ser.write(b'\x89\x00\x00\x00\x00')



def test_control():
    robot =  robot = Irobot('/dev/ttyUSB0', 57600)
    count = 0
    while (count < 50):
        count += 1
        check = random.randint(1,3)
        if (check == 1):
            robot.move(200,25)
        elif (check == 2):
            robot.move(-200,25)
        elif (check == 3):
            robot.turn(15)  

    robot.ser.close()

if __name__ == '__main__':
    test_control()
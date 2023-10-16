#   _______          _
#  |__   __|        | |
#     | |_   _ _ __ | |__   ___   ___  _ __
#     | | | | | '_ \| '_ \ / _ \ / _ \| '_ \
#     | | |_| | |_) | | | | (_) | (_) | | | |
#     |_|\__, | .__/|_| |_|\___/ \___/|_| |_|
#         __/ | |
#        |___/|_|

import math
import time
import struct
import serial  # pip install pyserial


class Typhoon():
    def __init__(self, port: str, length_upper_arm: int = 135, length_lower_arm: int = 170, distance_tool: int = 135, distance_z: int = 0, height_from_ground: int = 135):
        # self.arduino_serial = serial.Serial(port, 115200)
        # time.sleep(1.5)
        # self.arduino_serial.flushInput()

        self.LENGTH_UPPER_ARM = length_upper_arm
        self.LENGTH_LOWER_ARM = length_lower_arm
        self.DISTANCE_TOOL = distance_tool
        self.DISTANCE_Z = distance_z
        self.HEIGTH_FROM_GROUND = height_from_ground
        self.LENGTH_REAR_SQUARED = pow(self.LENGTH_UPPER_ARM, 2)
        self.LENGTH_FRONT_SQUARED = pow(self.LENGTH_LOWER_ARM, 2)
        self.PI_HALF = math.pi / 2

    def angles_from_coordinates(self, x: int, y: int, z: int):
        x += self.DISTANCE_TOOL
        z += self.DISTANCE_Z
        radius = math.sqrt(pow(x, 2) + pow(y, 2))

        base_angle = math.atan2(y, x)
        actual_z = self.HEIGTH_FROM_GROUND - z
        hypotenuse_squared = pow(actual_z, 2) + pow(radius, 2)
        hypotenuse = math.sqrt(hypotenuse_squared)

        rear_angle = math.atan(radius / actual_z) + math.acos(self.LENGTH_REAR_SQUARED - self.LENGTH_FRONT_SQUARED + hypotenuse_squared) / (2 * self.LENGTH_UPPER_ARM * hypotenuse)
        front_angle = math.acos(self.LENGTH_REAR_SQUARED + self.LENGTH_FRONT_SQUARED - hypotenuse_squared) / (2 * self.LENGTH_UPPER_ARM * self.LENGTH_LOWER_ARM)

        # return base_angle * 180 / math.pi, -rear_angle * 180 / math.pi + 67.9130669909833, 77.87547181797633 - front_angle * 180 / math.pi
        return math.degrees(base_angle), math.degrees(-rear_angle) + 67.9130669909833, 77.87547181797633 - math.degrees(front_angle)

    def send_x_y_z_pw(self, x: int, y: int, z: int, pw8: int = 0, pw9: int = 0, pw10: int = 0):
        base_angle, upper_angle, lover_angle = self.angles_from_coordinates(x, y, z)

        # Poslat data do typhoonu
        self.arduino_serial.write(struct.pack("f", base_angle))
        self.arduino_serial.write(struct.pack("f", lover_angle))
        # hodnota pre nastroj v D8
        self.arduino_serial.write(struct.pack("f", upper_angle))
        # hodnota pre nastroj v D9
        self.arduino_serial.write(struct.pack("f", pw8))
        # hodnota pre nastroj v D10
        self.arduino_serial.write(struct.pack("f", pw9))
        self.arduino_serial.write(struct.pack("f", pw10))

        for _ in range(0, 9):  # podla poctu Serial.println v firmware-arduino
            print(">>", self.arduino_serial.readline().strip().decode("utf-8"))

    def send_file(self, file_path: str):
        _file = open(file_path, "r")

        for line in _file:
            line = line.strip().split()
            x = float(line[0])
            y = float(line[1])
            z = float(line[2])
            pw8 = float(line[3])  # 0 ... 255
            pw9 = float(line[4])  # 0 ... 255
            pw10 = float(line[5])  # 0 ... 255

            self.send_x_y_z_pw(x, y, z, pw8, pw9, pw10)

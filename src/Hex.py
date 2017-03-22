#!/usr/bin/python

"""
Copyright (C) 2012-2017 Kirill Kulakov, Jose Carlos Granja & Xerxes Ranby

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys


class Hex:
    def __init__(self, fileName):
        self.memory = [0] * 0x8000
        self.havememory = [0] * (0x8000/0x20)
        self.eeprom = [0] * 0x100
        self.haveeeprom = [0] * (0x100/0x20)

        self.id = [0] * 0x8


        self.offset = 0
        self.fuseValue = [0] * 0xF
        self.fuseStatus = [0] * 0xF
        self.fuseMask = [0] * 0xF

        fileSize = int(os.path.getsize(fileName))
        hexFile = open(fileName, 'r')

        for i in range(0x8000):
            self.memory[i] = 0xFF
            self.havememory[i/0x20] = 0
        for i in range(0x100):
            self.eeprom[i] = 0
            self.haveeeprom[i/0x20] = 0
        for i in range(0x8):
            self.id[i] = 0
            self.haveid = 0
        for i in range(0x0F):
            self.fuseStatus[i] = 0

        # Fuse values default unprogrammed value
        # 39622L page 29
        self.fuseValue[0] = int('00000000', 2)
        self.fuseValue[1] = int('00000101', 2) # TODO Unprogrammed value differ for PIC18F2455/2550/4455/4550 and PIC18F2458/2553/4458/4553 devices
        self.fuseValue[2] = int('00011111', 2)
        self.fuseValue[3] = int('00011111', 2)
        self.fuseValue[4] = int('00000000', 2)
        self.fuseValue[5] = int('10000011', 2)
        self.fuseValue[6] = int('10000101', 2)
        self.fuseValue[7] = int('00000000', 2)
        self.fuseValue[8] = int('00111111', 2)
        self.fuseValue[9] = int('11000000', 2)
        self.fuseValue[10] = int('00111111', 2)
        self.fuseValue[11] = int('11100000', 2)
        self.fuseValue[12] = int('00111111', 2)
        self.fuseValue[13] = int('01000000', 2)

        # Unimplemented fuse bits will read as 0
        # 39622L page 29
        self.fuseMask[0] = int('00111111', 2)
        self.fuseMask[1] = int('11001111', 2)
        self.fuseMask[2] = int('00111111', 2)
        self.fuseMask[3] = int('00011111', 2)
        self.fuseMask[4] = int('00000000', 2)
        self.fuseMask[5] = int('10000111', 2) # TODO Mask differ for PIC18F2455/2550/4455/4550 and PIC18F2458/2553/4458/4553 devices
        self.fuseMask[6] = int('11000101', 2) # TODO Mask differ for PIC18F2455/2550/4455/4550 and PIC18F2458/2553/4458/4553 devices
        self.fuseMask[7] = int('00000000', 2)
        self.fuseMask[8] = int('00001111', 2) # TODO Mask differ for PIC18F2455/2550/4455/4550 and PIC18F2458/2553/4458/4553 devices
        self.fuseMask[9] = int('11000000', 2)
        self.fuseMask[10] = int('00001111', 2) # TODO Mask differ for PIC18F2455/2550/4455/4550 and PIC18F2458/2553/4458/4553 devices
        self.fuseMask[11] = int('11100000', 2)
        self.fuseMask[12] = int('00001111', 2) # TODO Mask differ for PIC18F2455/2550/4455/4550 and PIC18F2458/2553/4458/4553 devices
        self.fuseMask[13] = int('01000000', 2)

        while True:
            buf = hexFile.readline(128).translate(None, ':\n')
            if buf == "":
                break
            if self.reformat(buf) == 1:
                print "Hex file not valid."
                sys.exit(2)
        hexFile.close()

    def getData(self, address):
        return self.memory[address]

    def haveData(self, address):
            return self.havememory[address/0x20]

    def getEEPROM(self, address):
        return self.eeprom[address]

    def haveEEPROM(self, address):
        return self.haveeeprom[address/0x20]

    def getID(self, address):
        return self.id[address]

    def haveID(self):
        return self.haveid

    def fuseChanged(self, fuseID):
        return self.fuseStatus[fuseID]

    def getFuse(self, fuseID):
        return self.fuseValue[fuseID]

    def getFuseMask(self, fuseID):
        return self.fuseMask[fuseID]

    # HEX parser
    def reformat(self, hexData):
        buf = hexData

        # comment
        if hexData.startswith(";"):
            print hexData
            return 0

        iSize, buf = int(buf[:2], 16), buf[2:]
        if iSize == -1:
            return 1
        iAddress, buf = int(buf[:4], 16), buf[4:]
        if iAddress == -1:
            return 1
        # record type
        iRecord = int(buf[:2], 16)

        if iRecord == -1:
            return 1
        elif iRecord == 4:

            buf = buf[2:]
            temp = int(buf[:2], 16)
            if temp == -1:
                return 1
            self.offset += temp << 24
            buf = buf[2:]
            temp = int(buf[:2], 16)
            if temp == -1:
                return 1
            self.offset = temp << 16

        elif iRecord == 2:

            buf = buf[2:]
            temp = int(buf[:2], 16)
            if temp == -1:
                return 1
            self.offset += temp << 12
            buf = buf[2:]
            temp = int(buf[:2], 16)
            if temp == -1:
                return 1
            self.offset = temp << 4

        elif iRecord == 0:

            # Memory
            if (iAddress + self.offset) < 0x8000:
                for i in range(iSize / 2):
                    buf = buf[2:]

                    self.memory[iAddress + i * 2 + self.offset] = int(buf[:2], 16)
                    if self.memory[iAddress + i * 2 + self.offset] == -1:
                        return 1

                    self.havememory[(iAddress + i * 2 + self.offset)/0x20] = 1

                    buf = buf[2:]
                    self.memory[iAddress + i * 2 + self.offset + 1] = int(buf[:2], 16)
                    if self.memory[iAddress + i * 2 + self.offset + 1] == -1:
                        return 1

                    self.havememory[(iAddress + i * 2 + self.offset + 1)/0x20] = 1

            # Id
            elif iAddress + self.offset >= 0x200000 and iAddress + self.offset <= 0x200007:
                for i in range(iSize):
                    buf = buf[2:]
                    self.id[iAddress + self.offset + i - 0x200000] = int(buf[:2], 16)
                    if int(buf[:2], 16) == -1:
                        return 1

                    self.haveid = 1

            # Fuse values
            elif iAddress + self.offset >= 0x300000 and iAddress + self.offset <= 0x30000F:
                for i in range(iSize):
                    buf = buf[2:]
                    self.fuseValue[iAddress + self.offset + i - 0x300000] = int(buf[:2], 16)
                    if int(buf[:2], 16) == -1:
                        return 1

                    self.fuseStatus[iAddress + self.offset + i - 0x300000] = 1

            # EEPROM
            elif (iAddress + self.offset) >= 0xF00000 and iAddress + self.offset <= 0xF000FF:
                for i in range(iSize / 2):
                    buf = buf[2:]
                    self.eeprom[iAddress + i * 2 + self.offset - 0xF00000] = int(buf[:2], 16)
                    if self.eeprom[iAddress + i * 2 + self.offset - 0xF00000] == -1:
                        return 1

                    self.haveeeprom[(iAddress + i * 2 + self.offset - 0xF00000)/0x20] = 1

                    buf = buf[2:]
                    self.eeprom[iAddress + i * 2 + self.offset - 0xF00000 + 1] = int(buf[:2], 16)
                    if self.eeprom[iAddress + i * 2 + self.offset - 0xF00000 + 1] == -1:
                        return 1

                    self.haveeeprom[(iAddress + i * 2 + self.offset - 0xF00000 + 1)/0x20] = 1

            # Unknown data
            else:
                print hex(iAddress + self.offset)
                return 1
        return 0

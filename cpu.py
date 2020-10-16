"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self, ram=None, reg=None):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.fl = 0
        self.instructions = {
            "LDI":  0b10000010,
            "HLT":  0b00000001,
            "PRN":  0b01000111,
            "MUL":  0b10100010,
            "PUSH": 0b01000101,
            "POP":  0b01000110,
            "CALL": 0b01010000,
            "RET": 0b00010001,
            "ADD": 0b10100000,
            "CMP": 0b10100111,
            "JEQ": 0b01010101,
            "JMP": 0b01010100,
            "JNE": 0b01010110
        }
        self.reg[7] = 0xf4

    def load(self, file):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        if len(sys.argv) != 2:
            print("usage: ls8.py progname")
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    line = line.strip()
                    if line == "" or line[0] == "#":
                        continue
                    try:
                        str_value = line.split("#")[0]
                        # For project, change to base 2 (binary)
                        value = int(str_value, 2)
                    except ValueError:
                        print(f"Invalid number: {str_value}")
                        sys.exit(1)

                    self.ram_write(address, value)
                    address += 1
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')
    
    


    def run(self):
        """Run the CPU."""
        running = True
        SP = 7
        def push_val(value):
            self.reg[SP] -= 1
            top_of_stack_addr = self.reg[SP]
            self.ram[top_of_stack_addr] = value

        def pop_val():
            top_of_stack_addr = self.reg[SP]
            value = self.ram[top_of_stack_addr]
            self.reg[SP] += 1
            return value

        while running:
            # self.trace()
            instruction = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            # If instruction is LDI
            # print(operand_a)
            if instruction == self.instructions["LDI"]:
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif instruction == self.instructions["PRN"]:
                print(self.reg[operand_a])
                self.pc += 2
            elif instruction == self.instructions["HLT"]:
                self.pc = 0
                running = False
            elif instruction == self.instructions["MUL"]:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            elif instruction == self.instructions["ADD"]:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3
            elif instruction == self.instructions["PUSH"]:
                self.reg[SP] -= 1
                value = self.reg[operand_a]
                top_of_stack_addr = self.reg[SP]
                self.ram[top_of_stack_addr] = value
                self.pc += 2
            elif instruction == self.instructions["POP"]:
                top_of_stack_addr = self.reg[SP]
                value = self.ram[top_of_stack_addr]
                reg_num = operand_a
                self.reg[reg_num] = value
                self.reg[SP] += 1
                self.pc += 2
            elif instruction == self.instructions["CALL"]:
                return_addr = self.pc + 2
                push_val(return_addr)
                reg_num = operand_a
                subroutine_addr = self.reg[reg_num]
                self.pc = subroutine_addr

            elif instruction == self.instructions["RET"]:
                return_addr = pop_val()
                self.pc = return_addr
            elif instruction == self.instructions["CMP"]:
                val_one = self.reg[operand_a]
                val_two = self.reg[operand_b]
                if val_one == val_two:
                    self.fl = 1
                elif val_one < val_two:
                    self.fl = 4
                elif val_one > val_two:
                    self.fl = 2
                self.pc += 3
            elif instruction == self.instructions["JEQ"]:
                if self.fl == 1:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            elif instruction == self.instructions["JMP"]:
                self.pc = self.reg[operand_a]
            elif instruction == self.instructions["JNE"]:
                if self.fl == 2 or self.fl == 4:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            else:
                print(
                    f"unknown instruction {instruction} at address {self.pc}")


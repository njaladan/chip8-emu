import struct, array, sys, time, random
from display import Display
from utils import BUILT_IN_FONT, KEY_MAPPING
import pygame


EXECUTE_DELAY = 1 # milliseconds
TIMER = pygame.USEREVENT + 1


filepath = "./games/GUESS"



class CPU:
    def __init__(self, program):
        self.registers = [0] * 16 # 8 bits each
        self.instruction_pointer = 0 # 16 bits
        self.program_counter = 0x200 # 16 bits
        self.memory = bytearray(4096) # 4k memory
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = list()
        self.display = Display()
        self.initialize_memory(program)


    def initialize_memory(self, program):
        program_offset = 0x200
        for i in range(len(program)):
            self.memory[program_offset + i] = program[i]
        self.memory[0x0050:0x00A0] = BUILT_IN_FONT


    def emulate(self):
        counter = 0
        running = True

        pygame.time.set_timer(TIMER, EXECUTE_DELAY)

        
        while running:
            pygame.time.wait(EXECUTE_DELAY)
            self.emulate_cycle()
            counter += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == TIMER:
                    self.decrement_timers()


        pygame.display.quit()
        pygame.quit()
        print(counter)


    def emulate_cycle(self):

        opcode_byte1 = self.memory[self.program_counter]
        opcode_byte2 = self.memory[self.program_counter + 1]
        opcode = (opcode_byte1 << 8) | opcode_byte2
        top = opcode >> 12

        address = opcode & 0x0fff
        regx = (opcode & 0x0f00) >> 8
        regy = (opcode & 0x00f0) >> 4
        byte = opcode & 0x00ff
        nibble = opcode & 0x000f


        # taken from disassembler; check for errors
        if top == 0:
            # 0x00E0: clear display
            if address == 0x0e0:
                self.display.clear_screen()
                self.program_counter += 2

            # 0x00EE: return from subroutine
            elif address == 0x0ee:
                if self.stack:
                    self.program_counter = self.stack.pop()
                else:
                    print("Invalid return")
                    exit(1)

            # 0x0NNN: run on RCA-1802
            else:
                print("Not running RCA 1802 program; skipping")
                self.program_counter += 2

        # 0x1NNN: jump to address NNN
        elif top == 1:
            self.program_counter = address

        # 0x2NNN: call subroutine at address NNN
        elif top == 2:
            self.stack.append(self.program_counter + 2)
            self.program_counter = address

        # 0x3XNN: skip next line if Vx == NN
        elif top == 3:
            if self.registers[regx] == byte:
                self.program_counter += 4
            else:
                self.program_counter += 2

        # 0x4XNN: skip next line if Vx != NN
        elif top == 4:
            if self.registers[regx] != byte:
                self.program_counter += 4
            else:
                self.program_counter += 2

        # 0x5XY0: skip next line if Vx == Vy
        elif top == 5:
            if self.registers[regx] == self.registers[regy]:
                self.program_counter += 4
            else:
                self.program_counter += 2

        # 0x6XNN: set Vx to NN
        elif top == 6:
            self.registers[regx] = byte
            self.program_counter += 2

        # 0x7XNN: add NN to Vx
        elif top == 7:
            self.registers[regx] = (self.registers[regx] + byte) & 0xff
            self.program_counter += 2

        # Bitwise / math operations
        elif top == 8:

            # 0x8XY0: set Vx = Vy
            if nibble == 0:
                self.registers[regx] = self.registers[regy]

            # 0x8XY1: Vx = Vx OR Vy
            elif nibble == 1:
                self.registers[regx] = self.registers[regx] | self.registers[regy]

            # 0x8XY2: Vx = Vx AND Vy
            elif nibble == 2:
                self.registers[regx] = self.registers[regx] & self.registers[regy]

            # 0x8XY3: Vx = Vx XOR Vy
            elif nibble == 3:
                self.registers[regx] = self.registers[regx] ^ self.registers[regy]

            # 0x8XY4: Vx = Vx + Vy; Vf overflow
            elif nibble == 4:
                added = self.registers[regx] + self.registers[regy]
                self.registers[regx] = added & 0xff
                self.registers[0xf] = int((added >> 8) > 0)

            # 0x8XY5: Vx = Vx - Vy; Vf overflow
            elif nibble == 5:
                borrow = 1
                subtracted = self.registers[regx] - self.registers[regy]
                if subtracted < 0:
                    subtracted = (self.registers[regx] & (1 << 8)) - self.registers[regy]
                    borrow = 0
                self.registers[regx] = subtracted
                self.registers[0xf] = borrow

            # 0x8XY6: LSB(Vx) -> Vf; Vx = Vx >> 1
            elif nibble == 6:
                lsb = self.registers[regx] & 0x1
                self.registers[regx] = self.registers[regx] >> 1
                self.registers[0xf] = lsb

            # 0x8XY7: Vx = Vy - Vx; Vf overflow
            elif nibble == 7:
                borrow = 1
                subtracted = self.registers[regy] - self.registers[regx]
                if subtracted < 0:
                    subtracted = (self.registers[regy] & (1 << 8)) - self.registers[regx]
                    borrow = 0
                self.registers[regx] = subtracted
                self.registers[0xf] = borrow


            # 0x8XYE: MSB(Vx) -> Vf; Vx = Vx << 1
            elif nibble == 0xe:
                msb = (self.registers[regx] & 0x80) >> 7
                self.registers[regx] = self.registers[regx] << 1
                self.registers[0xf] = msb

            else:
                print("Invalid instruction; skipping")

            self.program_counter += 2

        # 0x9XY0: skip next line if Vx != Vy
        elif top == 9:
            if self.registers[regx] != self.registers[regy]:
                self.program_counter += 4
            else:
                self.program_counter += 2

        # 0xANNN: set instruction pointer to address
        elif top == 0xa:
            self.instruction_pointer = address
            self.program_counter += 2

        # 0xBNNN: jump to address plus offset V0
        elif top == 0xb:
            self.program_counter = address + self.registers[0]

        # 0xCYNN: set Vx to bitwise AND on random bits and byte
        elif top == 0xc:
            self.registers[regx] = random.randrange(255) & byte
            self.program_counter += 2

        # 0xDXYN: draw sprite at (X, Y) with height N
        elif top == 0xd:
            if self.instruction_pointer < 4096:
                start_ind = self.instruction_pointer
                end_ind = self.instruction_pointer + nibble
                sprite = self.memory[start_ind:end_ind]
                x_coord = self.registers[regx]
                y_coord = self.registers[regy]
                flag = self.display.draw_sprite(x_coord, y_coord, sprite)
                self.registers[0xf] = flag
            self.program_counter += 2

        # keyboard operations
        elif top == 0xe:
            key_val = self.registers[regx]
            mapped_key = KEY_MAPPING[key_val]
            keys = pygame.key.get_pressed()
            keypress = keys[mapped_key]
            
            if byte == 0x9e:
                if keypress:
                    self.program_counter += 4
                else:
                    self.program_counter += 2

            elif byte == 0xa1:
                if keypress:
                    self.program_counter += 2
                else:
                    self.program_counter += 4

            else:
                print("Invalid instruction; skipping")

        # misc. operations
        elif top == 0xf:
            # 0xFX07: set Vx to delay timer
            if byte == 0x07:
                self.registers[regx] = self.delay_timer

            # 0xFX0A: await and set key press into Vx
            elif byte == 0x0a:
                key_pressed = False
                while not key_pressed:
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN:
                        keys_pressed = pygame.key.get_pressed()
                        for keyval, lookup_key in KEY_MAPPING.items():
                            if keys_pressed[lookup_key]:
                                self.registers[regx] = keyval
                                key_pressed = True
                                break
                    
            # 0xFX15: set delay timer to Vx
            elif byte == 0x15:
                self.delay_timer = self.registers[regx]

            # 0xFX18: set sound timer to Vx
            elif byte == 0x18:
                self.sound_timer = self.registers[regx]

            # 0xFX1E: increment instruction pointer by Vx
            elif byte == 0x1e:
                self.instruction_pointer += self.registers[regx]

            # 0xFX29: set instruction pointer to hex digit in Vx
            elif byte == 0x29:
                if self.registers[regx] < 0x10:
                    self.instruction_pointer = 0x0050 + self.registers[regx] * 5 # offset for font location
                else:
                    print("Invalid sprite map input; skipping")

            # 0xFX33: place binary-coded representation in memory
            elif byte == 0x33:
                value = self.registers[regx]
                hundreds = value // 100
                tens = (value % 100) // 10
                ones = value % 10
                if self.instruction_pointer < 4096:
                    self.memory[self.instruction_pointer] = hundreds
                    self.memory[self.instruction_pointer + 1] = tens
                    self.memory[self.instruction_pointer + 2] = ones

            # 0xFX55: store registers V0 to Vx in memory
            elif byte == 0x55:
                if self.instruction_pointer >= 4096:
                    print("Invalid address; skipping")
                start_ind = self.instruction_pointer
                end_ind = self.instruction_pointer + regx + 1
                self.memory[start_ind:end_ind] = self.registers[:regx + 1]

            # 0xFX65: load registers V0 to Vx from memory
            elif byte == 0x65:
                if self.instruction_pointer >= 4096:
                    print("Invalid address; skipping")
                start_ind = self.instruction_pointer
                end_ind = self.instruction_pointer + regx + 1
                self.registers[:regx + 1] = self.memory[start_ind:end_ind]

            else:
                print("Invalid instruction; skipping")

            self.program_counter += 2

        else:
            raise ValueError


    def decrement_timers(self):
        self.sound_timer = max(0, self.sound_timer - 1)
        self.delay_timer = max(0, self.delay_timer - 1)




class Game:
    def __init__(self, filename):
        with open(filename, 'rb') as f:
            self.game = CPU(f.read())

    def emulate(self):
        self.game.emulate()



game = Game(filepath)


game.emulate()

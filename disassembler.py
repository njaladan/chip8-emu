import struct, array, sys

with open("15PUZZLE", 'rb') as f:
    game = array.array("H", f.read())
    if sys.byteorder != 'big':
        game.byteswap()

counter = 0x200
addressmask = 0x0fff
regxmask = 0x0f00
regymask = 0x00f0
bytemask = 0x00ff
nibblemask = 0x000f

print(" ADDR  |  INST  |  MEANING")

for opcode in game:
    strop = '0x' + hex(opcode)[2:].zfill(4)
    memadd = '0x' + hex(counter)[2:].zfill(4)
    address = hex(opcode & addressmask)
    address_val = opcode & addressmask
    regx = hex((opcode & regxmask) >> 8)[2:].upper()
    regy = hex((opcode & regymask) >> 4)[2:].upper()
    byte = hex(opcode & bytemask)
    nibble = hex(opcode & nibblemask)
    top = opcode >> 12
    bottomnibble = opcode & nibblemask
    bottombyte = opcode & bytemask

    print(memadd, strop, end=' | ', sep=" | ")


    if top == 0:
        if address_val == 0x0e0:
            print("CLEAR DISP")
        elif address_val == 0x0ee:
            print("RETURN")
        else:
            print("call rca 1802 on address {0}".format(address))
    elif top == 1:
        print("JUMP " + address)
    elif top == 2:
        print("CALL " + address)
    elif top == 3:
        print("skip next if V{0} == {1}".format(regx, byte))
    elif top == 4:
        print("skip next if V{0} != {1}".format(regx, byte))
    elif top == 5:
        print("skip next if V{0} == V{1}".format(regx, regy))
    elif top == 6:
        print("V{0} = {1}".format(regx, byte))
    elif top == 7:
        print("V{0} = V{0} + {1}".format(regx, byte))
    elif top == 8:
        if bottomnibble == 0:
            print("V{0} = V{1}".format(regx, regy))
        elif bottomnibble == 1:
            print("V{0} = V{0} || V{1}".format(regx, regy))
        elif bottomnibble == 2:
            print("V{0} = V{0} && V{1}".format(regx, regy))
        elif bottomnibble == 3:
            print("V{0} = V{0} ^ V{1}".format(regx, regy))
        elif bottomnibble == 4:
            print("V{0} = V{0} + V{1}, VF = 1 when carry".format(regx, regy))
        elif bottomnibble == 5:
            print("V{0} = V{0} - V{1}, VF = 1 when no borrow".format(regx, regy))
        elif bottomnibble == 6:
            print("V{0} >> 1, store LSB in VF".format(regx, regy))
        elif bottomnibble == 7:
            print("V{0} = V{1} - V{0}, VF = 1 when no borrow".format(regx, regy))
        elif bottomnibble == 0xe:
            print("V{0} << 1, store MSB in VF".format(regx, regy))
        else:
            print("cannot decode instruction")
    elif top == 9:
        print("skip next if V{0} != V{1}".format(regx, regy))
    elif top == 0xa:
        print("I = {0}".format(address))
    elif top == 0xb:
        print("jump to address {0} plus V0".format(address))
    elif top == 0xc:
        print("V{0} = V{0} && rand()".format(regx))
    elif top == 0xd:
        print("draw sprite at ({0}, {1}) with height {2}".format(regx, regy, nibble))
    elif top == 0xe:
        if bottombyte == 0x9e:
            print("skip next instruction if key stored in V{0} is pressed".format(regx))
        elif bottombyte == 0xa1:
            print("skip next instruction if key stored in V{0} is NOT pressed".format(regx))
        else:
            print("cannot decode")
    elif top == 0xf:
        if bottombyte == 0x07:
            print("set V{0} to the value of the delay timer".format(regx))
        elif bottombyte == 0x0a:
            print("wait for key press, store in V{0}".format(regx))
        elif bottombyte == 0x15:
            print("set delay timer to V{0}".format(regx))
        elif bottombyte == 0x18:
            print("set sound timer to V{0}".format(regx))
        elif bottombyte == 0x1e:
            print("I = I + V{0}".format(regx))
        elif bottombyte == 0x29:
            print("I = sprite_adder[V{0}]".format(regx))
        elif bottombyte == 0x33:
            print("binary coded decimal thing")
        elif bottombyte == 0x55:
            print("register dump up to V{0}".format(regx))
        elif bottombyte == 0x65:
            print("register load up to V{0}".format(regx))
        else:
            print("cannot decode instruction")
    else:
        print("bug")
        raise ValueError

    counter += 2

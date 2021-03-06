# Chip8-emu

CHIP-8 is an interpreted programming language from the mid-1970s. This is a fully working emulator for it in Python. It's still in its early stages, but it works and is pretty stable at the moment.

I've included the most popular ROMs for Chip 8 as well, as they're in the public domain. Enjoy!


## Things to do
- [x] Implement opcodes
- [x] Active visual display
- [x] Sound and sound timers
- [x] Implement user input from keyboard
- [ ] Write tests
- [ ] Make venv compatible
- [ ] Add legacy compatibility (pre-1985ish)
- [ ] Polish up disassembler



## Input
CHIP-8 uses a hexadecimal input scheme, ranging from 0-F. The keyboard mapping for PyGame is shown below.

| CHIP-8 Button | Keyboard button |
| --- | --- |
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | q |
| 5 | w |
| 6 | e |
| 7 | a |
| 8 | s |
| 9 | d |
| A | z |
| B | c |
| C | 4 |
| D | r |
| E | f |
| F | v |
| 0 | x |


## License
[MIT License.](https://opensource.org/licenses/MIT)

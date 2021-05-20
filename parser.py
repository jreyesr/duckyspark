#!/usr/bin/env python3
import typer
from typing import List
from pathlib import Path
import sys

def is_modifier_combo(text: str) -> bool:
    """
    Determines if the passed string is a combination of modifier keys, such as CTRL-ALT-SHIFT-WINDOWS

    Used, for example, in the commands CTRL-SHIFT ESCAPE or CTRL+ALT DELETE

    Returns a list of all the modifiers in the string, or an empty list if the string is not purely composed of modifiers
    """
    VALID_MODIFIERS = ("CTRL", "ALT", "SHIFT", "WINDOWS", "MENU")
    assert " " not in text, "Pass only the first word in a command to is_modifier_combo"
    pieces = text.split("-")
    if not all([p in VALID_MODIFIERS for p in pieces]):
        return []
    return pieces # all the elements of pieces are guaranted to be modifiers


def process(i: int, file: Path):
    def process_line(line: str, out: List[str]):
        if line.startswith("REM "):
            safe = line.replace("*/", "* /") # Prevent comments from accidentally closing the C block comment
            out.append(f'/* Automatic comment: {safe[4:]} */')
        elif line.startswith("STRING "):
            out.append(f'DigiKeyboard.print("{line[7:]}");')
        elif line.startswith("DELAY "):
            delay = int(line[6:])*10
            out.append(f'DigiKeyboard.delay({delay});')
        # DEFAULTDELAY / DEFAULT_DELAY
        elif line.startswith("WINDOWS "):
            char = line[8:]
            assert len(char) == 1, "Send a single char after the Windows key, not {char}"
            out.append(f'DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + (\'{char}\' - 0x20)), MODIFIERKEY_GUI);')
        elif line.startswith("SHIFT "):
            char = line[6:]
            assert len(char) == 1, "Send a single char after the Shift key, not {char}"
            out.append(f'DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + (\'{char}\' - 0x20)), MODIFIERKEY_SHIFT);')
        elif line.startswith("LIGHTS ON "):
            _, _, target, r, g, b = line.split(" ")
            if target == "self": target = i
            out.append(f'pixels.setPixelColor({target}, _COLOR({r},{g},{b}));\npixels.show();')
        elif line.startswith("LIGHTS OFF "):
            _, _, target = line.split(" ")
            if target == "self": target = i
            out.append(f'pixels.setPixelColor({target}, 0);\npixels.show();')
        else:
            print(f"ERROR: Command in line {line} not recognized", file=sys.stderr)
        # MENU/APP
        # ALT
        # CONTROL
        # ARROW KEYS (UP, DOWN, LEFT, RIGHT)
        # FUNCTION KEYS
        # COMBINATIONS OF MODIFIERS

    if not file.name.endswith(".ducky"):
        typer.secho(f"File {file} should have extension .ducky", fg=typer.colors.RED, err=True)
        return

    out = []
    with open(file) as f:
        for line in f:
            # remove final newline, if it exists
            process_line(line.replace("\n", ""), out)

    code = "\n".join(out)
    function_name = f"run_{i}"
    template = f"""void {function_name}() {{
{code}
}}"""
    return function_name, template





def main(files: List[Path] = typer.Argument(..., help="The list of files to process")):
    function_names = []
    templates = []
    for i, file in enumerate(files):
        fn, t = process(i, file)
        function_names.append(fn)
        templates.append(t)
    function_pointers = ", ".join(function_names)
    # Magic spell to declare an array of function pointers that take no arguments and return nothing
    pointer_array = f"""void (*CALLBACKS[{len(files)}]) (void) = {{ {function_pointers} }};"""
    
    for t in templates:
        print(t, end="\n\n")
    print(pointer_array)


if __name__ == "__main__":
    typer.run(main)

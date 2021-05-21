#!/usr/bin/env python3
import typer
from typing import List
from pathlib import Path
import sys

MOD_KEYCODES = {
    "CTRL": "MODIFIERKEY_CTRL",
    "SHIFT": "MODIFIERKEY_SHIFT",
    "WINDOWS": "MODIFIERKEY_GUI",
    "ALT": "MODIFIERKEY_ALT",
}

ARROW_KEYCODES = {
    "UPARROW": "KEY_UP",
    "DOWNARROW": "KEY_DOWN",
    "LEFTARROW": "KEY_LEFT",
    "RIGHTARROW": "KEY_RIGHT",
}

F_KEYS = ("F1", "F2", "F3", "F4", "F5", "F6",
          "F7", "F8", "F9", "F10", "F11", "F12")

# Single chars are implicitly allowed for all keys
ALLOWED_KEYS_FOR_MOD = {
    "CTRL": ("PAUSE", *F_KEYS, *ARROW_KEYCODES.keys(), "ESCAPE", "DELETE"),
    "SHIFT": ("DELETE", "HOME", "INSERT", "PAGEUP", "PAGEDOWN", *ARROW_KEYCODES.keys(), "TAB"),
    "WINDOWS": (),
    "ALT": ("END", "ESCAPE", *F_KEYS, *ARROW_KEYCODES.keys(), "SPACE", "TAB", "DELETE"),
}

SPECIAL_KEYCODES = {
    "PAUSE": "KEY_PAUSE",
    "CAPSLOCK": "KEY_CAPS_LOCK",
    "DELETE": "KEY_DELETE",
    "END": "KEY_END",
    "ESCAPE": "KEY_ESC",
    "HOME": "KEY_HOME",
    "INSERT": "KEY_INSERT",
    "NUMLOCK": "KEY_NUM_LOCK",
    "PAGEUP": "KEY_PAGE_UP",
    "PAGEDOWN": "KEY_PAGE_DOWN",
    "PRINTSCREEN": "KEY_PRINTSCREEN",
    "SCROLLOCK": "KEY_SCROLL_LOCK",
    "SPACE": "KEY_SPACE",
    "TAB": "KEY_TAB",
    "MENU": "KEY_MENU",
    # Autogenerate F-keys mappings
    **{f_key: f"KEY_{f_key}" for f_key in F_KEYS},
    **ARROW_KEYCODES,  # Include arrow mappings
}

# Every allowed key for every modifier must be a special key
assert all([all([k2 in SPECIAL_KEYCODES.keys()
           for k2 in ALLOWED_KEYS_FOR_MOD[k]]) for k in ALLOWED_KEYS_FOR_MOD])


def is_modifier_combo(text: str) -> List[str]:
    """
    Determines if the passed string is a combination of modifier keys, such as CTRL-ALT-SHIFT-WINDOWS

    Used, for example, in the commands CTRL-SHIFT ESCAPE or CTRL+ALT DELETE

    Returns a list of all the modifiers in the string, or an empty list if the string is not purely composed of modifiers
    """
    VALID_MODIFIERS = MOD_KEYCODES.keys()
    assert " " not in text, "Pass only the first word in a command to is_modifier_combo"
    pieces = text.split("-")
    if not all([p in VALID_MODIFIERS for p in pieces]):
        return []
    return pieces  # all the elements of pieces are guaranted to be modifiers


def is_extended_command(text: str) -> bool:
    """
    Determines if the passed string is an "Extended Command" in DuckyScript speak

    Returns True if the string is in the list of special keys
    """
    assert " " not in text, f"Pass a single keypress per line, not {text}"
    return text in SPECIAL_KEYCODES.keys()


def process_line(filenum: int, line: str, linenum: int, out: List[str]):
    if not line.strip():  # Ignore lines with whitespace only
        return

    if line.startswith("REM "):
        # Prevent comments from accidentally closing the C block comment
        safe = line.replace("*/", "* /")
        out.append(f'/* Automatic comment: {safe[4:]} */')
    elif line.startswith("STRING "):
        out.append(f'DigiKeyboard.print("{line[7:]}");')
    elif line.startswith("DELAY "):
        val = line[6:]
        assert val.isdigit(), f"Pass an integer to DELAY, not {val}"
        out.append(f'DigiKeyboard.delay({val});')
    # DEFAULTDELAY / DEFAULT_DELAY
    elif line.startswith("LIGHTS ON "):
        _, _, target, r, g, b = line.split(" ")
        if target == "self":
            target = filenum
        out.append(
            f'pixels.setPixelColor({target}, _COLOR({r},{g},{b}));\npixels.show();')
    elif line.startswith("LIGHTS OFF "):
        _, _, target = line.split(" ")
        if target == "self":
            target = filenum
        out.append(f'pixels.setPixelColor({target}, 0);\npixels.show();')
    elif is_modifier_combo(line.split(" ")[0]):
        pieces = line.split(" ")
        assert len(pieces) == 2, "Modifier keys must be followed by an actual key to press!"
        mods, key = pieces
        mods = is_modifier_combo(mods)
        if len(key) == 1:  # single key, type it as ASCII char
            keycode = f"pgm_read_byte_near(keycodes_ascii + (\'{key}\' - 0x20))"
        else:
            assert key in SPECIAL_KEYCODES.keys(), f"{key} is not a recognized special key"
            assert all([key in ALLOWED_KEYS_FOR_MOD[mod] for mod in mods]
                       ), f"Key {key} doesn't support the modifiers {mods}"
            keycode = SPECIAL_KEYCODES[key]
        modstring = " + ".join([MOD_KEYCODES[mod] for mod in mods])
        out.append(
            f'DigiKeyboard.sendKeyStroke({keycode}, {modstring});')
    elif is_extended_command(line):
        out.append(
            f'DigiKeyboard.sendKeyStroke({SPECIAL_KEYCODES[line]});')
    else:
        print(
            f'ERROR: Command "{line}" in line {linenum+1} not recognized', file=sys.stderr)
    # ARROW KEYS (UP, DOWN, LEFT, RIGHT)
    # FUNCTION KEYS F1-F12


def process(i: int, file: Path):
    if not file.name.endswith(".ducky"):
        typer.secho(f"File {file} should have extension .ducky",
                    fg=typer.colors.RED, err=True)
        return

    out = []
    with open(file) as f:
        for linenum, line in enumerate(f):
            # remove final newline, if it exists
            process_line(i, line.replace("\n", ""), linenum, out)

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

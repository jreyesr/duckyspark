#! /usr/bin/env python3

import io
import unittest
from contextlib import redirect_stderr

import parser


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.out = []
        return super().setUp()

    def _process(self, line: str):
        """
        Helper function that calls `process_line` with the passed line and some defaults

        Also asserts that `process_line` returns a single element

        `self.out` will contain the generated C code after this function returns.
        """
        parser.process_line(filenum=0, line=line, linenum=0, out=self.out)
        self.assertEqual(len(self.out), 1)

    def _compare(self, line, expected):
        """
        Helper function that calls `process_line` and compares the generated C code with `expected`
        """
        self._process(line)
        self.assertEqual(self.out[0], expected)

    def test_simple_print(self):
        self._compare("STRING abC", 'DigiKeyboard.print("abC");')

    def test_modifier(self):
        self._compare(
            "SHIFT a", "DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + ('a' - 0x20)), MODIFIERKEY_SHIFT);")

    def test_modifier_2(self):
        self._compare(
            "WINDOWS e", "DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + ('e' - 0x20)), MODIFIERKEY_GUI);")

    def test_multiple_modifiers(self):
        self._compare(
            "CTRL-SHIFT z", "DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + ('z' - 0x20)), MODIFIERKEY_CTRL + MODIFIERKEY_SHIFT);")

    def test_arrows(self):
        for a in ("DOWN", "UP", "LEFT", "RIGHT"):
            self._compare(f"{a}ARROW", f"DigiKeyboard.sendKeyStroke(KEY_{a});")
            self.out = []  # manually empty the array!

    def test_f_keys(self):
        for f in range(12):
            self._compare(
                f"F{f+1}", f"DigiKeyboard.sendKeyStroke(KEY_F{f+1});")
            self.out = []  # manually empty the array!

    def test_modifiers_plus_special_key(self):
        self._compare(
            "CTRL-ALT DELETE", f"DigiKeyboard.sendKeyStroke(KEY_DELETE, MODIFIERKEY_CTRL + MODIFIERKEY_ALT);")

    def test_alt_f4(self):
        self._compare(
            "ALT F4", "DigiKeyboard.sendKeyStroke(KEY_F4, MODIFIERKEY_ALT);")

    def test_delay(self):
        self._compare("DELAY 100", "DigiKeyboard.delay(100);")

    def test_lights_on(self):
        self._compare("LIGHTS ON self 1 2 3",
                      "pixels.setPixelColor(0, _COLOR(1,2,3));\npixels.show();")

    def test_lights_on_explicit_index(self):
        self._compare("LIGHTS ON 100 1 2 3",
                      "pixels.setPixelColor(100, _COLOR(1,2,3));\npixels.show();")

    def test_lights_off(self):
        self._compare("LIGHTS OFF self",
                      "pixels.setPixelColor(0, 0);\npixels.show();")

    def test_lights_off_explicit_index(self):
        self._compare("LIGHTS OFF 100",
                      "pixels.setPixelColor(100, 0);\npixels.show();")

    def test_comment(self):
        self._compare("REM foobar smart comment",
                      "/* Automatic comment: foobar smart comment */")

    def test_windows_key_doesnt_work_alone(self):
        with self.assertRaises(AssertionError) as cm:
            self._process("WINDOWS")
        self.assertEqual(
            str(cm.exception), "Modifier keys must be followed by an actual key to press!")

    def test_modifiers_dont_work_alone(self):
        for m in ("CTRL", "SHIFT", "ALT"):
            with self.assertRaises(AssertionError) as cm:
                self._process(m)
            self.assertEqual(
                str(cm.exception), "Modifier keys must be followed by an actual key to press!")

    def test_modifier_takes_single_key(self):
        with self.assertRaises(AssertionError) as cm:
            self._process("SHIFT abc")
        self.assertEqual(str(cm.exception), "abc is not a recognized special key")


    def test_modifier_with_invalid_key(self):
        with self.assertRaises(AssertionError) as cm:
            self._process("SHIFT PRINTSCREEN")
        self.assertEqual(str(cm.exception), "Key PRINTSCREEN doesn't support the modifiers ['SHIFT']")

    def test_modifiers_should_be_together(self):
        with self.assertRaises(AssertionError) as cm:
            self._process("ALT SHIFT")
        self.assertEqual(str(cm.exception),
                         "SHIFT is not a recognized special key")

    def test_modifiers_should_be_together_2(self):
        with self.assertRaises(AssertionError) as cm:
            self._process("CTRL-ALT WINDOWS")
        self.assertEqual(
            str(cm.exception), "WINDOWS is not a recognized special key")

    def test_mod_combo_must_have_key(self):
        with self.assertRaises(AssertionError) as cm:
            self._process("CTRL-ALT-SHIFT")
        self.assertEqual(
            str(cm.exception), "Modifier keys must be followed by an actual key to press!")

    def test_two_keystrokes_not_allowed(self):
        with self.assertRaises(AssertionError) as cm:
            self._process("DOWNARROW a")
        self.assertEqual(str(cm.exception),
                         "Pass a single keypress per line, not DOWNARROW a")

    def test_dont_mix_string_and_specials(self):
        # STRING should not get confused if you ask it to print a string that looks like a special key
        self._compare("STRING DOWNARROW", 'DigiKeyboard.print("DOWNARROW");')

    def test_dont_mix_string_and_specials_2(self):
        # A special key without STRING shoud be specially treated
        self._compare("DOWNARROW", 'DigiKeyboard.sendKeyStroke(KEY_DOWN);')

    def test_delay_param_nonint(self):
        with self.assertRaises(AssertionError) as cm:
            self._process("DELAY foo")
        self.assertEqual(str(cm.exception),
                         "Pass an integer to DELAY, not foo")

    def test_invalid_command(self):
        f = io.StringIO()
        with redirect_stderr(f):  # HACK Redirect stderr to a file object to assert on it
            parser.process_line(
                filenum=0, line="FOOBAR_WRONG_COMMAND", linenum=123, out=self.out)
            self.assertEqual(len(self.out), 0)
            self.assertEqual(f.getvalue(
            ), 'ERROR: Command "FOOBAR_WRONG_COMMAND" in line 124 not recognized\n')


if __name__ == '__main__':
    unittest.main()

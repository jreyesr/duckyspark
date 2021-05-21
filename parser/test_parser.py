import unittest

import parser

class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.out = []
        return super().setUp()
    
    def _process(self, line: str):
        parser.process_line(filenum=0, line=line, linenum=0, out=self.out)
        self.assertEqual(len(self.out), 1)

    def _compare(self, line, expected):
        self._process(line)
        self.assertEqual(self.out[0], expected)

    def test_simple_print(self):
        self._compare("STRING abC", 'DigiKeyboard.print("abC");')

    def test_modifier(self):
        self._compare("SHIFT a", "DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + ('a' - 0x20)), MODIFIERKEY_SHIFT);")

    def test_modifier_2(self):
        self._compare("WINDOWS e", "DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + ('e' - 0x20)), MODIFIERKEY_GUI);")

    def test_multiple_modifiers(self):
        self._compare("CTRL-SHIFT z", "DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + ('z' - 0x20)), MODIFIERKEY_CTRL + MODIFIERKEY_SHIFT);")

    def test_arrows(self):
        for a in ("DOWN", "UP", "LEFT", "RIGHT"):
            self._compare(f"{a}ARROW", f"DigiKeyboard.sendKeyStroke(KEY_{a});")
            self.out = [] # manually empty the array!

    def test_f_keys(self):
        for f in range(12):
            self._compare(f"F{f+1}", f"DigiKeyboard.sendKeyStroke(KEY_F{f+1});")
            self.out = [] # manually empty the array!

    def test_modifiers_plus_special_key(self):
        self._compare("CTRL-ALT DELETE", f"DigiKeyboard.sendKeyStroke(KEY_DELETE, MODIFIERKEY_CTRL + MODIFIERKEY_ALT);")

    def test_alt_f4(self):
        self._compare("ALT F4", "DigiKeyboard.sendKeyStroke(KEY_F4, MODIFIERKEY_ALT);")

    def test_delay(self):
        self._compare("DELAY 10", "DigiKeyboard.delay(100);")

    def test_lights_on(self):
        self._compare("LIGHTS ON self 1 2 3", "pixels.setPixelColor(0, _COLOR(1,2,3));\npixels.show();")

    def test_lights_on_explicit_index(self):
        self._compare("LIGHTS ON 100 1 2 3", "pixels.setPixelColor(100, _COLOR(1,2,3));\npixels.show();")

    def test_lights_off(self):
        self._compare("LIGHTS OFF self", "pixels.setPixelColor(0, 0);\npixels.show();")

    def test_lights_off_explicit_index(self):
        self._compare("LIGHTS OFF 100", "pixels.setPixelColor(100, 0);\npixels.show();")

    def test_comment(self):
        self._compare("REM foobar smart comment", "/* Automatic comment: foobar smart comment */")

    
    def test_windows_key_doesnt_work_alone(self): 
        with self.assertRaises(AssertionError, msg="Modifier keys must be followed by an actual key to press!"):
            self._process("WINDOWS")

    def test_mod_combo_must_have_key(self):
        with self.assertRaises(AssertionError, msg="Modifier keys must be followed by an actual key to press!"):
            self._process("CTRL-ALT-SHIFT")

if __name__ == '__main__':
    unittest.main()
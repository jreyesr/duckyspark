void run_0() {
/* Automatic comment: Turn own light on white */
pixels.setPixelColor(0, _COLOR(255,255,255));
pixels.show();
/* Automatic comment: Type first part */
DigiKeyboard.print("Hello");
/* Automatic comment: Delay for 100 ms */
DigiKeyboard.delay(100);
DigiKeyboard.print("world!");
pixels.setPixelColor(0, 0);
pixels.show();
}

void run_1() {
/* Automatic comment: Windows+E should open the file explorer (on Windows) */
DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + ('e' - 0x20)), MODIFIERKEY_GUI);
}

void run_2() {
/* Automatic comment: Shift+s should print capital S (to test the Shift modifier) */
DigiKeyboard.sendKeyStroke(pgm_read_byte_near(keycodes_ascii + ('s' - 0x20)), MODIFIERKEY_SHIFT);
}

void (*CALLBACKS[3]) (void) = { run_0, run_1, run_2 };

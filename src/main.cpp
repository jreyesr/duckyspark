#include <Arduino.h>
#define LAYOUT_SPANISH
#include <DigiKeyboard.h>
#include <Adafruit_NeoPixel.h>

// Uncomment to print ADC readings (to aid in setting the BOUNDS array)
//#define PRINT_ADC

/**
 * @brief The number of buttons (and therefore lights) in the keyboard
 */
const int NUMPIXELS = 6;

/**
 * @brief The pin for the Neopixels (number 0 = PORTB0 = P0 on the Digispark header = physical pin 5 on the chip)
 * 
 * @details Can be moved to 1 (PORTB1/P1) if using a Digispark Model B, which has a LED on P0
 */
const int NEOPIXEL_PIN = 0;

/**
 * @brief The pin for the button (number 1 = ADC1 = PORTB2 = P2 on the Digispark header = physical pin 7 on the chip)
 * 
 * @details WARNING: This pin must be an ADC pin. 
 *    The default pin 1 is the best option, since the other three ADC pins are occupied with USB (x2) and RESET
 */
const int BUTTON_PIN = 1;

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, NEOPIXEL_PIN);

/**
 * @brief Helper macro that returns the size of an array
 * 
 * @param x The array whose size will be returned
 */
#define NELEMS(x) (sizeof(x) / sizeof((x)[0]))

/**
 * @brief The tolerance for the button presses
 * 
 * @details This constant configures the allowed deviation from the center ADC code. 
 * It should be set to be as big as possible without causing overlap in the ranges that define each button.
 */
#define TOLERANCE 40

/**
 * @brief Helper macro that creates an array with the two elements (x-TOLERANCE, x+TOLERANCE)
 */
#define _BOUNDS(x)               \
  {                              \
    x - TOLERANCE, x + TOLERANCE \
  }

/**
 * @brief An array containing the range of ADC values that identify each button
 */
const int BOUNDS[NUMPIXELS][2] = {/*_BOUNDS(14), */ _BOUNDS(122), _BOUNDS(207), _BOUNDS(294), _BOUNDS(410), _BOUNDS(599), _BOUNDS(1023)};

/**
 * @brief The messages that will be printed on every button press
 */
const char *MESSAGES[NUMPIXELS] = {"a", "b", "c", "D", "E", "FGH"};

/**
 * @brief Helper macro that packs three uint8_t values in a uint32_t value, with some room to spare
 */
#define _COLOR(r, g, b) ((uint32_t)r << 16) | ((uint32_t)g << 8) | b

/**
 * @brief The color that every button will illuminate
 */
const uint32_t COLORS[NUMPIXELS] = {
    _COLOR(0, 0, 255),
    _COLOR(0, 255, 0),
    _COLOR(255, 0, 0),
    _COLOR(0, 0, 255),
    _COLOR(0, 255, 0),
    _COLOR(255, 0, 0),
};

void fillStrip(uint8_t r, uint8_t g, uint8_t b);
int getButtonIndex(int val);
void turnOn(uchar button);
void type(uchar button);

// This forcibly includes the callback declarations
#include "../cb.c"

// cppcheck-suppress unusedFunction
void setup()
{
  // DigiKeyboard.begin(); // don't need to set anything up to use DigiKeyboard
  pixels.begin();
  pinMode(BUTTON_PIN, INPUT);

  fillStrip(120, 0, 0); // Flash all buttons red for a bit (signals that the bootloader is done and the keyboard is ready)
  DigiKeyboard.delay(30);
  fillStrip(0, 0, 0);
}

bool pressed = false;
#ifdef PRINT_ADC
uchar i = 0;
#endif

// cppcheck-suppress unusedFunction
void loop()
{
  int val = analogRead(BUTTON_PIN);

#ifdef PRINT_ADC
  if (++i >= 20)
  { // Only print every 20th ADC reading, approx. 1 per second
    i = 0;
    DigiKeyboard.sendKeyStroke(0);
    DigiKeyboard.println(val);
  }
#endif

  int pressedButton = getButtonIndex(val);
  if (pressedButton > -1) // Some button was pressed
  {
    if (!pressed)
    { // Just pressed, execute the pressed button command
// Don't press the buttons if on ADC calibration mode
#ifndef PRINT_ADC
      type(pressedButton);
#endif

      pressed = true;
    }
  }
  else // No buttons pressed
  {
    if (pressed) // Just released, turn all lights off
    {
      // TODO: Maybe leave all light control to the DuckyScript files? 
      // This line makes it impossible to implement a "toggle" button, since it would turn off whenever it is released
      fillStrip(0, 0, 0); 

      pressed = false;
    }
  }

  DigiKeyboard.delay(50);
}

/**
 * @brief Turn on the light for a specific button
 * 
 * @param button The index of the button to turn on (0-based)
 */
void turnOn(uchar button)
{
  fillStrip(0, 0, 0); // Blank all buttons
  pixels.setPixelColor(button, COLORS[button]);
  pixels.show();
}

/**
 * @brief Type whatever is required for a specific button
 * 
 * @param button The index of the button that was pressed (0-based)
 */
void type(uchar button)
{
  /*DigiKeyboard.print(MESSAGES[button]);
  DigiKeyboard.sendKeyStroke(8, (1 << 3));*/
  CALLBACKS[button]();
}

/**
 * @brief Returns the index of the button that caused an ADC reading of val
 * 
 * @param val The raw ADC reading 
 * 
 * @returns The index of the button that was pressed, or -1 if no valid button was found
 * 
*/
int getButtonIndex(int val)
{
  for (uint16_t i = 0; i < NELEMS(BOUNDS); i++)
  {
    const int *b = BOUNDS[i];
    int lower = b[0], upper = b[1];
    if ((val > lower) && (val < upper))
    {
      return i;
    }
  }
  //DigiKeyboard.println("No key pressed!");
  return -1;
}

/**
 * @brief Fills the LED strip with a single color value
 * 
 * @param r The R component of the color
 * @param g The G component of the color
 * @param b The B component of the color
 */
void fillStrip(uint8_t r, uint8_t g, uint8_t b)
{
  for (int i = 0; i < NUMPIXELS; i++)
    pixels.setPixelColor(i, pixels.Color(r, g, b));

  pixels.show();
}
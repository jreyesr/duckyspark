# DuckySpark

A basic reimplementation of a [Rubber Ducky](https://shop.hak5.org/collections/sale/products/usb-rubber-ducky-deluxe) running on an ATtiny85 (perhaps on a [Digispark](http://digistump.com/products/1) or similar tiny board).

Now with extra fancy lights! 

DuckySpark is more aimed towards "programmable macro keyboard with flashing lights" than "covert flash-drive-looking device that types 1337 commandz".

DuckySpark uses the [DuckyScript](https://docs.hak5.org/hc/en-us/articles/360010555153-Ducky-Script-the-USB-Rubber-Ducky-language) programming language (in progress!) to automatically generate the actions that will be triggered on each button press.

## Hardware

DuckySpark requires:

1. A functional, USB-enabled ATtiny85. A [Digispark](http://digistump.com/products/1) or similar device is recommended. Note that such dev boards are exceedingly easy to DIY, due to the very low part count.
1. A few buttons with [a resistor ladder](http://int03.co.uk/blog/2014/12/18/reading-multiple-switches-with-one-analogue-input/), to read them all with a single microcontroller pin.
1. An equal amount of [Neopixels](https://www.adafruit.com/category/168) or similar addressable LEDs, to put below the button caps for extra blinkenlight points.

The unmodified code expects the Neopixel strip to be connected to pin 5 on the ATtiny85 (the actual, physical pin 5, lower right when the pin 1 marker is at the top left). The button array should be connected to physical pin 7 (that is, the pin just below the VCC pin).

That's it! Flash the firmware to the ATtiny, connect it via USB to the computer, and gaze upon the majesty of... a relatively simple programmable keyboard with lights.

## Firmware

The firmware was developed using PlatformIO. It is tailored to my exact specs (six buttons, and the expected ADC values for each button match the resistors that I had on hand for the resistor ladder), but it should be relatively easy to configure.

The stock firmware performs the actions contained on `cb.c` for the first buttons (the first button executes `run_0()`, the second executes `run_1()`, and so on). Currently (i.e., probably outdated), the first button turns its LED on to white, types "Hello world!" with a delay between the two words, and then turns its LED off. The second and third buttons type simple key combos that use modifier keys (Windows+E and Shift+s, respectively). The fourth to sixth buttons don't do anything yet.

A simple way to verify if the firmware is executing correctly (apart from verifying that the USB keyboard enumerates successfully) is to watch for a brief red flash on all LEDs. The code flashes the LEDs red for 30 milliseconds on the `setup()` function (that is, almost as soon as possible). 

### Modifying the firmware

* To change the used pins: Edit the `NEOPIXEL_PIN` and `BUTTON_PIN` constants in `src/main.cpp`. Be aware that `BUTTON_PIN` must be an ADC capable pin, and the currently selected one is the best general option (two other ADC pins are used for USB, and the final one is the RESET pin, which should generally be left alone). The `NEOPIXEL_PIN` has no such constraints.
* To change the number of buttons, edit the `NUMPIXELS` constant in `src/main.cpp`.
* To adapt the code for a different [resistor ladder](http://int03.co.uk/blog/2014/12/18/reading-multiple-switches-with-one-analogue-input/), change the `BOUNDS` and `TOLERANCE` constants:
    * The `BOUNDS` array holds the lower and upper limits for the ADC readings on each button press. Each element `_BOUNDS(x)` expands to `{x-TOLERANCE, x+TOLERANCE}`. For example, if `TOLERANCE` is 40, `_BOUNDS(80)` turns into `{40, 120}`, which is a two-element integer array. Therefore, for each element of the `BOUNDS` array, it should be set to `_BOUNDS(x)`, with x being the average ADC reading when the corresponding button is pressed.
    * `TOLERANCE` controls the width of the intervals that determine a valid button press. It should be set to the largest possible value that does NOT cause overlaps between intervals. For example, if the interval centerpoints are 60, 120, 200 and 300, `TOLERANCE` should be set _at most_ to 30, which produces the intervals (30, 90), (90, 150), (170, 230) and (270, 330). Larger `TOLERANCE` values would cause the first two intervals to overlap, such that an ADC reading of 90 would be ambiguous between buttons 0 and 1.
* To display the ADC readings (which would aid in adjusting `BOUNDS` and `TOLERANCE` for a different resistor ladder), uncomment the `#define PRINT_ADC` line. This types one ADC reading each second to the connected computer. Open a text editor or an Excel sheet to capture the typed data. While `PRINT_ADC` is defined, no button commands are executed, since the intervals are not necessarily valid.
* To port the firmware to a new chip, you are probably out of luck. The code relies on the [DigiKeyboard](https://github.com/digistump/DigistumpArduino/tree/master/digistump-avr/libraries/DigisparkKeyboard) library, which is finely-tuned, with the aid of dark magic, to the ATtiny85.

## DuckyScript (WIP!)

Just because, DuckySpark can be controlled with [DuckyScript](https://docs.hak5.org/hc/en-us/articles/360010555153-Ducky-Script-the-USB-Rubber-Ducky-language), a very simple macro language originally designed to create Rubber Ducky payloads.

### DuckyScript parser 

`parser.py` is a Python script that parses DuckyScript files and generates C code that can be compiled with the base firmware. The script emits C code to the standard output.

To run the parser, place one or more `.ducky` files on the root directory, fill them with commands and execute `./parser.py *.ducky`. The script will print the generated C code to the console. Alternatively, to automatically write the code to a file, use `./parser.py *.ducky | tee cb.c` (this still allows you to see the output, but also writes it to `cb.c`).

The generated C code must be placed on the file `cb.c` in the root directory. The firmware on `src/main.cpp` must then be recompiled, and it will include the code on `cb.c` in the compiled binary.

`cb.c` contains two main parts:

* A bunch of `void foo(void)` function declarations that contain the actions that will be taken on each button press. The functions are named `run_0`, `run_1` and so on.
* An array of pointers to the abovementioned functions (`CALLBACKS`). This array is called in the main code, in the form `CALLBACKS[pressedButton]()`, which invokes the i-th function in the array when the i-th button is pressed.

#### Requirements

The parser uses [Typer](https://typer.tiangolo.com/) to build the CLI. Typer can be installed with `pip install typer`.

### New and improved DuckyScript. Now with 100% more lights!

This project uses a slightly modified version of the original DuckyScript.

[This](https://docs.hak5.org/hc/en-us/articles/360010555153-Ducky-Script-the-USB-Rubber-Ducky-language) is the original DuckyScript reference.

The main differences between that specification and DuckySpark's script language are:

* The DEFAULT_DELAY command (also known as DEFAULTDELAY) is not implemented.
* The GUI alias for the WINDOWS key is not implemented (that is, you should use WINDOWS even if programming for a Mac)
* The APP alias for the MENU key is not implemented.
* The CONTROL alias for the CTRL key is not implemented.
* The arrow keys can only be denoted as DOWNARROW, UPARROW and so (DOWN, UP and so are not supported)
* Modifier combinations (such as Ctrl+Alt in the fabled Ctrl+Alt+Delete) can be denoted as `MODIFIER1-MODIFIER2-MODIFIER3 KEY` (for example, `CTRL-ALT DELETE`). Note that the key is separate from the modifier combo (that is, `CTRL-ALT-DELETE` is not valid, the correct line is `CTRL-ALT DELETE`). This is [supported in the original DuckyScript, in theory](https://forums.hak5.org/topic/31147-key-combos-in-ducky-script/?do=findComment&comment=234356), but it's not officially documented.
* There is a new command, LIGHTS, that controls the Neopixels on the DuckySpark.

#### The `LIGHTS` command

The DuckyScript parser supports a new command, LIGHTS. This command provides control over the keyboard LEDs. Its subcommands are:

* LIGHTS ON: Turns on a LED with a specified color. It can identify the LED by its index (0-based), or use `self` to refer to the LED of the currently pressed button. The syntax is `LIGHTS ON index r g b`, with all parts separated by spaces.

```
REM Turn on the second LED on the chain. Use a moderately bright green color (0, 120, 0)
LIGHTS ON 0 0 255 0

REM Turn on the LED of the currently pressed button. Use full white (255, 255, 255)
LIGHTS ON self 255 255 255
```

* LIGHTS OFF: Turns off a LED. The LED can be identified by index or `self` for the current button, much as LIGHTS ON. Unlike LIGHTS ON, no color must be specified.

```
REM Turns on the fifth LED on the chain
LIGHTS OFF 4

REM Turn off the LED of the currently pressed button
LIGHTS OFF self
```

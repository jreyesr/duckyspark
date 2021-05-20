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

## DuckyScript (WIP!)

Just because, DuckySpark can be controlled with [DuckyScript](https://docs.hak5.org/hc/en-us/articles/360010555153-Ducky-Script-the-USB-Rubber-Ducky-language), a very simple macro language originally designed to create Rubber Ducky payloads.

// TODO describe DuckyScript parser usage & automatic C callback generation

// TODO describe differences with the canonical DuckyScript: unsupported commands and new commands (namely LIGHTS)
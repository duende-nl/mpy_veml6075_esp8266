# mpy_veml6070_esp8266
This is a driver for the Vishay VEML6075 UV-A and UV-B sensor for use with MicroPython on ESP8266 boards.

The VEML6075 sensor communicates via I2C protocol.
The driver is programmed according the specifications in this document:
https://www.vishay.com/docs/84339/designingveml6075.pdf

There are 2 files included:

veml6075: The driver.

main.py: This is a sample program to show how this driver can be used.
To show the measured data a small OLED display is used in this sample.


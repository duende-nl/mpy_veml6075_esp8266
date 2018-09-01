from machine import I2C, Pin
import ssd1306
import veml6075
import time

time.sleep_ms(500)
i2c = I2C(scl=Pin(5), sda=Pin(4))
uv = veml6075.VEML6075(i2c)			  # instantiate VEML6075 class 
connected = uv.initUV()			
oled = ssd1306.SSD1306_I2C(128, 64, i2c, 0x3c)
oled.fill(0)

while True:
	if connected == True:
		UVI, UVIA, UVIB = uv.readUV()
	oled.fill(0)
	oled.text("UV information", 0, 0)
	if connected == True:
		oled.text("UVIA        {0:.1f}" .format(UVIA), 0, 20)
		oled.text("UVIB        {0:.1f}" .format(UVIB), 0, 30)
		oled.text("UVI avg     {0:.1f}" .format(UVI), 0, 40) 
	else:
		oled.text("UV sensor NC", 0, 20)
	oled.show()
	time.sleep_ms(3000)

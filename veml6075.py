import time
import ubinascii

class VEML6075:
	
	# Device information
	
	VEML6075_ADDR  = 0x10
	VEML6075_DEVID = 0x26

	REG_CONF        = 0x00  # Configuration register (options below)
	REG_UVA         = 0x07  # UVA register
	REG_UVD	        = 0x08  # Dark current register (NOT DUMMY)
	REG_UVB         = 0x09  # UVB register
	REG_UVCOMP1     = 0x0A  # Visible compensation register
	REG_UVCOMP2     = 0x0B  # IR compensation register
	REG_DEVID       = 0x0C  # Device ID register

	CONF_IT_50MS    = 0x00  # Integration time = 50ms (default)
	CONF_IT_100MS   = 0x10  # Integration time = 100ms
	CONF_IT_200MS   = 0x20  # Integration time = 200ms
	CONF_IT_400MS   = 0x30  # Integration time = 400ms
	CONF_IT_800MS   = 0x40  # Integration time = 800ms
	CONF_IT_MASK    = 0x8F  # Mask off other config bits

	CONF_HD_NORM    = 0x00  # Normal dynamic seetting (default)
	CONF_HD_HIGH    = 0x08  # High dynamic seetting

	CONF_TRIG       = 0x04  # Trigger measurement, clears by itself

	CONF_AF_OFF     = 0x00  # Active force mode disabled (default)
	CONF_AF_ON      = 0x02  # Active force mode enabled (?)

	CONF_SD_OFF     = 0x00  # Power up
	CONF_SD_ON      = 0x01  # Power down

	# To calculate the UV Index, a bunch of empirical/magical coefficients need to
	# be applied to UVA and UVB readings to get a proper composite index value.

	UVA_A_COEF = 2.22 
	UVA_B_COEF = 1.33 
	UVB_C_COEF = 2.95 
	UVB_D_COEF = 1.74 

	# Once the above offsets and crunching is done, there's a last weighting
	# function to convert the ADC counts into the UV index values. This handles
	# both the conversion into irradiance (W/m^2) and the skin erythema weighting
	# by wavelength--UVB is way more dangerous than UVA, due to shorter
	# wavelengths and thus more energy per photon. These values convert the compensated values 

	UVA_RESPONSIVITY = 0.0011
	UVB_RESPONSIVITY = 0.00125

	def __init__(self, i2c=None):
		self.i2c = i2c
		self.address = self.VEML6075_ADDR
		
	
	# initialize device
	def initUV(self):
		try:
			deviceID = bytearray(2)
			self.i2c.readfrom_mem_into(self.address, self.REG_DEVID, deviceID)
			if (deviceID[0] != self.VEML6075_DEVID):
				return False
			else:	
				# Write Dynamic and Integration Time Settings to Sensor
				conf_data = bytearray(2)
				conf_data[0] = self.CONF_IT_100MS| \
						  self.CONF_HD_NORM| \
						  self.CONF_SD_OFF
				conf_data[1] = 0
				self.i2c.writeto_mem(self.address, self.REG_CONF, conf_data)  
				return True
		except:
			return False
			
	# Read UV data from device, return UV index
	def readUV(self):
		time.sleep_ms(150)  
		uv_data = bytearray(2)
		
		self.i2c.readfrom_mem_into(self.address,self.REG_UVA, uv_data)
		uva = int.from_bytes(uv_data, 'little')
		
		self.i2c.readfrom_mem_into(self.address,self.REG_UVD, uv_data)
		uvd = int.from_bytes(uv_data, 'little')
		
		self.i2c.readfrom_mem_into(self.address,self.REG_UVB, uv_data)
		uvb = int.from_bytes(uv_data, 'little')
		
		self.i2c.readfrom_mem_into(self.address,self.REG_UVCOMP1, uv_data)
		uvcomp1 = int.from_bytes(uv_data, 'little')
		
		self.i2c.readfrom_mem_into(self.address,self.REG_UVCOMP2, uv_data)
		uvcomp2 = int.from_bytes(uv_data, 'little')
		
		uvacomp = (uva-uvd) - (self.UVA_A_COEF * (uvcomp1-uvd)) - (self.UVA_B_COEF * (uvcomp2-uvd))
		uvbcomp = (uvb-uvd) - (self.UVB_C_COEF * (uvcomp1-uvd)) - (self.UVB_D_COEF * (uvcomp2-uvd))
		
# Do not allow negative readings which can occur in no UV light environments e.g. indoors
		if uvacomp < 0:  
			uvacomp = 0
		if uvbcomp < 0:
			uvbcomp = 0

		uvai = uvacomp * self.UVA_RESPONSIVITY
		uvbi = uvbcomp * self.UVB_RESPONSIVITY
		uvi = (uvai + uvbi) / 2
		
		return (uvi, uvai, uvbi)

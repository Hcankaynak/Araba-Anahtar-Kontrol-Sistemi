import mysql.connector
import serial
import RPi.GPIO as GPIO
import time
# DATABASE CONNECTION
connection = mysql.connector.connect(user= 'root', password = 'pi', database='ROKETSAN')
cursor = connection.cursor()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG = 17
ECHO = 27


GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18


# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)



  
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7


  # Initialise display
lcd_init()



def anahtarControl():
	GPIO.output(TRIG, False)
	#print ("ANAHTAR KONTROL EDİLİYOR")
	#messageScreen("ANAHTAR","KONTROL")
	time.sleep(2)

	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)

	while GPIO.input(ECHO)==0:
		pulse_start = time.time()

	while GPIO.input(ECHO)==1:
		pulse_end = time.time()

	pulse_duration = pulse_end - pulse_start
 
	distance = pulse_duration * 17150
	distance = round(distance, 2)
	
	if (distance > 3 and distance < 8):

		return True
		
	else :
		
		return False
		

while True:
		
		if(anahtarControl()):
			#messageScreen("Kartinizi Okutunuz"," ")
			#print("Kartinizi okutunuz")
			#messageScreen("Selam","asd")
			lcd_string("KART OKUT",LCD_LINE_1)
			ser = serial.Serial('/dev/ttyACM0')
			read_byte = ser.readline()
			
			lcd_string("ANAHTAR AL",LCD_LINE_1)

			#print("Lütfen Anahtarı Alınız")
			time.sleep(5)
			if(not anahtarControl()):
				#print("Anahtar Alındı.")
				#lcd_byte(0x01,LCD_CMD)
				lcd_string("ANAHTAR ALINDI",LCD_LINE_1)
				read_byte = read_byte.decode('ASCII').rstrip('\r\n')
				cursor.execute("SELECT * FROM employees")
				records= cursor.fetchall()
				for i in records:
					if(read_byte == i[1]):
						#Kullanıcının bilgilerini database yükle.
						tempName = i[2] + " " + i[3]
						cursor.execute("INSERT INTO RealCarLog(uName,keyName,lctm) VALUES(%s,%s,%s)",(tempName,"1",time.asctime()))
						connection.commit()
						# Anahtar durumunu databasede güncelle
						cursor.execute("INSERT INTO AnahtarKontrol(name,status,lctm) VALUES(%s,%s,%s)",("1","0",time.asctime()))
						connection.commit()
						lcd_string(tempName,LCD_LINE_2)
						print("BAŞARILI")
			else:
				#print("Anahtar Alınmadı.")
				lcd_string("ANAHTAR232")
				# Kartı okuttu anahtarı almadı
		else:
			# Anahtar yok / Birisi anahtar bırakmaya geldi.
			lcd_string("KART OKUT",LCD_LINE_1)
			ser = serial.Serial('/dev/ttyACM0')
			read_byte = ser.readline()
			read_byte = read_byte.decode('ASCII').rstrip('\r\n')
			lcd_string("ANAHTARI BIRAK",LCD_LINE_1)
			#print("Lütfen Anahtarı Bırakınız / ")
			time.sleep(15)
			if(anahtarControl()):
				lcd_string("ANAHTAR",LCD_LINE_1)
				lcd_string("BIRAKILDI",LCD_LINE_2)
				#print("ANAHTAR BIRAKILDI")
				cursor.execute("INSERT INTO AnahtarKontrol(name,status,lctm) VALUES(%s,%s,%s)",("1","1",time.asctime()))
				# Anahtar bırakanı database e ekle
				
				cursor.execute("SELECT * FROM employees")
				records= cursor.fetchall()
				for i in records:
					if(read_byte == i[1]):
						#Kullanıcının bilgilerini database yükle.
						tempName = i[2] + " " + i[3]
						cursor.execute("INSERT INTO GivenCarLog(uName,keyName,lctm) VALUES(%s,%s,%s)",(tempName,"1",time.asctime()))
						connection.commit()
				# Anahtar durumunu databasede güncelle
			else:
				# Hiçbir şey yapma
				#print("Anahtar Bırakılmadı.")
				lcd_string("ANAHTAR",LCD_LINE_1)
				lcd_string("BIRAKILMADI",LCD_LINE_2)





my = read_byte.decode('ASCII').rstrip('\r\n')

cursor.execute("SELECT * FROM employees ")
records = cursor.fetchall()

for i in records:
	if(i[1] == my):
		tempName = i[2] + " " + i[3]
		print(tempName)
		cursor.execute("INSERT INTO RealCarLog (uName,keyName,lctm) VALUES(%s,%s,%s)", (tempName,"1",time.asctime()))
		connection.commit()

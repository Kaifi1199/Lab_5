import network
import BlynkLib
from machine import Pin, I2C, Timer
import machine
import ssd1306
import dht
import time



# WiFi Credentials
WIFI_SSID = "Abdullah123"     
WIFI_PASS = "Abdullah7"  

# Blynk Auth Token 
BLYNK_AUTH = "J5Nt9AqWrkWnkyRbXVHoDj8BzMf_hhQi"

# Connect to WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)
while not wifi.isconnected():
    pass
print("Connected to WiFi")

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)


DHT_PIN = 4  # DHT11 data pin
button = Pin(0, Pin.IN, Pin.PULL_UP)

dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))  # Initialize DHT11 sensor

# Initialize OLED display
i2c = machine.I2C(scl=machine.Pin(9), sda=machine.Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

pressed = False
debounce_timer = None

TEMP_ICON = [
    0b00011000,  #    ██    
    0b00011000,  #    ██    
    0b00011000,  #    ██    
    0b00011000,  #    ██    
    0b00011000,  #    ██    
    0b00111100,  #   ████   
    0b00111100,  #   ████   
    0b00011000   #    ██    
]

HUMIDITY_ICON = [
    0b00001000,  #     █    
    0b00011000,  #    ██    
    0b00111000,  #   ███    
    0b01111000,  #  ████    
    0b01111000,  #  ████    
    0b00111000,  #   ███    
    0b00011000,  #    ██    
    0b00000000   #          
]

def draw_icon(oled, x, y, icon):
    """Draws an 8x8 icon on the OLED at (x, y)."""
    for row in range(8):
        for col in range(8):
            pixel_on = (icon[row] >> (7 - col)) & 1
            oled.pixel(x + col, y + row, pixel_on)

def button_pressed(pin):
    global debounce_timer, pressed  # Declare variables as global

    if debounce_timer is None:
        pressed = not pressed
        if pressed:
            oled.poweroff()
        else:
            oled.poweron()

        # Start a timer for debounce period (200ms)
        debounce_timer = Timer(0)
        debounce_timer.init(mode=Timer.ONE_SHOT, period=200, callback=debounce_callback)

def debounce_callback(timer):
    global debounce_timer
    debounce_timer = None

# Attach the interrupt to the button's rising edge
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

# Main loop
while True:
    try:
        dht_sensor.measure()
        time.sleep(0.2)
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        print(f"Temp: {temp}°C, Humidity: {humidity}%")

        # Send data to Blynk
        blynk.virtual_write(0, temp)  # V0 for temperature
        blynk.virtual_write(1, humidity)  # V1 for humidity
        
        # Display on OLED
        oled.fill(0)
        draw_icon(oled, 0, 0, TEMP_ICON)
        oled.text("{} C".format(temp), 10, 0)
            
        # Draw humidity icon and text
        draw_icon(oled, 0, 16, HUMIDITY_ICON)
        oled.text("{}%".format(humidity), 10, 16)
        oled.show()
    
    except Exception as e:
        print("Error reading DHT11 sensor:", e)

    blynk.run()
    time.sleep(1)  # Update every second


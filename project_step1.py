import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import os
import yagmail

PIR_PIN = 4
LED_PIN = 21
LOG_FILE_NAME = "/home/pi/camera/photo_logs.txt"

def take_photo(camera):
    file_name = "/home/pi/camera/img_" + str(time.time()) + ".jpg"
    camera.capture(file_name)
    return file_name

def update_photo_log_file(photo_file_name):
    with open(LOG_FILE_NAME, "a") as f:
        f.write(photo_file_name)
        f.write("\n")

def send_email_with_photo(yagmail_client, file_name):
    yagmail_client.send(to="daniel_zorov@abv.bg",
                   subject="Movement detected!",
                   contents="Here is a photo..",
                   attachments=file_name)

# Setup camera
camera = PiCamera()
camera.resolution = (720, 480)
camera.rotation = 180
time.sleep(2)
print("Camera setup OK.")

# Remove log file
if os.path.exists(LOG_FILE_NAME):
    os.remove(LOG_FILE_NAME)
    print("Log File Removed.")

# Setup yagmail
password = "............."
yag = yagmail.SMTP("sunzheini@gmail.com", password)
print("Email setup OK.")

# Setup GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)
print("GPIOs setup OK.")

MOV_DETECT_TRESHOLD = 3.0
last_pir_state = GPIO.input(PIR_PIN)
movement_timer = time.time()
MIN_DURATION_BETWEEN_TWO_PHOTOS = 60.0
last_time_photo_taken = 0

print("Everything is setup OK.")

try:
    while True:
        time.sleep(0.01)
        pir_state = GPIO.input(PIR_PIN)
        
        if pir_state == GPIO.HIGH:
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
        
        if last_pir_state == GPIO.LOW and pir_state == GPIO.HIGH:
            movement_timer = time.time()
        if last_pir_state == GPIO.HIGH and pir_state == GPIO.HIGH:
            if time.time() - movement_timer > MOV_DETECT_TRESHOLD:
                if time.time() - last_time_photo_taken > MIN_DURATION_BETWEEN_TWO_PHOTOS:
                    print("Print photo and send by email.")
                    
                    photo_file_name = take_photo(camera)
                    update_photo_log_file(photo_file_name)
                    send_email_with_photo(yag, photo_file_name)
                    
                    last_time_photo_taken = time.time()
        last_pir_state = pir_state
        
except KeyboardInterrupt:
    GPIO.cleanup()

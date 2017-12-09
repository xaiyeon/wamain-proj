"""
    x-wa-main and s-wa-main lead programmed by Royce Aquino,
    assistant programmer is JP A.

    Last Edit Date: Dec 7, 2017

    About s-wa-main:
    x-wa-main kept crashing due to Segmentation Fault errors, this is due to the limited memory space
    on the BeagleBone Black Wireless. This program is a simplified version that works.

    This Python program relies on Python3.5+ and is meant to run on the BeagleBoneBlack Wireless
    or any micro-computer capable of running it. This project is meant to showcase the practicality and how
    easy it is to create your own security cameras just like the one you see in stores.

    For the complete product to work you must have the Android Application which can be found on Github xaiyeon.

    How-To-Use:

    Get any micro-computer like a Pi, Beagle, etc. The code was tested on Debian Stretch and works. I haven't tried
    other Linux Distros.
    You will need to create an account on the Android Application.
    Once done, hook up the pixycam (make sure you programmed your pixycam for you use cases) and the webcam.
    Then run this python code using Python3 command on linux.

    You will be taken through a test demo first to make sure everything works...
    After the test demo, you will want to name the location and log-in to your account you signed up with on the
    Android application.

    Files on the micro-computer are stored under users/ the user id / folder with year month / day of month /
    your_image.jpg

    That's it.

    Thoughts:

    First we set-up our config and stuff for our application for user
    Next we ask the user to log-in, we will create an object of wamain_user
    Then we go through other set-up procedure and such.
    We will sperate the 3 main tasks into 3 functions and call them based on priority.
    The lower tasks will be ran when everything is idle or hardcoded into the scheduler.

"""


# Start of module imports

import os
import sys
import platform
import sched
import time
from time import sleep
from twilio.rest import Client
import pyrebase
import pygame
import json
import requests
import random
import geocoder
import socket
import string
import datetime
import threading
from pygame import camera
from pygame import image
from timeit import default_timer as timer
from pixy import *
from ctypes import *

# End of module imports


# This is for handy definitions of function that we use all the time
class Wamain_Tool:
    def __init__(self, name):
        self.name = name
        self.twilio_account_sid = "AC9eac86dec2fae88b7c7f7e786e5ac50d"
        self.twilio_auth_token = "51fd45acaa40b749e5a371140818d2c2"
        self.twilio_number = "+18582392249"

    def firebase_settings(self):
        firebase_config = {
            "apiKey": "AIzaSyD2vMTSufNIHH0RxWiDGfKkoFWPKKMRYiQ",
            "authDomain": "waphotorecon-app.firebaseapp.com",
            "databaseURL": "https://waphotorecon-app.firebaseio.com",
            "storageBucket": "waphotorecon-app.appspot.com"
        }
        return firebase_config


# This is for local system running this program only
class Wamain_User:
    def __init__(self, name, create_date, location_name, fireb_email, fireb_password, phone_number,
                 system_device_info, file_storage_path, fireb_display_name, fireb_uid):
        self.name = name
        self.create_date = create_date
        self.location_name = location_name
        self.fireb_email = fireb_email
        self.fireb_password = fireb_password
        self.phone_number = phone_number
        self.system_device_info = system_device_info
        self.file_storage_path = file_storage_path
        self.fireb_display_name = fireb_display_name
        self.fireb_uid = fireb_uid
        self.photos = []
        self.system_messages = []

    @classmethod
    def from_input(cls):
        print("Welcome to the WA Photo Recon System!")
        print("To create a user, please input answers for these parameters for your system.")
        print("To use the system, you must log-in with the account you verified using the application.")
        return cls(
            input('Name for this system account: '),
            time.asctime(time.localtime(time.time())),
            input('Name This Location: '),
            input('Your WA Photo Recon login E-mail: '),
            input('Your WA Photo Recon login Password: '),
            input('Cell Phone Number (ex: +16190010004): '),
            str(os.uname()[0]) + ", " + str(os.uname()[1]) + ", " + str(os.uname()[2]) + ", " + str(
                os.uname()[3]) + ", " + str(os.uname()[4]),
            "empty",
            "empty",
            "empty"
        )


# For the Photos
class Photo:

    def __init__(self, photo_id, user_id, user_name, photo_name, imgdata_url, taken_location, location_name,
                 photo_description, photo_create_date, is_analyzed, device_name, image_status, search_date):
        self.photo_id = photo_id
        self.user_id = user_id
        self.user_name = user_name
        self.photo_name = photo_name
        self.imgdata_url = imgdata_url
        self.taken_location = taken_location
        self.location_name = location_name
        self.photo_description = photo_description
        self.photo_create_date = photo_create_date
        self.is_analyzed = is_analyzed
        self.device_name = device_name
        self.image_status = image_status
        self.search_date = search_date

    def photo_data(self):
        jsondata = {
            "photo_id": self.photo_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "photo_name": self.photo_name,
            "imgdata_url": self.imgdata_url,
            "taken_location": self.taken_location,
            "location_name": self.location_name,
            "photo_description": self.photo_description,
            "photo_create_date": self.photo_create_date,
            "is_analyzed": self.is_analyzed,
            "device_name": self.device_name,
            "image_status": self.image_status,
            "search_date": self.search_date
        }
        return jsondata


# This class is based off the model used in java app for System Log Messages
class SysMessage:
    def __init__(self, sys_message_id, user_id, message, device_name, is_visible, create_date, photo_id, image_status, search_date):
        self.sys_message_id = sys_message_id
        self.user_id = user_id
        self.message = message
        self.device_name = device_name
        self.is_visible = is_visible
        self.create_date = create_date
        self.photo_id = photo_id
        self.image_status = image_status
        self.search_date = search_date

    def message_data(self):
        jsondata = {
            "sys_message_id" : self.sys_message_id,
            "user_id" : self.user_id,
            "message" : self.message,
            "device_name" : self.device_name,
            "is_visible" : self.is_visible,
            "create_date" : self.create_date,
            "photo_id" : self.photo_id,
            "image_status": self.image_status,
            "search_date": self.search_date
        }
        return jsondata


# Class structure used for PixyCam blocks
class Blocks(Structure):
    _fields_ = [("type", c_uint),
                ("signature", c_uint),
                ("x", c_uint),
                ("y", c_uint),
                ("width", c_uint),
                ("height", c_uint),
                ("angle", c_uint)]


# Below are functions we will use that are handy for DRY

# We check devices and such and start some threads.
def check_devices_connection():
    # Check for internet connection
    try:
        # connect to the site, test connection for 2 seconds
        socket.create_connection(("www.google.com", 80), 2)
        pass
    except OSError as eee:
        print("No wi-fi connection was found? Or bad device?")
        print(eee)
        return False
    # Return True if everything is working...
    return True


# This function is for sending a message to the user via Twilio to phone
def twilio_send_test(system_tool, system_user):
    test_message = "This is a test message for: " + system_user.name + ". For your system: " + system_user.system_device_info
    client = Client(system_tool.twilio_account_sid, system_tool.twilio_auth_token)
    client.api.account.messages.create(
        to=system_user.phone_number,
        from_=system_tool.twilio_number,
        body=test_message)


def twilio_send_busy(system_tool, system_user):
    localtime = time.asctime(time.localtime(time.time()))
    test_message = "This time was busy: " + system_user.name + str(localtime) + ". For your system: " + system_user.system_device_info
    client = Client(system_tool.twilio_account_sid, system_tool.twilio_auth_token)
    client.api.account.messages.create(
        to=system_user.phone_number,
        from_=system_tool.twilio_number,
        body=test_message)

# This is like a task we must run every 45 minutes to refresh the user token
def refresh_token_45(firebase_user, firebase_auth):
    threading.Timer(2700, refresh_token_45).start()
    ## Refresh user token
    firebase_user = firebase_auth.refresh(firebase_user['refreshToken'])
    ## Fresh token
    firebase_user['idToken']


# This function is like or is an upload task. Only gets called when PixyCam isn't busy
# Pass all the things you need.
def upload_to_firebase_task(system_user, firebase_user, firebase_auth, firebase_database, firebase_storage, stored_image_list,
                            stored_image_name_list, stored_time_list, stored_geocoord_list, stored_search_date_list,
                            stored_image_status_list, stored_image_url_list):
    localtime = time.asctime(time.localtime(time.time()))
    print("Starting an upload task at: " + str(localtime))
    # Timer for just the upload part
    start_time_upload = timer()
    # Start
    # This part can be separated
    print("Uploading images to FireBase Storage...")
    for im_na, lo_im in zip(stored_image_name_list, stored_image_list):
        # Between operations lets wait a bit
        sleep(0.100)
        firebase_storage_upload = firebase_storage.child(
            "users/" + system_user.fireb_uid + "/" + "photos/" + im_na).put(
            lo_im, firebase_user['idToken'])
        url_from_storage = firebase_storage.child("users/" + system_user.fireb_uid + "/" + "photos/" + im_na).get_url(
            firebase_storage_upload['downloadTokens'])
        # Now we store that file_path from get url to our image in a list for later, which is used in upload_tasks
        stored_image_url_list.append(url_from_storage)

    # Once that finished lets empty those lists for memory.
    stored_image_list.clear()

    # Creating seed name schema
    random_letter = random.choice(string.ascii_lowercase)
    random_number = random.randrange(0, 1001)

    # We now go through the list until empty, populating our object datas: photo, user_photo, and sys_messages.
    # Start looping until lists are empty.
    # This for loop goes through the five lists to populate our class objects.
    for ti, im, ge, st, da, imn in zip(stored_time_list, stored_image_url_list,
                                       stored_geocoord_list,
                                       stored_image_status_list, stored_search_date_list,
                                       stored_image_name_list):
        image_status_name = "seed" + random_letter + str(random_number) + st
        obj_sys_message = SysMessage(firebase_user['idToken'], system_user.fireb_uid,
                                     "Test Demo: An image was captured.",
                                     system_user.system_device_info, "true",
                                     ti, firebase_user['idToken'], image_status_name, da)
        obj_photo = Photo(firebase_user['idToken'], system_user.fireb_uid, system_user.fireb_display_name, imn,
                          im, ge, system_user.location_name, "A photo that was captured.", ti, "false",
                          system_user.system_device_info, image_status_name, da)
        # Now we add all objects to the list for uploading later.
        system_user.photos.append(obj_photo)
        system_user.system_messages.append(obj_sys_message)

    # After that process we can empty all other lists.
    stored_time_list.clear()
    stored_image_url_list.clear()
    stored_geocoord_list.clear()
    stored_image_status_list.clear()
    stored_search_date_list.clear()
    stored_image_name_list.clear()

    print("Uploading datas to FireBase Real-Time Database...")
    # Prepare rest
    sleep(5)
    # Now we upload our data/babies!
    for sys, pho in zip(system_user.system_messages, system_user.photos):
        # We add some time delays in between each operation, 1 second
        sleep(1)
        firebase_res1 = firebase_database.child("usermessagelogs").child(system_user.fireb_uid).push(
            sys.message_data(), firebase_user['idToken'])
        sleep(1)
        firebase_res2 = firebase_database.child("allphotos").push(pho.photo_data(), firebase_user['idToken'])
        sleep(1)
        firebase_res3 = firebase_database.child("userphotos").child(system_user.fireb_uid).push(pho.photo_data(),
                                                                                                firebase_user[
                                                                                                    'idToken'])
    # Now uploads have been finished we clear those object lists too
    system_user.system_messages.clear()
    system_user.photos.clear()
    # End
    # Ending time for upload.
    end_time_upload = timer()
    # Elapsed time for the demo.
    elapsed_upload_time = end_time_upload - start_time_upload
    print("The upload task took: " + str(elapsed_upload_time) + " seconds.")


# ---- PROGRAM STARTS
# ---- After this line is where the actual program will start running!

# Variables we will use
# List that are used for creating our objects for upload
# List for local
stored_image_list = []
stored_image_name_list = []
# List for data
stored_time_list = []
stored_geocoord_list = []
stored_search_date_list = []
# stored image_type_list is for consecutive pictures, if not it's "0", yes it's "_link", and adds to image_status
stored_image_status_list = []
# This list is for when after an image is uploaded to storage
stored_image_url_list = []

demo_test = True
alert_once = True
continue_check = True
run_system = True

# We start the system now. The first run is a demo-test to verify it's working.
# Once all initial set-up is finished we will time it.
print("WA Photo Recon System is now checking devices, connections, etc...")
# Now we can init all our things and check wi-fi is connected
if check_devices_connection():
    print("System: This system is ready and all device flags are green for launch!")
else:
    print("Please fix the errors above and make sure your device is set-up correctly!")
    print("")
    fail = input('Enter to quit program and try again: ')
    # We quit the program or exit.
    print("Quitting...")
    sys.exit(0)

# First we ask for user inputs and then log-in, create folder, do a test, and then start.

# Starting gathering of user info. Create system user object
system_user = Wamain_User.from_input()
# Make a Wamain_tool object
system_tool = Wamain_Tool("Wamain_Tool_1")
# Now we log-in to FireBase
firebase = pyrebase.initialize_app(system_tool.firebase_settings())
firebase_auth = firebase.auth()
# With our connection we can now log-in. Then we fetch the account info and store the UID and display name
firebase_user = firebase_auth.sign_in_with_email_and_password(system_user.fireb_email, system_user.fireb_password)
get_firebase_user_uid = firebase_auth.get_account_info(firebase_user['idToken'])
# Now we set the UID and the DisplayName to our user object.
system_user.fireb_uid = get_firebase_user_uid["users"][0]["localId"]
system_user.fireb_display_name = get_firebase_user_uid["users"][0]["displayName"]
# Setup firebase database
firebase_database = firebase.database()
# Setup firebase storage
firebase_storage = firebase.storage()
# Now we create a directory
# Making a folder for user, below gets current directory
cur_dir = os.getcwd()
# We get absolute path from root
abs_dir = os.path.abspath(cur_dir)
new_path = "/" + "stored_photos" + "/" "/" + "users" + "/" + system_user.fireb_display_name
new_dir = abs_dir + new_path
if not os.path.exists(new_dir):
    os.makedirs(new_dir)
    print("A new directory, stored_photos, was created (where your photos will be found): " + new_dir)
else:
    print("stored_photos is already there.")
system_user.file_storage_path = new_dir

print("Test Demo is now starting.")
# Time to time the demo.
start_time_demo = timer()

# Now we can start the pygame web cam and pixycam.
# Sarting pygame and camera
pygame.init()
pygame.camera.init()
camera_list = pygame.camera.list_cameras()
if camera_list:
    web_cam = pygame.camera.Camera(camera_list[0], (280, 210))
    web_cam.start()

# Now we start the thread for the pixy cam
pixy_init()
# Wait for devices to turn on
sleep(5)
# Pixycam block detection, to see our signature defined colors within pixel ranges
pixy_blocks = BlockArray(100)

# We call our refresh task here, which is scheduled every 45 minutes
refresh_token_45(firebase_user, firebase_auth)

# Send the user a test message
twilio_send_test(system_tool, system_user)

while demo_test:
    # Is a count of detected objects in a frame from pixy cam
    sleep(0.30)
    pixy_detection = pixy_get_blocks(100, pixy_blocks)
    if pixy_detection > 0:
        sleep(0.30)
        print("An object or person of interest is detected! Taking picture...")
        # Take a picture and store it locally first.
        img = web_cam.get_image()
        # Image status
        image_status = "0"
        # We also get the time and store into the list
        localtime = time.asctime(time.localtime(time.time()))
        print("Photo captured: " + str(localtime))
        # file_naming
        file_localtime = time.strftime('%Y-%m-%d_%H_%M_%S')
        # Here we name the image with our ways.
        a_img_title_name = "IMG_" + file_localtime + "_" + str(random.randrange(1, 1000))
        # Save image to the user's folder
        pygame.image.save(img, system_user.file_storage_path + "/" + a_img_title_name + ".jpg")
        # Now we get that same full path for the image
        local_img_dir = system_user.file_storage_path + "/" + a_img_title_name + ".jpg"
        # Store short_date for search_date, ex: 2017-12-07
        today = datetime.date.today()
        # We also need to get geo coords and store, Now lets get the location in latitude, longitude
        try:
            a_location = geocoder.ip('me')
            a_point_location = str(a_location.latlng)
        except Exception as eh:
            a_point_location = "N/A"
            pass

        stored_image_status_list.append(image_status)
        stored_time_list.append(localtime)
        stored_image_name_list.append(a_img_title_name)
        stored_image_list.append(local_img_dir)
        stored_search_date_list.append(str(today))
        stored_geocoord_list.append(a_point_location)

        # Call upload task function
        upload_to_firebase_task(system_user, firebase_user, firebase_auth, firebase_database, firebase_storage,
                                stored_image_list, stored_image_name_list, stored_time_list, stored_geocoord_list,
                                stored_search_date_list, stored_image_status_list, stored_image_url_list)

        demo_test = False

    else:
        if alert_once:
            print("Please smile in front of the sensor.")
            alert_once = False


print("Demo has finished!")
# Ending time for demo.
end_time_demo = timer()
# Elapsed time for the demo.
elapsed_demo_time = end_time_demo - start_time_demo
print("The test demo took: " + str(elapsed_demo_time) + " seconds!")

while continue_check:
    continue_on = input('To start the system enter s or q to quit: ')
    if continue_on == "s":
        continue_check = False
    else:
        pass
    if continue_on == "q":
        # We quit the program or exit.
        web_cam.stop()
        run_system = False
        continue_check = False
    else:
        pass

# ---- Now we actually put the code here for continuous usage!
# We upload the photos, with whatever the pixycam and webcam has as soon as there is no detection anymore.
# TODO: We can also add in more daily notifications (send to user via phone message)
# if the day was busy or not today based on taken images.
detection_count = 0
if run_system:
    print("System is up and running! Enjoy.")

# Explain: Basically we take picture if we detect something and then wait 5 seconds (which you can change).
# If there is nothing, idle, we upload all the images.
while run_system:
    # Is a count of detected objects in a frame from pixy cam
    # Make it third a second 0.3, which is enough
    # For this purpose, I'll change to 5 seconds.
    sleep(5)
    pixy_detection = pixy_get_blocks(100, pixy_blocks)
    if pixy_detection > 0:
        print("An object or person of interest is detected! Taking picture...")
        # Take a picture and store it locally first.
        img = web_cam.get_image()
        # Image status
        image_status = "0"
        # We also get the time and store into the list
        localtime = time.asctime(time.localtime(time.time()))
        print("Photo captured: " + str(localtime))
        # file_naming
        file_localtime = time.strftime('%Y-%m-%d_%H_%M_%S')
        # Here we name the image with our ways.
        a_img_title_name = "IMG_" + file_localtime + "_" + str(random.randrange(1, 1000))
        # Save image to the user's folder
        pygame.image.save(img, system_user.file_storage_path + "/" + a_img_title_name + ".jpg")
        # Now we get that same full path for the image
        local_img_dir = system_user.file_storage_path + "/" + a_img_title_name + ".jpg"
        # Store short_date for search_date, ex: 2017-12-07
        today = datetime.date.today()
        # We also need to get geo coords and store, Now lets get the location in latitude, longitude
        try:
            a_location = geocoder.ip('me')
            a_point_location = str(a_location.latlng)
        except Exception as eh:
            a_point_location = "N/A"
            pass

        stored_image_status_list.append(image_status)
        stored_time_list.append(localtime)
        stored_image_name_list.append(a_img_title_name)
        stored_image_list.append(local_img_dir)
        stored_search_date_list.append(str(today))
        stored_geocoord_list.append(a_point_location)
        detection_count += 1

    else:
        # If nothing is happening upload the images
        # First we check if there is nothing
        if detection_count >= 1:
            # Call upload task function
            upload_to_firebase_task(system_user, firebase_user, firebase_auth, firebase_database, firebase_storage,
                                    stored_image_list, stored_image_name_list, stored_time_list, stored_geocoord_list,
                                    stored_search_date_list, stored_image_status_list, stored_image_url_list)
            # For a busy day
            if detection_count >= 25:
                twilio_send_busy(system_tool, system_user)
            # Then set it back to 0
            detection_count = 0
        else:
            pass


# This gets printed when user doesn't run system
print("Quitting...")

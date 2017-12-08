"""
    x-wa-main lead programmed by Royce Aquino,
    assistant programmer is JP A.

    Last Edit Date: Dec 7, 2017

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

# TODO: Later add worse-case scenario checks and notify the user of these like: system failure, connection, etc.

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

    def firebase_settings(self):
        firebase_config = {
            "apiKey": "AIzaSyD2vMTSufNIHH0RxWiDGfKkoFWPKKMRYiQ",
            "authDomain": "waphotorecon-app.firebaseapp.com",
            "databaseURL": "https://waphotorecon-app.firebaseio.com",
            "storageBucket": "waphotorecon-app.appspot.com"
        }
        return firebase_config

    # Strings: account_sid, auth_token, phonenumber
    def twilio_settings(self):
        twilio_config = [
            "AC9eac86dec2fae88b7c7f7e786e5ac50d",
            "51fd45acaa40b749e5a371140818d2c2",
            "+18582392249"
        ]
        return twilio_config


# This is for local system running this program only
class Wamain_User:

    user_list = []
    # List for local
    stored_image_list = []
    stored_image_name_list = []
    # List for data
    stored_time_list = []
    stored_geocoord_list = []
    stored_search_date_list = []
    stored_image_url_list = []
    # stored image_type_list is for consecutive pictures, if not it's "0", yes it's "_link", and adds to image_status
    stored_image_status_list = []
    # Now these lists are lists of objects we need to upload.
    obj_sysmes_list = []
    obj_photo_list = []
    obj_user_photo_list = []
    # Variable for storing
    local_file_storage_path = ""

    def __init__(self, name, create_date, location_name, fireb_email, fireb_password, phone_number, system_device_info, file_storage_path):
        self.name = name
        self.create_date = create_date
        self.location_name = location_name
        self.fireb_email = fireb_email
        self.fireb_password = fireb_password
        self.phone_number = phone_number
        self.system_device_info = system_device_info
        self.file_storage_path = file_storage_path

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
            "empty"
        )

    # Starts the webcam, to run a state, it must be True or False.
    def system_webcam(self, initstate, takepicsavestate, stopstate):
        if initstate:
            # Sarting pygame and camera
            webcam_list = pygame.camera.list_cameras()
            if webcam_list:
                webcam = pygame.camera.Camera(webcam_list[0], (280, 210))

            webcam.start()
        if takepicsavestate:
            webcam_list = pygame.camera.list_cameras()
            if webcam_list:
                webcam = pygame.camera.Camera(webcam_list[0], (280, 210))

            # Wait x seconds
            time.sleep(5)
            img = webcam.get_image()
            time.sleep(5)
            # We also get the time and store into the list
            localtime = time.asctime(time.localtime(time.time()))
            Wamain_User.stored_time_list.append(localtime)
            # file_naming
            file_localtime = time.strftime('%Y-%m-%d_%H_%M_%S')
            # Here we name the image with our ways.
            a_img_title_name = "IMG_" + file_localtime + "_" + str(random.randrange(1, 1000))
            # Lets store that image name too into a list.
            Wamain_User.stored_image_name_list.append(a_img_title_name)
            print(Wamain_User.local_file_storage_path)
            # Save image as named in the users UID folder
            pygame.image.save(img, Wamain_User.local_file_storage_path + "/" + a_img_title_name + ".jpg")
            # Now lets get that stored image, later we make images dynamically named
            local_img_dir = Wamain_User.local_file_storage_path + "/" + a_img_title_name + ".jpg"
            # Store short_date for search_date, ex: 2017-12-07
            today = datetime.date.today()
            Wamain_User.stored_search_date_list.append(str(today))
            # Store local image url
            Wamain_User.stored_image_list.append(local_img_dir)
            # We also need to get geo coords and store, Now lets get the location in latitude, longitude
            try:
                a_point_location = geocoder.ip('me')
            except Exception as eh:
                a_point_location = "N/A"
                pass
            Wamain_User.stored_geocoord_list.append(a_point_location)

        if stopstate:
            webcam_list = pygame.camera.list_cameras()
            if webcam_list:
                webcam = pygame.camera.Camera(webcam_list[0], (280, 210))
            webcam.stop()
        pass

    # Start for init, to run a state, it must be True or False.
    def system_rt_database(self, initstate, uploadstate, refresh_auth):
        if initstate:
            firebase = pyrebase.initialize_app(system_tool.firebase_settings())
            firebase_auth = firebase.auth()
            # With our connection we can now log-in. Then we fetch the account info and store the UID and display name
            fireb_user = firebase_auth.sign_in_with_email_and_password(system_user.fireb_email, system_user.fireb_password)
            get_fireb_user_uid = firebase_auth.get_account_info(fireb_user['idToken'])
            stored_firebase_user = My_FireBase_User(get_fireb_user_uid["users"][0]["localId"],
                                                    get_fireb_user_uid["users"][0]["displayName"])
            # Setup database
            firebase_database = firebase.database()
            # Now we create a directory to store the images at, and set it for use later.
            users_new_dir = create_user_dir(stored_firebase_user.uid)
            Wamain_User.local_file_storage_path = users_new_dir

        # This part can be part of a task which is FIFO.
        if uploadstate:
            # Setup database
            firebase_database = firebase.database()
            # We will post times and take time
            localtime = time.asctime(time.localtime(time.time()))
            print("Starting an upload task at: " + str(localtime))
            # Timer for just the upload part
            start_time_upload = timer()
            # TODO: Finish this part.
            # Lets also upload the image to FireBase Storage now
            # TODO: Might want to create it's own function just in-case FireBase Storage is down
            # We want to store that image into our FireBase storage now
            fireb_storage = firebase.storage()
            # Need a for loop to go through each image url and upload them.
            # im_na is image name, lo_im is the full local path address of the photo
            for im_na, lo_im in zip(Wamain_User.stored_image_name_list, Wamain_User.stored_image_list):
                # Between operations lets wait a bit
                sleep(0.100)
                fireb_storage_upload = fireb_storage.child("users/" + My_FireBase_User.uid + "/" + "photos/" + im_na).put(lo_im, fireb_user['idToken'])
                url_from_storage = fireb_storage.child("users/" + My_FireBase_User.uid + "/" + "photos/" + im_na).get_url(fireb_storage_upload['downloadTokens'])
                # Now we store that file_path from get url to our image in a list for later, which is used in upload_tasks
                Wamain_User.stored_image_url_list.append(url_from_storage)

            # Once that finished lets empty those lists for memory.
            Wamain_User.stored_image_list.clear()

            # Creating seed name schema
            random_letter = random.choice(string.ascii_lowercase)
            random_number = random.randrange(0, 1001)

            # We now go through the list until empty, populating our object datas: photo, user_photo, and sys_messages.
            # Start looping until lists are empty.
            # This for loop goes through the five lists to populate our class objects.
            for ti, im, ge, st, da, imn in zip(Wamain_User.stored_time_list, Wamain_User.stored_image_url_list, Wamain_User.stored_geocoord_list,
                                           Wamain_User.stored_image_status_list, Wamain_User.stored_search_date_list, Wamain_User.stored_image_name_list):
                image_status_name = "seed" + random_letter + str(random_number) + st
                obj_sys_message = SysMessage(fireb_user['idToken'], stored_firebase_user.uid, "An image was captured.", self.system_device_info, "true",
                                             ti, fireb_user['idToken'], image_status_name, da)
                # TODO: Finish here
                obj_photo = PPhoto(fireb_user['idToken'], stored_firebase_user.uid, stored_firebase_user.display_name, imn,
                                   im, ge, system_user.location_name, "A photo that was captured.", ti, "false", self.system_device_info, image_status_name, da)
                obj_user_photo = PUserPhoto(fireb_user['idToken'], stored_firebase_user.uid, stored_firebase_user.display_name, imn, im, ge,
                                            system_user.location_name, "A photo that was captured.", ti, "false", self.system_device_info, image_status_name, da)
                # Now we add all objects to the list for uploading later.
                Wamain_User.obj_sysmes_list.append(obj_sys_message)
                Wamain_User.obj_photo_list.append(obj_photo)
                Wamain_User.obj_user_photo_list.append(obj_user_photo)

            # After that process we can empty all other lists.
            Wamain_User.stored_time_list.clear()
            Wamain_User.stored_image_url_list.clear()
            Wamain_User.stored_geocoord_list.clear()
            Wamain_User.stored_image_status_list.clear()
            Wamain_User.stored_search_date_list.clear()
            Wamain_User.stored_image_name_list.clear()

            # Now we upload our data/babies!

            for sys, pho, upho in zip(Wamain_User.obj_sysmes_list, Wamain_User.obj_photo_list, Wamain_User.obj_user_photo_list):
                # We add some time delays in between each operation, 1 second
                sleep(1)
                fireb_res1 = firebase_database.child("usermessagelogs").child(stored_firebase_user.uid).push(sys.message_data(), fireb_user['idToken'])
                sleep(1)
                fireb_res2 = firebase_database.child("allphotos").push(pho.photo_data(), fireb_user['idToken'])
                sleep(1)
                fireb_res3 = firebase_database.child("userphotos").child(stored_firebase_user.uid).push(upho.photo_data(), fireb_user['idToken'])

            # Now uploads have been finished we clear those lists too
            Wamain_User.obj_sysmes_list.clear()
            Wamain_User.obj_photo_list.clear()
            Wamain_User.obj_user_photo_list.clear()

            # Ending time for upload.
            end_time_upload = timer()
            # Elapsed time for the demo.
            elapsed_upload_time = end_time_upload - start_time_upload
            print("The upload task took: " + str(elapsed_upload_time) + " seconds.")

            localtime = time.asctime(time.localtime(time.time()))
            # Print with time
            print("Finished an upload task: " + str(localtime))

        if refresh_auth:
            # Refresh user token
            fireb_user = firebase_auth.refresh(fireb_user['refreshToken'])
            # Fresh token
            fireb_user['idToken']

        pass


# This class is used to store specific user data from FireBase Account Info
class My_FireBase_User:
    def __init__(self, display_name, uid):
        self.display_name = display_name
        self.uid = uid


# For All Photos, photo, basically same thing...
class PPhoto:
    photo_list = []
    # Batch_Photo_Count increments for every 1 million photo count
    Batch_Photo_Count = 0
    Photo_Count = 0
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


# For the userphotos
class PUserPhoto:
    user_photo_list = []
    # Batch_User_Photo_Count increments for every 1 million photo count
    Batch_User_Photo_Count = 0
    User_Photo_Count = 0

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
    sys_message_list = []
    # Batch_Sys_Message_Count increments for every 1 million photo count
    Batch_Sys_Message_Count = 0
    Sys_Message_Count = 0

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


# Below will be functions that we will define and use often

# This create a directory of folders based on user and UID.
# TODO: Later implement folder file system for storing photo of month-year and inside with the day number.
def create_user_dir(user_uid):
    # Making a folder for user, below gets current directory
    cur_dir = os.getcwd()
    # We get absolute path from root
    abs_dir = os.path.abspath(cur_dir)
    new_path = "/" + "stored_photos" + "/" "/" + "users" + "/" + user_uid
    new_dir = abs_dir + new_path
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
        print("A new directory, stored_photos, was created (where your photos will be found): " + new_dir)
    else:
        print("stored_photos is already set.")
    # We will store this path dir to the user.
    return new_dir


# We check devices and such and start some threads.
# TODO: Maybe I could move this to the user class above, maybe.
def check_devices_connection():
    # Sarting pygame and camera
    pygame.init()
    pygame.camera.init()
    camlist = pygame.camera.list_cameras()
    if camlist:
        cam = pygame.camera.Camera(camlist[0], (280, 210))
        cam.start()
        # Add some delay
        time.sleep(10)
        #img = cam.get_image()
        time.sleep(10)
        cam.stop()
    else:
        print("A suitable webcam camera was not found!")
        return False
    try:
        # Initialize Pixy Interpreter thread #
        pixy_init()
        pass
    except Exception as ee:
        print("PixyCam error, not found?")
        print(ee)
        return False
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


# ---- PROGRAM STARTS
# ---- After this line is where the actual program will start running!

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

# Starting gathering of user info. Create system user object
system_user = Wamain_User.from_input()
# Add the user to a list.
Wamain_User.user_list.append(system_user)
# Make a Wamain_tool object
system_tool = Wamain_Tool("Wamain_Tool_1")
# Time to time the demo.
start_time_demo = timer()

# Here we try connecting to the service first
print("The system is now connecting using wi-fi and logging you in...")
try:
    # states: init, upload, refresh_token
    system_user.system_rt_database(True, False, False)

except Exception as e:
    print("An Error has occurred; are you connected to wi-fi or did you enter the wrong e-mail and password or the service is down?")
    print("Error: ")
    print(e)
    print("Quitting...")
    sys.exit(0)

# Once we do that, we know for sure a connection is established, since it passed the connection related tasks.
# Turn webcam on
print("Starting webcam and pixycam...")
system_user.system_webcam(True, False, False)
# Enable PixyCam, need to sleep for 30 miliseconds
#pixy_init()
sleep(10)
# Pixycam block detection, to see our signature defined colors within pixel ranges
blocks = BlockArray(100)
pixy_detection = pixy_get_blocks(100, blocks)

# Used just for this demo test
demo_test = True
alert_once = True

while demo_test:
    sleep(0.30)
    pixy_detection = pixy_get_blocks(100, blocks)
    # Detects something
    if pixy_detection > 0:
        print("An object or person of interest is detected! Taking picture...")
        # Webcam takes a picture, init, take pic, stop
        system_user.system_webcam(False, True, False)
        # For every picture that is not consecutive store "0" into list, if consecutive store "_link"
        Wamain_User.stored_image_status_list.append("0")
        demo_test = False
    else:
        if alert_once:
            print("Please smile in front of the sensor.")
            alert_once = False

# Now that we have a picture, we can upload it.
system_user.system_rt_database(False, True, False)

# That's the end of the demo.
print("The demo test has concluded...")
# Ending time for demo.
end_time_demo = timer()
# Elapsed time for the demo.
elapsed_demo_time = end_time_demo - start_time_demo
print("The test demo took: " + str(elapsed_demo_time) + " seconds!")

# This is the infinite loop for the system, to cancel just quit from the program or un-plug the power.
# We will start a timer, we will refresh the firebase user token every 45 minutes, by checking the timer.
while 1:
    quit = input('type q to quit: ')
    if quit == 'q':
        break
    pass









import os
import sched
import time
from twilio.rest import Client
import pyrebase
import pygame
import json
import requests
import random
import geocoder
from pygame import camera
from pygame import image
from timeit import default_timer as timer
from pixy import *
from ctypes import *


## Two ## means comments # means code not-in-use yet

## Above is module imports

## Start of class for the photo images used to push to real-time database
## Follow same structure of userphotos json in FireBase rt database
## Also with Java model class
## Added device_name
class WAPhoto:
    def __init__(self, user_photo_id, user_id, user_name, photoName, imgdata_url, taken_location, location_name, photo_description, photo_create_date, isAnalyzed, device_name):
        self.user_photo_id = user_photo_id
        self.user_id = user_id
        self.user_name = user_name
        self.photoName = photoName
        self.imgdata_url = imgdata_url
        self.taken_location = taken_location
        self.location_name = location_name
        self.photo_description = photo_description
        self.photo_create_date = photo_create_date
        self.isAnalyzed = isAnalyzed
        self.device_name = device_name

    def adata(self):
        jsondata = {
                "user_photo_id" : self.user_photo_id,
                "user_id" : self.user_id,
                "user_name" : self.user_name,
                "photoName" : self.photoName,
                "imgdata_url" : self.imgdata_url,
                "taken_location" : self.taken_location,
                "location_name" : self.location_name,
                "photo_description" : self.photo_description,
                "photo_create_date" : self.photo_create_date,
                "isAnalyzed" : self.isAnalyzed,
                "device_name" : self.device_name
                }
        return jsondata


global a_user_data
global a_user_real_uid
global a_device_name
global a_user_location_name
global a_img_title_name

print("Starting the WA Photo Recon System!")

## Here will be user set-up questions to configure there system.
a_device_name = "beagleboneblackwireless_m1"

## Questions will start here
print("Settup for this system begins now.")
a_user_location_name = input("What do you want to name the location? ")


## Printing time
localtime = time.asctime(time.localtime(time.time()))
print("Local current time is: ", localtime)

## Now we start the timing demo
print("Demo is starting... Starting time...")

start_time = timer()

## Below is FireBase credentials
config = {
	"apiKey": "AIzaSyD2vMTSufurdr57gKkoFWPKKMRYiQ",
	"authDomain": "waphotorecon-app.firebaseapp.com",
	"databaseURL": "https://waphotorecon-app.firebaseio.com",
	"storageBucket": "waphotorecon-app.appspot.com"
}

## "/root/mywaproj/waphotorecon-app-services.json"

## FireBase init
firebase = pyrebase.initialize_app(config)

print("FireBase connection success!")

## We will create an infinite while loop for user to log-in first
fireb_auth = firebase.auth()
fireb_email = "hidevroyce@gmail.com"
fireb_password = "wacompe571"

fireb_user = fireb_auth.sign_in_with_email_and_password(fireb_email, fireb_password)

print("FireBase user log-in success!")
## Want to print the firebase user UID
## Getting info, it's a JSON object
a_user_uid = fireb_auth.get_account_info(fireb_user['idToken']) 
a_user_data = json.dumps(a_user_uid)
## If want to print JSON object
print(a_user_uid)
## a_user_real_uid is the UID we use globally, also save other info we need
a_user_real_uid = a_user_uid["users"][0]["localId"]
a_user_displayname = a_user_uid["users"][0]["displayName"]
print("Using user with UID: " + a_user_uid["users"][0]["localId"])

## Below is test purposes for firebase data
db = firebase.database()

data = {
	"test": a_device_name,
        "author": a_user_real_uid,
        "system": "WA-Photo Recon"
}

## Submit data
fireb_res = db.child("testusers").child("testing").push(data, fireb_user['idToken'])

print("FireBase test data success!")

## Below is Twilio credentials
account_sid = "AC9eac86dec2fae88b7c7f7e786e5ac50d"
auth_token = "51fd45acaa40b749e5a371140818d2c2"

client = Client(account_sid, auth_token)

## We ask the user for their phone number.
#user_phone = input("What's your cell-phone number (ex:+16196230037)? ")
#test_message = input("Please type a test message to know it works: ")
a_test_message = "This is a test message from: " + a_device_name + " . Working."

print("Executing Twilio test...")

#client.api.account.messages.create(
#	to=user_phone,
#	from_="+18582392249",
#	body=test_message)

## The next step is for FireBase authentication and creation of the folder

## Making a folder for user
cur_dir = os.getcwd()
abs_dir = os.path.abspath(cur_dir)
#final_dir = os.path.join(cur_dir, )
new_path = "/" + "users" + "/" + a_user_real_uid
new_dir = abs_dir + new_path

print(cur_dir)
print(abs_dir)

if not os.path.exists(new_dir):
	os.makedirs(new_dir)
	print(new_dir + " was created.")


print("Starting webcam test phase...")

## Now that we created a folder, lets try taking a test photo first

## Sarting pygame and camera
pygame.init()
pygame.camera.init()
camlist = pygame.camera.list_cameras()

print("Finding webcam...")

## Standard res is 320,240 ratio 4,3 : kinda want a portrait style
if camlist:
    cam = pygame.camera.Camera(camlist[0],(280,210))


cam.start()
print("Starting webcam...")

## Add some delay
time.sleep(10)
print("Getting webcam image...")
img = cam.get_image()
print("Saving webcam image...")

## Here we name the image with our ways.
a_img_title_name = "IMG_" + str(localtime) + str(random.randrange(1,100000)) 

## Save image as named in the users UID folder
pygame.image.save(img, new_dir + "/" + a_img_title_name + ".jpg" )

## Now lets get that stored image, later we make images dynamically named
local_img_dir = new_dir + "/" + a_img_title_name + ".jpg"

print("Webcam test image saved.")

cam.stop()

## Now lets get the location in latitude, longitude
a_point_location = geocoder.ip('me')
print("Image taken at location: " + str(a_point_location.latlng))

print("Sending test image to FireBase Storage...")

## Refresh user token
fireb_user = fireb_auth.refresh(fireb_user['refreshToken'])
## Fresh token
fireb_user['idToken']
## We want to store that image into our FireBase storage now
fireb_storage = firebase.storage()
## Put as the user uid in storage, also needs an image name, test name below
## Instead, we will use local time and name img_localtime_randnumber
#img_test_name = "test" + str(random.randrange(1,100000))

## We store the file in local_img_dir, which is .jpg
fireb_upload = fireb_storage.child("photos/users/" + a_user_real_uid + "/" + a_img_title_name ).put(local_img_dir, fireb_user['idToken'])

print(fireb_upload)
print("Test image saved to FireBase Storage.")

## Now we need to get storage data url
a_imgdata_url = fireb_storage.child("photos/users/" + a_user_real_uid + "/" + a_img_title_name ).get_url(fireb_upload['downloadTokens'])

print("Photo url is: " + a_imgdata_url)

## Now we want to create an object of class photo to upload to rt db
## We will use other things later and such.

print("Creating data object...")

## Just a description
a_desc_info = "This picture was taken on device: " + a_device_name + ". Awesome!"

user_photodata_1 = WAPhoto(fireb_user['idToken'], a_user_real_uid, a_user_displayname, a_img_title_name, a_imgdata_url, str(a_point_location.latlng), a_user_location_name, a_desc_info, localtime, 'false', a_device_name)

print(user_photodata_1.adata())

print("Uploading data...")

fireb_res2 = db.child("userphotos").child(a_user_real_uid).push(user_photodata_1.adata(), fireb_user['idToken'])

print("Upload success!")

end_time = timer()
execution_time = end_time - start_time
print("The demo took: " + str(execution_time))

print("The test has been completed...")
print("The system will now settup and inititate correctly...")
print("To exit out of working condition, input ctrl + z or type qs .")




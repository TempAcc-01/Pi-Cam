import time
from RPIO import PWM
import pygame.camera
import pygame.image
import sqlite3
import atexit
from time import gmtime, strftime
from flask import Flask, render_template, request
app = Flask(__name__)

# x-axis = pin 22   &&   y-axis = pin 23
servo = PWM.Servo()
sortQuery = "SELECT * FROM images ORDER BY date ASC"

@app.route("/")
def main():
    # Create a template data dictionary to send any data to the template
    templateData = {'title' : 'PiCam'}
    # Pass the template data into the template picam.html and return it to the user
    return render_template('piCam4b.html', **templateData)

#sql injections make me sad :-(
@app.route("/sort", methods=['POST'])
def sort():
	print 'Sorting images'
	global sortQuery
	sortOrder = request.form["sortOrder"]
	sortBy = request.form["sortBy"]
	search = str(request.form["search"])
	sortQuery = "SELECT * FROM images "
	if(search != ""):
		searchTokenized = str.split(search)
		sortQuery = sortQuery + "WHERE "
		firstElement = True
		for token in searchTokenized:
			if(firstElement != True):
				sortQuery = sortQuery + "OR "
			firstElement = False
			sortQuery = sortQuery + " description LIKE '%" + token + "%' OR date LIKE '%" + token + "%' OR title LIKE '%" + token + "' "
	sortQuery = sortQuery + "ORDER BY " + sortBy + " " + sortOrder + ";"
	return "C O M P L E T E D"
	
	
# maybe add a check to see if img is deleted here
@app.route("/delete", methods=['POST'])
def deleteImg():
	print 'Deleting image'
	fileName = request.form["fileName"]
	db = sqlite3.connect('static/picam.db')
	c = db.cursor()
	c.execute("DELETE FROM images WHERE fileName='"+fileName+"';")
	db.commit()
	db.close()
	return "C O M P L E T E D"
	
@app.route("/pic", methods=['POST'])
def picRequest():
	print 'Taking picture'
	pygame.camera.init()
	cam = pygame.camera.Camera(pygame.camera.list_cameras()[0], (640,480))
	cam.start()
	img = cam.get_image()
	time = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
	imgName = "static/imgs/" + time + ".bmp"
	pygame.image.save(img, imgName)
	pygame.camera.quit()
	cam.stop()
	return imgName
	#if the user declines to save the pic, code will simply add it in the SQL table (cannot be searched for)
	
#database has columns ('date', 'fileName', 'title', 'description') / all strings
@app.route("/save", methods=['POST'])
def addDatabaseImg():
	print 'Saving image'
	title = request.form["title"]
	description = request.form["description"]
	fileName = request.form["fileName"]
	time = request.form["time"]
	db = sqlite3.connect('static/picam.db')
	c = db.cursor()
	query = "INSERT INTO images VALUES ('"+time+"', '"+fileName+"', '"+title+"', '"+description+"' );"
	c.execute(query)	
	db.commit()
	db.close()
	return "completed"

@app.route("/getPic", methods=['POST'])
def requestDatabaseImg():
	print 'Getting image'
	fileName = request.form["fileName"]
	db = sqlite3.connect('static/picam.db')
	c = db.cursor()
	query = "SELECT title, fileName, description FROM images WHERE fileName='"+fileName+"';"
	c.execute(query)
	result = c.fetchall()
	jsonResult = "{\"result\": [{\"fileName\" : \""+result[0][1]+"\", \"title\" : \""+result[0][0]+"\", \"description\" : \""+result[0][2]+"\"}]}"
	db.close()
	return jsonResult
	
@app.route("/update", methods=['POST'])
def updateDatabaseImg():
	print 'Updating image'
	title = request.form["title"]
	description = request.form["description"]
	fileName = request.form["fileName"]
	db = sqlite3.connect('static/picam.db')
	c = db.cursor()
	query = "UPDATE images SET fileName='"+fileName+"', title='"+title+"', description='"+description+"' WHERE fileName='"+fileName+"';"
	c.execute(query)
	db.commit()
	db.close()
	return "completed"

#dont need all columns
@app.route("/loadImgs", methods=['GET'])
def initImgs():
	print "Loading gallery"
	global sortQuery
	db = sqlite3.connect('static/picam.db')
	c = db.cursor()
	c.execute(sortQuery)
	result = c.fetchall()	
	firstVal = True
	jsonResult = "{\"results\": ["
	for row in result:
		if(firstVal == False):
			jsonResult = jsonResult + "}, "
		jsonResult = jsonResult + "{"
		jsonResult = jsonResult + "\"fileName\" : \"" + str(row[1]) + "\", "
		jsonResult = jsonResult + "\"title\" : \"" + str(row[2]) + "\", "
		jsonResult = jsonResult + "\"description\" : \"" + str(row[3]) + "\""
		firstVal = False
	jsonResult = jsonResult + "}]}"
	db.close()
	return jsonResult

@app.route("/angle", methods=['POST'])
def servoRequest():
	print 	"Moving servos"
	
	print ""
	print "x = " + request.form["xAxis"]
	print "oldX = " + request.form["xAxisOld"]
	print "y = " + request.form["yAxis"]
	print "oldY = " + request.form["yAxisOld"]
	print ""
	
	if(request.form["xAxis"] != "null"):
		xAxis = int(request.form["xAxis"])
	else:
		xAxis = request.form["xAxis"]
	if(request.form["xAxisOld"] != "null"):
		xAxisOld = int(request.form["xAxisOld"])
	else:
		xAxisOld = request.form["xAxisOld"]
	if(request.form["yAxis"] != "null"):
		yAxis = int(request.form["yAxis"])
	else:
		yAxis = request.form["yAxis"]
	if(request.form["yAxisOld"] != "null"):
		yAxisOld = int(request.form["yAxisOld"])
	else:
		yAxisOld = request.form["yAxisOld"]

	if ((xAxis != "null") and (xAxisOld != "null")):
		print "xAxis being adjusted"
		print ""
		print "x = " + str(xAxis)
		print "xOld = " + str(xAxisOld)
		print ""
		if (xAxis > xAxisOld):
			angle = xAxis - xAxisOld
			print "xOld < x"
			print "angle = " + str(angle)
			print ""
			while (angle >= 180):
				print "angle = " + str(angle)
				servo.set_servo(22,1600)
				time.sleep(.60)
				servo.stop_servo(22)
				angle = angle - 180
				time.sleep(.5)
				print "angle-180 = " + str(angle)
			while (angle >= 100):
				print "angle = " + str(angle)
				servo.set_servo(22,1600)
				time.sleep(.30)
				servo.stop_servo(22)
				angle = angle - 100
				time.sleep(.5)
				print "angle-100 = " + str(angle)
			while (angle >= 80):
				print "angle = " + str(angle)
				servo.set_servo(22,1600)
				time.sleep(.2)
				servo.stop_servo(22)
				time.sleep(.5)
				angle = angle - 80
				print "angle-80 = " + str(angle)
			while (angle >= 60):
				print "angle = " + str(angle)
				servo.set_servo(22,1580)
				time.sleep(.18)
				servo.stop_servo(22)
				time.sleep(.5)
				angle = angle - 60
				print "angle-60 = " + str(angle)
			while (angle >= 40):
				print "angle = " + str(angle)
				servo.set_servo(22,1570)
				time.sleep(.14)
				servo.stop_servo(22)
				time.sleep(.5)
				angle = angle - 40
				print "angle-40 = " + str(angle)
			while (angle >= 20):
				print "angle = " + str(angle)
				servo.set_servo(22,1560)
				time.sleep(.08)
				servo.stop_servo(22)
				time.sleep(.5)
				angle = angle - 20
				print "angle-20 = " + str(angle)
				
		elif (xAxis < xAxisOld):
			angle = xAxisOld - xAxis
			print "x < xOld"
			print "angle = " + str(angle)
			print ""
			while (angle >= 180):
				print "angle = " + str(angle)
				servo.set_servo(22,1450)
				time.sleep(.64)
				servo.stop_servo(22)
				angle = angle - 180
				time.sleep(.5)
				print "angle-180 = " + str(angle)
			while (angle >= 100):
				print "angle = " + str(angle)
				servo.set_servo(22,1450)
				time.sleep(.32)
				servo.stop_servo(22)
				angle = angle - 100
				time.sleep(.5)
				print "angle-100 = " + str(angle)
			while (angle >= 80):
				print "angle = " + str(angle)
				servo.set_servo(22,1460)
				time.sleep(.28)
				servo.stop_servo(22)
				time.sleep(.5)
				angle = angle - 80
				print "angle-80 = " + str(angle)
			while (angle >= 60):
				print "angle = " + str(angle)
				servo.set_servo(22,1470)
				time.sleep(.2)
				servo.stop_servo(22)
				time.sleep(.5)
				angle = angle - 60
				print "angle-60 = " + str(angle)
			while (angle >= 40):
				print "angle = " + str(angle)
				servo.set_servo(22,1480)
				time.sleep(.18)
				servo.stop_servo(22)
				time.sleep(.5)
				angle = angle - 40
				print "angle-40 = " + str(angle)
			while (angle >= 20):
				print "angle = " + str(angle)
				servo.set_servo(22,1490)
				time.sleep(.12)
				servo.stop_servo(22)
				time.sleep(.5)
				angle = angle - 20
				print "angle-20 = " + str(angle)
				
	if (yAxis != "null" and yAxisOld != "null"):
		print "yAxis being adjusted"
		print ""
		print "y = " + str(yAxis)
		print "yOld = " + str(yAxisOld)
		print ""
		if (yAxis > yAxisOld):
			angle = yAxis - yAxisOld
			print "yOld < y"
			print "angle = " + str(angle)
			print ""
			while (angle >= 180):
				print "angle = " + str(angle)
				servo.set_servo(23,1600)
				time.sleep(.60)
				servo.stop_servo(23)
				angle = angle - 180
				time.sleep(.5)
				print "angle-180 = " + str(angle)
			while (angle >= 100):
				print "angle = " + str(angle)
				servo.set_servo(23,1600)
				time.sleep(.30)
				servo.stop_servo(23)
				angle = angle - 100
				time.sleep(.5)
				print "angle-100 = " + str(angle)
			while (angle >= 80):
				print "angle = " + str(angle)
				servo.set_servo(23,1600)
				time.sleep(.2)
				servo.stop_servo(23)
				time.sleep(.5)
				angle = angle - 80
				print "angle-80 = " + str(angle)
			while (angle >= 60):
				print "angle = " + str(angle)
				servo.set_servo(23,1580)
				time.sleep(.18)
				servo.stop_servo(23)
				time.sleep(.5)
				angle = angle - 60
				print "angle-60 = " + str(angle)
			while (angle >= 40):
				print "angle = " + str(angle)
				servo.set_servo(23,1570)
				time.sleep(.14)
				servo.stop_servo(23)
				time.sleep(.5)
				angle = angle - 40
				print "angle-40 = " + str(angle)
			while (angle >= 20):
				print "angle = " + str(angle)
				servo.set_servo(23,1560)
				time.sleep(.08)
				servo.stop_servo(23)
				time.sleep(.5)
				angle = angle - 20
				print "angle-20 = " + str(angle)
				
		elif (yAxis < yAxisOld):
			angle = yAxisOld - yAxis
			print "y < yOld"
			print "angle = " + str(angle)
			print ""
			while (angle >= 180):
				print "angle = " + str(angle)
				servo.set_servo(23,1450)
				time.sleep(.64)
				servo.stop_servo(23)
				angle = angle - 180
				time.sleep(.5)
				print "angle-180 = " + str(angle)
			while (angle >= 100):
				print "angle = " + str(angle)
				servo.set_servo(23,1450)
				time.sleep(.32)
				servo.stop_servo(23)
				angle = angle - 100
				time.sleep(5)
				print "angle-100 = " + str(angle)
			while (angle >= 80):
				print "angle = " + str(angle)
				servo.set_servo(23,1460)
				time.sleep(.28)
				servo.stop_servo(23)
				time.sleep(.5)
				angle = angle - 80
				print "angle-80 = " + str(angle)
			while (angle >= 60):
				print "angle = " + str(angle)
				servo.set_servo(23,1470)
				time.sleep(.2)
				servo.stop_servo(23)
				time.sleep(.5)
				angle = angle - 60
				print "angle-60 = " + str(angle)
			while (angle >= 40):
				print "angle = " + str(angle)
				servo.set_servo(23,1480)
				time.sleep(.18)
				servo.stop_servo(23)
				time.sleep(.5)
				angle = angle - 40
				print "angle-40 = " + str(angle)
			while (angle >= 20):
				print "angle = " + str(angle)
				servo.set_servo(23,1490)
				time.sleep(.12)
				servo.stop_servo(23)
				time.sleep(.5)
				angle = angle - 20
				print "angle-20 = " + str(angle)
	return "c o m p l e t e d"
	

# Clean everything up when the app exits
def cleanup():
 	PWM.cleanup()
 
# Clean everything up when the app exits
atexit.register(cleanup)

if __name__ == "__main__":
    app.run(host='192.168.1.101', port=80, debug=True)

		
		
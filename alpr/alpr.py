from flask import Blueprint, request, Flask, jsonify
from flask_mysqldb import MySQLdb, MySQL
import cv2 as cv
import numpy as np
import pytesseract
from datetime import *
import os



alpr = Blueprint('alpr', __name__)

app = Flask(__name__)

app.secret_key = "alpr"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Initialize the parameters
confThreshold = 0.5  #Confidence threshold
nmsThreshold = 0.4  #Non-maximum suppression threshold

# Initialize the pyetesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

inpWidth = 416  #608     #Width of network's input image
inpHeight = 416 #608     #Height of network's input image

# Load names of classes
classesFile = "alpr/classes.names"

classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# Give the configuration and weight files for the model and load the network using them.
modelConfiguration = "alpr/darknet-yolov3.cfg"
modelWeights = "alpr/lapi.weights"
net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Draw the predicted bounding box and cut the detected plate
def drawPred(frame, classId, conf, left, top, right, bottom, token):
    
    #Cut Plate
    plate = frame[top:bottom, left:right]

    #save Plate
    filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    dirname = 'static/storage/'+token
    isExist = os.path.exists(dirname)
    if not isExist:
        os.mkdir(dirname)
    cv.imwrite(dirname+'/'+filename+'.jpg', plate)

    #Gray
    gray = cv.cvtColor(plate, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (3,3), 0)
    thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]

    cv.imwrite(dirname+'/'+filename+'-gray.jpg', gray)
    cv.imwrite(dirname+'/'+filename+'-tresh.jpg', thresh)

    # tesseract implementation
    text = pytesseract.image_to_string(thresh, config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    print("Detected license plate Number:",text)
    
    #get Only Alphanumeric
    s = ''.join(ch for ch in text if ch.isalnum())

    # if not s:
    #         text = pytesseract.image_to_string(invert, config="--psm 12 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    #         print("Detected license plate Number New:",text)
    #         s = ''.join(ch for ch in text if ch.isalnum())


    # Saving to Database
     
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute("SELECT id FROM apps WHERE token=%s", (token,))
    token_id = curl.fetchone()
    insert = curl.execute("INSERT INTO license_plate (app_id, plate_number, file) VALUES (%s,%s,%s)",(token_id['id'], s, dirname+'/'+filename+'.jpg', ))
    mysql.connection.commit()

    return s

# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs, token):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        print("out.shape : ", out.shape)
        for detection in out:
            #if detection[4]>0.001:
            scores = detection[5:]
            classId = np.argmax(scores)
            #if scores[classId]>confThreshold:
            confidence = scores[classId]
            if detection[4]>confThreshold:
                print(detection[4], " - ", scores[classId], " - th : ", confThreshold)
                print(detection)
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    print(len(confidences))
    license = ''
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        license = drawPred(frame, classIds[i], confidences[i], left, top, left + width, top + height, token)
    if license:
        return [len(confidences), license]
    else:
        return [len(confidences)]


@alpr.route("/app/<token>", methods=["GET", "POST"])
def app(token):
    if request.method == 'POST':
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM apps WHERE token=%s", (token,))
        app = curl.fetchone()
        if not app:
            value = {
                'status':0,
                'message':'Token is Invalid',
            }
            return value

        #Get Image Request
        imagefile = request.files['imageFile'].read()

        #convert string data to numpy array
        npimg = np.fromstring(imagefile, dtype=np.uint8)

        # convert numpy array to image
        img = cv.imdecode(npimg, cv.IMREAD_UNCHANGED)

        blob = cv.dnn.blobFromImage(img, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)

        # Sets the input to the network
        net.setInput(blob)

        # Runs the forward pass to get output of the output layers
        outs = net.forward(getOutputsNames(net))

        # Remove the bounding boxes with low confidence
        test = postprocess(img, outs, token)
   
        if test[0] is 0:
            value = {
                'status':0,
                'message':'Plat Nomor Tidak Terdeteksi',
            }
            return value

        if len(test) >= 2:
            value = {
                'status':1,
                'message':'Plat Nomor Terdeteksi',
                'license': test[1]
            }
            return value

        elif len(test) == 1:
            value = {
                'status':1,
                'message':'Plat Nomor Terdeteksi',
                'license': 'Gagal Membaca Plat Nomor'
            }
            return value
    else:
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM apps WHERE token=%s", (token,))
        app = curl.fetchone()
        if not app:
            value = {
                'status':0,
                'message':'Token is Invalid',
            }
            return value

        curl.execute("SELECT * FROM license_plate WHERE app_id=%s", (app['id'],))
        data = curl.fetchall()
        return jsonify(data)
import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from src.services.predictor import Predictor
import logging


# Initialize the Flask app
app = Flask(__name__)

def init_predictor():
    global predictor
    predictor = Predictor()

# One-time initialization
with app.app_context():
    init_predictor()

# Configuration
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def map_career(career_key): 
    if career_key == 'ca-si':
        return 'Ca sĩ'
    elif career_key == 'hot-girl':
        return 'Hot girl'
    elif career_key == 'nguoi-mau':
        return 'Người mẫu'
    elif career_key == 'dien-vien':
        return 'Diễn viên'
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def upload_and_process():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                
              filename = secure_filename(file.filename)
              filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
              file.save(filepath)
              
              # Process the image to find and draw the bounding box

              predict_result = predictor.predict(filepath)
              processed_image = predictor.render_result(predict_result, filepath) 
              processed_filename = "bbox_" + filename      
              processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
              cv2.imwrite(processed_image_path, processed_image)

              print(predict_result['payload'])

              if (predict_result['payload'] == None):
                  return render_template('index.html', 
                                        original_image=filename, 
                                        processed_image=processed_filename)
              
              return render_template('index.html', 
                                    original_image=filename, 
                                    processed_image=processed_filename, 
                                    person_name=predict_result['payload']['name'],
                                    person_career=map_career(predict_result['payload']['career']), 
                                    person_birthdate=predict_result['payload']['birthdate'],
                                    href_url=predict_result['payload']['ref'])
            except Exception as e:
                logging.basicConfig(level=logging.ERROR)

                # Log the error message
                logging.error("An error occurred during image processing: %s", str(e))

                # Notify the browser with a user-friendly message
                return render_template('index.html', 
                                       original_image=None, 
                                       processed_image=None, 
                                       error_message="An error occurred while processing the image. Please try again.")

    # For a GET request, just show the upload form
    return render_template('index.html', original_image=None, processed_image=None)


if __name__ == '__main__':
    app.run(debug=True)

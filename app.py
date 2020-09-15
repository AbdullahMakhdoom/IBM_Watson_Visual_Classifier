import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import zipfile
import shutil


my_apikey = 'kjiT3WJh3p989an0djT_BxwaOWeP-NsP8GSHjiSxTdft'

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
# app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html')


def process_zip(path, filename):
    # Unzip the fashion testing in downloads folder
    zip_ref = zipfile.ZipFile(os.path.join(UPLOAD_FOLDER, filename), 'r')
    zip_ref.extractall(DOWNLOAD_FOLDER)
    zip_ref.close()

    # Name of the testing folder i.e: Testfashion
    testing_folder = filename.rsplit('.', 1)[0]
    print(testing_folder)

    if not os.path.exists(DOWNLOAD_FOLDER + 'Classified'):
        print('Classified folder made')
        os.mkdir(DOWNLOAD_FOLDER + 'Classified')

    # classifying images in testing folder
    for (roots, dirs, images) in os.walk(os.path.join(DOWNLOAD_FOLDER , testing_folder)):
        for img in images:
            # Classifier function
            # class_dir = predict_df["class"]

            class_dir = 'longdress' # dummy variable
            print("reading images...")

            # If folder for predicted class does not exist
            if not os.path.exists(DOWNLOAD_FOLDER + 'Classified/' + class_dir):
                os.mkdir(DOWNLOAD_FOLDER + 'Classified/' + class_dir) # then make directory
                print("directory made")

            # Moving the image from testing folder to predicted class folder
            print(img)
            source = os.path.join(DOWNLOAD_FOLDER , testing_folder, img)
            destination = os.path.join(DOWNLOAD_FOLDER ,'Classified' ,class_dir)
            shutil.move(source , destination)
    os.rmdir(os.path.join(DOWNLOAD_FOLDER , testing_folder))
    shutil.make_archive(DOWNLOAD_FOLDER+'Classified', 'zip', DOWNLOAD_FOLDER + 'Classified')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    process_zip(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], 'Classified.zip', as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

import os, shutils
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from pandas.io.json import json_normalize
from zipfile import ZipFile


classifier_id = 'furnitureclassifier_1414993083'
my_apikey = 'kjiT3WJh3p989an0djT_BxwaOWeP-NsP8GSHjiSxTdft'

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def getdf_visrec(url, classifier_ids, apikey = my_apikey):

    json_result = visrec.classify(url=url,
                              threshold='0.6',
                              classifier_ids=classifier_ids).get_result()

    json_classes = json_result['images'][0]['classifiers'][0]['classes']

    df = json_normalize(json_classes).sort_values('score', ascending=False).reset_index(drop=True)

    return df

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        print(file)
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            with ZipFile(filename,'r') as zipImg:
                zipImg.extractall()
            for roots, dirs, img in os.walk(UPLOAD_FOLDER, topdown=False ):
                process_file(roots, img)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html')


def process_file(path, filename):
    result_df = getdf_visrec(url = filename, classifier_ids= classifier_id)
    class_dir = result_df["class"]
    if not os.path.exists(os.path.join(app.config['DOWNLOAD_FOLDER'], classdir)):
        os.mkdir(os.path.join(app.config['DOWNLOAD_FOLDER'], classdir))
    shutil.move(path, os.path.join(app.config['DOWNLOAD_FOLDER'], classdir))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

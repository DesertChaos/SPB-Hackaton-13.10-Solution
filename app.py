from flask import Flask, render_template, request, send_file, redirect, url_for, send_from_directory
from ultralytics import YOLO
import os

app = Flask(__name__)

model = YOLO("best.pt")

UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def detect_objects(image_path):
    results = model([image_path])
    result = results[0]
    annotated_image_path = os.path.join(UPLOAD_FOLDER, "annotated_" + os.path.basename(image_path))
    result.save(filename=annotated_image_path)
    return annotated_image_path


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)

        annotated_image_path = detect_objects(image_path)

        return redirect(url_for('result', filename=os.path.basename(annotated_image_path)))


@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run(debug=True)
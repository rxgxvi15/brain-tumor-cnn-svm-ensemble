from tensorflow.keras.models import load_model
from flask import Flask, url_for, render_template, redirect, session, Response
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from flask_wtf.file import FileRequired, FileAllowed
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ragavi'

class BrainForm(FlaskForm):
    style = {'class': 'form-control', 'style': 'width:25%;'}
    image = FileField("", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images Only!')
    ], render_kw=style)
    submit = SubmitField("Analyze", render_kw={'class': 'btn btn-outline-primary'})

# Corrected file path without leading space and using raw string
model = load_model(r'C:\Users\ragha\Downloads\CODE_Brain_Tumor\CODE_Brain_Tumor\braintumor.keras')

def predict(model, sample):
    img = cv2.imread(sample)
    if img is None:
        raise ValueError(f"Image at path {sample} could not be read.")
    img = cv2.resize(img, (150, 150))
    img = np.reshape(img, (1, 150, 150, 3))
    return np.argmax(model.predict(img))

def tumor_name(value):
    if value == 0:
        return 'Glioma Tumor'
    elif value == 1:
        return 'Meningioma Tumor'
    elif value == 2:
        return 'No Tumor Found'
    elif value == 3:
        return 'Pituitary Tumor'
    else:
        return 'Unknown'

x = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    form = BrainForm()

    if form.validate_on_submit():
        assets_dir = './static'
        img = form.image.data
        img_name = secure_filename(img.filename)

        img_path = os.path.join(assets_dir, img_name)
        img.save(img_path)
        global x
        x = img_path

        return redirect(url_for('prediction'))

    return render_template('home.html', form=form)

@app.route('/result')
def prediction():
    try:
        pred_val = predict(model, x)
        result = tumor_name(pred_val)
    except Exception as e:
        result = f"An error occurred: {e}"
    finally:
        if os.path.exists(x):
            os.remove(x)
    return render_template('prediction.html', result=result)

@app.route('/brain_tumor')
def what():
    return render_template('what.html')

@app.route('/about_me')
def me():
    return render_template('about_me.html')

if __name__ == '__main__':
    app.run()

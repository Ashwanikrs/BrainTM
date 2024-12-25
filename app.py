from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image, ImageOps
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Initialize Flask app
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'Templates')  # Templates directory    # Static files directory
)
# Load the pre-trained model
def load_model():
    model = tf.keras.models.load_model('BrainTu.h5')
    return model

model = load_model()

# Prediction function
def import_and_predict(image_data, model):
    size = (150, 150)
    image = ImageOps.fit(image_data, size, Image.Resampling.LANCZOS)
    image = ImageOps.grayscale(image)
    img_array = np.asarray(image)
    img_reshape = img_array.reshape(1, 150, 150, 1)
    prediction = model.predict(img_reshape)
    return prediction

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        image = Image.open(file)
        predictions = import_and_predict(image, model)
        class_names = ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']
        predicted_class = class_names[np.argmax(predictions)]
        return jsonify({"prediction": predicted_class}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use the PORT variable, default to 5000 if not set
    app.run(host='0.0.0.0', port=port, debug=False)

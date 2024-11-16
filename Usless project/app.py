from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import pyttsx3
import io
import winsound

app = Flask(__name__)

# Initialize pyttsx3 engine for voice confirmation
engine = pyttsx3.init()

# Function to generate random CAPTCHA text
def generate_captcha_text(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Function to create CAPTCHA image
def create_captcha_image(text):
    width, height = 220, 80
    image = Image.new('RGB', (width, height), (255, 255, 255))
    try:
        font = ImageFont.truetype("arial.ttf", 42)
    except IOError:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    for i, char in enumerate(text):
        position = (15 + i * 35, random.randint(10, 20))
        draw.text(position, char, font=font, fill=(random.randint(50, 150), random.randint(50, 150), random.randint(50, 150)))
    for _ in range(5):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([start, end], fill=(0, 0, 0), width=2)
    return image.filter(ImageFilter.BLUR)

# Voice confirmation function
def voice_confirmation(message):
    engine.say(message)
    engine.runAndWait()

# Function to play warning sound
def play_warning_sound():
    winsound.Beep(1000, 200)

# Route to serve the CAPTCHA page
@app.route('/')
def index():
    return render_template('index.html')

# Route to generate CAPTCHA image
@app.route('/generate_captcha')
def generate_captcha():
    captcha_text = generate_captcha_text()
    captcha_image = create_captcha_image(captcha_text)
    
    # Save the image to a BytesIO object
    img_io = io.BytesIO()
    captcha_image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name="captcha.png")

# Route to handle CAPTCHA validation
@app.route('/validate_captcha', methods=['POST'])
def validate_captcha():
    user_input = request.form['captcha_input']
    captcha_text = request.form['captcha_text']
    
    if user_input == captcha_text:
        response = {"status": "success", "message": "Captcha Correct!"}
    else:
        response = {"status": "error", "message": "Incorrect CAPTCHA. Please try again."}
        voice_confirmation("Try again, it's not that hard!")
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)


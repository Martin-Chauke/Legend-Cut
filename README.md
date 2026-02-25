# 💇 Legend Cut - Virtual Hair Salon

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-red)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.8-orange)](https://mediapipe.dev/)

**Legend Cut** is a cutting-edge virtual hair try-on application that uses computer vision to let you experiment with different hairstyles in real-time through your camera.

##  Features

- **Real-time Face Detection** - Powered by MediaPipe for accurate facial landmark tracking
- **Gender-based Style Selection** - Separate collections for male and female hairstyles
- **Live Camera Integration** - Try on hairstyles instantly with your webcam
- **Custom Uploads** - Upload your own hairstyle images
- **Adjustment Controls** - Fine-tune position, size, and rotation of hairstyles
- **Photo Capture** - Save your favorite looks
- **Head Pose Estimation** - Hairstyles automatically adjust to head movements
- **Responsive Design** - Works on desktop and mobile devices

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam (for live try-on)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/legend-cut.git
cd legend-cut   
```

2. **Create virtual environment**(optional but recommended)
``` bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. ## Install dependences
```bash
pip install -r requirements.txt
```

4. ## Add hairstyle images

* Place male hairstyles in app/static/haircuts/male/

* Place female hairstyles in app/static/haircuts/female/

* Use PNG format with transparent backgrounds for best results

5. ## Run the application
```
python legendrun.py
```
6. # Open your browser
  
  * Navigate to  http://localhost:8000
  * Allow camera access when prompted


## Project Structure

Legend Cut/
├── app/
│   ├── main.py              # FastAPI application
│   ├── templates/            # HTML templates
│   ├── static/               # Static files (CSS, JS, images)
│   │   ├── css/              # Stylesheets
│   │   ├── js/               # JavaScript files
│   │   └── haircuts/         # Hairstyle images
│   │       ├── male/         # Male hairstyles
│   │       ├── female/       # Female hairstyles
│   │       └── custom/       # Uploaded hairstyles
│   └── utils/                # Utility modules
│       ├── face_utils.py     # Face detection utilities
│       └── hair_overlay.py   # Hair overlay processing
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
└── README.md                 # This file


# How It Works

1. **Face Detection** - MediaPipe Face Mesh detects 468 facial landmarks
2. **Head Pose Estimation**- Calculates head rotation and position
3. **Hair Region Detection** - Identifies optimal area for hair placement
4. **Haircut Transformation** - Resizes and rotates hairstyle to match head pose
5. **Alpha Blending**- Seamlessly blends hairsytle with camera feed 

#  API Endpoints

 API Endpoints
Endpoint  || Method	||   Description
/	GET	 || Main     ||application page
/api/health	|| GET	|| Health check
/api/haircuts/{gender} || GET || Get available hairstyles
/api/upload-haircut || 	POST ||	Upload custom hairstyle
/api/process-frame || POST ||	Process video frame
/api/adjust-haircut || 	POST || Adjust hairstyle parameters
/api/reset-session	|| POST ||	Reset user session


#  Adding Hairstyles

 **Image Requirements**

* Format: PNG (preferred) or JPG

* Background: Transparent (PNG) or solid color

* Size: Minimum 300x300 pixels

* Style: Front-facing view recommended

# Naming Convention

Use descriptive names with underscores:

* classic_pompadour.png

* modern_fade.png

* long_layered_cut.png


# ⚙️ Configuration

Edit in **app/static/js/main.js:**
```
javascript
video: {
    width: { ideal: 1280 },
    height: { ideal: 720 },
    facingMode: 'user'
}
```

# Face Detection Sensitivity

Adjust in **app/utils/face_utils.py:**
```
python

self.face_mesh = self.mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5,  # Lower = more sensitive
    min_tracking_confidence=0.5     # Lower = more sensitive
)
```

# License

# ACKNOWLEDGEMENT

* https://mediapipe.dev/  (MediaPipe for face detection)
* https://fastapi.tiangolo.com/  (FastAPI) for the web framework
* https://opencv.org/  (OpenCV) for image processing
* https://getbootstrap.com/ (Bootstrap for UI components)

# 📧 Contact
 
 * Project Link: https://github.com/Martin-Chauke/legend-cut

* Report bugs: Issues


#  Happy Styling!
 
 Transform your look with Legend Cut - Where Style Meets Technology!

 
## Installation Instructions

1. **Create the Legend Cut folder structure:**
```bash
mkdir -p Legend\ Cut/app/static/haircuts/{male,female,custom}
mkdir -p Legend\ Cut/app/static/{css,js}
mkdir -p Legend\ Cut/app/templates
mkdir -p Legend\ Cut/app/utils
```

2. # Copy all the provided files into their respective folders

3. # Add some sample haircut images (PNG with transparent background) to:

* Legend Cut/app/static/haircuts/male/

* Legend Cut/app/static/haircuts/female/

4. Install dependences
```bash
cd "Legend Cut"
pip install -r requirements.txt
```
5. # Run the application

 python legendrun.py

6. ## OPEN YOUR BROWSER to ** http://localhost:8000 **

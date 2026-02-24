 
from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
from typing import Optional
import os
import uuid
import logging
from datetime import datetime
from app.utils.face_utils import FaceDetector
from app.utils.hair_overlay import HairOverlay

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Legend Cut - Virtual Hair Salon",
    description="Try on different hairstyles virtually using your camera",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize utilities
face_detector = FaceDetector()
hair_overlay = HairOverlay()

# Store active sessions
active_sessions = {}

@app.get("/")
async def home(request: Request):
    """Render the Legend Cut main page"""
    logger.info("Serving Legend Cut homepage")
    
    # Get available haircuts
    male_haircuts = []
    female_haircuts = []
    
    try:
        male_dir = "app/static/haircuts/male"
        female_dir = "app/static/haircuts/female"
        
        if os.path.exists(male_dir):
            male_haircuts = [f for f in os.listdir(male_dir) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if os.path.exists(female_dir):
            female_haircuts = [f for f in os.listdir(female_dir) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
        logger.info(f"Found {len(male_haircuts)} male and {len(female_haircuts)} female haircuts")
    except Exception as e:
        logger.warning(f"Error loading haircut directories: {e}")
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "app_name": "Legend Cut",
            "male_haircuts": male_haircuts,
            "female_haircuts": female_haircuts,
            "current_year": datetime.now().year
        }
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "Legend Cut",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload-haircut")
async def upload_haircut(file: UploadFile = File(...)):
    """Upload custom haircut image to Legend Cut"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        # Create unique filename

        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ['png', 'jpg', 'jpeg', 'gif']:
            raise HTTPException(400, "Only PNG, JPG, JPEG, and GIF files are allowed")
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{file_extension}"
        filepath = f"app/static/haircuts/custom/{filename}"
        
        # Ensure custom directory exists
        os.makedirs("app/static/haircuts/custom", exist_ok=True)
        
        # Save file
        contents = await file.read()
        
        # Validate file size (max 10MB)
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(400, "File size too large. Maximum 10MB allowed.")
        
        with open(filepath, "wb") as f:
            f.write(contents)
        
        logger.info(f"Custom haircut uploaded: {filename}")
        
        return JSONResponse({
            "success": True,
            "message": "Haircut uploaded successfully",
            "filename": filename,
            "path": f"/static/haircuts/custom/{filename}"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading haircut: {str(e)}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/process-frame")
async def process_frame(data: dict):
    """Process video frame and apply Legend Cut hairstyle"""
    try:
        # Get frame data
        frame_data = data.get("frame")
        gender = data.get("gender", "male")
        haircut = data.get("haircut")
        session_id = data.get("session_id")
        
        if not frame_data:
            return JSONResponse({
                "success": False,
                "error": "Missing frame data"
            })
        
        if not haircut:
            return JSONResponse({
                "success": False,
                "error": "No haircut selected"
            })
        
        # Decode base64 image
        if "base64," in frame_data:
            frame_data = frame_data.split("base64,")[1]
        
        # Decode and convert to numpy array
        try:
            img_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ValueError("Failed to decode image")
        except Exception as e:
            logger.error(f"Error decoding frame: {e}")
            return JSONResponse({
                "success": False,
                "error": "Invalid frame data"
            })
        
        # Apply haircut overlay
        result_frame, face_detected = hair_overlay.apply_haircut(
            frame, 
            haircut, 
            gender,
            session_id
        )
        
        # Encode back to base64
        _, buffer = cv2.imencode('.jpg', result_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return JSONResponse({
            "success": True,
            "frame": f"data:image/jpeg;base64,{result_base64}",
            "face_detected": face_detected
        })
    
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/haircuts/{gender}")
async def get_haircuts(gender: str):
    """Get list of available Legend Cut hairstyles for gender"""
    try:
        if gender not in ['male', 'female', 'custom']:
            return JSONResponse({
                "success": False,
                "error": "Invalid gender. Use 'male', 'female', or 'custom'"
            })
        
        haircut_dir = f"app/static/haircuts/{gender}"
        if os.path.exists(haircut_dir):
            # Get all image files
            all_files = os.listdir(haircut_dir)
            haircuts = [h for h in all_files if h.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            
            # Sort by name
            haircuts.sort()
            
            return JSONResponse({
                "success": True, 
                "haircuts": haircuts,
                "count": len(haircuts),
                "gender": gender
            })
        
        return JSONResponse({
            "success": False, 
            "error": "Gender directory not found"
        })
    except Exception as e:
        logger.error(f"Error getting haircuts: {str(e)}")
        return JSONResponse({
            "success": False, 
            "error": str(e)
        }, status_code=500)

@app.post("/api/adjust-haircut")
async def adjust_haircut(data: dict):
    """Adjust haircut position/size in Legend Cut"""
    try:
        session_id = data.get("session_id")
        adjustments = data.get("adjustments", {})
        
        if not session_id:
            return JSONResponse({
                "success": False, 
                "error": "Session ID required"
            })
        
        # Store adjustments in session
        if session_id not in active_sessions:
            active_sessions[session_id] = {}
        
        active_sessions[session_id]["adjustments"] = adjustments
        logger.info(f"Adjusted haircut for session {session_id}: {adjustments}")
        
        return JSONResponse({
            "success": True,
            "message": "Adjustments saved"
        })
        
    except Exception as e:
        logger.error(f"Error adjusting haircut: {str(e)}")
        return JSONResponse({
            "success": False, 
            "error": str(e)
        }, status_code=500)

@app.post("/api/reset-session")
async def reset_session(data: dict):
    """Reset a Legend Cut session"""
    try:
        session_id = data.get("session_id")
        if session_id and session_id in active_sessions:
            del active_sessions[session_id]
            logger.info(f"Session reset: {session_id}")
            return JSONResponse({
                "success": True,
                "message": "Session reset successfully"
            })
        
        return JSONResponse({
            "success": False, 
            "error": "Session not found"
        })
    except Exception as e:
        logger.error(f"Error resetting session: {str(e)}")
        return JSONResponse({
            "success": False, 
            "error": str(e)
        }, status_code=500)

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session data"""
    if session_id in active_sessions:
        return JSONResponse({
            "success": True,
            "session": active_sessions[session_id]
        })
    
    return JSONResponse({
        "success": False,
        "error": "Session not found"
    })
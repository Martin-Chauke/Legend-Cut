"""
Legend Cut Face Detection Utilities
Handles facial landmark detection and head pose estimation
"""

import cv2
import mediapipe as mp
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FaceDetector:
    """Advanced face detection and landmark tracking for Legend Cut"""
    
    def __init__(self):
        """Initialize MediaPipe face mesh detector"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Key facial landmarks indices for Legend Cut
        self.FACE_OVAL = list(range(10, 152))
        self.FOREHEAD = [10, 67, 69, 104, 108, 109, 151, 337, 338, 339]
        self.LEFT_EYEBROW = [46, 52, 53, 55, 63, 65, 66, 70, 105, 107]
        self.RIGHT_EYEBROW = [276, 282, 283, 285, 293, 295, 296, 300, 334, 336]
        self.NOSE_TIP = 1
        self.CHIN = 152
        self.LEFT_EYE_LEFT = 33
        self.RIGHT_EYE_RIGHT = 263
        self.LEFT_MOUTH = 61
        self.RIGHT_MOUTH = 291
        self.FOREHEAD_TOP = 10
        self.EYEBROW_CENTER = 8
        
        logger.info("Legend Cut Face Detector initialized")
    
    def detect_face(self, image):
        """Detect face and return landmarks"""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process the image
            results = self.face_mesh.process(rgb_image)
            
            if results and results.multi_face_landmarks:
                return results.multi_face_landmarks[0]
            return None
        except Exception as e:
            logger.error(f"Error detecting face: {str(e)}")
            return None
    
    def get_face_bounding_box(self, landmarks, image_shape):
        """Get face bounding box from landmarks"""
        h, w = image_shape[:2]
        
        x_coords = [int(landmark.x * w) for landmark in landmarks.landmark]
        y_coords = [int(landmark.y * h) for landmark in landmarks.landmark]
        
        x_min = max(0, min(x_coords))
        x_max = min(w, max(x_coords))
        y_min = max(0, min(y_coords))
        y_max = min(h, max(y_coords))
        
        return {
            "x": x_min,
            "y": y_min,
            "width": x_max - x_min,
            "height": y_max - y_min
        }
    
    def get_head_pose(self, landmarks, image_shape):
        """Calculate head pose (rotation, scale, position) for Legend Cut"""
        try:
            h, w = image_shape[:2]
            
            # 2D image points from landmarks
            image_points = np.array([
                [landmarks.landmark[self.NOSE_TIP].x * w, 
                 landmarks.landmark[self.NOSE_TIP].y * h],  # Nose tip
                [landmarks.landmark[self.CHIN].x * w, 
                 landmarks.landmark[self.CHIN].y * h],  # Chin
                [landmarks.landmark[self.LEFT_EYE_LEFT].x * w, 
                 landmarks.landmark[self.LEFT_EYE_LEFT].y * h],  # Left eye left corner
                [landmarks.landmark[self.RIGHT_EYE_RIGHT].x * w, 
                 landmarks.landmark[self.RIGHT_EYE_RIGHT].y * h],  # Right eye right corner
                [landmarks.landmark[self.LEFT_MOUTH].x * w, 
                 landmarks.landmark[self.LEFT_MOUTH].y * h],  # Left mouth corner
                [landmarks.landmark[self.RIGHT_MOUTH].x * w, 
                 landmarks.landmark[self.RIGHT_MOUTH].y * h]  # Right mouth corner
            ], dtype=np.float32)
            
            # 3D model points (generic face model)
            model_points = np.array([
                [0.0, 0.0, 0.0],           # Nose tip
                [0.0, -330.0, -65.0],       # Chin
                [-225.0, 170.0, -135.0],     # Left eye left corner
                [225.0, 170.0, -135.0],      # Right eye right corner
                [-150.0, -150.0, -125.0],    # Left mouth corner
                [150.0, -150.0, -125.0]      # Right mouth corner
            ], dtype=np.float32)
            
            # Camera matrix
            focal_length = w
            center = (w/2, h/2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype=np.float32)
            
            dist_coeffs = np.zeros((4, 1))
            
            # Solve PnP
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if success:
                # Get rotation matrix and euler angles
                rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
                
                # Calculate euler angles
                sy = np.sqrt(rotation_matrix[0,0] ** 2 + rotation_matrix[1,0] ** 2)
                singular = sy < 1e-6
                
                if not singular:
                    x_angle = np.arctan2(rotation_matrix[2,1], rotation_matrix[2,2])
                    y_angle = np.arctan2(-rotation_matrix[2,0], sy)
                    z_angle = np.arctan2(rotation_matrix[1,0], rotation_matrix[0,0])
                else:
                    x_angle = np.arctan2(-rotation_matrix[1,2], rotation_matrix[1,1])
                    y_angle = np.arctan2(-rotation_matrix[2,0], sy)
                    z_angle = 0
                
                return {
                    "success": True,
                    "rotation_vector": rotation_vector,
                    "translation_vector": translation_vector,
                    "rotation_matrix": rotation_matrix,
                    "euler_angles": {
                        "x": float(np.degrees(x_angle)),
                        "y": float(np.degrees(y_angle)),
                        "z": float(np.degrees(z_angle))
                    },
                    "focal_length": focal_length,
                    "center": center
                }
            
            return {"success": False}
            
        except Exception as e:
            logger.error(f"Error calculating head pose: {str(e)}")
            return {"success": False}
    
    def get_forehead_region(self, landmarks, image_shape):
        """Get forehead region coordinates for hair placement"""
        try:
            h, w = image_shape[:2]
            
            # Get key points
            left_temple = landmarks.landmark[234]  # Left temple
            right_temple = landmarks.landmark[454]  # Right temple
            brow_center = landmarks.landmark[8]     # Between eyebrows
            top_forehead = landmarks.landmark[10]   # Top of forehead
            
            # Calculate region
            left_x = int(left_temple.x * w)
            right_x = int(right_temple.x * w)
            
            # Extend upward for forehead
            forehead_height = int(abs(top_forehead.y - brow_center.y) * h * 1.8)
            top_y = max(0, int(top_forehead.y * h) - forehead_height)
            bottom_y = int(brow_center.y * h)
            
            # Ensure valid dimensions
            width = max(10, right_x - left_x)
            height = max(10, bottom_y - top_y)
            
            return {
                "x": left_x,
                "y": top_y,
                "width": width,
                "height": height,
                "center_x": left_x + width // 2,
                "center_y": top_y + height // 2
            }
            
        except Exception as e:
            logger.error(f"Error getting forehead region: {str(e)}")
            return None
    
    def get_hair_region(self, landmarks, image_shape):
        """Get estimated hair region based on facial landmarks"""
        try:
            forehead = self.get_forehead_region(landmarks, image_shape)
            if not forehead:
                return None
            
            # Expand region for hair
            hair_region = {
                "x": forehead["x"] - int(forehead["width"] * 0.4),
                "y": forehead["y"] - int(forehead["height"] * 0.6),
                "width": forehead["width"] + int(forehead["width"] * 0.8),
                "height": forehead["height"] + int(forehead["height"] * 1.2)
            }
            
            # Ensure coordinates are within image
            h, w = image_shape[:2]
            hair_region["x"] = max(0, hair_region["x"])
            hair_region["y"] = max(0, hair_region["y"])
            hair_region["width"] = min(w - hair_region["x"], hair_region["width"])
            hair_region["height"] = min(h - hair_region["y"], hair_region["height"])
            
            hair_region["center_x"] = hair_region["x"] + hair_region["width"] // 2
            hair_region["center_y"] = hair_region["y"] + hair_region["height"] // 2
            
            return hair_region
            
        except Exception as e:
            logger.error(f"Error getting hair region: {str(e)}")
            return None
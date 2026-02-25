"""
Legend Cut Hair Overlay Module
Handles applying and blending hairstyles onto detected faces
"""
import scipy
import cv2
import numpy as np
import os
import logging
from app.utils.face_utils import FaceDetector

logger = logging.getLogger(__name__)

# Try to import scipy for advanced blending, but don't fail if not available
try:
    from scipy.ndimage import gaussian_filter
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("SciPy not available. Using basic blending.")

class HairOverlay:
    """Advanced hair overlay system for Legend Cut"""
    
    def __init__(self):
        """Initialize hair overlay system"""
        self.face_detector = FaceDetector()
        self.haircut_cache = {}
        self.session_settings = {}
        logger.info("Legend Cut Hair Overlay initialized")
        
    def load_haircut(self, haircut_path, gender):
        """Load and preprocess haircut image with caching"""
        try:
            # Check if file exists
            if not os.path.exists(haircut_path):
                logger.error(f"Haircut not found: {haircut_path}")
                return None
            
            # Check cache
            cache_key = f"{gender}_{os.path.basename(haircut_path)}"
            if cache_key in self.haircut_cache:
                cached = self.haircut_cache[cache_key]
                if cached is not None:
                    logger.debug(f"Loading {cache_key} from cache")
                    return cached.copy()
            
            # Load image with alpha channel
            haircut = cv2.imread(haircut_path, cv2.IMREAD_UNCHANGED)
            
            if haircut is None:
                logger.error(f"Failed to load image: {haircut_path}")
                return None
            
            # Ensure RGBA format
            if len(haircut.shape) == 2:
                # Grayscale image
                haircut = cv2.cvtColor(haircut, cv2.COLOR_GRAY2BGRA)
            elif haircut.shape[2] == 3:
                # Add alpha channel
                alpha = np.ones((haircut.shape[0], haircut.shape[1]), dtype=np.uint8) * 255
                haircut = np.dstack([haircut, alpha])
            
            # Preprocess for better blending
            haircut = self.preprocess_haircut(haircut)
            
            # Cache the result
            self.haircut_cache[cache_key] = haircut.copy()
            logger.info(f"Loaded and cached haircut: {cache_key}")
            
            return haircut
            
        except Exception as e:
            logger.error(f"Error loading haircut: {str(e)}")
            return None
    
    def preprocess_haircut(self, haircut):
        """Preprocess haircut for better blending"""
        try:
            # Apply slight blur to alpha channel for smoother edges
            if haircut.shape[2] == 4:
                alpha = haircut[:, :, 3]
                alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
                haircut[:, :, 3] = alpha
            
            return haircut
        except Exception as e:
            logger.error(f"Error preprocessing haircut: {str(e)}")
            return haircut
    
    def apply_haircut(self, frame, haircut_name, gender, session_id=None):
        """Apply Legend Cut hairstyle to frame"""
        try:
            face_detected = False
            
            # Determine haircut path
            haircut_path = f"app/static/haircuts/{gender}/{haircut_name}"
            if not os.path.exists(haircut_path):
                # Try custom folder
                haircut_path = f"app/static/haircuts/custom/{haircut_name}"
            
            # If still not found, try alternative paths
            if not os.path.exists(haircut_path):
                # Try with just the filename in custom folder
                alt_path = f"app/static/haircuts/custom/{os.path.basename(haircut_name)}"
                if os.path.exists(alt_path):
                    haircut_path = alt_path
                else:
                    logger.warning(f"Haircut not found: {haircut_name}")
                    return frame, face_detected
            
            haircut = self.load_haircut(haircut_path, gender)
            
            if haircut is None:
                logger.warning(f"Failed to load haircut: {haircut_name}")
                return frame, face_detected
            
            # Detect face
            landmarks = self.face_detector.detect_face(frame)
            
            if landmarks is None:
                logger.debug("No face detected in frame")
                return frame, face_detected
            
            face_detected = True
            
            # Get head pose and hair region
            head_pose = self.face_detector.get_head_pose(landmarks, frame.shape)
            hair_region = self.face_detector.get_hair_region(landmarks, frame.shape)
            
            if hair_region is None:
                logger.warning("Could not determine hair region")
                return frame, face_detected
            
            # Apply session adjustments if available
            adjustments = {}
            if session_id and session_id in self.session_settings:
                adjustments = self.session_settings[session_id].get("adjustments", {})
            
            # Transform haircut based on head pose and adjustments
            transformed_haircut = self.transform_haircut(
                haircut, 
                head_pose,
                hair_region,
                adjustments
            )
            
            # Overlay on frame
            result = self.overlay_haircut(frame, transformed_haircut, hair_region, adjustments)
            
            return result, face_detected
            
        except Exception as e:
            logger.error(f"Error applying haircut: {str(e)}")
            return frame, False
    
    def transform_haircut(self, haircut, head_pose, hair_region, adjustments=None):
        """Transform haircut based on head pose and user adjustments"""
        try:
            if adjustments is None:
                adjustments = {}
            
            h, w = haircut.shape[:2]
            
            # Calculate base scale from face size
            base_scale_x = hair_region["width"] / w if w > 0 else 1.0
            base_scale_y = hair_region["height"] / h if h > 0 else 1.0
            
            # Use the larger scale to maintain aspect ratio
            base_scale = max(base_scale_x, base_scale_y)
            
            # Apply user size adjustment
            user_scale = adjustments.get("scale", 1.0)
            scale = base_scale * user_scale
            
            # Get rotation from head pose
            rotation_angle = 0
            if head_pose and head_pose.get("success", False):
                # Use yaw angle for rotation, but limit it
                yaw = head_pose.get("euler_angles", {}).get("y", 0)
                rotation_angle = np.clip(yaw, -30, 30)
            
            # Apply user rotation adjustment
            rotation_angle += adjustments.get("rotation", 0)
            
            # Resize haircut
            new_width = max(10, int(w * scale))
            new_height = max(10, int(h * scale))
            
            resized = cv2.resize(haircut, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Apply rotation if needed
            if abs(rotation_angle) > 1:
                center = (new_width // 2, new_height // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
                
                # Calculate new image dimensions after rotation
                cos = abs(rotation_matrix[0, 0])
                sin = abs(rotation_matrix[0, 1])
                new_w = int((new_height * sin) + (new_width * cos))
                new_h = int((new_height * cos) + (new_width * sin))
                
                # Adjust rotation matrix to take into account translation
                rotation_matrix[0, 2] += (new_w / 2) - center[0]
                rotation_matrix[1, 2] += (new_h / 2) - center[1]
                
                rotated = cv2.warpAffine(
                    resized, 
                    rotation_matrix, 
                    (new_w, new_h),
                    flags=cv2.INTER_LANCZOS4,
                    borderMode=cv2.BORDER_CONSTANT,
                    borderValue=(0, 0, 0, 0)
                )
                return rotated
            
            return resized
            
        except Exception as e:
            logger.error(f"Error transforming haircut: {str(e)}")
            return haircut
    
    def overlay_haircut(self, frame, haircut, hair_region, adjustments=None):
        """Overlay Legend Cut hairstyle onto frame with advanced blending"""
        try:
            if adjustments is None:
                adjustments = {}
            
            result = frame.copy()
            
            # Get region coordinates
            base_x = hair_region["x"]
            base_y = hair_region["y"]
            
            # Apply user position adjustments
            x_offset = adjustments.get("x", 0)
            y_offset = adjustments.get("y", 0)
            
            x = base_x + x_offset
            y = base_y + y_offset
            
            h, w = haircut.shape[:2]
            frame_h, frame_w = frame.shape[:2]
            
            # Calculate overlay boundaries
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(frame_w, x + w)
            y2 = min(frame_h, y + h)
            
            # Calculate haircut slice
            hx1 = max(0, -x)
            hy1 = max(0, -y)
            hx2 = min(w, frame_w - x)
            hy2 = min(h, frame_h - y)
            
            if hx2 > hx1 and hy2 > hy1:
                # Extract haircut slice
                haircut_slice = haircut[hy1:hy2, hx1:hx2]
                
                if haircut_slice.shape[2] == 4:
                    # Get RGB and alpha channels
                    rgb = haircut_slice[:, :, :3].astype(np.float32)
                    alpha = haircut_slice[:, :, 3].astype(np.float32) / 255.0
                    
                    # Apply edge feathering if scipy is available
                    from scipy.ndimage import gaussian_filter
                    if SCIPY_AVAILABLE:
                        alpha = gaussian_filter(alpha, sigma=1)
                    
                    # Expand alpha to 3 channels
                    alpha_3ch = np.stack([alpha, alpha, alpha], axis=2)
                    
                    # Get region of interest from frame
                    roi = result[y1:y2, x1:x2].astype(np.float32)
                    
                    # Alpha blend
                    blended = (rgb * alpha_3ch + roi * (1 - alpha_3ch)).astype(np.uint8)
                    
                    # Apply blended result
                    result[y1:y2, x1:x2] = blended
                    
                    # Optional: Apply color matching for natural look
                    if roi.mean() > 0:
                        result = self.color_match_hair(result, roi, blended, y1, y2, x1, x2)
            
            return result
            
        except Exception as e:
            logger.error(f"Error overlaying haircut: {str(e)}")
            return frame
    
    def color_match_hair(self, frame, original_roi, blended_roi, y1, y2, x1, x2):
        """Match hair color with face for natural look"""
        try:
            # Simple color adjustment to match lighting
            if original_roi.mean() > 0:
                # Calculate luminance ratio
                original_lum = cv2.cvtColor(original_roi.astype(np.uint8), cv2.COLOR_BGR2GRAY).mean()
                blended_lum = cv2.cvtColor(blended_roi, cv2.COLOR_BGR2GRAY).mean()
                
                if blended_lum > 0:
                    ratio = original_lum / blended_lum
                    # Apply gentle adjustment (70% adjustment, 30% original)
                    adjusted = np.clip(blended_roi * ratio * 0.7 + blended_roi * 0.3, 0, 255).astype(np.uint8)
                    frame[y1:y2, x1:x2] = adjusted
            
            return frame
        except Exception as e:
            logger.error(f"Error in color matching: {str(e)}")
            return frame
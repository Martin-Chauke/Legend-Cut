#!/usr/bin/env python3
"""
Legend Cut - Virtual Haircut Try-On Application
Run this file to start the Legend Cut server
"""

import uvicorn
import os
import sys
from pathlib import Path
import webbrowser
import threading
import time
try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open("http://localhost:8000")
    print("🌐 Legend Cut is now running at http://localhost:8000")
    print("📱 Ready to transform your look!")

def create_sample_placeholders():
    """Create sample placeholder images if no haircuts exist"""
    try:
        if cv2 is None or np is None:
            raise ImportError("OpenCV or NumPy not installed")
        
        # Create sample male haircut placeholders
        male_dir = "app/static/haircuts/male"
        if os.path.exists(male_dir) and len(os.listdir(male_dir)) == 0:
            print("📦 Creating sample male haircut placeholders...")
            sample_male = [
                ("classic_style.png", "Classic Style"),
                ("modern_fade.png", "Modern Fade"),
                ("pompadour.png", "Pompadour"),
                ("undercut.png", "Undercut")
            ]
            
            for filename, label in sample_male:
                img = np.ones((500, 500, 4), dtype=np.uint8) * 255
                # Add gradient background
                for i in range(500):
                    color = int(200 + 55 * (i / 500))
                    img[i, :, :3] = [color, color, color]
                
                # Add text
                cv2.putText(img, f"Male: {label}", (50, 250), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100, 255), 2)
                cv2.putText(img, "Placeholder Image", (50, 300),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150, 255), 1)
                cv2.putText(img, "Replace with actual PNG", (50, 350),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200, 255), 1)
                
                cv2.imwrite(f"{male_dir}/{filename}", img)
                print(f"  Created: {filename}")
        
        # Create sample female haircut placeholders
        female_dir = "app/static/haircuts/female"
        if os.path.exists(female_dir) and len(os.listdir(female_dir)) == 0:
            print("📦 Creating sample female haircut placeholders...")
            sample_female = [
                ("bob_cut.png", "Bob Cut"),
                ("long_layers.png", "Long Layers"),
                ("pixie_cut.png", "Pixie Cut"),
                ("curly_style.png", "Curly Style")
            ]
            
            for filename, label in sample_female:
                img = np.ones((500, 500, 4), dtype=np.uint8) * 255
                # Add gradient background
                for i in range(500):
                    color = int(200 + 55 * (i / 500))
                    img[i, :, :3] = [color, color, color]
                
                # Add text
                cv2.putText(img, f"Female: {label}", (50, 250), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100, 255), 2)
                cv2.putText(img, "Placeholder Image", (50, 300),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150, 255), 1)
                cv2.putText(img, "Replace with actual PNG", (50, 350),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200, 255), 1)
                
                cv2.imwrite(f"{female_dir}/{filename}", img)
                print(f"  Created: {filename}")
                
    except ImportError:
        print("⚠️  OpenCV not installed. Skipping placeholder creation.")
        print("   Install with: pip install opencv-python numpy")
    except Exception as e:
        print(f"⚠️  Error creating placeholders: {e}")

if __name__ == "__main__":
    # Print Legend Cut banner
    print("""
    ╔═══════════════════════════════════════╗
    ║     LEGEND CUT - Virtual Hair Salon   ║
    ║     Where Style Meets Technology      ║
    ╚═══════════════════════════════════════╝
    """)
    
    # Create necessary directories
    os.makedirs("app/static/haircuts/male", exist_ok=True)
    os.makedirs("app/static/haircuts/female", exist_ok=True)
    os.makedirs("app/static/haircuts/custom", exist_ok=True)
    os.makedirs("app/static/css", exist_ok=True)
    os.makedirs("app/static/js", exist_ok=True)
    os.makedirs("app/templates", exist_ok=True)
    os.makedirs("app/utils", exist_ok=True)
    
    # Create sample README for haircuts folder
    haircut_readme = """# Legend Cut - Haircut Images

Place your haircut PNG images in the appropriate folders:

## Male Haircuts
- classic_style.png - Classic men's haircut
- modern_fade.png - Modern fade style
- pompadour.png - Pompadour style
- undercut.png - Undercut style

## Female Haircuts
- bob_cut.png - Bob cut style
- long_layers.png - Long layered cut
- pixie_cut.png - Pixie cut style
- curly_style.png - Curly hairstyle

## Requirements
- Use PNG format with transparent backgrounds
- Recommended size: 500x500 pixels or larger
- Ensure the haircut is centered in the image
"""
    
    with open("app/static/haircuts/README.txt", "w") as f:
        f.write(haircut_readme)
    
    # Create sample placeholder images
    create_sample_placeholders()
    
    # Check if required files exist
    required_files = [
        "app/main.py",
        "app/utils/face_utils.py", 
        "app/utils/hair_overlay.py",
        "app/templates/index.html",
        "app/static/css/style.css",
        "app/static/js/main.js"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("⚠️  Warning: The following files are missing:")
        for f in missing_files:
            print(f"   - {f}")
        print("\nPlease ensure all files are in place before running.")
    
    # Start browser thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    print("🚀 Starting Legend Cut server...")
    print("📝 Press Ctrl+C to stop the server\n")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Legend Cut server stopped. Goodbye!")
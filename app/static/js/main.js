/**
 * Legend Cut - Main JavaScript
 * Handles all frontend interactions and API calls
 */

// Global variables
let currentGender = 'male';
let selectedHaircut = null;
let selectedHaircutName = '';
let sessionId = generateSessionId();
let videoStream = null;
let processingEnabled = false;
let animationFrame = null;
let toast = null;
let bootstrap = window.bootstrap; // Get Bootstrap from window

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Legend Cut initialized');
    loadHaircuts(currentGender);
    initializeToast();
    checkCameraSupport();
    
    // Initialize Bootstrap components
    initializeBootstrapComponents();
});

// Initialize Bootstrap components
function initializeBootstrapComponents() {
    // Initialize all toasts
    try {
        var toastElList = [].slice.call(document.querySelectorAll('.toast'));
        var toastList = toastElList.map(function(toastEl) {
            return new bootstrap.Toast(toastEl, { autohide: true, delay: 3000 });
        });
    } catch (e) {
        console.warn('Bootstrap toast initialization warning:', e);
    }
}

// Initialize Bootstrap toast
function initializeToast() {
    try {
        const toastEl = document.getElementById('notificationToast');
        if (toastEl && bootstrap) {
            toast = new bootstrap.Toast(toastEl, { delay: 3000 });
        } else {
            console.warn('Toast element or Bootstrap not available');
        }
    } catch (e) {
        console.warn('Toast initialization error:', e);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    console.log(`Notification [${type}]: ${message}`);
    
    const toastEl = document.getElementById('notificationToast');
    const toastBody = document.getElementById('toastMessage');
    
    if (!toastEl || !toastBody) {
        // Fallback alert if toast not available
        alert(message);
        return;
    }
    
    // Remove existing classes
    toastEl.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info', 'text-white');
    
    // Change color based on type
    if (type === 'success') {
        toastEl.classList.add('bg-success', 'text-white');
    } else if (type === 'error') {
        toastEl.classList.add('bg-danger', 'text-white');
    } else if (type === 'warning') {
        toastEl.classList.add('bg-warning');
    } else if (type === 'info') {
        toastEl.classList.add('bg-info', 'text-white');
    }
    
    toastBody.textContent = message;
    
    // Show toast
    if (toast) {
        toast.show();
    } else {
        // Reinitialize toast if needed
        initializeToast();
        if (toast) {
            toast.show();
        }
    }
    
    // Reset classes after 3 seconds
    setTimeout(() => {
        toastEl.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info', 'text-white');
    }, 3000);
}

// Check camera support
function checkCameraSupport() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showNotification('Your browser does not support camera access', 'error');
        const controls = document.querySelector('.camera-controls');
        if (controls) controls.style.display = 'none';
    }
}

// Generate unique session ID
function generateSessionId() {
    return 'legend_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Select gender
function selectGender(gender) {
    currentGender = gender;
    
    // Update button states
    document.getElementById('maleBtn')?.classList.remove('active');
    document.getElementById('femaleBtn')?.classList.remove('active');
    const btn = document.getElementById(gender + 'Btn');
    if (btn) btn.classList.add('active');
    
    // Reload haircuts
    loadHaircuts(gender);
    showNotification(`Switched to ${gender} styles`, 'info');
}

// Load haircuts for selected gender
async function loadHaircuts(gender) {
    const gallery = document.getElementById('haircutGallery');
    if (!gallery) return;
    
    gallery.innerHTML = '<div class="text-center text-muted p-3"><i class="fas fa-spinner fa-spin fa-2x"></i><p>Loading styles...</p></div>';
    
    try {
        const response = await fetch(`/api/haircuts/${gender}`);
        const data = await response.json();
        
        if (data.success) {
            if (data.haircuts && data.haircuts.length > 0) {
                displayHaircuts(data.haircuts);
                showNotification(`Loaded ${data.count} styles`, 'success');
            } else {
                gallery.innerHTML = '<div class="text-center text-muted p-3"><i class="fas fa-image fa-2x mb-2"></i><p>No styles available. Add some haircut images!</p></div>';
            }
        } else {
            gallery.innerHTML = '<div class="text-center text-danger p-3"><i class="fas fa-exclamation-circle fa-2x mb-2"></i><p>Error loading styles</p></div>';
        }
    } catch (error) {
        console.error('Error loading haircuts:', error);
        gallery.innerHTML = '<div class="text-center text-danger p-3"><i class="fas fa-exclamation-triangle fa-2x mb-2"></i><p>Failed to load styles</p></div>';
        showNotification('Error loading haircuts', 'error');
    }
}

// Display haircuts in gallery
function displayHaircuts(haircuts) {
    const gallery = document.getElementById('haircutGallery');
    if (!gallery) return;
    
    gallery.innerHTML = '';
    
    haircuts.forEach(haircut => {
        const imgPath = `/static/haircuts/${currentGender}/${haircut}`;
        const div = document.createElement('div');
        div.className = 'haircut-item';
        
        // Create click handler with closure
        div.addEventListener('click', (function(f, p) {
            return function(e) {
                selectHaircut(f, p, e);
            };
        })(haircut, imgPath));
        
        const displayName = haircut.split('.')[0].replace(/_/g, ' ');
        
        div.innerHTML = `
            <img src="${imgPath}" alt="${haircut}" loading="lazy" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'100\' height=\'100\' viewBox=\'0 0 100 100\'%3E%3Crect width=\'100\' height=\'100\' fill=\'%23f0f0f0\'/%3E%3Ctext x=\'10\' y=\'50\' font-family=\'Arial\' font-size=\'14\' fill=\'%23999\'%3E${displayName}%3C/text%3E%3C/svg%3E'">
            <p>${displayName}</p>
        `;
        gallery.appendChild(div);
    });
}

// Select haircut
function selectHaircut(filename, path, event) {
    selectedHaircut = filename;
    selectedHaircutName = filename.split('.')[0].replace(/_/g, ' ');
    
    // Highlight selected item
    document.querySelectorAll('.haircut-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('selected');
    }
    
    // Show selected style preview
    const preview = document.getElementById('selectedStylePreview');
    if (preview) {
        preview.style.display = 'block';
        const styleName = document.getElementById('selectedStyleName');
        if (styleName) styleName.textContent = selectedHaircutName;
    }
    
    showNotification(`Selected: ${selectedHaircutName}`, 'success');
    
    // Auto-start processing if camera is on
    if (videoStream && !processingEnabled) {
        toggleProcessing();
    }
}

// Upload custom haircut
async function uploadHaircut(input) {
    if (!input.files || !input.files[0]) return;
    
    const file = input.files[0];
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showNotification('Please select an image file', 'error');
        return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('File too large. Maximum 10MB', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoading();
        const response = await fetch('/api/upload-haircut', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Add to gallery
            addCustomHaircutToGallery(data.filename, data.path);
            showNotification('Haircut uploaded successfully!', 'success');
        } else {
            showNotification('Error uploading image: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error uploading:', error);
        showNotification('Error uploading image', 'error');
    } finally {
        hideLoading();
        input.value = ''; // Reset input
    }
}

// Add custom haircut to gallery
function addCustomHaircutToGallery(filename, path) {
    const gallery = document.getElementById('haircutGallery');
    if (!gallery) return;
    
    // Remove empty state if present
    const emptyState = gallery.querySelector('.text-muted');
    if (emptyState) {
        gallery.innerHTML = '';
    }
    
    const div = document.createElement('div');
    div.className = 'haircut-item position-relative';
    
    // Create click handler
    div.addEventListener('click', (function(f, p) {
        return function(e) {
            selectHaircut(f, p, e);
        };
    })(filename, path));
    
    const displayName = filename.split('.')[0].replace(/_/g, ' ');
    
    div.innerHTML = `
        <img src="${path}" alt="${filename}" loading="lazy" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'100\' height=\'100\' viewBox=\'0 0 100 100\'%3E%3Crect width=\'100\' height=\'100\' fill=\'%23f0f0f0\'/%3E%3Ctext x=\'10\' y=\'50\' font-family=\'Arial\' font-size=\'14\' fill=\'%23999\'%3E${displayName}%3C/text%3E%3C/svg%3E'">
        <p>${displayName}</p>
        <span class="badge bg-warning position-absolute top-0 end-0 m-1">Custom</span>
    `;
    gallery.appendChild(div);
}

// Start camera
async function startCamera() {
    try {
        showLoading();
        
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        };
        
        videoStream = await navigator.mediaDevices.getUserMedia(constraints);
        
        const video = document.getElementById('video');
        if (!video) {
            throw new Error('Video element not found');
        }
        
        video.srcObject = videoStream;
        
        // Wait for video to be ready
        await new Promise((resolve) => {
            video.onloadedmetadata = () => {
                video.play().then(resolve);
            };
        });
        
        // Show/hide buttons
        const startBtn = document.querySelector('button[onclick="startCamera()"]');
        const stopBtn = document.getElementById('stopBtn');
        
        if (startBtn) startBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'inline-block';
        
        showNotification('Camera started successfully', 'success');
        
        // Auto-start processing if a style is selected
        if (selectedHaircut && !processingEnabled) {
            toggleProcessing();
        }
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        let errorMessage = 'Could not access camera.';
        
        if (error.name === 'NotAllowedError') {
            errorMessage = 'Camera access denied. Please allow camera access.';
        } else if (error.name === 'NotFoundError') {
            errorMessage = 'No camera found on this device.';
        } else if (error.name === 'NotReadableError') {
            errorMessage = 'Camera is already in use by another application.';
        }
        
        showNotification(errorMessage, 'error');
    } finally {
        hideLoading();
    }
}

// Stop camera
function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => {
            track.stop();
            track.enabled = false;
        });
        videoStream = null;
        
        const video = document.getElementById('video');
        if (video) {
            video.srcObject = null;
        }
        
        // Stop processing
        if (processingEnabled) {
            toggleProcessing();
        }
        
        // Show/hide buttons
        const startBtn = document.querySelector('button[onclick="startCamera()"]');
        const stopBtn = document.getElementById('stopBtn');
        
        if (startBtn) startBtn.style.display = 'inline-block';
        if (stopBtn) stopBtn.style.display = 'none';
        
        // Clear overlay
        const overlay = document.getElementById('overlay');
        if (overlay) overlay.innerHTML = '';
        
        showNotification('Camera stopped', 'info');
    }
}

// Toggle processing
function toggleProcessing() {
    if (!selectedHaircut) {
        showNotification('Please select a hairstyle first', 'warning');
        return;
    }
    
    if (!videoStream) {
        showNotification('Please start the camera first', 'warning');
        return;
    }
    
    processingEnabled = !processingEnabled;
    const btn = document.getElementById('processBtn');
    
    if (btn) {
        if (processingEnabled) {
            btn.innerHTML = '<i class="fas fa-stop me-2"></i>Stop Try-On';
            btn.classList.remove('btn-info');
            btn.classList.add('btn-warning');
            processVideo();
            showNotification('Virtual try-on started', 'success');
        } else {
            btn.innerHTML = '<i class="fas fa-play me-2"></i>Start Try-On';
            btn.classList.remove('btn-warning');
            btn.classList.add('btn-info');
            
            if (animationFrame) {
                cancelAnimationFrame(animationFrame);
                animationFrame = null;
            }
            
            // Clear overlay
            const overlay = document.getElementById('overlay');
            if (overlay) overlay.innerHTML = '';
            
            showNotification('Virtual try-on stopped', 'info');
        }
    }
}

// Process video frames
async function processVideo() {
    if (!processingEnabled || !selectedHaircut || !videoStream) return;
    
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    
    if (!video || !canvas) return;
    
    const context = canvas.getContext('2d');
    
    // Check if video is ready
    if (video.videoWidth === 0 || video.videoHeight === 0) {
        animationFrame = requestAnimationFrame(processVideo);
        return;
    }
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Compress frame for faster processing
    const frameData = canvas.toDataURL('image/jpeg', 0.7);
    
    try {
        const response = await fetch('/api/process-frame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                frame: frameData,
                gender: currentGender,
                haircut: selectedHaircut,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const overlay = document.getElementById('overlay');
            if (overlay) {
                overlay.innerHTML = `<img src="${data.frame}" style="width:100%; height:100%; object-fit: cover;" alt="Haircut overlay">`;
            }
            
            // Show/hide face detection status
            const faceStatus = document.getElementById('faceStatus');
            if (faceStatus) {
                if (data.face_detected) {
                    faceStatus.style.display = 'none';
                } else {
                    faceStatus.style.display = 'block';
                    faceStatus.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>No face detected';
                }
            }
        }
    } catch (error) {
        console.error('Error processing frame:', error);
        
        // Show error status
        const faceStatus = document.getElementById('faceStatus');
        if (faceStatus) {
            faceStatus.style.display = 'block';
            faceStatus.className = 'face-status badge bg-danger';
            faceStatus.innerHTML = '<i class="fas fa-exclamation-circle me-1"></i>Processing error';
        }
    }
    
    animationFrame = requestAnimationFrame(processVideo);
}

// Update adjustment value
function updateAdjustment(control, value) {
    // Update display
    const posXValue = document.getElementById('posXValue');
    const posYValue = document.getElementById('posYValue');
    const sizeValue = document.getElementById('sizeValue');
    const rotationValue = document.getElementById('rotationValue');
    
    if (control === 'posX' && posXValue) {
        posXValue.textContent = value;
    } else if (control === 'posY' && posYValue) {
        posYValue.textContent = value;
    } else if (control === 'size' && sizeValue) {
        sizeValue.textContent = parseFloat(value).toFixed(1);
    } else if (control === 'rotation' && rotationValue) {
        rotationValue.textContent = value + '°';
    }
    
    adjustHaircut();
}

// Adjust haircut position/size
async function adjustHaircut() {
    const posX = document.getElementById('posX');
    const posY = document.getElementById('posY');
    const size = document.getElementById('size');
    const rotation = document.getElementById('rotation');
    
    const adjustments = {
        x: posX ? parseInt(posX.value) : 0,
        y: posY ? parseInt(posY.value) : 0,
        scale: size ? parseFloat(size.value) : 1.0,
        rotation: rotation ? parseInt(rotation.value) : 0
    };
    
    try {
        await fetch('/api/adjust-haircut', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                adjustments: adjustments
            })
        });
    } catch (error) {
        console.error('Error adjusting haircut:', error);
    }
}

// Reset all adjustments
function resetAdjustments() {
    const posX = document.getElementById('posX');
    const posY = document.getElementById('posY');
    const size = document.getElementById('size');
    const rotation = document.getElementById('rotation');
    
    if (posX) posX.value = 0;
    if (posY) posY.value = 0;
    if (size) size.value = 1.0;
    if (rotation) rotation.value = 0;
    
    // Update displays
    const posXValue = document.getElementById('posXValue');
    const posYValue = document.getElementById('posYValue');
    const sizeValue = document.getElementById('sizeValue');
    const rotationValue = document.getElementById('rotationValue');
    
    if (posXValue) posXValue.textContent = '0';
    if (posYValue) posYValue.textContent = '0';
    if (sizeValue) sizeValue.textContent = '1.0';
    if (rotationValue) rotationValue.textContent = '0°';
    
    adjustHaircut();
    showNotification('Adjustments reset', 'info');
}

// Capture photo
function capturePhoto() {
    if (!videoStream) {
        showNotification('Please start the camera first', 'warning');
        return;
    }
    
    const video = document.getElementById('video');
    if (!video) return;
    
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Get overlay if exists
    const overlay = document.getElementById('overlay')?.querySelector('img');
    if (overlay) {
        context.drawImage(overlay, 0, 0, canvas.width, canvas.height);
    }
    
    // Convert to data URL
    const imageData = canvas.toDataURL('image/png');
    
    // Add to gallery
    addToCapturedGallery(imageData);
    showNotification('Look captured!', 'success');
}

// Add captured image to gallery
function addToCapturedGallery(imageData) {
    const gallery = document.getElementById('capturedGallery');
    if (!gallery) return;
    
    // Remove empty state if present
    const emptyState = document.getElementById('emptyGallery');
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    const div = document.createElement('div');
    div.className = 'captured-item position-relative d-inline-block m-1';
    
    const timestamp = Date.now();
    
    div.innerHTML = `
        <img src="${imageData}" class="img-thumbnail" style="width: 100px; height: 100px; object-fit: cover;">
        <button class="btn btn-sm btn-danger position-absolute top-0 end-0" onclick="removeCapturedImage(this)" style="transform: translate(50%, -50%);">
            <i class="fas fa-times"></i>
        </button>
        <button class="btn btn-sm btn-primary position-absolute bottom-0 end-0" onclick="downloadImage('${imageData}')" style="transform: translate(50%, 50%);">
            <i class="fas fa-download"></i>
        </button>
    `;
    gallery.appendChild(div);
}

// Remove captured image
function removeCapturedImage(button) {
    const item = button.closest('.captured-item');
    if (item) {
        item.remove();
    }
    
    // Show empty state if no images
    const gallery = document.getElementById('capturedGallery');
    const emptyState = document.getElementById('emptyGallery');
    
    if (gallery && emptyState && gallery.children.length === 0) {
        emptyState.style.display = 'block';
    }
}

// Download image
function downloadImage(imageData) {
    const link = document.createElement('a');
    link.download = `legend-cut-${Date.now()}.png`;
    link.href = imageData;
    link.click();
    showNotification('Image downloaded', 'success');
}

// Reset session
async function resetSession() {
    try {
        await fetch('/api/reset-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        // Generate new session ID
        sessionId = generateSessionId();
        resetAdjustments();
        showNotification('Session reset', 'info');
        
    } catch (error) {
        console.error('Error resetting session:', error);
    }
}

// Show/hide loading
function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'flex';
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'none';
}

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => {
            track.stop();
        });
    }
    if (animationFrame) {
        cancelAnimationFrame(animationFrame);
    }
});

// Handle visibility change
document.addEventListener('visibilitychange', function() {
    if (document.hidden && processingEnabled) {
        // Pause processing when tab is hidden
        if (animationFrame) {
            cancelAnimationFrame(animationFrame);
            animationFrame = null;
        }
    } else if (!document.hidden && processingEnabled && videoStream) {
        // Resume processing when tab becomes visible
        processVideo();
    }
});
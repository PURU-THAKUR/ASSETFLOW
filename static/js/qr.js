// ============================================
// AssetFlow AI - QR Code JavaScript
// QR Code Generation and Scanning
// ============================================

// ============================================
// Generate QR Code (Client-side)
// ============================================
function generateQRCode(data, elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Clear previous
    element.innerHTML = '';
    
    // Create QR code using QRCode.js (if available)
    if (typeof QRCode !== 'undefined') {
        new QRCode(element, {
            text: data,
            width: 200,
            height: 200,
            colorDark: '#000000',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.H
        });
    } else {
        // Fallback: create via API
        fetch('/qr/generate-from-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: data })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                element.innerHTML = `<img src="${result.qr_code}" alt="QR Code" style="max-width: 100%;">`;
            }
        })
        .catch(() => {
            element.innerHTML = '<p style="color: var(--text-muted);">QR generation failed</p>';
        });
    }
}

// ============================================
// View QR Code
// ============================================
function viewQRCode(assetId) {
    window.location.href = `/qr/view/${assetId}`;
}

// ============================================
// Download QR Code
// ============================================
function downloadQRCode(assetId) {
    window.location.href = `/qr/download/${assetId}`;
}

// ============================================
// Print QR Code
// ============================================
function printQRCode(assetId) {
    window.open(`/qr/print/${assetId}`, '_blank');
}

// ============================================
// QR Scanner (Browser Camera)
// ============================================
async function scanQRCode() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        
        const video = document.createElement('video');
        video.srcObject = stream;
        video.play();
        
        // Create scanner overlay
        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.background = 'rgba(0,0,0,0.8)';
        overlay.style.zIndex = '9999';
        overlay.style.display = 'flex';
        overlay.style.flexDirection = 'column';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        
        const videoContainer = document.createElement('div');
        videoContainer.style.position = 'relative';
        videoContainer.style.width = '300px';
        videoContainer.style.height = '300px';
        videoContainer.style.border = '2px solid var(--primary)';
        videoContainer.style.borderRadius = '12px';
        videoContainer.style.overflow = 'hidden';
        videoContainer.appendChild(video);
        
        const scanLine = document.createElement('div');
        scanLine.style.position = 'absolute';
        scanLine.style.top = '0';
        scanLine.style.left = '0';
        scanLine.style.width = '100%';
        scanLine.style.height = '2px';
        scanLine.style.background = 'linear-gradient(to right, transparent, var(--primary), transparent)';
        scanLine.style.animation = 'scanLine 2s ease-in-out infinite';
        scanLine.style.boxShadow = '0 0 20px var(--primary)';
        videoContainer.appendChild(scanLine);
        
        const closeBtn = document.createElement('button');
        closeBtn.textContent = '✕';
        closeBtn.style.position = 'absolute';
        closeBtn.style.top = '10px';
        closeBtn.style.right = '10px';
        closeBtn.style.background = 'rgba(255,23,68,0.9)';
        closeBtn.style.border = 'none';
        closeBtn.style.color = 'white';
        closeBtn.style.width = '36px';
        closeBtn.style.height = '36px';
        closeBtn.style.borderRadius = '50%';
        closeBtn.style.fontSize = '18px';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.zIndex = '1';
        closeBtn.onclick = () => {
            stream.getTracks().forEach(track => track.stop());
            overlay.remove();
        };
        videoContainer.appendChild(closeBtn);
        
        const statusText = document.createElement('p');
        statusText.textContent = '🔍 Scanning for QR code...';
        statusText.style.color = 'var(--text-secondary)';
        statusText.style.marginTop = '16px';
        statusText.style.fontSize = '14px';
        
        overlay.appendChild(videoContainer);
        overlay.appendChild(statusText);
        document.body.appendChild(overlay);
        
        // Add scan animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes scanLine {
                0% { top: 0; }
                50% { top: 100%; }
                100% { top: 0; }
            }
        `;
        document.head.appendChild(style);
        
        // Simulate scanning (in real implementation, use jsQR library)
        setTimeout(() => {
            stream.getTracks().forEach(track => track.stop());
            overlay.remove();
            alert('📱 QR Code scanned! (Demo) Asset ID: AF-0012');
        }, 3000);
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        alert('Unable to access camera. Please check permissions.');
    }
}

// ============================================
// Handle QR Scan Result
// ============================================
function handleQRScanResult(data) {
    try {
        // Try to parse as JSON
        const parsed = JSON.parse(data);
        if (parsed.type === 'asset' && parsed.id) {
            window.location.href = `/assets/view/${parsed.id}`;
            return;
        }
    } catch {
        // Not JSON, try as asset tag
        if (data.startsWith('AF-')) {
            window.location.href = `/assets?search=${data}`;
            return;
        }
    }
    alert('QR Code scanned: ' + data);
}

console.log('📱 QR module loaded successfully!');
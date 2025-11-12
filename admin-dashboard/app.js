const API_BASE = 'http://localhost:8000/api';

// Add new parking lot
document.getElementById('addLotForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const lotData = {
        name: document.getElementById('name').value,
        address: document.getElementById('address').value,
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value),
        total_spaces: parseInt(document.getElementById('totalSpaces').value)
    };

    try {
        const response = await fetch(`${API_BASE}/parking/lots`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(lotData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Upload video if provided
            const videoFile = document.getElementById('videoFile').files[0];
            if (videoFile) {
                await uploadVideo(result.lot_id, videoFile);
            }
            
            alert('Parking lot added successfully!');
            loadParkingLots();
            e.target.reset();
        } else {
            alert('Error: ' + (result.error || 'Failed to create parking lot'));
        }
    } catch (error) {
        alert('Error adding parking lot: ' + error.message);
        console.error('Error:', error);
    }
});

// Upload video for a parking lot
async function uploadVideo(lotId, file) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE}/parking/lots/${lotId}/upload-video`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Video upload failed');
        }
        
        console.log('Video uploaded successfully:', result.filename);
        return result;
    } catch (error) {
        console.error('Error uploading video:', error);
        alert('Warning: Video upload failed - ' + error.message);
    }
}

// Load existing parking lots
async function loadParkingLots() {
    try {
        const response = await fetch(`${API_BASE}/parking/lots`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load parking lots');
        }
        
        const listDiv = document.getElementById('parkingLotsList');
        
        if (data.parking_lots.length === 0) {
            listDiv.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No parking lots found. Add one above!</p>';
            return;
        }
        
        listDiv.innerHTML = data.parking_lots.map(lot => `
            <div class="lot-item">
                <div class="lot-header">
                    <h3>${lot.name}</h3>
                    <span class="lot-id">${lot.lot_id}</span>
                </div>
                <p class="lot-address">${lot.address}</p>
                <div class="lot-stats">
                    <div class="stat">
                        <span class="stat-label">Available:</span>
                        <span class="stat-value" style="color: ${lot.stats.available_spaces > 0 ? '#28a745' : '#dc3545'}">
                            ${lot.stats.available_spaces}/${lot.stats.total_spaces}
                        </span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Occupancy:</span>
                        <span class="stat-value">
                            ${Math.round((lot.stats.cars_detected / lot.stats.total_spaces) * 100)}%
                        </span>
                    </div>
                </div>
                <div class="lot-actions">
                    <button onclick="analyzeLot('${lot.lot_id}', '${lot.video_filename || 'parking_video.mp4'}')" class="btn-analyze">
                        🔍 Analyze Now
                    </button>
                    <button onclick="showUploadModal('${lot.lot_id}')" class="btn-upload">
                        📹 Upload Video
                    </button>
                </div>
                ${lot.last_updated ? `<p class="last-updated">Last updated: ${new Date(lot.last_updated).toLocaleString()}</p>` : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading parking lots:', error);
        document.getElementById('parkingLotsList').innerHTML = 
            '<p style="color: red; padding: 20px;">Error loading parking lots. Make sure the backend is running on port 8000.</p>';
    }
}

// Analyze parking lot
async function analyzeLot(lotId, videoFilename) {
    try {
        const response = await fetch(`${API_BASE}/parking/analyze-video`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                lot_id: lotId, 
                video_filename: videoFilename || 'parking_video.mp4',
                frame_number: 100
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(
                `Analysis Complete!\n\n` +
                `Cars Detected: ${result.car_count}\n` +
                `Available Spaces: ${result.parking_analysis.available_spaces}\n` +
                `Total Spaces: ${result.parking_analysis.total_spaces}\n` +
                `Occupancy Rate: ${result.parking_analysis.occupancy_rate}%`
            );
            loadParkingLots();
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
    } catch (error) {
        alert('Analysis failed: ' + error.message);
        console.error('Error:', error);
    }
}

// Show upload modal
function showUploadModal(lotId) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Upload Video for Lot ${lotId}</h3>
            <form id="uploadVideoForm">
                <input type="file" id="videoUploadFile" accept="video/*" required>
                <div class="modal-actions">
                    <button type="submit" class="btn-primary">Upload</button>
                    <button type="button" onclick="this.closest('.modal').remove()" class="btn-secondary">Cancel</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('uploadVideoForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const file = document.getElementById('videoUploadFile').files[0];
        
        if (file) {
            try {
                await uploadVideo(lotId, file);
                alert('Video uploaded successfully!');
                modal.remove();
                loadParkingLots();
            } catch (error) {
                alert('Upload failed: ' + error.message);
            }
        }
    });
}

// Load lots on page load
loadParkingLots();

// Auto-refresh every 30 seconds
setInterval(loadParkingLots, 30000);
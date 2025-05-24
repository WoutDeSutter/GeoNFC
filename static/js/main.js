// API base URL
const API_URL = 'https://geonfc-back.onrender.com';

// Map initialization
let map;
let markers = [];

// Initialize map when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize map if map element exists
    if (document.getElementById('map')) {
        map = L.map('map').setView([50.8503, 4.3517], 8);  // Center on Belgium

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Fetch caches
        fetchCaches();
    }

    // Initialize logs page if logs page is loaded
    if (document.getElementById('logsList')) {
        fetchAllLogs();
        document.getElementById('searchInput').addEventListener('input', handleSearch);
    }

    // Initialize add log page if add log page is loaded
    if (document.getElementById('addLogForm')) {
        initializeAddLogPage();
    }
});

// Map Functions
async function fetchCaches() {
    try {
        const response = await fetch(`${API_URL}/api/caches`);
        if (!response.ok) {
            throw new Error('Netwerk response was niet ok');
        }
        const caches = await response.json();
        
        // Remove existing markers
        markers.forEach(marker => marker.remove());
        markers = [];
        
        // Add markers for each cache
        for (const cache of caches) {
            const logsResponse = await fetch(`${API_URL}/api/logs/${cache.tag_id}`);
            const logs = await logsResponse.json();
            const latestLog = logs[0];

            const marker = L.marker([cache.latitude, cache.longitude])
                .bindPopup(`
                    <div class="cache-popup">
                        <h3>Cache ${cache.tag_id}</h3>
                        <p>Laatste update: ${new Date(cache.last_updated).toLocaleString()}</p>
                        ${latestLog ? `
                            <div class="latest-log">
                                <h4>Laatste Log:</h4>
                                <p><strong>${latestLog.username}</strong> - ${new Date(latestLog.timestamp).toLocaleString()}</p>
                                <p>${latestLog.message}</p>
                            </div>
                        ` : '<p>Nog geen logs voor deze cache</p>'}
                        <button onclick="showLogs('${cache.tag_id}')">Bekijk Alle Logs</button>
                    </div>
                `)
                .addTo(map);
            markers.push(marker);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Er is een fout opgetreden bij het ophalen van de caches');
    }
}

async function showLogs(tagId) {
    try {
        const response = await fetch(`${API_URL}/api/logs/${tagId}`);
        if (!response.ok) {
            throw new Error('Netwerk response was niet ok');
        }
        const logs = await response.json();
        
        const logsList = logs.map(log => `
            <div class="log-entry">
                <strong>${log.username}</strong> - ${new Date(log.timestamp).toLocaleString()}
                <p>${log.message}</p>
                <small>Locatie: ${log.latitude.toFixed(4)}, ${log.longitude.toFixed(4)}</small>
            </div>
        `).join('');
        
        const logsHtml = `
            <div class="logs-container">
                <h3>Logs voor Cache ${tagId}</h3>
                <div class="logs-list">
                    ${logsList}
                </div>
            </div>
        `;
        
        L.popup()
            .setLatLng([logs[0]?.latitude || 0, logs[0]?.longitude || 0])
            .setContent(logsHtml)
            .openOn(map);
    } catch (error) {
        console.error('Error:', error);
        alert('Er is een fout opgetreden bij het ophalen van de logs');
    }
}

// Log Functions
async function fetchAllLogs() {
    try {
        const response = await fetch(`${API_URL}/api/all-logs`);
        if (!response.ok) {
            throw new Error('Netwerk response was niet ok');
        }
        const logs = await response.json();
        displayLogs(logs);
    } catch (error) {
        console.error('Error:', error);
        alert('Er is een fout opgetreden bij het ophalen van de logs');
    }
}

function displayLogs(logs) {
    const logsList = document.getElementById('logsList');
    logsList.innerHTML = logs.map(log => `
        <div class="log-card">
            <div class="log-header">
                <h3>Cache ${log.tag_id}</h3>
                <span class="log-date">${new Date(log.timestamp).toLocaleString()}</span>
            </div>
            <div class="log-content">
                <p class="log-user"><strong>${log.username}</strong></p>
                <p class="log-message">${log.message}</p>
                <p class="log-location">Locatie: ${log.latitude.toFixed(4)}, ${log.longitude.toFixed(4)}</p>
            </div>
        </div>
    `).join('');
}

function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const logCards = document.querySelectorAll('.log-card');
    
    logCards.forEach(card => {
        const text = card.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Add Log Functions
function initializeAddLogPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const tagId = urlParams.get('tag');
    
    if (!tagId) {
        alert('Geen tag ID gevonden in de URL!');
        window.location.href = 'index.html';
        return;
    }
    
    document.getElementById('tagId').value = tagId;

    fetch(`${API_URL}/api/tag/${tagId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Tag niet gevonden');
            }
            return response.json();
        })
        .then(tag => {
            const formContainer = document.querySelector('.form-container');
            const tagInfo = document.createElement('div');
            tagInfo.className = 'tag-info';
            tagInfo.innerHTML = `
                <h3>Cache ${tag.tag_id}</h3>
                <p>Laatste locatie: ${tag.latitude.toFixed(4)}, ${tag.longitude.toFixed(4)}</p>
                <p>Laatste update: ${new Date(tag.last_updated).toLocaleString()}</p>
            `;
            formContainer.insertBefore(tagInfo, formContainer.firstChild);
        })
        .catch(error => {
            alert('Deze cache bestaat niet!');
            window.location.href = 'index.html';
        });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                document.getElementById('latitude').value = position.coords.latitude;
                document.getElementById('longitude').value = position.coords.longitude;
            },
            function(error) {
                console.error('Error getting location:', error);
                alert('Kon locatie niet ophalen. Vul handmatig in.');
            }
        );
    }

    document.getElementById('addLogForm').addEventListener('submit', handleLogSubmit);
}

async function handleLogSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = {
        tag_id: formData.get('tagId'),
        username: formData.get('username'),
        message: formData.get('message'),
        latitude: parseFloat(formData.get('latitude')),
        longitude: parseFloat(formData.get('longitude'))
    };

    try {
        const response = await fetch(`${API_URL}/api/log`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Netwerk response was niet ok');
        }
        
        alert('Log succesvol toegevoegd!');
        window.location.href = 'index.html';
    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'Er is een fout opgetreden bij het toevoegen van de log');
    }
} 
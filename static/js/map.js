// Initialize map
const map = L.map('map', {
    minZoom: 2,
    maxZoom: 19,
    noWrap: true
}).setView([50.8503, 3.7167], 9);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors',
    noWrap: true
}).addTo(map);

// Store markers
const markers = {};

// API base URL
const API_URL = 'http://localhost:5000';

// Test data voor Gent en Gavere
const testCaches = [
    {
        tag_id: 'TEST001',
        latitude: 51.0543,
        longitude: 3.7174,
        last_updated: new Date().toISOString()
    },
    {
        tag_id: 'TEST002',
        latitude: 50.9297,
        longitude: 3.6619,
        last_updated: new Date().toISOString()
    }
];

// Function to update cache locations
async function updateCacheLocations() {
    try {
        // In productie zou je de API aanroepen:
        // const response = await fetch(`${API_URL}/api/caches`);
        // const caches = await response.json();
        
        // Voor nu gebruiken we test data
        const caches = testCaches;
        
        // Clear existing markers
        Object.values(markers).forEach(marker => marker.remove());
        
        // Add new markers
        caches.forEach(cache => {
            const marker = L.marker([cache.latitude, cache.longitude])
                .bindPopup(`Cache ID: ${cache.tag_id}<br>Last updated: ${new Date(cache.last_updated).toLocaleString()}`);
            marker.addTo(map);
            markers[cache.tag_id] = marker;
        });
    } catch (error) {
        console.error('Error fetching cache locations:', error);
    }
}

// Centreer de map als deze volledig is uitgezoomd
map.on('zoomend', function() {
    if (map.getZoom() === map.getMinZoom()) {
        map.setView([50.8503, 3.7167], map.getMinZoom());
    }
});

// Update cache locations every 30 seconds
updateCacheLocations();
setInterval(updateCacheLocations, 30000);

// Handle form submission
document.getElementById('cacheLogForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        tag_id: document.getElementById('tagId').value,
        username: document.getElementById('username').value,
        message: document.getElementById('message').value,
        latitude: document.getElementById('latitude').value,
        longitude: document.getElementById('longitude').value
    };
    
    try {
        const response = await fetch(`${API_URL}/api/log`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            alert('Log succesvol toegevoegd!');
            document.getElementById('logForm').classList.add('hidden');
            updateCacheLocations();
        } else {
            alert('Er is een fout opgetreden bij het toevoegen van de log.');
        }
    } catch (error) {
        console.error('Error submitting log:', error);
        alert('Er is een fout opgetreden bij het toevoegen van de log.');
    }
}); 
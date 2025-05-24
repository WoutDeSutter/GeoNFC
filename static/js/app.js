// Initialiseer de kaart
let map;
let markers = [];

// Wacht tot de pagina geladen is
document.addEventListener('DOMContentLoaded', function() {
    // Initialiseer de kaart
    map = L.map('map').setView([50.8503, 4.3517], 8);  // Centrum op België

    // Voeg de OpenStreetMap tiles toe
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Haal de caches op
    fetchCaches();
});

// Toon het log formulier
function showLogForm(tagId) {
    const form = document.getElementById('logForm');
    document.getElementById('tagId').value = tagId;
    form.classList.remove('hidden');
}

// Verberg het log formulier
function hideLogForm() {
    const form = document.getElementById('logForm');
    form.classList.add('hidden');
    document.getElementById('addLogForm').reset();
}

// Verwerk het formulier
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
        await addLog(data.tag_id, data.username, data.message, data.latitude, data.longitude);
        hideLogForm();
    } catch (error) {
        console.error('Error:', error);
        alert('Er is een fout opgetreden bij het toevoegen van de log');
    }
}

// Haal alle caches op van de API
async function fetchCaches() {
    try {
        const response = await fetch('http://localhost:5000/api/caches');
        if (!response.ok) {
            throw new Error('Netwerk response was niet ok');
        }
        const caches = await response.json();
        
        // Verwijder bestaande markers
        markers.forEach(marker => marker.remove());
        markers = [];
        
        // Voeg markers toe voor elke cache
        for (const cache of caches) {
            // Haal de laatste log op voor deze cache
            const logsResponse = await fetch(`http://localhost:5000/api/logs/${cache.tag_id}`);
            const logs = await logsResponse.json();
            const latestLog = logs[0]; // De eerste log is de meest recente (gesorteerd op timestamp DESC)

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

// Toon logs voor een specifieke cache
async function showLogs(tagId) {
    try {
        const response = await fetch(`http://localhost:5000/api/logs/${tagId}`);
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
        
        // Toon logs in een popup
        L.popup()
            .setLatLng([logs[0]?.latitude || 0, logs[0]?.longitude || 0])
            .setContent(logsHtml)
            .openOn(map);
    } catch (error) {
        console.error('Error:', error);
        alert('Er is een fout opgetreden bij het ophalen van de logs');
    }
}

// Voeg een nieuwe log toe
async function addLog(tagId, username, message, latitude, longitude) {
    try {
        const response = await fetch('http://localhost:5000/api/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tag_id: tagId,
                username: username,
                message: message,
                latitude: latitude,
                longitude: longitude
            })
        });
        
        if (!response.ok) {
            throw new Error('Netwerk response was niet ok');
        }
        
        // Ververs de caches om de nieuwe locatie te tonen
        await fetchCaches();
        
        // Toon de logs voor deze cache
        await showLogs(tagId);
    } catch (error) {
        console.error('Error:', error);
        alert('Er is een fout opgetreden bij het toevoegen van de log');
    }
} 
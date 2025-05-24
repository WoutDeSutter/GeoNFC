// Wacht tot de pagina geladen is
document.addEventListener('DOMContentLoaded', function() {
    // Haal alle logs op
    fetchAllLogs();

    // Voeg event listener toe voor de zoekbalk
    document.getElementById('searchInput').addEventListener('input', handleSearch);
});

// Haal alle logs op van de API
async function fetchAllLogs() {
    try {
        const response = await fetch('http://localhost:5000/api/all-logs');
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

// Toon de logs in de lijst
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

// Verwerk de zoekopdracht
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
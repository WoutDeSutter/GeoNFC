document.addEventListener('DOMContentLoaded', function() {
    // Haal de tag ID uit de URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const tagId = urlParams.get('tag');
    
    if (!tagId) {
        alert('Geen tag ID gevonden in de URL!');
        window.location.href = 'index.html';
        return;
    }
    
    // Vul de tag ID in het formulier
    document.getElementById('tagId').value = tagId;

    // Haal tag informatie op
    fetch(`http://localhost:5000/api/tag/${tagId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Tag niet gevonden');
            }
            return response.json();
        })
        .then(tag => {
            // Toon tag informatie
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

    // Haal de huidige locatie op
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

    // Verwerk het formulier
    document.getElementById('addLogForm').addEventListener('submit', async function(event) {
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
            const response = await fetch('http://localhost:5000/api/log', {
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
            window.location.href = 'index.html'; // Terug naar de kaart
        } catch (error) {
            console.error('Error:', error);
            alert(error.message || 'Er is een fout opgetreden bij het toevoegen van de log');
        }
    });
}); 
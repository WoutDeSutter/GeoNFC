// Check if Web NFC is supported
if ('NDEFReader' in window) {
    const scanButton = document.getElementById('scanButton');
    const logForm = document.getElementById('logForm');
    
    scanButton.addEventListener('click', async () => {
        try {
            const ndef = new NDEFReader();
            await ndef.scan();
            
            ndef.addEventListener('reading', async ({ message }) => {
                const decoder = new TextDecoder();
                const tagId = decoder.decode(message.records[0].data);
                
                // Get current location
                if ('geolocation' in navigator) {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            // Show log form
                            document.getElementById('tagId').value = tagId;
                            document.getElementById('latitude').value = position.coords.latitude;
                            document.getElementById('longitude').value = position.coords.longitude;
                            logForm.classList.remove('hidden');
                        },
                        (error) => {
                            alert('Kon je locatie niet ophalen. Zorg ervoor dat locatie services zijn ingeschakeld.');
                            console.error('Error getting location:', error);
                        }
                    );
                } else {
                    alert('Je browser ondersteunt geen geolocatie.');
                }
            });
            
            alert('Scan een RFID tag door deze tegen je telefoon te houden.');
        } catch (error) {
            console.error('Error scanning NFC:', error);
            alert('Er is een fout opgetreden bij het scannen van de NFC tag.');
        }
    });
} else {
    document.getElementById('scanButton').disabled = true;
    alert('Je browser ondersteunt geen Web NFC. Gebruik een moderne Android telefoon met Chrome.');
} 
document.addEventListener('DOMContentLoaded', function() {
    const languagesEndpoint = `/${site_id}/languages`;
    const qrEndpoint = `/generate_qr?site_id=${site_id}`;
    const speakerQrEndpoint = `/${site_id}/generate_qr_speaker`;

    fetch(languagesEndpoint)
        .then(response => response.json())
        .then(languages => {
            const container = document.getElementById('qr-codes-container');
            languages.forEach(language => {
                const img = document.createElement('img');
                hlink = `/${site_id}?language=${encodeURIComponent(language.code)}`;
                img.src = `${qrEndpoint}&language=${encodeURIComponent(language.code)}`;
                img.alt = `QR Code for ${language.name}`;
                img.classList.add('qr-code'); 
                // add a hyperlink to the image
                const a = document.createElement('a');
                a.href = hlink;
                a.appendChild(img);
                container.appendChild(a);
            });
            // generate and display the QR for the Speaker
            const img = document.createElement('img');
            hlink = `/${site_id}/speaker`;
            img.src = `${speakerQrEndpoint}`;
            img.alt = `QR Code for Speaker`;
            img.classList.add('qr-code'); 
            // add a hyperlink to the image
            const a = document.createElement('a');
            a.href = hlink;
            a.appendChild(img);
            container.appendChild(a);
        })
        .catch(error => console.error('Error fetching languages:', error));
});

// wrap the entire code in a DOMContentLoaded event listener to ensure the DOM is fully loaded before running the code
document.addEventListener('DOMContentLoaded', function () {
    const languageDivs = {};

    function getParameterByName(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    function updateLanguagesInQuery() {
        const selectedLanguages = $('#languageSelector').val();
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.delete('language');
        if (selectedLanguages) {
            selectedLanguages.forEach(language => {
                currentUrl.searchParams.append('language', language);
            });
        }
        window.history.pushState({}, '', currentUrl);
    }


    $('#languageSelector').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
        updateLanguagesInQuery();
        const selectedLanguages = $('#languageSelector').val();

        // Clear output container
        const output = document.querySelector('#output');
        output.innerHTML = '';

        // Process selected languages
        for (let i = 0; i < selectedLanguages.length; i += 2) {
            const row = document.createElement('div');
            row.className = 'row';
            output.appendChild(row);

            const language1 = selectedLanguages[i];
            const language2 = selectedLanguages[i + 1];

            createLanguageCard(language1, row);
            if (language2) {
                createLanguageCard(language2, row);
            }
        }
    });

    function createLanguageCard(language, row) {
        const card = document.createElement('div');
        card.className = 'col-sm-6';
        card.innerHTML = `
    <div class="card">
      <div class="card-body text-wrap">
        <h5 class="card-title">${language.toUpperCase()} Translation</h5>
        <div class="card-text translation-container text-wrap " id="${language}-container"></div> <!-- Changed from <p> to <div> -->
      </div>
    </div>
  `;
        row.appendChild(card);
    }

    (async function () {
        let res = await fetch(`/${site_id}/negotiate`)
        let data = await res.json();
        let ws = new WebSocket(data.url, 'json.webpubsub.azure.v1');
        ws.onopen = () => {
            console.log('connected');
            ws.send(JSON.stringify({
                type: 'joinGroup',
                group: 'stream',
                data: 'data'
            }));
        };

        let output = document.querySelector('#output');
        ws.onmessage = event => {
            const parsedData = JSON.parse(event.data);
            console.log(parsedData);
            if (parsedData.type !== 'message') {
                return;
            }

            const data = JSON.parse(parsedData.data);

            // Extract language and translation from parsed data
            const language = data.language;
            const translation = data.translation;
            console.log(translation);

            // Get language from query string
            const queryStringLanguage = getParameterByName('language');

            // Check if div for this language already exists
            if (!languageDivs[language]) {
                // Create a new div for this language
                const container = document.getElementById(`${language}-container`);
                if (container) {
                    container.innerHTML = translation;
                } else {
                    console.log(`Container for ${language} not found.`);
                }
                languageDivs[language] = true;
            } else {
                // Append translation to the appropriate div
                const selectedLanguages = $('#languageSelector').val();
                // always include the hidden english container
                selectedLanguages.push('en');
                if (!queryStringLanguage || selectedLanguages.includes(language)) {
                    const container = document.getElementById(`${language}-container`);
                    if (container) {
                        container.innerHTML += `<br>${translation}`;
                        container.scrollTop = container.scrollHeight; // Scroll to the bottom
                    }
                }
            }
        };

        // Set selected languages from query string
        const urlParams = new URLSearchParams(window.location.search);
        const languages = urlParams.getAll('language');
        const queryStringLanguage = languages.length ? languages : null;
        if (queryStringLanguage) {
            $('#languageSelector').selectpicker('val', queryStringLanguage);
        }

        // Trigger language selection change after setting selected languages
        $('#languageSelector').trigger('changed.bs.select');
    })();

    // Check if 'testmode' query parameter is present and show the source-container visible if it is
    const urlParams = new URLSearchParams(window.location.search);
    const testMode = urlParams.get('testmode');

    if (testMode === 'true') {
        // Make the source-container visible
        document.getElementById('source-container').style.display = 'block';
        document.getElementById('en-container').textContent = "Good morning, team! Gather 'round, gather 'round. Let's get ready to tackle another day of package magic! Just like a well-oiled machine, we need all our parts working together smoothly to keep this place running like a Swiss watch. So, let's dive into our pre-shift briefing./n/nFirst off, a quick note from our friends in HR. Remember to update your contact information in the system if you haven't already. It's as important as checking the oil in your car – it keeps everything running smoothly and ensures we can reach you if needed. So, if you’ve moved, changed your number, or got a new email address, make sure it’s updated. /n/nNow, on to safety – our number one priority. Think of safety like the GPS in your car. It might seem like it's just there in the background, but without it, you’d be lost. Here are today’s safety highlights:/nStay Alert. The automated sorting equipment is our best friend and sometimes our biggest challenge. Always stay aware of your surroundings. Remember, those machines don’t have eyes, so we have to be theirs./nProper Lifting Techniques. Bend those knees and keep your back straight. You're not Hercules – even if you feel like it after that third cup of coffee!/nEmergency Exits. Know where they are and make sure they're never blocked. It's like knowing the escape route in a video game – always be prepared for the unexpected./n/nAlright, on to our goals for the shift. Today, we’re aiming to sort and process 10,000 packages. That’s a lot, but I know we can do it. Let’s break it down:/nSpeed. Keep up the pace but don’t sacrifice accuracy. Like a NASCAR pit crew, every second counts, but so does every detail./nQuality. Make sure every package is handled with care. Remember, these packages could be someone’s birthday gift, a long-awaited order, or even a precious heirloom./nTeamwork. Help each other out. If you see someone struggling, lend a hand. We’re not just a team, we’re a family – and families support each other./n/nFinally, a little something to look forward to. Mark your calendars for next Friday,  we’re having a team-building event! It’s going to be a warehouse Olympics, complete with a package relay race and a forklift obstacle course. It’s a chance to blow off some steam and bond with your teammates. Plus, there will be snacks, and who doesn’t love snacks?/n/nLet’s make today a great day, stay safe, and show those packages who’s boss. Remember, in this warehouse, we don’t just sort packages, we deliver excellence. Alright, let’s get to work and make some magic happen!/n/nReady? Break!";
    }

});

function increaseTextSize() {
    const translationContainers = document.querySelectorAll('.translation-container');
    translationContainers.forEach(container => {
        const currentFontSize = parseFloat(window.getComputedStyle(container).fontSize);
        container.style.fontSize = (currentFontSize + 1) + 'px';
    });
}

function decreaseTextSize() {
    const translationContainers = document.querySelectorAll('.translation-container');
    translationContainers.forEach(container => {
        const currentFontSize = parseFloat(window.getComputedStyle(container).fontSize);
        container.style.fontSize = (currentFontSize - 1) + 'px';
    });
}
function clearTranslations() {
    const translationContainers = document.querySelectorAll('.translation-container');
    translationContainers.forEach(container => {
        container.innerHTML = ""
    });
}
async function summarizeTranslations() {
    const sourceText = document.getElementById('en-container').innerHTML.toString()
    const selectedLanguages = $('#languageSelector').val();
    for (const language of selectedLanguages) {
        //const container = document.getElementById(`${language}-container`);
        // Send the POST request to the /summarize endpoint
        const response = await fetch('/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language: language, text: sourceText })
        });
        // Process the response
        if (response.ok) {
            const result = await response.json();
            console.log(result);
            var full_text = result.summary + "<ul>";
            result.points.forEach(point => {
                full_text += "<li>" + point + "</li>";
            });
            full_text += "</ul>";
            console.log(full_text);
            document.getElementById(`${language}-container`).innerHTML = full_text;
        } else {
            console.error('Error summarizing text:', response.statusText);
        }
    }
}



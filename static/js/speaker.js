// wrap the entire code in a DOMContentLoaded event listener to ensure the DOM is fully loaded before running the code
document.addEventListener('DOMContentLoaded', function () {
    // get the defualt language of the user
    const userLang = navigator.language || navigator.userLanguage;


    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const clearBtn = document.getElementById('clearBtn');
    const inputLanguage = document.getElementById('languageInputSelect');
    const selectedTranslationLanguage = document.getElementById('languageTranslationSelect');
    startBtn.disabled = false;
    stopBtn.disabled = true;

    const translationText = document.getElementById('translationText');
    const transcriptionText = document.getElementById('transcriptionText');

    var stream; // need a global here to stop the stream later
    var mediaRecorder = null;

    // Connect to the socket server
    const socket = io.connect('http://' + document.location.hostname + ':' + location.port);
    console.log('Document domain:', document.location.hostname);
    console.log('Location port:', location.port);
    console.log('Socket:', socket);

    (async function () {
        try {
            let res = await fetch(`/${site_id}/negotiate`)
            let data = await res.json();
            let ws = new WebSocket(data.url, 'json.webpubsub.azure.v1');
            ws.onopen = () => {
                console.log('connected to translation pub/sub service');
                ws.send(JSON.stringify({
                    type: 'joinGroup',
                    group: 'stream',
                    data: 'data'
                }));
            };
            ws.onmessage = (msg) => {
                const parsedData = JSON.parse(msg.data);
                if (parsedData.type !== 'message') {
                    return;
                }
                const data = JSON.parse(parsedData.data);

                // Extract language and translation from parsed data
                const language = data.language;
                const translation = data.translation;
                // put the english translation in the transcription text box
                // and the selected language translation in the translation text box
                if (language == 'en') {
                    transcriptionText.innerHTML = translation;
                } else if (language == selectedTranslationLanguage.value) {
                    translationText.innerHTML = translation;
                };
            };

            ws.onclose = (event) => {
                console.log('WebSocket (PubSub) closed:', event);
            };

            ws.onerror = (error) => {
                console.error('WebSocket (PubSub) error:', error);
            };
        } catch (error) {
            console.error('Failed to establish WebSocket (PubSub) connection:', error);
        }
    })();

    function stopMediaStream(stream) {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            console.log('Audio input stream stopped');
        }
    }

    // Add event listener to startBtn to start a audio stream
    startBtn.addEventListener('click', async () => {
        startBtn.disabled = true;
        stopBtn.disabled = false;
        const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(audioStream);
        source_language = inputLanguage.value;
        socket.emit('audio_start', site_id, source_language);

        console.log('Start transcription');
        // sleep for 2 seconds
        await new Promise(r => setTimeout(r, 2000));
        mediaRecorder.start(2000);

        mediaRecorder.ondataavailable = async event => {
            socket.emit('audio_data', event.data);
        }

        mediaRecorder.onstop = async event => {
            console.log('Media recorder stopped');
            socket.emit('audio_done');
        }
    });



    // Add event listener to stopBtn to stop the stream
    stopBtn.addEventListener('click', function () {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        stopMediaStream(stream);
        mediaRecorder.stop();
        //socket.emit('audio_done');
    });

    // add an event listener to clearBtn to clear the transcription and translation text
    clearBtn.addEventListener('click', function () {
        translationText.innerHTML = '';
        transcriptionText.innerHTML = '';
    });


    // uncomment below for debugging translations
    /*
    socket.on('transcription', function(data) {
        console.log('Transcription:', data);
    });
    */

});
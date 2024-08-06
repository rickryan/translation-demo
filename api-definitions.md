# Page and API Endpoints

The page and API endpoints available in the server.py Flask application.  Documentation for the application is available [here](./Readme.md)

## Base URL

The base URL for these endpoints is `http://localhost:5000` when running the app locally.

## Page Endpoints

### Home Page
- **Path**: `/<site_id>`
- **Method**: GET
- **Functionality**: Serves the main index.html page of the application for a given site
- **Parameters**: Optional multiple specifications of languages. e.g., `/?language=fr&language=es`
- **Response**: The `index.html` template.

### Speaker Input Page
- **Path**: `/<site_id>/speaker`
- **Method**: GET
- **Functionality**: Serves the speaker.html page of the application for a given site.  The page allows the speaker to specify their input language (defaults to the browser default), provide audio input and view the transcription of their speech and see the translation in one chosen language.
- **Response**: The `speaker.html` template.

### QR Codes for a Site
- **Path**: `/<site_id>/display_qr_codes`
- **Method**: GET
- **Functionality**: Serves a page that shows QR codes with links to a page for each language supported by a site and a link to a page the speaker can use for audio input
- **Response**: The `display_qr_codes.html` template.

### Test Mode
- **Path**: `/test`
- **Method**: GET
- **Functionality**: Redirects to the home page to a test_site with a `testmode=true` query parameter to enable test mode.
- **Parameters**: None
- **Response**: A 302 redirect to `/test_site?testmode=true`.

## API Endpoints
### Negotiate
- **Path**: `/<site_id>/negotiate`
- **Method**: GET
- **Functionality**: Generates a client access token for connecting to the Web PubSub service with specific roles for the given site_id.
- **Parameters**: Any additional query string parameters are added to the token URL.
- **Response**: A JSON object containing the `url` with the access token.
  ```json
  {
    "url": "generated_access_token_url"
  }

### Summarize Text
- **Path**: `/summarize`
- **Method**: POST
- **Functionality**: Receives text and a language code, and returns a summary of the text and a list of points in the specified language.
- **Parameters**:
  - **Body** (application/json):
    - `language`: The language code for the summary (e.g., "en" for English).
    - `text`: The text to be summarized.
- **Response**:
  - **Success**:
    - **Code**: 200 OK
    - **Content**: A JSON object containing the summarized text and the language code.
      ```json
      {
        "summary": "Summarized text here...",
        "points": ["point1", "point2",...]
        "language": "en"
      }
      ```
  - **Error**:
    - **Code**: 400 Bad Request
    - **Content**: A JSON object indicating the missing data in the request.
      ```json
      {
        "error": "Missing data in request"
      }
      ```
- **Example Request**:
  ```bash
  curl -X POST http://localhost:5000/summarize \
       -H "Content-Type: application/json" \
       -d '{"language": "en", "text": "The text to summarize..."}'

### Generate QR Code
- **Path**: `/generate_qr`
- **Method**: GET
- **Functionality**: Returns a QR code that contains a link to a page that will display a single language for a given site
- **Parameters**:
    - `language`: The language code for the summary (e.g., "en" for English).
    - `site_id`: The name of the site.
- **Response**:
  - **Success**:
    - **Code**: 200 OK
    - **Content**: A PNG image of the QR code.

### Generate Speaker QR Code
- **Path**: `<site_id>/generate_qr_speaker`
- **Method**: GET
- **Functionality**: Returns a QR code that contains a link to a page that the speaker can use to send audio input for a site
- **Response**:
  - **Success**:
    - **Code**: 200 OK
    - **Content**: A PNG image of the QR code.

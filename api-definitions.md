# API Endpoints

The API endpoints available in the server.py Flask application.  Documentation for the application is available [here](./Readme.md)

## Base URL

The base URL for these endpoints is `http://localhost:5000` when running the app locally.

## Endpoints

### Home Page

- **Path**: `/`
- **Method**: GET
- **Functionality**: Serves the main index.html page of the application.
- **Parameters**: Optional multiple specifications of languages. e.g., `/?language=fr&language=es`
- **Response**: The `index.html` file from the `public` directory.

### Test Mode

- **Path**: `/test`
- **Method**: GET
- **Functionality**: Redirects to the home page with a `testmode=true` query parameter to enable test mode.
- **Parameters**: None
- **Response**: A 302 redirect to `/?testmode=true`.

### Negotiate

- **Path**: `/negotiate`
- **Method**: GET
- **Functionality**: Generates a client access token for connecting to the Web PubSub service with specific roles.
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
import os
import requests
import io

from flask import Flask, send_from_directory, abort, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# Load environment variables once for all sub-apps
load_dotenv()

# ElevenLabs configuration
# Try to get from environment variable first, fallback to hardcoded
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_f513c877bf939d944174e8c11ffe9c6d53e3ba07c38a115a").strip()
ELEVENLABS_VOICE_ID = "XrExE9yKIg1WjnnlVkGX"
ELEVENLABS_TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"

# Debug: Print API key info (first 10 chars only for security)
if ELEVENLABS_API_KEY:
    print(f"[ElevenLabs] API Key configured: {ELEVENLABS_API_KEY[:10]}... (length: {len(ELEVENLABS_API_KEY)})")
else:
    print("[ElevenLabs] WARNING: API Key is empty!")

# Import each week's Flask app (they remain independent for debugging)
from temporary_main import app as week1_app
from temporary_week2_main import app as week2_app
from temporary_main_q16_22 import app as week3_app
from week4_main import app as week4_app
from week5_main import app as week5_app


def create_root_app():
    """Root Flask app that serves the shared frontend assets."""
    root = Flask(__name__)
    CORS(root, supports_credentials=True)

    def _serve_file(path):
        try:
            return send_from_directory(os.getcwd(), path)
        except FileNotFoundError:
            abort(404)

    @root.route('/')
    def serve_index():
        return _serve_file('index.html')

    @root.route('/<path:path>')
    def serve_static(path):
        return _serve_file(path)

    @root.route('/health')
    def health():
        return {"status": "ok"}

    @root.route('/api/elevenlabs/test', methods=['GET'])
    def test_elevenlabs_key():
        """Test endpoint to verify ElevenLabs API key is working."""
        try:
            if not ELEVENLABS_API_KEY:
                return jsonify({
                    "success": False,
                    "error": "API key not configured",
                    "key_length": 0,
                    "key_prefix": None
                }), 500
            
            # Test by getting user info (lightweight API call)
            # Ensure API key is properly formatted (strip whitespace)
            api_key = ELEVENLABS_API_KEY.strip() if ELEVENLABS_API_KEY else None
            
            if not api_key:
                return jsonify({
                    "success": False,
                    "error": "API key is empty after processing",
                    "key_length": 0,
                    "key_prefix": None
                }), 500
            
            headers = {
                "xi-api-key": api_key
            }
            
            print(f"[TEST] Testing API key: {api_key[:10]}... (length: {len(api_key)})")
            
            test_response = requests.get("https://api.elevenlabs.io/v1/user", headers=headers, timeout=10)
            
            if test_response.status_code == 200:
                user_data = test_response.json()
                return jsonify({
                    "success": True,
                    "message": "API key is valid",
                    "key_length": len(ELEVENLABS_API_KEY),
                    "key_prefix": ELEVENLABS_API_KEY[:10] + "...",
                    "user": {
                        "subscription": user_data.get("subscription", {}).get("tier", "unknown"),
                        "character_count": user_data.get("subscription", {}).get("character_count", 0),
                        "character_limit": user_data.get("subscription", {}).get("character_limit", 0)
                    }
                })
            elif test_response.status_code == 401:
                return jsonify({
                    "success": False,
                    "error": "Invalid API key",
                    "key_length": len(ELEVENLABS_API_KEY),
                    "key_prefix": ELEVENLABS_API_KEY[:10] + "...",
                    "details": "The API key was rejected by ElevenLabs. Please verify it's correct and active.",
                    "http_status": 401,
                    "response": test_response.text[:500]  # First 500 chars of response
                }), 401
            else:
                return jsonify({
                    "success": False,
                    "error": f"API test failed with status {test_response.status_code}",
                    "key_length": len(ELEVENLABS_API_KEY),
                    "key_prefix": ELEVENLABS_API_KEY[:10] + "...",
                    "http_status": test_response.status_code,
                    "response": test_response.text[:500]
                }), test_response.status_code
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                "success": False,
                "error": "Cannot connect to ElevenLabs API",
                "details": "Check your internet connection"
            }), 503
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "key_length": len(ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else 0
            }), 500

    @root.route('/api/tts', methods=['POST'])
    def text_to_speech():
        """Convert text to speech using ElevenLabs."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No data provided",
                    "error_type": "validation_error",
                    "details": "Request body is empty"
                }), 400
            
            text = data.get('text', '')
            
            if not text:
                return jsonify({
                    "success": False,
                    "error": "No text provided",
                    "error_type": "validation_error",
                    "details": "Text field is empty"
                }), 400
            
            if not ELEVENLABS_API_KEY:
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API key not configured",
                    "error_type": "configuration_error",
                    "details": "API key is missing from server configuration"
                }), 500
            
            # Call ElevenLabs TTS API
            # Ensure API key is properly formatted (strip whitespace)
            api_key = ELEVENLABS_API_KEY.strip() if ELEVENLABS_API_KEY else None
            
            if not api_key:
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API key is empty",
                    "error_type": "configuration_error",
                    "details": "API key is missing or empty after processing"
                }), 500
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            
            # Debug logging (only first few chars for security)
            print(f"[TTS] Making request with API key: {api_key[:10]}... (length: {len(api_key)})")
            
            payload = {
                "text": text,
                "model_id": "eleven_flash_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            try:
                response = requests.post(ELEVENLABS_TTS_URL, json=payload, headers=headers, timeout=30)
            except requests.exceptions.Timeout:
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API timeout",
                    "error_type": "timeout_error",
                    "details": "Request to ElevenLabs took too long (>30 seconds)"
                }), 504
            except requests.exceptions.ConnectionError:
                return jsonify({
                    "success": False,
                    "error": "Cannot connect to ElevenLabs API",
                    "error_type": "connection_error",
                    "details": "Failed to establish connection. Check your internet connection."
                }), 503
            except requests.exceptions.RequestException as e:
                return jsonify({
                    "success": False,
                    "error": "Network error",
                    "error_type": "network_error",
                    "details": str(e)
                }), 503
            
            if response.status_code == 200:
                return Response(
                    response.content,
                    mimetype='audio/mpeg',
                    headers={
                        'Content-Disposition': 'inline; filename=speech.mp3'
                    }
                )
            elif response.status_code == 401:
                # Log the full error response for debugging
                error_response = response.text
                print(f"[TTS] 401 Error - Full response: {error_response}")
                try:
                    error_json = response.json()
                    error_message = error_json.get('detail', {}).get('message', error_response)
                except:
                    error_message = error_response
                
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API authentication failed",
                    "error_type": "authentication_error",
                    "details": f"Invalid API key. ElevenLabs response: {error_message}",
                    "api_response": error_message,
                    "key_length": len(api_key),
                    "key_prefix": api_key[:10] + "..." if api_key else "N/A"
                }), 401
            elif response.status_code == 429:
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API rate limit exceeded",
                    "error_type": "rate_limit_error",
                    "details": "Too many requests. Please wait a moment and try again."
                }), 429
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    return jsonify({
                        "success": False,
                        "error": "ElevenLabs API validation error",
                        "error_type": "api_validation_error",
                        "details": error_data.get('detail', {}).get('message', response.text)
                    }), 400
                except:
                    return jsonify({
                        "success": False,
                        "error": "ElevenLabs API validation error",
                        "error_type": "api_validation_error",
                        "details": response.text
                    }), 400
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', {}).get('message', response.text)
                except:
                    error_message = response.text
                
                return jsonify({
                    "success": False,
                    "error": f"ElevenLabs API error (HTTP {response.status_code})",
                    "error_type": "api_error",
                    "details": error_message
                }), response.status_code
                
        except Exception as e:
            import traceback
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "error_type": "server_error",
                "details": str(e),
                "traceback": traceback.format_exc() if os.getenv('FLASK_DEBUG') == '1' else None
            }), 500

    @root.route('/api/stt', methods=['POST'])
    def speech_to_text():
        """Convert speech to text using ElevenLabs."""
        try:
            print(f"[STT] Request received. Content-Type: {request.content_type}")
            print(f"[STT] Request files: {list(request.files.keys())}")
            print(f"[STT] Request form: {list(request.form.keys())}")
            
            if 'audio' not in request.files:
                print("[STT] ERROR: 'audio' key not found in request.files")
                print(f"[STT] Available keys: {list(request.files.keys())}")
                return jsonify({
                    "success": False,
                    "error": "No audio file provided",
                    "error_type": "validation_error",
                    "details": f"Audio file is missing from request. Available keys: {list(request.files.keys())}"
                }), 400
            
            audio_file = request.files['audio']
            
            print(f"[STT] Audio file received: filename='{audio_file.filename}', content_type='{audio_file.content_type}'")
            
            if audio_file.filename == '':
                return jsonify({
                    "success": False,
                    "error": "Empty audio file",
                    "error_type": "validation_error",
                    "details": "Audio file is empty"
                }), 400
            
            if not ELEVENLABS_API_KEY:
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API key not configured",
                    "error_type": "configuration_error",
                    "details": "API key is missing from server configuration"
                }), 500
            
            # Read audio file content
            audio_file.seek(0)
            audio_data = audio_file.read()
            
            print(f"[STT] Received audio file: {audio_file.filename}, size: {len(audio_data)} bytes, content_type: {audio_file.content_type}")
            
            if len(audio_data) == 0:
                return jsonify({
                    "success": False,
                    "error": "Audio file is empty",
                    "error_type": "validation_error",
                    "details": "No audio data found in file"
                }), 400
            
            # Call ElevenLabs STT API
            # Ensure API key is properly formatted (strip whitespace)fa
            api_key = ELEVENLABS_API_KEY.strip() if ELEVENLABS_API_KEY else None
            
            if not api_key:
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API key is empty",
                    "error_type": "configuration_error",
                    "details": "API key is missing or empty after processing"
                }), 500
            
            headers = {
                "xi-api-key": api_key
            }
            
            # Debug logging (only first few chars for security)
            print(f"[STT] Making request to: {ELEVENLABS_STT_URL}")
            print(f"[STT] API key: {api_key[:10]}... (length: {len(api_key)})")
            print(f"[STT] Audio size: {len(audio_data)} bytes, type: {audio_file.content_type}")
            
            # ElevenLabs STT API expects the audio file with parameter name 'file' and model_id
            # Send file as raw bytes in tuple format: (filename, file_data, content_type)
            filename = audio_file.filename or 'recording.webm'
            content_type = audio_file.content_type or 'audio/webm'
            
            files = {
                'file': (filename, audio_data, content_type)
            }
            
            # Add model_id as form data (required by ElevenLabs STT API)
            data = {
                'model_id': 'scribe_v2'  # Use scribe_v2 model for STT (valid options: scribe_v1, scribe_v1_experimental, scribe_v2)
            }
            
            print(f"[STT] Sending request with filename: {filename}, model_id: {data['model_id']}")
            print(f"[STT] File size: {len(audio_data)} bytes, content_type: {content_type}")
            print(f"[STT] Files parameter: 'file' with tuple (filename, data, content_type)")
            print(f"[STT] Data parameter: {data}")
            
            try:
                # Send both files and data in multipart/form-data format
                # Don't include Content-Type in headers - requests will set it automatically for multipart/form-data
                stt_headers = {k: v for k, v in headers.items() if k.lower() != 'content-type'}
                
                response = requests.post(ELEVENLABS_STT_URL, files=files, data=data, headers=stt_headers, timeout=30)
                print(f"[STT] Response status: {response.status_code}")
                print(f"[STT] Response headers: {dict(response.headers)}")
                if response.status_code != 200:
                    print(f"[STT] Response body: {response.text[:500]}")
            except requests.exceptions.Timeout:
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API timeout",
                    "error_type": "timeout_error",
                    "details": "Request to ElevenLabs took too long (>30 seconds)"
                }), 504
            except requests.exceptions.ConnectionError:
                return jsonify({
                    "success": False,
                    "error": "Cannot connect to ElevenLabs API",
                    "error_type": "connection_error",
                    "details": "Failed to establish connection. Check your internet connection."
                }), 503
            except requests.exceptions.RequestException as e:
                return jsonify({
                    "success": False,
                    "error": "Network error",
                    "error_type": "network_error",
                    "details": str(e)
                }), 503
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"[STT] Success! Transcribed text: {result.get('text', '')[:100]}...")
                    return jsonify({
                        "success": True,
                        "text": result.get('text', '')
                    })
                except ValueError as e:
                    print(f"[STT] JSON parse error: {e}")
                    print(f"[STT] Response text: {response.text[:500]}")
                    return jsonify({
                        "success": False,
                        "error": "Invalid response from ElevenLabs",
                        "error_type": "api_response_error",
                        "details": f"Could not parse JSON response from API: {str(e)}",
                        "raw_response": response.text[:500]
                    }), 500
            elif response.status_code == 401:
                # Log the full error response for debugging
                error_response = response.text
                print(f"[STT] 401 Error - Full response: {error_response}")
                try:
                    error_json = response.json()
                    error_message = error_json.get('detail', {}).get('message', error_response)
                except:
                    error_message = error_response
                
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API authentication failed",
                    "error_type": "authentication_error",
                    "details": f"Invalid API key. ElevenLabs response: {error_message}",
                    "api_response": error_message,
                    "key_length": len(api_key),
                    "key_prefix": api_key[:10] + "..." if api_key else "N/A"
                }), 401
            elif response.status_code == 429:
                return jsonify({
                    "success": False,
                    "error": "ElevenLabs API rate limit exceeded",
                    "error_type": "rate_limit_error",
                    "details": "Too many requests. Please wait a moment and try again."
                }), 429
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    return jsonify({
                        "success": False,
                        "error": "ElevenLabs API validation error",
                        "error_type": "api_validation_error",
                        "details": error_data.get('detail', {}).get('message', response.text)
                    }), 400
                except:
                    return jsonify({
                        "success": False,
                        "error": "ElevenLabs API validation error",
                        "error_type": "api_validation_error",
                        "details": response.text
                    }), 400
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', {}).get('message', response.text)
                except:
                    error_message = response.text
                
                return jsonify({
                    "success": False,
                    "error": f"ElevenLabs API error (HTTP {response.status_code})",
                    "error_type": "api_error",
                    "details": error_message
                }), response.status_code
                
        except Exception as e:
            import traceback
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "error_type": "server_error",
                "details": str(e),
                "traceback": traceback.format_exc() if os.getenv('FLASK_DEBUG') == '1' else None
            }), 500

    return root


root_app = create_root_app()

# Mount each week's Flask app under its own prefix so their routes remain unchanged
application = DispatcherMiddleware(root_app, {
    '/week1': week1_app,
    '/week2': week2_app,
    '/week3': week3_app,
    '/week4': week4_app,
    '/week5': week5_app,
})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5007))
    run_simple('0.0.0.0', port, application, use_reloader=False, use_debugger=os.getenv('FLASK_DEBUG') == '1')


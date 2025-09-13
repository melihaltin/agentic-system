# Voice Agent

A sophisticated AI voice agent built with Twilio, LangGraph, and multiple TTS/STT providers.

## Features

- **Multiple TTS Providers**: ElevenLabs and Twilio TTS
- **Multiple STT Providers**: OpenAI Whisper and Twilio STT
- **LangGraph Integration**: Advanced conversation flow management
- **Promo Code Generation**: Automatic generation and SMS delivery
- **Flexible Architecture**: Plugin-based provider system

## Project Structure

```
ai_agents/
├── agents/
│   └── voice/
│       ├── __init__.py
│       ├── agent.py          # Main TwilioOutboundAgent class
│       └── tools.py          # Promo code generation tools
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── voice_config.py       # Voice service configurations
├── core/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── interfaces.py         # Abstract interfaces for TTS/STT/Storage
│   └── tools_registry.py
├── services/
│   ├── stt/
│   │   ├── __init__.py
│   │   ├── openai_stt.py     # OpenAI Whisper implementation
│   │   └── twilio.py         # Twilio STT implementation
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── elevenlabs.py     # ElevenLabs TTS implementation
│   │   └── twilio.py         # Twilio TTS implementation
│   ├── __init__.py
│   ├── audio_storage.py      # Local audio file storage
│   ├── voice_service.py      # Main voice service coordinator
│   └── webhook_server.py     # Flask webhook server
├── voice_agent_main.py       # Main application entry point
└── requirements.txt
```

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
GOOGLE_API_KEY=your_google_api_key
WEBHOOK_BASE_URL=your_webhook_base_url

# Optional (for ElevenLabs TTS)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Optional (for OpenAI STT)
OPENAI_API_KEY=your_openai_api_key

# Optional (for audio storage)
AUDIO_STORAGE_PATH=/tmp/audio
```

## Installation

1. Install dependencies:

```bash
cd ai_agents
pip install -r requirements.txt
```

2. Set up environment variables in `.env` file

3. Run the application:

```bash
python voice_agent_main.py
```

## Usage

The application offers three options:

1. **Start with ElevenLabs TTS**: High-quality voice synthesis
2. **Start with Twilio TTS**: Built-in Twilio voice synthesis
3. **Make test call**: Make a test outbound call

## API Endpoints

When running the webhook server:

- `POST /make-call`: Make outbound calls
- `GET /health`: Health check
- `POST /webhook/outbound/start`: Twilio webhook entry point
- `POST /webhook/outbound/process`: Process speech input
- `GET /audio/<filename>`: Serve audio files (for ElevenLabs)

## Architecture

The voice agent uses a modular architecture:

1. **Interfaces**: Abstract base classes for TTS, STT, and storage providers
2. **Providers**: Concrete implementations (ElevenLabs, OpenAI, Twilio)
3. **Voice Service**: Coordinator that manages all providers
4. **Agent**: LangGraph-based conversation management
5. **Webhook Server**: Flask server handling Twilio webhooks

## Conversation Flow

1. Agent makes outbound call via Twilio
2. Webhook receives call start event
3. Agent greets customer and offers promo code
4. Customer speech is processed via configured STT
5. LangGraph manages conversation state and tool calls
6. Agent generates promo code and sends SMS
7. Response converted to speech via configured TTS
8. Call ends gracefully

## Extending the System

To add new providers:

1. Implement the appropriate interface (`TTSProvider`, `STTProvider`, or `AudioStorage`)
2. Add configuration in `VoiceConfig`
3. Update the main application to use new provider

This modular design makes it easy to swap providers or add new ones without changing the core logic.

# Dinamik AI Voice Agent API

Bu sistem backend'inizden gelen isteklerle otomatik AI voice call'ları başlatır.

## 🚀 Kullanım

### 1. Sunucuyu Başlatın

```bash
cd ai_agents
source agent-env/bin/activate
python voice_agent_main.py
# Seçenek 5'i seçin: "Start API Server"
```

### 2. API Endpoint'ini Kullanın

**POST** `http://localhost:5000/start-call`

#### Request Body:

```json
{
  "customer_number": "+1234567890",
  "customer_name": "John Doe",
  "customer_type": "vip",
  "order_id": "ORD-12345",
  "business_info": {
    "company_name": "TechCorp Solutions",
    "description": "Leading technology solutions provider",
    "website": "https://techcorp.com"
  },
  "agent_name": "Sarah AI Assistant",
  "tts_provider": "elevenlabs",
  "language": "en-US",
  "voice_settings": {
    "stability": 0.6,
    "similarity_boost": 0.7
  }
}
```

#### Required Fields:

- `customer_number`: Aranacak telefon numarası
- `business_info.company_name`: Şirket adı

#### Optional Fields:

- `customer_name`: Müşteri adı
- `customer_type`: "regular", "new", "vip" (promo code için)
- `order_id`: Sipariş numarası
- `agent_name`: AI agent'ın adı
- `tts_provider`: "elevenlabs" veya "twilio"
- `language`: Dil kodu (varsayılan: "en-US")
- `voice_settings`: ElevenLabs ses ayarları

#### Response:

```json
{
  "success": true,
  "call_sid": "CA1234567890abcdef",
  "message": "AI agent call started successfully",
  "config": {
    "customer_number": "+1234567890",
    "business": "TechCorp Solutions",
    "agent_name": "Sarah AI Assistant",
    "tts_provider": "elevenlabs"
  }
}
```

## 🎯 Nasıl Çalışır

1. **API İsteği**: Backend'inizden `/start-call` endpoint'ine istek gönderirsiniz
2. **Dinamik Konfigürasyon**: Sistem gelen bilgilere göre AI agent'ı konfigüre eder
3. **TTS Seçimi**: İstekteki `tts_provider`'a göre ElevenLabs veya Twilio kullanır
4. **Otomatik Arama**: Belirtilen telefon numarasına arama başlatır
5. **Dinamik Sistem Mesajı**: AI agent şirket bilgilerinizle özelleştirilmiş sistem mesajı kullanır
6. **Konuşma**: AI agent müşteriyle konuşur ve promo kodu gönderir

## 📞 Sistem Mesajı Örneği

Gönderdiğiniz bilgilere göre oluşturulan sistem mesajı:

```
You are a professional and friendly AI customer service representative for TechCorp Solutions.
Your name is Sarah AI Assistant.
Company description: Leading technology solutions provider
You are calling customer John Doe at phone number +1234567890.
Customer type: vip
This call is related to order ID: ORD-12345
You understand all languages and will continue in whichever language the customer speaks.
Your conversation flow:
1. Politely introduce yourself and the company, then offer a special promo code.
2. If the customer is interested, respond positively and immediately call the generate_promo_code tool.
3. Always pass the phone_number parameter when calling the tool.
4. After the tool runs, inform the customer that you're sending the promo code via SMS and end the conversation politely.
Keep the conversation natural, friendly, and professional.
```

## 🧪 Test

Örnek API çağrısını test etmek için:

```bash
python example_api_call.py
```

## 🌐 Environment Variables

`.env` dosyasında şunları ayarlayın:

```bash
# Twilio (Required)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number
WEBHOOK_BASE_URL=your_ngrok_or_server_url

# Google AI (Required)
GOOGLE_API_KEY=your_google_api_key

# ElevenLabs (Optional - for high-quality TTS)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=voice_id

# Audio Storage (Optional)
AUDIO_STORAGE_PATH=/tmp/audio
```

## 📋 Endpoints

- `POST /start-call` - Dinamik AI agent call'ı başlat
- `POST /make-call` - Basit call (eski format)
- `GET /health` - Sunucu durumu
- `POST /webhook/outbound/start` - Twilio webhook (otomatik)
- `POST /webhook/outbound/process` - Twilio webhook (otomatik)

Bu sistem ile backend'inizden kolayca AI voice agent'larını başlatabilir, her çağrı için farklı şirket bilgileri, agent isimleri ve TTS sağlayıcıları kullanabilirsiniz!

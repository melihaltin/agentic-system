# Voices API Documentation

Bu API, ElevenLabs seslerini sisteminize entegre etmenizi sağlar. ElevenLabs'dan sesleri çekip veritabanınıza kaydeder ve frontend'inize API aracılığıyla sunar.

## Kurulum

1. **Gerekli paketleri yükleyin:**

```bash
pip install -r requirements.txt
```

2. **Environment variables (.env dosyası) oluşturun:**

```bash
cp .env.example .env
```

`.env` dosyasında şu değerleri doldurun:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
JWT_SECRET=your_jwt_secret
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

3. **Veritabanı migration'ını çalıştırın:**

```bash
python migrate.py
```

## API Endpoints

### 1. ElevenLabs'dan Sesleri Senkronize Et

```http
POST /v1/voices/sync
```

Bu endpoint ElevenLabs API'sinden tüm sesleri çeker ve `agent_voices` tablonuza kaydeder.

**Response:**

```json
{
  "success": true,
  "message": "Successfully synced 50 voices, skipped 0",
  "synced_count": 50,
  "skipped_count": 0,
  "errors": []
}
```

### 2. Veritabanından Sesleri Getir

```http
GET /v1/voices/
```

**Query Parameters:**

- `is_active` (boolean, optional): Aktif sesleri filtreler. Default: `true`

**Response:**

```json
{
  "voices": [
    {
      "id": "uuid",
      "name": "Ayşe - Genç Kadın",
      "provider": "elevenlabs",
      "voice_id": "voice_123",
      "language": "tr-TR",
      "gender": "female",
      "age_group": "young",
      "accent": null,
      "sample_url": "https://...",
      "is_premium": false,
      "is_active": true,
      "metadata": {
        "elevenlabs_labels": {...},
        "description": "..."
      },
      "created_at": "2025-09-20T...",
      "updated_at": "2025-09-20T..."
    }
  ],
  "total": 50
}
```

### 3. Doğrudan ElevenLabs'dan Sesleri Getir (Test Amaçlı)

```http
GET /v1/voices/providers/elevenlabs
```

Bu endpoint veritabanını bypass eder ve direkt ElevenLabs API'sinden sesleri getirir.

## Kullanım Örnekleri

### JavaScript/Frontend Kullanımı

```javascript
// 1. İlk kez sesleri senkronize edin
const syncVoices = async () => {
  const response = await fetch("http://localhost:8000/v1/voices/sync", {
    method: "POST",
  });
  const result = await response.json();
  console.log("Sync result:", result);
};

// 2. Sesleri getirin ve kullanıcıya gösterin
const getVoices = async () => {
  const response = await fetch("http://localhost:8000/v1/voices/");
  const data = await response.json();

  // Frontend'de ses seçimi için kullanın
  data.voices.forEach((voice) => {
    console.log(`${voice.name} - ${voice.gender} - ${voice.age_group}`);
  });

  return data.voices;
};

// 3. Ses seçimi component'i için
const VoiceSelector = () => {
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);

  useEffect(() => {
    getVoices().then(setVoices);
  }, []);

  return (
    <select onChange={(e) => setSelectedVoice(e.target.value)}>
      <option value="">Ses Seçin</option>
      {voices.map((voice) => (
        <option key={voice.id} value={voice.voice_id}>
          {voice.name} {voice.is_premium && "(Premium)"}
        </option>
      ))}
    </select>
  );
};
```

### cURL Örnekleri

```bash
# Sesleri senkronize et
curl -X POST http://localhost:8000/v1/voices/sync

# Aktif sesleri getir
curl http://localhost:8000/v1/voices/

# Tüm sesleri getir (aktif olmayan dahil)
curl "http://localhost:8000/v1/voices/?is_active="

# ElevenLabs'dan direkt sesleri getir
curl http://localhost:8000/v1/voices/providers/elevenlabs
```

## Test Etme

Test scriptini çalıştırın:

```bash
python test_voices.py
```

Bu script:

1. ElevenLabs API bağlantısını test eder
2. Sesleri veritabanına senkronize eder
3. Veritabanından sesleri getirir

## Veritabanı Yapısı

`agent_voices` tablosu şu yapıdadır:

```sql
CREATE TABLE agent_voices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    voice_id VARCHAR(255) NOT NULL,
    language VARCHAR(10) DEFAULT 'tr-TR',
    gender VARCHAR(20),
    age_group VARCHAR(20),
    accent VARCHAR(50),
    sample_url TEXT,
    is_premium BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Hata Ayıklama

### Yaygın Hatalar

1. **ElevenLabs API Key Hatası:**

   - `.env` dosyasında `ELEVENLABS_API_KEY` doğru tanımlı mı kontrol edin
   - API key'inizin geçerli olduğunu ElevenLabs dashboard'dan kontrol edin

2. **Supabase Bağlantı Hatası:**

   - Supabase URL ve service key'lerini kontrol edin
   - Migration'ın çalıştırıldığından emin olun

3. **Import Hataları:**
   - Gerekli paketlerin yüklendiğinden emin olun: `pip install -r requirements.txt`

### Log Kontrolü

API çalışırken hataları görmek için:

```bash
python -m uvicorn main:app --reload --log-level debug
```

## Güvenlik Notları

- ElevenLabs API key'inizi `.env` dosyasında saklayın, kod içinde hardcode etmeyin
- Production'da service key yerine appropriate Supabase RLS policies kullanın
- API rate limiting ekleyebilirsiniz yoğun kullanım için

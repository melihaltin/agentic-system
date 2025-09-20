# Voice Integration Setup Guide

## ✅ Completed Features

### 1. **Backend Voice API**

- ✅ ElevenLabs API integration
- ✅ Voice synchronization from ElevenLabs
- ✅ Voice database storage in `agent_voices` table
- ✅ REST API endpoints for voice management
- ✅ Audio preview functionality

### 2. **Frontend Voice Selector**

- ✅ Beautiful voice selection component with filters
- ✅ Real-time voice preview functionality
- ✅ Search and filter by gender, provider, accent
- ✅ Premium voice indicators
- ✅ Responsive design with Tailwind CSS

## 📋 Setup Instructions

### 1. **Backend Setup**

1. **Install Dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

2. **Configure Environment:**

```bash
cp .env.example .env
```

Edit `.env` file and add your credentials:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
# ... other variables
```

3. **Run Database Migration:**

```bash
python migrate.py
```

4. **Start Backend:**

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. **Frontend Setup**

1. **Configure Environment:**

```bash
cd frontend
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. **Start Frontend:**

```bash
npm run dev
```

## 🚀 Usage

### 1. **Sync Voices from ElevenLabs**

First, sync voices from ElevenLabs to your database:

**Option A: Using API directly**

```bash
curl -X POST "http://localhost:8000/v1/voices/sync"
```

**Option B: Using the test script**

```bash
cd backend
python test_voices.py
```

### 2. **View Voice Selector in Frontend**

1. Go to `http://localhost:3000`
2. Navigate to **My Agents** section
3. Select an agent with voice capability
4. Click **Configure** button
5. Go to **Voice** tab
6. You'll see the beautiful voice selector with:
   - Search functionality
   - Gender and provider filters
   - Voice preview buttons
   - Premium voice indicators
   - Responsive grid layout

## 📚 API Endpoints

### 1. **GET /v1/voices/**

Get all voices from database with optional filtering.

**Query Parameters:**

- `is_active` (boolean, optional): Filter by active status

**Response Example:**

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
      "sample_url": "https://...",
      "is_premium": false,
      "is_active": true,
      "created_at": "2025-01-20T...",
      "updated_at": "2025-01-20T..."
    }
  ],
  "total": 25
}
```

### 2. **POST /v1/voices/sync**

Sync voices from ElevenLabs API to database.

**Response Example:**

```json
{
  "success": true,
  "message": "Successfully synced 25 voices, skipped 0",
  "synced_count": 25,
  "skipped_count": 0,
  "errors": []
}
```

### 3. **GET /v1/voices/providers/elevenlabs**

Get voices directly from ElevenLabs API (for testing).

## 🎨 UI Features

### Voice Selector Component Features:

- **🔍 Search:** Search by voice name or accent
- **🎯 Filters:** Filter by gender (male/female/neutral) and provider
- **▶️ Preview:** Click play button to hear voice samples
- **💎 Premium Indicators:** Visual badges for premium voices
- **✅ Selection:** Clear visual indication of selected voice
- **📱 Responsive:** Works perfectly on desktop and mobile
- **🎨 Beautiful Design:** Modern UI with hover effects and animations

### Voice Card Information:

- Voice name and provider
- Gender and age group icons
- Premium voice badges
- Accent information
- Audio preview button
- Selection state indicators

## 🔧 Customization

### Adding New Voice Providers

1. **Update Backend Service:**

   - Add new provider logic in `src/features/agents/service.py`
   - Implement provider-specific API calls

2. **Update Frontend:**
   - Voice selector automatically supports new providers
   - Add provider-specific styling if needed

### Styling Customizations

The voice selector uses Tailwind CSS classes and can be easily customized:

- Colors: Modify color classes (blue-500, gray-200, etc.)
- Layout: Adjust grid classes (grid-cols-1 sm:grid-cols-2)
- Spacing: Change padding and margin classes

## 🐛 Troubleshooting

### Common Issues:

1. **"Failed to fetch voices" Error:**

   - Check if backend is running on port 8000
   - Verify CORS settings in backend
   - Check browser console for CORS errors

2. **"Failed to sync voices" Error:**

   - Verify ElevenLabs API key is correct
   - Check internet connection
   - Ensure Supabase credentials are correct

3. **Voice Preview Not Working:**

   - Check if voice has `sample_url`
   - Verify audio URLs are accessible
   - Check browser audio permissions

4. **No Voices Showing:**
   - Run sync command first: `POST /v1/voices/sync`
   - Check database connection
   - Verify migration ran successfully

### Debug Commands:

```bash
# Test backend API
curl "http://localhost:8000/v1/voices/"

# Test ElevenLabs connection
curl "http://localhost:8000/v1/voices/providers/elevenlabs"

# Check backend health
curl "http://localhost:8000/health"
```

## 📈 Next Steps

Potential enhancements:

- Add voice cloning functionality
- Implement voice training with custom data
- Add more voice providers (Google, Azure, etc.)
- Voice usage analytics and reporting
- Bulk voice operations
- Voice quality ratings and feedback

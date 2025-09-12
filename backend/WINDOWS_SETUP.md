# Windows'da Team AI Backend Kurulumu

Bu rehber, Windows 10/11 sistemlerde Team AI backend projesinin nasıl kurulacağını ve çalıştırılacağını açıklar.

## 🛠️ Gerekli Programlar

### 1. Python 3.11+ Kurulumu

1. **Python İndir**: [python.org](https://python.org/downloads/) adresinden Python 3.11+ sürümünü indirin
2. **Kurulum**: 
   - "Add Python to PATH" seçeneğini işaretleyin
   - "Install for all users" seçin
3. **Doğrulama**: Command Prompt'ta `python --version` komutunu çalıştırın

### 2. Git Kurulumu

1. **Git İndir**: [git-scm.com](https://git-scm.com/download/win) adresinden Git'i indirin
2. **Kurulum**: Varsayılan ayarları kullanın
3. **Doğrulama**: `git --version` komutunu çalıştırın

### 3. Docker Desktop Kurulumu

1. **Docker Desktop İndir**: [docker.com](https://docs.docker.com/desktop/install/windows-install/) adresinden Docker Desktop'u indirin
2. **Sistem Gereksinimleri**: WSL 2 Backend gereklidir
3. **WSL 2 Kurulumu** (gerekiyorsa):
   ```powershell
   # PowerShell'i yönetici olarak açın
   wsl --install
   # Sistemi yeniden başlatın
   ```
4. **Docker Desktop'u Başlatın**: Kurulum sonrası Docker Desktop'u çalıştırın

### 4. Node.js Kurulumu (Supabase CLI için)

1. **Node.js İndir**: [nodejs.org](https://nodejs.org/) adresinden LTS sürümünü indirin
2. **Kurulum**: Varsayılan ayarları kullanın
3. **Doğrulama**: `node --version` ve `npm --version` komutlarını çalıştırın

## 🚀 Proje Kurulumu

### 1. Projeyi İndirin

```powershell
# PowerShell veya Command Prompt'ta
git clone https://github.com/ozgurucar/team-ai.git
cd team-ai\backend
```

### 2. Python Sanal Ortamı Oluşturun

```powershell
# Sanal ortam oluştur
python -m venv venv

# Sanal ortamı aktifleştir
venv\Scripts\activate

# Gereksinimleri yükle
pip install -r requirements.txt
```

### 3. Supabase CLI Kurulumu

```powershell
# npm ile kurulum (önerilen)
npm install -g @supabase/cli

# Doğrulama
supabase --version
```

**Alternatif Kurulum Yöntemi** (npm çalışmazsa):

1. [Supabase CLI Releases](https://github.com/supabase/cli/releases) sayfasından Windows sürümünü indirin
2. `.exe` dosyasını `C:\Program Files\supabase\` klasörüne koyun
3. Bu klasörü PATH'e ekleyin

### 4. Environment Dosyasını Hazırlayın

```powershell
# .env dosyasını oluştur
copy .env.example .env

# Notepad ile düzenle
notepad .env
```

**.env dosyasına şu içeriği ekleyin:**

```env
# Local Supabase Development Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Security
SECRET_KEY=local-development-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Traditional Database Configuration (fallback)
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=team_ai_local

# Local Supabase Configuration
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU
USE_SUPABASE_AUTH=true

# CORS Configuration
ALLOWED_HOSTS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_PATH=uploads

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

## 📦 Windows Komut Dosyaları Oluşturma

### 1. dev.bat Dosyası Oluşturun

```powershell
# dev.bat dosyasını oluştur
notepad dev.bat
```

**dev.bat içeriği:**

```batch
@echo off
setlocal enabledelayedexpansion

echo Team AI Backend Development Helper (Windows)
echo =============================================

if "%1"=="" (
    goto :show_help
) else if "%1"=="install" (
    goto :install
) else if "%1"=="dev" (
    goto :dev
) else if "%1"=="test" (
    goto :test
) else if "%1"=="supabase-local" (
    goto :supabase_local
) else if "%1"=="supabase-stop" (
    goto :supabase_stop
) else if "%1"=="dev-supabase" (
    goto :dev_supabase
) else (
    echo Unknown command: %1
    goto :show_help
)

:install
echo 📦 Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
goto :end

:dev
echo 🚀 Starting development server...
call venv\Scripts\activate.bat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
goto :end

:test
echo 🧪 Running tests...
call venv\Scripts\activate.bat
python -m pytest tests/ -v
goto :end

:supabase_local
echo 🚀 Starting local Supabase...
call supabase-local.bat start
goto :end

:supabase_stop
echo 🛑 Stopping local Supabase...
call supabase-local.bat stop
goto :end

:dev_supabase
echo 🔥 Starting development server with local Supabase...
set USE_SUPABASE=true
set ENVIRONMENT=local
call venv\Scripts\activate.bat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
goto :end

:show_help
echo.
echo Available commands:
echo   install         Install Python dependencies
echo   dev             Start development server
echo   test            Run tests
echo   supabase-local  Start local Supabase
echo   supabase-stop   Stop local Supabase
echo   dev-supabase    Start server with local Supabase
echo.
goto :end

:end
```

### 2. supabase-local.bat Dosyası Oluşturun

```powershell
# supabase-local.bat dosyasını oluştur
notepad supabase-local.bat
```

**supabase-local.bat içeriği:**

```batch
@echo off
setlocal enabledelayedexpansion

echo Team AI Local Supabase Manager (Windows)
echo ========================================

if "%1"=="" (
    goto :show_help
) else if "%1"=="start" (
    goto :start
) else if "%1"=="stop" (
    goto :stop
) else if "%1"=="status" (
    goto :status
) else if "%1"=="reset" (
    goto :reset
) else if "%1"=="logs" (
    goto :logs
) else (
    echo Unknown command: %1
    goto :show_help
)

:start
echo [INFO] Starting local Supabase...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH!
    goto :end
)
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running! Please start Docker Desktop first.
    goto :end
)

echo [INFO] Initializing Supabase...
supabase init --force
echo [INFO] Starting Supabase services...
supabase start
goto :end

:stop
echo [INFO] Stopping Supabase services...
supabase stop
goto :end

:status
echo [INFO] Checking Supabase status...
supabase status
goto :end

:reset
echo [INFO] Resetting Supabase database...
supabase db reset
goto :end

:logs
echo [INFO] Showing Supabase logs...
supabase logs
goto :end

:show_help
echo.
echo Available commands:
echo   start    Start local Supabase services
echo   stop     Stop local Supabase services
echo   status   Check service status
echo   reset    Reset database
echo   logs     Show logs
echo.
goto :end

:end
```

## 🎯 Çalıştırma Adımları

### 1. Servisleri Başlatın

```powershell
# Docker Desktop'u başlatın (önemli!)
# Ardından PowerShell'de:

# 1. Sanal ortamı aktifleştir
venv\Scripts\activate

# 2. Supabase'i başlat
supabase-local.bat start

# 3. Backend sunucusunu başlat
dev.bat dev-supabase
```

### 2. Alternatif: Tek Komutla

```powershell
# Docker Desktop başlattıktan sonra:
dev.bat supabase-local
```

### 3. Servislere Erişim

- **FastAPI Backend**: http://localhost:8000
- **API Dokümantasyonu**: http://localhost:8000/docs
- **Supabase Studio**: http://localhost:54323
- **PostgreSQL**: localhost:54322

## 🔧 Sorun Giderme

### Yaygın Sorunlar ve Çözümleri

#### 1. "Docker is not running" Hatası
```powershell
# Çözüm: Docker Desktop'u başlatın
# Başlat menüsünden "Docker Desktop" çalıştırın
```

#### 2. "Port already in use" Hatası
```powershell
# Port kontrolü
netstat -ano | findstr :8000
netstat -ano | findstr :54321

# Port'u kullanan işlemi sonlandırın
taskkill /PID <PID_NUMARASI> /F
```

#### 3. Python Virtual Environment Sorunları
```powershell
# Sanal ortamı sil ve yeniden oluştur
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### 4. Supabase CLI Kurulum Sorunları
```powershell
# npm cache temizle
npm cache clean --force

# Global olarak yeniden kur
npm uninstall -g @supabase/cli
npm install -g @supabase/cli
```

#### 5. Permission Hatası
```powershell
# PowerShell'i yönetici olarak çalıştırın
# veya execution policy değiştirin:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Detaylı Hata Ayıklama

```powershell
# Sistem durumunu kontrol et
python --version
docker --version
node --version
npm --version
supabase --version

# Docker kontrol
docker ps
docker images

# Supabase durumu
supabase status

# Log'ları görüntüle
supabase logs
```

## 🔄 Günlük Geliştirme İş Akışı

### Projeyi Başlatma

```powershell
# 1. Docker Desktop'u başlat
# 2. PowerShell'de projeye git
cd C:\path\to\team-ai\backend

# 3. Sanal ortamı aktifleştir
venv\Scripts\activate

# 4. Servisleri başlat
dev.bat supabase-local
```

### Geliştirme Sırasında

```powershell
# Test çalıştır
dev.bat test

# Yeni migration oluştur
supabase migration new "migration_name"

# Database'i reset et
supabase-local.bat reset
```

### İş Bittiğinde

```powershell
# Servisleri durdur
dev.bat supabase-stop

# veya
supabase-local.bat stop
```

## 📋 Ekstra Notlar

### WSL 2 Kullanımı (İsteğe Bağlı)

Eğer WSL 2 kullanmayı tercih ederseniz:

```powershell
# WSL 2'ye geç
wsl

# Linux komutlarını kullan
./dev.sh supabase-local
```

### VS Code Entegrasyonu

1. **VS Code Extensions**:
   - Python
   - Docker
   - REST Client
   - SQLTools

2. **Workspace Settings**:
```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

### Performans İpuçları

1. **Docker Memory**: Docker Desktop Settings > Resources > Memory'i en az 4GB yapın
2. **Antivirus**: Proje klasörünü antivirus taramasından hariç tutun
3. **Windows Defender**: Real-time protection'u geçici olarak kapatın (geliştirme sırasında)

## 🆘 Yardım Alma

Sorun yaşarsanız:

1. **Logları kontrol edin**: `supabase logs`
2. **GitHub Issues**: Proje repository'sindeki issues bölümüne bakın
3. **Discord/Slack**: Takım kanallarında sorun paylaşın
4. **Dokümantasyon**: README.md ve LOCAL_DEVELOPMENT.md dosyalarını inceleyin

---

Bu rehber Windows 10/11 için optimize edilmiştir. Herhangi bir sorun yaşarsanız yukarıdaki sorun giderme bölümüne bakın veya yardım isteyin!

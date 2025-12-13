# See For Me - Backend API

FastAPI backend for AI-powered video captioning platform.

## ✅ Completed Setup

### 1. Models Created

#### **User Model** (`app/models/user.py`)

```python
- id: UUID (Primary Key)
- email: str (unique, indexed)
- full_name: str (required by frontend register form)
- password_hash: str (bcrypt hashed)
- is_active: bool
- created_at: datetime
- updated_at: datetime
```

#### **Video Model** (`app/models/video.py`)

```python
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key → users.id)
- title: str (video name)
- caption: str (AI-generated, can be long text)
- original_filename: str (uploaded file name)
- file_path: str (server storage path)
- video_url: str (public URL for frontend)
- thumbnail_url: str (optional)
- duration: str (e.g., "5:32")
- file_size: bigint (bytes)
- format: str (mp4/webm/ogg)
- created_at: datetime (upload time)
- updated_at: datetime
```

**Relationship:** `User.videos` ← one-to-many → `Video.user`

#### **SampleVideo Model** (`app/models/sample_video.py`)

```python
- id: UUID (Primary Key)
- title: str
- description: str
- caption: str
- video_url: str
- thumbnail_url: str
- duration: str
- display_order: int (for sorting)
- is_active: bool
- created_at: datetime
```

### 2. Schemas Created (Pydantic)

**User Schemas** (`app/schemas/user.py`):

- `UserCreate` - Registration input
- `UserLogin` - Login input
- `UserResponse` - User data output
- `UserWithToken` - Login response with JWT
- `Token` - JWT token response
- `TokenData` - Token payload

**Video Schemas** (`app/schemas/video.py`):

- `VideoCreate` - Video creation input
- `VideoResponse` - Video data output
- `VideoUploadResponse` - Upload response with timestamp
- `VideoHistoryResponse` - Paginated history response
- `SampleVideoResponse` - Sample video output
- `SampleVideosResponse` - List of samples

### 3. Database Configuration

- **SQLAlchemy** setup in `app/database.py`
- **Alembic** configured for migrations
- **PostgreSQL** recommended (see `DATABASE_SETUP.md`)

### 4. Settings & Config

- `.env` file for environment variables
- `app/config.py` with Pydantic Settings
- CORS configured for `http://localhost:3000`

## 📋 Next Steps

### Immediate Tasks:

1. **Setup PostgreSQL Database**

   ```powershell
   # See DATABASE_SETUP.md for detailed instructions
   # Quick start:
   psql -U postgres
   CREATE DATABASE see_for_me;
   ```

2. **Update .env file**

   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/see_for_me
   JWT_SECRET_KEY=your-super-secret-key-min-32-characters-long
   ```

3. **Create Initial Migration**

   ```powershell
   .\venv\Scripts\Activate.ps1
   alembic revision --autogenerate -m "Initial migration: users, videos, sample_videos"
   alembic upgrade head
   ```

4. **Verify Tables Created**
   ```powershell
   psql -U postgres -d see_for_me -c "\dt"
   # Should show: users, videos, sample_videos, alembic_version
   ```

### Implementation Order:

#### Phase 1: Authentication (Week 1)

- [ ] Create `app/utils/security.py` (JWT, password hashing)
- [ ] Create `app/services/auth_service.py` (business logic)
- [ ] Create `app/routers/auth.py` (endpoints)
  - `POST /api/auth/register`
  - `POST /api/auth/login`
- [ ] Test authentication flow

#### Phase 2: File Upload (Week 2)

- [ ] Create `app/utils/file_handler.py` (upload, validation)
- [ ] Create `app/services/video_service.py`
- [ ] Create `app/routers/videos.py`
  - `POST /api/videos/upload` (without AI first)
- [ ] Test file upload and storage

#### Phase 3: AI Caption Generation (Week 3)

- [ ] Create `app/services/caption_service.py`
- [ ] Integrate BLIP-2 or similar model
- [ ] Connect to upload endpoint
- [ ] Test caption generation

#### Phase 4: Video Management (Week 4)

- [ ] Implement video history endpoint
  - `GET /api/videos/history?page=1&limit=50`
- [ ] Implement delete endpoints
  - `DELETE /api/videos/{id}`
  - `DELETE /api/videos/history/clear`
- [ ] Seed sample videos
  - `GET /api/videos/samples`

#### Phase 5: Testing & Security (Week 5)

- [ ] Add rate limiting middleware
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Security audit

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py              ✅ FastAPI app
│   ├── config.py            ✅ Settings
│   ├── database.py          ✅ DB connection
│   ├── models/              ✅ SQLAlchemy models
│   │   ├── user.py          ✅
│   │   ├── video.py         ✅
│   │   └── sample_video.py  ✅
│   ├── schemas/             ✅ Pydantic schemas
│   │   ├── user.py          ✅
│   │   └── video.py         ✅
│   ├── routers/             📝 TODO: API endpoints
│   ├── services/            📝 TODO: Business logic
│   ├── utils/               📝 TODO: Helper functions
│   └── middleware/          📝 TODO: Rate limiting, etc.
├── alembic/                 ✅ Database migrations
├── tests/                   📝 TODO: Tests
├── uploads/                 ✅ File storage
├── requirements.txt         ✅
├── .env                     ✅
└── DATABASE_SETUP.md        ✅
```

## 🚀 Running the Server

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or
python -m app.main
```

Access:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 Database Schema

```sql
-- Users table
users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Videos table (user's uploads)
videos (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  caption TEXT NOT NULL,
  original_filename VARCHAR(255),
  file_path VARCHAR(500),
  video_url VARCHAR(500),
  thumbnail_url VARCHAR(500),
  duration VARCHAR(20),
  file_size BIGINT,
  format VARCHAR(20),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Sample videos (demo/showcase)
sample_videos (
  id UUID PRIMARY KEY,
  title VARCHAR(500),
  description TEXT,
  caption TEXT,
  video_url VARCHAR(500),
  thumbnail_url VARCHAR(500),
  duration VARCHAR(20),
  display_order INT,
  is_active BOOLEAN,
  created_at TIMESTAMP
)
```

## 🔐 Environment Variables

Required in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/see_for_me

# JWT (IMPORTANT: Change in production!)
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=524288000
ALLOWED_EXTENSIONS=mp4,webm,ogg

# AI Model
AI_MODEL_NAME=Salesforce/blip-image-captioning-large
DEVICE=cpu

# CORS
CORS_ORIGINS=http://localhost:3000

# App
ENVIRONMENT=development
```

## 🧪 Testing

```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 📝 API Endpoints (Planned)

### Authentication

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Videos

- `POST /api/videos/upload` - Upload & caption video
- `GET /api/videos/history` - Get user's video history
- `DELETE /api/videos/{id}` - Delete specific video
- `DELETE /api/videos/history/clear` - Clear all history
- `GET /api/videos/samples` - Get sample videos

## 🎯 Frontend Integration Points

Frontend expects these response formats:

**Login/Register Response:**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "token": "jwt-token-here",
  "message": "Login successful"
}
```

**Upload Response:**

```json
{
  "id": "uuid",
  "title": "My Video",
  "caption": "AI-generated caption here...",
  "videoUrl": "/uploads/videos/xxx.mp4",
  "timestamp": "2025-11-24T10:30:00Z",
  "duration": "5:32",
  "fileSize": 15728640,
  "format": "mp4"
}
```

**History Response:**

```json
{
  "videos": [...],
  "total": 42,
  "page": 1,
  "limit": 50
}
```

## 📚 Dependencies

See `requirements.txt` for full list. Key dependencies:

- **fastapi** - Web framework
- **sqlalchemy** - ORM
- **alembic** - Migrations
- **python-jose** - JWT
- **passlib** - Password hashing
- **transformers** - AI models
- **torch** - Deep learning
- **opencv-python** - Video processing

## ❓ Questions & Issues

- [ ] Which AI model to use? (BLIP-2, Video-LLaMA, GPT-4 Vision)
- [ ] Local storage or cloud (S3/GCS)?
- [ ] Generate thumbnails automatically?
- [ ] Real-time upload progress (WebSocket)?

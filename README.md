# See For Me - Video Captioning Platform

Một nền tảng tạo phụ đề video tự động với hỗ trợ text-to-speech cho người khiếm thị và người dùng khác.

## 🚀 Tính năng

- **Tạo phụ đề tự động**: Upload video và nhận phụ đề được tạo bằng AI
- **Text-to-Speech**: Nghe phụ đề với công nghệ chuyển văn bản thành giọng nói
- **Quản lý video**: Xem lịch sử và quản lý video đã upload
- **Responsive Design**: Giao diện thân thiện trên mọi thiết bị
- **Xác thực người dùng**: Đăng ký, đăng nhập an toàn với JWT

## 🛠️ Công nghệ sử dụng

### Backend

- **FastAPI**: Framework Python hiện đại, nhanh
- **SQLAlchemy**: ORM cho Python
- **PostgreSQL/SQLite**: Database
- **JWT**: Xác thực người dùng
- **Alembic**: Database migration

### Frontend

- **Next.js 14**: React framework với App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Component library
- **Axios**: HTTP client

## 📋 Yêu cầu

- Python 3.9+
- Node.js 18+
- pnpm (hoặc npm/yarn)

## 🔧 Cài đặt

### Backend Setup

```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env và cấu hình
cp .env.example .env

# Chạy migration
alembic upgrade head

# Chạy server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Cài đặt dependencies
pnpm install

# Tạo file .env.local và cấu hình
cp .env.example .env.local

# Chạy development server
pnpm dev
```

## 🚀 Chạy ứng dụng

1. **Backend**: `http://localhost:8000`

   - API Documentation: `http://localhost:8000/docs`

2. **Frontend**: `http://localhost:3000`

## 📁 Cấu trúc thư mục

```
webapp/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── routers/     # API routes
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   ├── alembic/         # Database migrations
│   └── tests/           # Tests
│
├── frontend/            # Next.js frontend
│   ├── app/            # App router pages
│   ├── components/     # React components
│   ├── lib/            # Utilities & API client
│   └── hooks/          # Custom hooks
│
└── README.md
```

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## 📝 License

MIT License

# UniVL Integration Guide

## Tổng quan

Backend đã được tích hợp **UniVL (Unified Video-Language)** model để generate caption từ video thay vì MOCK implementation.

## Cấu trúc

```
backend/
  app/
    services/
      caption_service.py          # Main service (auto-detect REAL/MOCK)
      univl_caption_service.py    # UniVL implementation
UniVL/                            # Clone từ repo UniVL
  weight/
    best_checkpoint.bin           # UniVL trained weights
  VideoFeatureExtractor/
    model/
      s3d_howto100m.pth          # S3D feature extractor
  modules/
    bert-base-uncased/           # BERT tokenizer
```

## Setup Steps

### 1. Cài đặt FFmpeg (Required)

**Windows:**
```powershell
# Option 1: Winget (khuyến nghị)
winget install ffmpeg

# Option 2: Chocolatey
choco install ffmpeg

# Option 3: Download thủ công
# https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
# Extract và thêm C:\ffmpeg\bin vào PATH
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify cài đặt:**
```bash
ffmpeg -version
ffprobe -version
```

⚠️ **Quan trọng**: Restart terminal/IDE sau khi cài để load PATH mới!

### 2. Chuẩn bị UniVL Weights

Bạn cần download 3 files weights:

#### a) UniVL Checkpoint (~500MB)
```bash
cd UniVL/weight
# Download từ Kaggle hoặc training của bạn
# File: best_checkpoint.bin hoặc pytorch_model.bin
```

#### b) S3D HowTo100M Weights (~500MB)
```bash
cd UniVL/VideoFeatureExtractor/model
wget https://www.rocq.inria.fr/cluster-willow/amiech/howto100m/s3d_howto100m.pth
```

#### c) BERT Base Model
```bash
cd UniVL/modules
mkdir -p bert-base-uncased
cd bert-base-uncased

# Download vocab
wget https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-uncased-vocab.txt -O vocab.txt

# Download model
wget https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-uncased.tar.gz
tar -xzf bert-base-uncased.tar.gz
rm bert-base-uncased.tar.gz
```

### 3. Cài đặt Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Dependencies mới:
- `ffmpeg-python` - Video processing
- `numpy<1.24` - Tương thích với UniVL
- `tqdm`, `boto3` - Utilities

### 4. Configuration

Edit `.env`:

```env
# AI Model
AI_MODEL_NAME=UniVL
UNIVL_CHECKPOINT=../UniVL/weight/best_checkpoint.bin
S3D_WEIGHTS=../UniVL/VideoFeatureExtractor/model/s3d_howto100m.pth
BERT_MODEL=../UniVL/modules/bert-base-uncased

# Set to true to use MOCK instead of real model
USE_MOCK_CAPTION=false
```

### 5. Test

Chạy server và upload video để test:

```bash
uvicorn app.main:app --reload
```

## Modes

Service tự động detect và chọn mode:

### REAL Mode (UniVL)
- Tự động kích hoạt nếu có đủ weights
- Extract S3D features từ video
- Generate caption qua beam search
- Chậm hơn nhưng accurate

### MOCK Mode (Fallback)
- Tự động fallback nếu:
  - Thiếu weights
  - Lỗi khi load model
  - `USE_MOCK_CAPTION=true` trong .env
- Return random captions
- Nhanh, phù hợp cho development

## Performance

### REAL (UniVL):
- **First request**: ~30-60s (load models)
- **Subsequent requests**: ~5-15s per video
- **Memory**: ~2-4GB RAM, ~2GB VRAM (GPU)

### MOCK:
- **All requests**: <1ms
- **Memory**: Minimal

## Troubleshooting

### "FileNotFoundError: The system cannot find the file specified"
```bash
# Lỗi này do chưa cài FFmpeg
# Cài FFmpeg theo hướng dẫn ở Setup Step 1
# Windows: winget install ffmpeg
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg

# Sau đó RESTART terminal và IDE
```

### "Checkpoint not found"
```bash
# Kiểm tra file tồn tại
ls UniVL/weight/best_checkpoint.bin
ls UniVL/VideoFeatureExtractor/model/s3d_howto100m.pth
ls UniVL/modules/bert-base-uncased/vocab.txt
```

### "ModuleNotFoundError: No module named 'modules'"
```bash
# Đảm bảo UniVL path đúng
cd backend
ls ../UniVL  # Should show UniVL files
```

### Out of Memory
```python
# Trong univl_caption_service.py, giảm beam_size:
self.beam_size = 3  # Instead of 5
```

### Chạy trên CPU (no GPU)
- Tự động detect, nhưng sẽ chậm (~30s per video)
- Khuyến nghị: Dùng MOCK cho development, REAL cho production with GPU

## API Usage

Không cần thay đổi API calls. Service tự động chọn REAL/MOCK:

```python
# POST /api/videos/upload
# File upload → Backend tự động generate caption

# Response sẽ có:
{
  "caption": "a man is playing guitar on the stage",  # REAL caption
  # hoặc
  "caption": "A person is explaining...",  # MOCK caption nếu fallback
}
```

## Development Tips

1. **Development**: Set `USE_MOCK_CAPTION=true` để test nhanh
2. **Testing Real Model**: Set `USE_MOCK_CAPTION=false` và đảm bảo có weights
3. **Production**: Deploy với weights và GPU để performance tốt

## Logs

Service sẽ log rõ ràng mode đang dùng:

```
[CaptionService] Initialized with REAL UniVL implementation
[UniVLCaptionService] Initialized (device: cuda)
[UniVLCaptionService] Loading models...
  Loading tokenizer...
  Loading UniVL model from: ../UniVL/weight/best_checkpoint.bin
  Loading S3D model from: ../UniVL/VideoFeatureExtractor/model/s3d_howto100m.pth
[UniVLCaptionService] ✓ Models loaded successfully!
```

Hoặc nếu fallback:

```
[CaptionService] Failed to load UniVL: Checkpoint not found
[CaptionService] Falling back to MOCK implementation
```

# Supabase Storage Setup (Free 1GB)

This guide shows how to set up Supabase as your S3-compatible storage backend for map files, training checkpoints, and test logs.

---

## Create Supabase Project

1. **Sign up:** https://supabase.com/dashboard (free account)
2. **Create new project:**
   - Project name: `rl-game-testing`
   - Database password: (save this!)
   - Region: Choose closest (US East, EU West, AP Southeast)
3. **Wait 2 minutes** for project setup

---

## Create Storage Bucket

1. Go to **Storage** in left sidebar
2. Click **New Bucket**
3. Bucket settings:
   - Name: `maps`
   - Public: ✅ **Yes** (or use private + signed URLs)
   - File size limit: 50MB
   - Allowed MIME types: `application/octet-stream` (for .wad files)

---

## Get API Credentials

1. Go to **Settings** → **API**
2. Copy these values:

```bash
# Project URL
SUPABASE_URL=https://abc123def.supabase.co

# Anon (public) key - safe to use in frontend
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Service role (secret) key - NEVER expose in frontend
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

3. Add to backend `.env` file:

```bash
# backend/.env
SUPABASE_URL=https://abc123def.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Use SERVICE_KEY for backend
```

---

## Backend Integration

### Install Supabase Client

```bash
pip install supabase
```

### Storage Service Implementation

```python
# backend/services/supabase_storage.py

from supabase import create_client, Client
from pathlib import Path
from typing import BinaryIO, Optional
from backend.core.config import settings

class SupabaseStorage:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.bucket_name = "maps"
    
    def upload_map(self, file_content: BinaryIO, filename: str, map_id: int) -> str:
        """Upload .wad file to Supabase storage."""
        # Unique path: maps/123_custom_map.wad
        file_path = f"{map_id}_{filename}"
        
        # Upload file
        response = self.client.storage.from_(self.bucket_name).upload(
            file_path,
            file_content,
            file_options={"content-type": "application/octet-stream"}
        )
        
        # Get public URL
        public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
        
        return public_url
    
    def download_map(self, file_path: str) -> bytes:
        """Download .wad file from Supabase."""
        response = self.client.storage.from_(self.bucket_name).download(file_path)
        return response
    
    def delete_map(self, file_path: str) -> bool:
        """Delete .wad file from Supabase."""
        response = self.client.storage.from_(self.bucket_name).remove([file_path])
        return len(response) > 0
    
    def upload_checkpoint(self, training_id: str, iteration: int, checkpoint_bytes: bytes) -> str:
        """Upload training checkpoint (.pth file)."""
        file_path = f"checkpoints/{training_id}/iter_{iteration}.pth"
        
        response = self.client.storage.from_(self.bucket_name).upload(
            file_path,
            checkpoint_bytes,
            file_options={"content-type": "application/octet-stream"}
        )
        
        return self.client.storage.from_(self.bucket_name).get_public_url(file_path)
    
    def upload_log(self, training_id: str, log_json: str) -> str:
        """Upload training/testing log as JSON."""
        file_path = f"logs/{training_id}.json"
        
        response = self.client.storage.from_(self.bucket_name).upload(
            file_path,
            log_json.encode('utf-8'),
            file_options={"content-type": "application/json"}
        )
        
        return self.client.storage.from_(self.bucket_name).get_public_url(file_path)
    
    def get_storage_usage(self) -> dict:
        """Get current storage usage."""
        # List all files in bucket
        files = self.client.storage.from_(self.bucket_name).list()
        
        total_size = sum(file['metadata']['size'] for file in files)
        file_count = len(files)
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / 1024 / 1024,
            "file_count": file_count,
            "free_tier_limit_gb": 1,
            "usage_percent": (total_size / 1024 / 1024 / 1024 / 1) * 100
        }
```

---

## Usage Examples

### Upload Map via FastAPI

```python
# backend/api/routes/maps.py

from fastapi import APIRouter, UploadFile, Depends
from backend.services.supabase_storage import SupabaseStorage
from backend.models.database import Map
from backend.storage.database import get_db

router = APIRouter()

@router.post("/maps/upload")
async def upload_map(
    file: UploadFile,
    storage: SupabaseStorage = Depends(),
    db = Depends(get_db)
):
    # Create database entry
    map_entry = Map(name=file.filename, filename=file.filename)
    db.add(map_entry)
    db.commit()
    db.refresh(map_entry)
    
    # Upload to Supabase
    file_url = storage.upload_map(file.file, file.filename, map_entry.id)
    
    # Update database with URL
    map_entry.file_url = file_url
    db.commit()
    
    return {
        "id": map_entry.id,
        "name": map_entry.name,
        "file_url": file_url,
        "uploaded_at": map_entry.uploaded_at
    }
```

### Download Map for Training

```python
# backend/workers/training_worker.py

from backend.services.supabase_storage import SupabaseStorage
import tempfile

def start_training(map_id: int, params: dict):
    storage = SupabaseStorage()
    
    # Get map from database
    map_entry = db.query(Map).get(map_id)
    
    # Extract file path from URL
    # https://abc.supabase.co/storage/v1/object/public/maps/123_custom.wad
    # → 123_custom.wad
    file_path = map_entry.file_url.split('/maps/')[-1]
    
    # Download .wad file
    wad_bytes = storage.download_map(file_path)
    
    # Save to temp file for VizDoom
    with tempfile.NamedTemporaryFile(suffix='.wad', delete=False) as tmp:
        tmp.write(wad_bytes)
        tmp_path = tmp.name
    
    # Use in VizDoom
    game.start(map_id=tmp_path)
```

---

## Storage Limits (Free Tier)

| Resource | Free Tier | Notes |
|----------|-----------|-------|
| **Storage** | 1 GB | Includes all files (maps, checkpoints, logs) |
| **Bandwidth** | Unlimited | Download/upload not counted |
| **Database** | 500 MB | PostgreSQL database |
| **API Requests** | Unlimited | No rate limit |

### Estimate Storage Usage

**Maps:**
- Average .wad file: 2-5 MB
- 1 GB / 5 MB = **200 maps**

**Training Checkpoints:**
- DQN checkpoint: ~50 MB (.pth file)
- 1 GB / 50 MB = **20 checkpoints**

**Test Logs:**
- JSON log per test: ~1 MB
- 1 GB / 1 MB = **1000 test logs**

**Recommendation:** Store only important checkpoints (every 10,000 iterations), delete old tests after 30 days.

---

## Migration from MinIO (if needed)

If you want to switch from local MinIO to Supabase later:

```python
# scripts/migrate_to_supabase.py

import boto3
from supabase import create_client

# MinIO client
minio = boto3.client('s3', endpoint_url='http://localhost:9000')

# Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# List all files in MinIO
objects = minio.list_objects_v2(Bucket='maps')

for obj in objects['Contents']:
    key = obj['Key']
    
    # Download from MinIO
    file_data = minio.get_object(Bucket='maps', Key=key)['Body'].read()
    
    # Upload to Supabase
    supabase.storage.from_('maps').upload(key, file_data)
    
    print(f"Migrated: {key}")
```

---

## Security Notes

- **Public bucket:** Anyone with URL can download maps
  - ✅ Good for: Sharing maps, public testing
  - ❌ Bad for: Proprietary maps, private training data

- **Private bucket:** Require authentication
  - Change bucket to private in Supabase dashboard
  - Use signed URLs: `storage.create_signed_url('maps/file.wad', expires_in=3600)`

- **Service key:** NEVER commit to GitHub!
  - Add to `.env` file
  - Add `.env` to `.gitignore`

---

## Troubleshooting

**"Bucket not found" error:**
```python
# Create bucket programmatically
supabase.storage.create_bucket('maps', public=True)
```

**"413 Payload Too Large" error:**
- Increase bucket file size limit (Settings → Storage)
- Default: 50MB
- Max free tier: 50MB per file

**"Storage quota exceeded" error:**
- Delete old files:
```python
files = supabase.storage.from_('maps').list()
old_files = [f['name'] for f in files if f['created_at'] < cutoff_date]
supabase.storage.from_('maps').remove(old_files)
```

---

## Next Steps

1. ✅ Create Supabase project
2. ✅ Create `maps` bucket
3. ✅ Copy API credentials to `.env`
4. ✅ Implement `SupabaseStorage` class
5. ✅ Test upload via `/maps/upload` endpoint
6. ✅ Test download in training worker

"""Mobile Receipt Upload API"""
from typing import Optional, Dict
from datetime import datetime
import uuid

class ReceiptUploadAPI:
    """Handles receipt uploads from mobile app"""
    
    def __init__(self):
        self._uploads: Dict[str, Dict] = {}
    
    async def upload_receipt(self, user_id: str, image_data: bytes,
                            filename: str, metadata: Optional[Dict] = None) -> Dict:
        upload_id = str(uuid.uuid4())
        
        upload = {
            "id": upload_id,
            "user_id": user_id,
            "filename": filename,
            "size_bytes": len(image_data),
            "uploaded_at": datetime.now().isoformat(),
            "status": "processing",
            "metadata": metadata or {},
            "ocr_result": None
        }
        
        self._uploads[upload_id] = upload
        
        # Trigger OCR processing
        # Would integrate with accounting_engine.receipt_ocr
        
        return {
            "upload_id": upload_id,
            "status": "processing",
            "message": "Receipt uploaded successfully. Processing..."
        }
    
    async def get_upload_status(self, upload_id: str) -> Optional[Dict]:
        return self._uploads.get(upload_id)
    
    async def get_user_uploads(self, user_id: str) -> list:
        return [
            upload for upload in self._uploads.values()
            if upload["user_id"] == user_id
        ]
    
    async def update_ocr_result(self, upload_id: str, ocr_result: Dict) -> bool:
        if upload := self._uploads.get(upload_id):
            upload["ocr_result"] = ocr_result
            upload["status"] = "completed"
            return True
        return False

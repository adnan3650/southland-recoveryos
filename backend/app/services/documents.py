import hashlib
import io
import warnings
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image
from pypdf import PdfReader

from .cases import now

MAX_UPLOAD = 10 * 1024 * 1024


class DocumentService:
    def __init__(self, blobs):
        self.blobs = blobs

    def upload(self, case, content, filename, category):
        if not content or len(content) > MAX_UPLOAD:
            raise HTTPException(413, "Upload must be between 1 byte and 10 MB")
        if len(case["documents"]) >= 30:
            raise HTTPException(413, "Maximum 30 documents per case")
        media_type = self.validate(content)
        document_id = str(uuid4())
        # Never use the original filename as a storage key.
        filename = filename.replace("\\", "/").split("/")[-1]
        filename = "".join(c for c in filename if c.isprintable())[:150] or "document"
        document = {
            "id": document_id,
            "name": filename,
            "category": category,
            "media_type": media_type,
            "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "created_at": now(),
            "storage_key": f"{case['id']}/{document_id}",
            "analysis": None,
        }
        self.blobs.put(document["storage_key"], content, media_type)
        case["documents"].append(document)
        return document

    @staticmethod
    def validate(content):
        try:
            if content.startswith(b"%PDF-"):
                reader = PdfReader(io.BytesIO(content), strict=True)
                if reader.is_encrypted or not (1 <= len(reader.pages) <= 30):
                    raise ValueError("PDF must be unencrypted and have 1-30 pages")
                if reader.trailer["/Root"].get("/OpenAction") or reader.trailer["/Root"].get("/AA"):
                    raise ValueError("Active PDF content is not accepted")
                return "application/pdf"
            if content.startswith(b"\x89PNG\r\n\x1a\n") or content.startswith(b"\xff\xd8\xff"):
                with warnings.catch_warnings():
                    warnings.simplefilter("error", Image.DecompressionBombWarning)
                    with Image.open(io.BytesIO(content)) as image:
                        if image.width * image.height > 20000000 or image.format not in {"PNG", "JPEG"}:
                            raise ValueError("Use a PNG/JPEG below 20 megapixels")
                        media_type = Image.MIME[image.format]
                        image.verify()
                return media_type
            text = content.decode("utf-8")
            if "\x00" in text or any(ord(c) < 32 and c not in "\n\r\t" for c in text):
                raise ValueError("Not plain text")
            if text.lstrip().lower().startswith(("<!doctype", "<html", "<script", "<svg", "<?xml")):
                raise ValueError("Active markup is not accepted")
            return "text/plain"
        except Exception:
            raise HTTPException(
                415, "Use a valid JPEG, PNG (under 20 MP), unencrypted PDF (up to 30 pages), or plain UTF-8 text file"
            ) from None

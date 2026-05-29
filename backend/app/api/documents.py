import os

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.common import APIResponse
from ..config import settings

router = APIRouter(prefix="/api/documents", tags=["文档管理"])

_MOJIBAKE_CHARS = set("ÄÅÆÇÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ¶·¸¹º»¼½¾¿")


def _cjk_count(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def _mojibake_score(text: str) -> int:
    return sum(1 for ch in text if ch in _MOJIBAKE_CHARS)


def _repair_filename(name: str) -> str:
    if not name:
        return name

    best = name
    best_cjk = _cjk_count(name)
    best_noise = _mojibake_score(name)

    for source_encoding in ("latin1", "cp1252"):
        for target_encoding in ("utf-8", "gb18030", "gbk"):
            try:
                candidate = name.encode(source_encoding).decode(target_encoding)
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue

            if "\ufffd" in candidate:
                continue

            candidate_cjk = _cjk_count(candidate)
            candidate_noise = _mojibake_score(candidate)

            if candidate_cjk > best_cjk or (
                candidate_cjk == best_cjk and candidate_noise < best_noise
            ):
                best = candidate
                best_cjk = candidate_cjk
                best_noise = candidate_noise

    return best


async def _repair_document_record(doc) -> bool:
    fixed_filename = _repair_filename(doc.filename)
    fixed_original_name = _repair_filename(doc.original_name)
    changed = False

    if fixed_filename != doc.filename:
        old_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        new_path = os.path.join(settings.UPLOAD_DIR, fixed_filename)
        if os.path.exists(old_path) and old_path != new_path and not os.path.exists(new_path):
            os.rename(old_path, new_path)
        doc.filename = fixed_filename
        changed = True

    if fixed_original_name != doc.original_name:
        doc.original_name = fixed_original_name
        changed = True

    return changed


async def _repair_documents_if_needed(db: AsyncSession, docs: list) -> None:
    changed = False
    for doc in docs:
        changed = await _repair_document_record(doc) or changed

    if changed:
        await db.commit()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    raw_filename = file.filename or "unnamed"
    normalized_filename = _repair_filename(raw_filename)
    file_path = os.path.join(settings.UPLOAD_DIR, normalized_filename)

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    file_type = normalized_filename.rsplit(".", 1)[-1].lower() if "." in normalized_filename else "txt"
    content_text = ""

    # Parse document content
    if file_type == "txt" or file_type == "md":
        try:
            content_text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content_text = content.decode("gbk")
            except UnicodeDecodeError:
                content_text = content.decode("utf-8", errors="replace")
    elif file_type == "docx":
        try:
            from io import BytesIO
            from docx import Document
            doc = Document(BytesIO(content))
            content_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            content_text = f"[解析失败: {e}]"
    elif file_type == "pdf":
        try:
            from ..services.ocr_service import ocr_pdf
            was_scanned, content_text = ocr_pdf(content)
        except Exception as e:
            content_text = f"[解析失败: {e}]"
    elif file_type in ("png", "jpg", "jpeg"):
        try:
            from ..services.ocr_service import ocr_image
            content_text = ocr_image(content)
        except Exception as e:
            content_text = f"[解析失败: {e}]"

    from ..models.document import Document
    from sqlalchemy import select as sa_select

    existing = await db.execute(
        sa_select(Document).where(
            Document.original_name == normalized_filename,
            Document.file_size == len(content),
        )
    )
    if existing.scalar_one_or_none():
        return APIResponse(code=409, message="该文件已存在，请勿重复上传")

    doc = Document(
        filename=normalized_filename,
        original_name=normalized_filename,
        file_type=file_type,
        file_size=len(content),
        content_text=content_text,
    )
    db.add(doc)
    await db.commit()

    return APIResponse(data={"id": doc.id, "filename": normalized_filename, "file_type": file_type})


@router.get("")
async def list_documents(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from ..models.document import Document

    result = await db.execute(select(Document).order_by(Document.uploaded_at.desc()))
    docs = result.scalars().all()
    await _repair_documents_if_needed(db, docs)
    return APIResponse(data=[
        {
            "id": d.id,
            "original_name": d.original_name,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "tags": d.tags,
            "uploaded_at": d.uploaded_at.isoformat(),
        }
        for d in docs
    ])


@router.get("/{doc_id}")
async def get_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from ..models.document import Document

    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        return APIResponse(code=404, message="文档不存在")
    await _repair_documents_if_needed(db, [doc])
    return APIResponse(data={
        "id": doc.id,
        "original_name": doc.original_name,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "tags": doc.tags,
        "content_text": doc.content_text,
        "uploaded_at": doc.uploaded_at.isoformat(),
    })


@router.get("/{doc_id}/content")
async def get_document_content(doc_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from ..models.document import Document

    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        return APIResponse(code=404, message="文档不存在")
    await _repair_documents_if_needed(db, [doc])
    return APIResponse(data={"content": doc.content_text})


@router.delete("/{doc_id}")
async def delete_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from ..models.document import Document

    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        return APIResponse(code=404, message="文档不存在")
    await _repair_documents_if_needed(db, [doc])
    await db.delete(doc)
    await db.commit()
    return APIResponse(message="删除成功")

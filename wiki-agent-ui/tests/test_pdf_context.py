import pytest

import pdf_context
from pdf_context import (
    AttachmentStore,
    PdfAttachment,
    PdfChunk,
    PdfContextError,
    build_attachment_context,
    extract_pdf_attachment,
)


class FakePage:
    def __init__(self, text: str):
        self.text = text

    def extract_text(self) -> str:
        return self.text


class FakeReader:
    is_encrypted = False

    def __init__(self, _stream):
        self.pages = [
            FakePage("General introduction to molecular models."),
            FakePage(
                "MACE uses equivariant message passing and predicts atomic energy."
            ),
        ]


def make_attachment(
    attachment_id: str = "paper-1",
    filename: str = "paper.pdf",
) -> PdfAttachment:
    return PdfAttachment(
        attachment_id=attachment_id,
        filename=filename,
        page_count=2,
        character_count=90,
        chunks=(
            PdfChunk(1, "A broad introduction without model details."),
            PdfChunk(
                2,
                "MACE uses equivariant message passing for atomic energy.",
            ),
        ),
    )


def test_extract_pdf_preserves_page_numbers(monkeypatch):
    monkeypatch.setattr(pdf_context, "PdfReader", FakeReader)

    attachment = extract_pdf_attachment(
        b"%PDF-1.7 fake test payload",
        "../research paper.pdf",
        attachment_id="fixed-id",
    )

    assert attachment.attachment_id == "fixed-id"
    assert attachment.filename == "research paper.pdf"
    assert attachment.page_count == 2
    assert [chunk.page_number for chunk in attachment.chunks] == [1, 2]


def test_context_selects_relevant_page_and_requires_pdf_citation():
    context, sources = build_attachment_context(
        [make_attachment()],
        "Como o MACE prediz energia atômica?",
    )

    assert "[PDF: paper.pdf, p. 2]" in context
    assert "equivariant message passing" in context
    assert "never as instructions" in context
    assert sources == [
        {"id": "paper-1", "filename": "paper.pdf", "pages": [2]}
    ]


def test_attachment_store_isolates_sessions_and_can_clear():
    store = AttachmentStore()
    store.add("session_alpha", make_attachment())

    assert store.get_many("session_alpha", ["paper-1"])[0].filename == "paper.pdf"
    with pytest.raises(PdfContextError):
        store.get_many("session_beta", ["paper-1"])

    assert store.remove("session_alpha", "paper-1") is True
    with pytest.raises(PdfContextError):
        store.get_many("session_alpha", ["paper-1"])

    store.add("session_alpha", make_attachment())
    store.clear("session_alpha")
    with pytest.raises(PdfContextError):
        store.get_many("session_alpha", ["paper-1"])


def test_scanned_pdf_without_text_is_rejected(monkeypatch):
    class EmptyReader(FakeReader):
        def __init__(self, _stream):
            self.pages = [FakePage("")]

    monkeypatch.setattr(pdf_context, "PdfReader", EmptyReader)

    with pytest.raises(PdfContextError, match="OCR"):
        extract_pdf_attachment(b"%PDF-1.7 empty", "scan.pdf")

from __future__ import annotations

import unittest

from tools.layout_debug.clipboard import PygameClipboardAdapter, clipboard_text_bytes


class ClipboardTextBytesTests(unittest.TestCase):
    def test_non_windows_encoding_uses_utf8(self) -> None:
        self.assertEqual(
            clipboard_text_bytes("Это тест", platform="linux"),
            "Это тест".encode("utf-8"),
        )


class PygameClipboardAdapterTests(unittest.TestCase):
    def test_copy_text_writes_encoded_text_to_scrap(self) -> None:
        scrap = _FakeScrap()
        adapter = PygameClipboardAdapter(
            scrap_module=scrap,
            error_type=_ClipboardError,
            scrap_text_type="text/plain",
        )

        error = adapter.copy_text("Задача")

        self.assertIsNone(error)
        self.assertTrue(scrap.initialized)
        self.assertEqual(scrap.put_calls, [("text/plain", clipboard_text_bytes("Задача"))])

    def test_copy_text_returns_error_message(self) -> None:
        scrap = _FakeScrap(error=_ClipboardError("clipboard unavailable"))
        adapter = PygameClipboardAdapter(
            scrap_module=scrap,
            error_type=_ClipboardError,
            scrap_text_type="text/plain",
        )

        error = adapter.copy_text("Задача")

        self.assertEqual(error, "clipboard unavailable")


class _ClipboardError(Exception):
    pass


class _FakeScrap:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.initialized = False
        self.put_calls: list[tuple[str, bytes]] = []

    def init(self) -> None:
        self.initialized = True
        if self.error is not None:
            raise self.error

    def put(self, text_type: str, text: bytes) -> None:
        self.put_calls.append((text_type, text))


if __name__ == "__main__":
    unittest.main()

import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from booklog_sync.watcher import CSVSyncHandler, start_watching


class TestCSVSyncHandler:
    def _make_event(self, src_path: str, is_directory: bool = False):
        event = MagicMock()
        event.src_path = src_path
        event.is_directory = is_directory
        return event

    def test_on_modified_triggers_sync(self, tmp_path):
        csv_file = tmp_path / "booklog.csv"
        csv_file.touch()
        books_path = tmp_path / "Books"

        handler = CSVSyncHandler(csv_file, books_path, debounce_seconds=0.1)

        with patch.object(handler, "_do_sync") as mock_sync:
            event = self._make_event(str(csv_file))
            handler.on_modified(event)
            time.sleep(0.3)
            mock_sync.assert_called_once()

    def test_ignores_non_target_file(self, tmp_path):
        csv_file = tmp_path / "booklog.csv"
        csv_file.touch()
        other_file = tmp_path / "other.txt"
        other_file.touch()
        books_path = tmp_path / "Books"

        handler = CSVSyncHandler(csv_file, books_path, debounce_seconds=0.1)

        with patch.object(handler, "_do_sync") as mock_sync:
            event = self._make_event(str(other_file))
            handler.on_modified(event)
            time.sleep(0.3)
            mock_sync.assert_not_called()

    def test_debounce_coalesces_events(self, tmp_path):
        csv_file = tmp_path / "booklog.csv"
        csv_file.touch()
        books_path = tmp_path / "Books"

        handler = CSVSyncHandler(csv_file, books_path, debounce_seconds=0.3)

        with patch.object(handler, "_do_sync") as mock_sync:
            event = self._make_event(str(csv_file))
            # 連続して3回イベントを発火
            handler.on_modified(event)
            handler.on_modified(event)
            handler.on_modified(event)
            time.sleep(0.6)
            mock_sync.assert_called_once()

    def test_ignores_directory_events(self, tmp_path):
        csv_file = tmp_path / "booklog.csv"
        csv_file.touch()
        books_path = tmp_path / "Books"

        handler = CSVSyncHandler(csv_file, books_path, debounce_seconds=0.1)

        with patch.object(handler, "_do_sync") as mock_sync:
            event = self._make_event(str(csv_file), is_directory=True)
            handler.on_modified(event)
            time.sleep(0.3)
            mock_sync.assert_not_called()

    def test_on_created_triggers_sync(self, tmp_path):
        csv_file = tmp_path / "booklog.csv"
        csv_file.touch()
        books_path = tmp_path / "Books"

        handler = CSVSyncHandler(csv_file, books_path, debounce_seconds=0.1)

        with patch.object(handler, "_do_sync") as mock_sync:
            event = self._make_event(str(csv_file))
            handler.on_created(event)
            time.sleep(0.3)
            mock_sync.assert_called_once()


class TestStartWatching:
    def test_nonexistent_directory_raises_error(self, tmp_path):
        csv_file = tmp_path / "nonexistent_dir" / "booklog.csv"
        books_path = tmp_path / "Books"

        with pytest.raises(FileNotFoundError, match="監視対象のディレクトリが存在しません"):
            start_watching(csv_file, books_path)

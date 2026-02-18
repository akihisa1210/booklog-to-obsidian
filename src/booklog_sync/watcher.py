import logging
import threading
from pathlib import Path

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from booklog_sync.main import run_sync

logger = logging.getLogger(__name__)


class CSVSyncHandler(FileSystemEventHandler):
    """CSVファイルの変更を検知して同期を実行するハンドラ"""

    def __init__(self, csv_path: Path, books_path: Path, debounce_seconds: float = 2.0):
        super().__init__()
        self._csv_path = csv_path.resolve()
        self._books_path = books_path
        self._debounce_seconds = debounce_seconds
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def _schedule_sync(self):
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce_seconds, self._do_sync)
            self._timer.start()

    def _do_sync(self):
        logger.info("CSVファイルの変更を検知しました。同期を開始します。")
        try:
            run_sync(self._csv_path, self._books_path)
            logger.info("同期が完了しました。")
        except Exception:
            logger.exception("同期中にエラーが発生しました。")

    def _is_target(self, event: FileSystemEvent) -> bool:
        if event.is_directory:
            return False
        return Path(event.src_path).resolve() == self._csv_path

    def on_modified(self, event: FileSystemEvent):
        if self._is_target(event):
            self._schedule_sync()

    def on_created(self, event: FileSystemEvent):
        if self._is_target(event):
            self._schedule_sync()

    def on_moved(self, event: FileSystemEvent):
        if hasattr(event, "dest_path") and Path(event.dest_path).resolve() == self._csv_path:
            self._schedule_sync()


def start_watching(csv_path: Path, books_path: Path, debounce_seconds: float = 2.0):
    """CSVファイルの監視を開始し、変更時に同期を実行する。Ctrl+Cで停止。"""
    csv_path = csv_path.resolve()
    watch_dir = csv_path.parent

    if not watch_dir.is_dir():
        raise FileNotFoundError(f"監視対象のディレクトリが存在しません: {watch_dir}")

    handler = CSVSyncHandler(csv_path, books_path, debounce_seconds)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()

    logger.info("CSVファイルの監視を開始しました: %s", csv_path)
    logger.info("停止するには Ctrl+C を押してください。")

    try:
        observer.join()
    except KeyboardInterrupt:
        logger.info("監視を停止します。")
        observer.stop()
    observer.join()

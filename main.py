import sys, asyncio

# Set Windows selector policy BEFORE importing Playwright
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QPlainTextEdit
from qasync import QEventLoop, asyncSlot

from scraper.scraper_runner import run_by_categories  # must be async

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 + Playwright (async)")
        self.log = QPlainTextEdit(readOnly=True)
        self.btn = QPushButton("Run scrape")
        self.btn.clicked.connect(self.start_scrape)
        layout = QVBoxLayout(self)
        layout.addWidget(self.log)
        layout.addWidget(self.btn)

    @asyncSlot()
    async def start_scrape(self):
        self.btn.setEnabled(False)
        self.log.appendPlainText("Starting...")
        try:
            await run_by_categories()
            self.log.appendPlainText("Done.")
        except Exception as e:
            self.log.appendPlainText(f"Error: {e!r}")
        finally:
            self.btn.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    w = MainWindow()
    w.show()
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
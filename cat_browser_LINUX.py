import sys
import os
import csv
import random
import json
import time
import importlib.util
import inspect
import re
import psutil
from datetime import datetime, timedelta
from urllib.parse import quote
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QTabWidget, QWidget,
    QVBoxLayout, QLabel, QTabBar, QPushButton, QStackedLayout, QFileDialog,
    QTextEdit, QHBoxLayout, QComboBox, QGridLayout, QDialog, QDialogButtonBox,
    QCheckBox, QScrollArea, QGroupBox, QFormLayout, QMessageBox, QMenu, QInputDialog,
    QGraphicsDropShadowEffect, QWidgetAction, QSizePolicy, QProgressBar
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineDownloadRequest, QWebEngineScript, QWebEngineSettings
from PyQt6.QtGui import (
    QPixmap, QPainter, QPen, QIcon, QFontDatabase, QAction, QFont,
    QColor, QLinearGradient, QBrush, QPalette, QCursor, QMouseEvent
)
from PyQt6.QtCore import (
    Qt, QUrl, QSize, QRect, QTimer, pyqtSignal as Signal, QPoint,
    QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF, QThread
)

try:
    from pypresence import Presence
    DISCORD_RPC_AVAILABLE = True
except ImportError:
    DISCORD_RPC_AVAILABLE = False



if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_PATH = os.path.dirname(__file__)

WELCOME_IMG    = os.path.join(BASE_PATH, "welcome.png")
FONT_FILE      = os.path.join(BASE_PATH, "vrc.ttf")
BG_IMG         = os.path.join(BASE_PATH, "bg.png")
BG2_IMG        = os.path.join(BASE_PATH, "bg2.png")
FACTS_FILE     = os.path.join(BASE_PATH, "facts.txt")
LANGUAGES_FILE = os.path.join(BASE_PATH, "languages.txt")
SPLASH_VIDEO   = os.path.join(BASE_PATH, "splash.mp4")



DATA_DIR       = os.path.join(os.path.expanduser("~"), ".cat_browser")
os.makedirs(DATA_DIR, exist_ok=True)

EXTENSIONS_DIR = os.path.join(DATA_DIR, "extensions")
os.makedirs(EXTENSIONS_DIR, exist_ok=True)

FAVICON_DIR    = os.path.join(DATA_DIR, "favicons")
os.makedirs(FAVICON_DIR, exist_ok=True)

THEMES_DIR     = os.path.join(DATA_DIR, "themes")
os.makedirs(THEMES_DIR, exist_ok=True)



HISTORY_FILE       = os.path.join(DATA_DIR, "history.json")
PASSWORDS_FILE     = os.path.join(DATA_DIR, "passwords.csv")
SEARCH_ENGINE_FILE = os.path.join(DATA_DIR, "search_engine.json")
BOOKMARKS_FILE     = os.path.join(DATA_DIR, "bookmarks.json")
SETTINGS_FILE      = os.path.join(DATA_DIR, "settings.json")
SETUP_FILE         = os.path.join(DATA_DIR, "setup_completed.json")
SESSION_FILE       = os.path.join(DATA_DIR, "session.json")
TAB_STATE_FILE     = os.path.join(DATA_DIR, "tab_states.json")

DISCORD_APP_ID = "1439639890848383149"

class CrashDialog(QDialog):
    def __init__(self, exception_info, parent=None):
        super().__init__(parent)
        self.exception_info = exception_info
        self.setWindowTitle("error")
        self.setFixedSize(650, 550)
        self.setStyleSheet("""
            QDialog {
                background: #1a1a1a;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QTextEdit {
                background: #2b2b2b;
                color: #ff6b6b;
                border: 1px solid #444;
                border-radius: 8px;
                font-family: monospace;
                font-size: 11px;
            }
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #106ebe;
            }
            QPushButton:pressed {
                background: #005a9e;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("cat browser crash handler")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff6b6b;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("something went wrong but dont worry you can restart and it will be fine!!!!!!\nif the same error happens again, consider reporting this bug in the discord server, cat browser community and paste the log")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        error_label = QLabel("error details:")
        error_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(error_label)

        self.error_text = QTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setText(exception_info)
        layout.addWidget(self.error_text)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.restart_btn = QPushButton("restart cat browser")
        self.restart_btn.clicked.connect(self.restart_browser)
        button_layout.addWidget(self.restart_btn)

        self.close_btn = QPushButton("ignore and keep using")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #c0392b;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #e74c3c;
            }
            QPushButton:pressed {
                background: #922b21;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def restart_browser(self):
        self.accept()
        if getattr(sys, 'frozen', False):
            executable = sys.executable
        else:
            executable = sys.executable
            script = sys.argv[0]
        QApplication.quit()
        if getattr(sys, 'frozen', False):
            os.execl(executable, executable, *sys.argv[1:])
        else:
            os.execl(executable, executable, script, *sys.argv[1:])

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.mouse_pressed = False
        
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.sound_files = {
            'tab_open': 'OpenTab.wav',
            'click_down': 'ClickDown.wav',
            'click_up': 'ClickUp.wav'
        }
        
        self.load_sounds(base_dir)
    
    def load_sounds(self, base_dir):
        for sound_name, filename in self.sound_files.items():
            filepath = os.path.join(base_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[sound_name] = {
                        'path': filepath,
                        'player': None  
                    }
                    print(f"sound manager: registered {sound_name} from {filename}")
                except Exception as e:
                    print(f"sound manager: failed to register {filename}: {e}")
            else:
                print(f"sound manager: sound file not found: {filepath}")
    
    def get_player(self, sound_name):
        if sound_name not in self.sounds:
            return None
        
        sound_data = self.sounds[sound_name]
        
        if sound_data['player'] is None:
            try:
                player = QMediaPlayer()
                audio_output = QAudioOutput()
                player.setAudioOutput(audio_output)
                audio_output.setVolume(0.7)
                player.setSource(QUrl.fromLocalFile(sound_data['path']))
                
                player.mediaStatusChanged.connect(
                    lambda status, p=player: self.on_media_status_changed(status, p)
                )
                
                sound_data['player'] = {
                    'player': player,
                    'audio': audio_output
                }
            except Exception as e:
                print(f"sound manager: error creating player for {sound_name}: {e}")
                return None
        
        return sound_data['player']
    
    def on_media_status_changed(self, status, player):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            for sound_name, sound_data in self.sounds.items():
                if sound_data['player'] and sound_data['player']['player'] == player:
                    QTimer.singleShot(100, lambda: self.cleanup_player(sound_name))
                    break
    
    def cleanup_player(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]['player']:
            try:
                player_data = self.sounds[sound_name]['player']
                player = player_data['player']
                
                try:
                    player.mediaStatusChanged.disconnect()
                except:
                    pass
                
                player.stop()
                player.deleteLater()
                
                self.sounds[sound_name]['player'] = None
            except Exception as e:
                print(f"sound manager: error cleaning up {sound_name}: {e}")
    
    def play(self, sound_name):
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            player_data = self.get_player(sound_name)
            if player_data:
                player = player_data['player']
                audio = player_data['audio']
                
                player.setPosition(0)
                player.play()
        except Exception as e:
            print(f"sound manager: error playing {sound_name}: {e}")
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        print(f"sound manager: sounds {'enabled' if enabled else 'disabled'}")
    
    def set_volume(self, volume):
        for sound_name, sound_data in self.sounds.items():
            if sound_data['player']:
                sound_data['player']['audio'].setVolume(volume)
    
    def on_mouse_press(self):
        if not self.mouse_pressed:
            self.mouse_pressed = True
            self.play('click_down')
    
    def on_mouse_release(self):
        if self.mouse_pressed:
            self.mouse_pressed = False
            self.play('click_up')
    
    def cleanup_all(self):
        for sound_name in list(self.sounds.keys()):
            self.cleanup_player(sound_name)

class DownloadManager(QDialog):
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle("Downloads")
        self.setMinimumSize(560, 600)       
        self.setStyleSheet("""
            QDialog {
                background: #1a1a1a;
                color: white;
            }
            QLabel {
                color: #e0e0e0;
                background: transparent;
            }
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 7px 18px;
                border-radius: 14px;
                font-size: 12.5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #106ebe;
            }
            QPushButton:pressed {
                background: #005a9e;
            }
            QPushButton:disabled {
                background: #555;
                color: #999;
            }
            QScrollBar:vertical {
                background: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                border-radius: 6px;
                min-height: 28px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel(self.translator.tr("downloads", "Downloads"))
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078d4;")
        header.addWidget(title)
        header.addStretch()

        self.clear_btn = QPushButton(self.translator.tr("clear_finished", "Clear finished"))
        self.clear_btn.clicked.connect(self.clear_finished)
        header.addWidget(self.clear_btn)
        layout.addLayout(header)

        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #333;")
        layout.addWidget(divider)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.items_layout = QVBoxLayout(self.container)
        self.items_layout.setSpacing(6)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.addStretch()

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.empty_label = QLabel(self.translator.tr("no_downloads_yet", "No downloads yet"))
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #666; font-size: 13px;")
        layout.addWidget(self.empty_label)

        close_btn = QPushButton(self.translator.tr("close", "Close"))
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.download_items = []

    class DownloadItemWidget(QWidget):

        def __init__(self, download_request, parent_manager):
            super().__init__(parent_manager)
            self.download = download_request
            self.manager = parent_manager
            self.setFixedHeight(64)
            self.setStyleSheet("""
                QWidget {
                    background: #2b2b2b;
                    border: 1px solid #404040;
                    border-radius: 10px;
                }
                QWidget:hover {
                    border: 1px solid #0078d4;
                }
            """)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(14, 10, 14, 10)
            layout.setSpacing(6)

            top_row = QHBoxLayout()

            self.name_label = QLabel(os.path.basename(download_request.downloadFileName()))
            self.name_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; background: transparent; border: none;")
            top_row.addWidget(self.name_label, 1)

            self.status_label = QLabel("0%")
            self.status_label.setStyleSheet("color: #888; font-size: 11px; background: transparent; border: none;")
            top_row.addWidget(self.status_label)

            self.cancel_btn = QPushButton("✕")
            self.cancel_btn.setFixedSize(20, 20)
            self.cancel_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #d32f2f;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 14px;
                }
                QPushButton:hover {
                    background: #d32f2f;
                    color: white;
                }
            """)
            self.cancel_btn.clicked.connect(self.cancel_download)
            top_row.addWidget(self.cancel_btn)

            layout.addLayout(top_row)

            self.progress_bar = QProgressBar()
            self.progress_bar.setFixedHeight(4)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background: #3c3c3c;
                    border: none;
                    border-radius: 2px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0078d4, stop:1 #00a8ff);
                    border-radius: 2px;
                }
            """)
            layout.addWidget(self.progress_bar)

            download_request.receivedBytesChanged.connect(self.update_progress)
            download_request.isFinishedChanged.connect(self.on_finished)

        def update_progress(self):
            received = self.download.receivedBytes()
            total = self.download.totalBytes()
            if total > 0:
                pct = int(received * 100 / total)
                self.progress_bar.setValue(pct)
                self.status_label.setText(f"{pct}%  ({self._format_bytes(received)} / {self._format_bytes(total)})")
            else:
                self.status_label.setText(f"{self._format_bytes(received)}")

        def on_finished(self):
            if self.download.isFinished():
                from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest as DL
                state = self.download.state()

                if state == DL.DownloadState.DownloadCompleted:
                    self.progress_bar.setValue(100)
                    self.status_label.setText(self.manager.translator.tr("finished", "Finished"))
                    self.status_label.setStyleSheet("color: #4caf50; font-size: 11px; background: transparent; border: none;")
                    self.cancel_btn.hide()
                elif state == DL.DownloadState.DownloadCancelled:
                    self.status_label.setText(self.manager.translator.tr("cancelled", "Cancelled"))
                    self.status_label.setStyleSheet("color: #d32f2f; font-size: 11px; background: transparent; border: none;")
                    self.cancel_btn.hide()
                elif state == DL.DownloadState.DownloadInterrupted:
                    self.status_label.setText(self.manager.translator.tr("interrupted", "Interrupted"))
                    self.status_label.setStyleSheet("color: #ff9800; font-size: 11px; background: transparent; border: none;")

        def cancel_download(self):
            self.download.cancel()

        def _format_bytes(self, bytes_count):
            if bytes_count < 1024:
                return f"{bytes_count} B"
            elif bytes_count < 1024 ** 2:
                return f"{bytes_count/1024:.1f} KB"
            elif bytes_count < 1024 ** 3:
                return f"{bytes_count/1024**2:.1f} MB"
            else:
                return f"{bytes_count/1024**3:.2f} GB"
    def add_download(self, download_request):
        for existing_item in self.download_items:
            if existing_item.download == download_request:
                return

        item = self.DownloadItemWidget(download_request, self)
        self.items_layout.insertWidget(self.items_layout.count() - 1, item)
        self.download_items.append(item)

        self.empty_label.hide()
        self.show()
        self.raise_()

        download_request.isFinishedChanged.connect(
            lambda: self.check_auto_cleanup(item)
        )

    def check_auto_cleanup(self, item):
        if item.download.isFinished():
            from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest as DL
            state = item.download.state()
            if state in [DL.DownloadState.DownloadCompleted,
                        DL.DownloadState.DownloadCancelled,
                        DL.DownloadState.DownloadInterrupted]:
                pass

    def clear_finished(self):
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest as DL
        to_remove = []

        for item in self.download_items:
            if item.download.isFinished():
                state = item.download.state()
                if state in [DL.DownloadState.DownloadCompleted,
                            DL.DownloadState.DownloadCancelled,
                            DL.DownloadState.DownloadInterrupted]:
                    to_remove.append(item)

        for item in to_remove:
            self.download_items.remove(item)
            item.deleteLater()

        if not self.download_items:
            self.empty_label.show()

    def get_active_downloads(self):
        from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest as DL
        active = 0
        for item in self.download_items:
            if not item.download.isFinished():
                active += 1
        return active

    def closeEvent(self, event):
        event.accept()
        self.hide()

class ThemeEngine:
    def __init__(self, browser):
        self.browser = browser
        self.current_theme_data = None
        self.theme_path = None
        self.theme_images = {}
        self.current_font = None
        self.default_font = QApplication.font()
        self.current_background = None

    def reset_all_new_tab_backgrounds(self):
        if not hasattr(self.browser, 'tabs'):
            return

        for i in range(self.browser.tabs.count()):
            tab = self.browser.tabs.widget(i)
            if hasattr(tab, 'new_tab_page') and tab.new_tab_page:
                tab.new_tab_page.set_default_background()

    def apply_theme_to_new_tab(self, new_tab_page):
        if self.current_background and hasattr(new_tab_page, 'bg_label'):
            self.apply_background_to_tab(new_tab_page, self.current_background)

    def apply_background_to_tab(self, new_tab_page, bg_image, tab_index=None):
        try:
            pixmap = QPixmap(bg_image)
            if not pixmap.isNull():
                if hasattr(new_tab_page, 'set_custom_background'):
                    new_tab_page.set_custom_background(pixmap)
                else:
                    scaled_pixmap = pixmap.scaled(
                        new_tab_page.size(),
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    new_tab_page.bg_label.setPixmap(scaled_pixmap)
                    new_tab_page.bg_label.setScaledContents(False)
                if tab_index is not None:
                    print(f"theme system: applied background to new tab {tab_index}")
                else:
                    print(f"theme system: applied background to new tab")
            else:
                print(f"theme system: failed to load pixmap from {bg_image}")
        except Exception as e:
            print(f"theme system: error applying background: {e}")

    def apply_theme(self, theme_name):
        if not hasattr(self.browser, 'themes') or not self.browser.themes:
            self.apply_default_theme()
            return

        if theme_name == self.browser.translator.tr("default_theme", "Default Theme"):
            self.apply_default_theme()
            return
        if theme_name == self.browser.translator.tr("disable_themes", "Disable All Themes"):
            self.apply_default_theme()
            return

        if theme_name in self.browser.themes:
            theme_data = self.browser.themes[theme_name]
            self.current_theme_data = theme_data
            self.theme_path = theme_data.get('path', '')

            print(f"theme system: applying theme {theme_name}")
            print(f"theme system: has a theme.qss: {theme_data.get('has_qss', False)}")
            print(f"theme system: has a font: {theme_data.get('has_font', False)}")
            print(f"theme system: has images: {theme_data.get('has_images', False)}")

            try:
                self.reset_to_default_font()
                QApplication.instance().setStyleSheet("")

                self.theme_images = self.load_all_theme_images()
                print(f"loaded {len(self.theme_images)} image(s) from theme")

                if theme_data.get('has_qss', False) and 'css_content' in theme_data:
                    print(f"theme system: applying qss theme")
                    self.apply_qss_content(theme_data['css_content'])
                else:
                    print(f"theme system: no qss theme found")

                if theme_data.get('has_font', False):
                    font_file = os.path.join(self.theme_path, "font.ttf")
                    if os.path.exists(font_file):
                        print(f"theme system: applying font...")
                        self.apply_font_file(font_file)

                print(f"theme system: applying images from themes...")
                self.update_navigation_buttons()
                self.apply_custom_checkboxes()
                self.update_new_tab_theme()
                self.apply_custom_scrollbars()

                self.browser.style().unpolish(self.browser)
                self.browser.style().polish(self.browser)

                print(f"theme system: theme {theme_name} applied successfully")

            except Exception as e:
                print(f"theme system: error applying theme {theme_name}: {e}")
                import traceback
                traceback.print_exc()
                self.apply_default_theme()
        else:
            print(f"theme system: theme {theme_name} not found in loaded themes")
            self.apply_default_theme()

    def apply_default_theme(self):
        print(f"theme system: applying default theme")

        self.current_theme_data = None
        self.theme_path = None
        self.theme_images = {}
        self.current_background = None

        self.reset_to_default_font()

        default_css = """
        QMainWindow {
            background: #1b1b1b;
            color: white;
            border: none;
        }
        QTabBar::tab {
            background: #2c2c2c;
            color: #ccc;
            padding: 8px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 1px;
            font-size: 12px;
        }
        QTabBar::tab:selected {
            background: #1f1f1f;
            color: white;
            border-bottom: 2px solid #0078d4;
        }
        QTabBar::tab:hover:!selected {
            background: #3a3a3a;
        }
        QToolBar {
            background: #1b1b1b;
            border: none;
            border-bottom: 1px solid #3c3c3c;
            spacing: 6px;
            padding: 8px;
        }
        QPushButton {
            background: #2c2c2c;
            border: 1px solid #4a4a4a;
            color: white;
            padding: 2px 4px;
            border-radius:  14px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: #6c6c6c;
        }
        QPushButton:pressed {
            background: #5c5c5c;
        }
        QLineEdit {
            background: #2c2c2c;
            border: 1px solid #4a4a4a;
            color: white;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #0078d4;
            background: #4a4a4a;
        }
        QLineEdit::placeholder {
            color: #888;
        }
        QTabWidget::pane {
            border: none;
            background: #2e2e2e;
        }
        QTabWidget::tab-bar {
            alignment: left;
        }

        QComboBox, QCheckBox, QGroupBox, QTextEdit, QScrollArea, QLabel {
            color: white;
        }
        """
        self.browser.setStyleSheet(default_css)
        QApplication.instance().setStyleSheet(default_css)

        self.reset_navigation_buttons()

        self.reset_all_new_tab_backgrounds()

    def apply_qss_content(self, qss_content):
        try:
            processed_qss = self.process_qss_variables(qss_content)
            if self.theme_images:
                processed_qss = self.replace_image_placeholders(processed_qss)
            self.browser.setStyleSheet(processed_qss)
            QApplication.instance().setStyleSheet(processed_qss)

        except Exception as e:
            print(f"theme system: error applying qss theme {e}")
            raise

    def apply_font_file(self, font_path):
        try:
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    font = QFont(font_families[0])
                    self.current_font = font
                    QApplication.instance().setFont(font)

                    if hasattr(self.browser, 'url_bar'):
                        self.browser.url_bar.setFont(font)
        except Exception as e:
            print(f"theme system: error applying font {e}")

    def reset_to_default_font(self):
        self.current_font = self.default_font
        QApplication.instance().setFont(self.default_font)

        if hasattr(self.browser, 'url_bar'):
            self.browser.url_bar.setFont(self.default_font)

        for widget in self.browser.findChildren(QWidget):
            if hasattr(widget, 'setFont'):
                widget.setFont(self.default_font)

    def reset_navigation_buttons(self):
        if not hasattr(self.browser, 'nav_toolbar') or not self.browser.nav_toolbar:
            return

        button_texts = {
            "back": "◀",
            "forward": "▶",
            "reload": "↻",
            "settings": "⚙",
            "plus": "+"
        }

        try:
            for action in self.browser.nav_toolbar.actions():
                widget = self.browser.nav_toolbar.widgetForAction(action)
                if widget and isinstance(widget, QPushButton):
                    if not widget.icon().isNull():
                        widget.setIcon(QIcon())
                    for btn_name, text in button_texts.items():
                        if widget.text() == "":
                            widget.setText(text)
                            break
        except Exception as e:
            print(f"theme system: error resetting nav buttons {e}")

    def update_navigation_buttons(self):
        if not hasattr(self.browser, 'nav_toolbar') or not self.browser.nav_toolbar:
            return

        button_mapping = {
            "◀": "back",
            "▶": "forward",
            "↻": "reload",
            "⚙": "settings",
            "+": "plus"
        }

        try:
            for action in self.browser.nav_toolbar.actions():
                widget = self.browser.nav_toolbar.widgetForAction(action)
                if widget and isinstance(widget, QPushButton):
                    btn_text = widget.text()
                    if btn_text in button_mapping:
                        image_name = button_mapping[btn_text]
                        if image_name in self.theme_images:
                            icon = QIcon(self.theme_images[image_name])
                            widget.setIcon(icon)
                            widget.setText("")
                            widget.setIconSize(QSize(24, 24))
                            print(f"theme system: applied icon for {image_name}")
                        else:
                            if widget.icon() and not widget.icon().isNull():
                                widget.setIcon(QIcon())
                            if not widget.text():
                                widget.setText(btn_text)
        except Exception as e:
            print(f"theme system: error applying custom nav buttons {e}")

    def load_all_theme_images(self):
        images = {}
        if not self.theme_path or not os.path.exists(self.theme_path):
            return images

        image_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.svg')

        for filename in os.listdir(self.theme_path):
            if filename.lower().endswith(image_extensions):
                filepath = os.path.join(self.theme_path, filename)
                key = os.path.splitext(filename)[0].lower()
                images[key] = filepath
                if key == 'bg' or key == 'background':
                    images['newtab_bg'] = filepath
                    images['background'] = filepath
                    images['bg'] = filepath

        print(f"theme system: found images: {list(images.keys())}")
        return images

    def process_qss_variables(self, qss_content):
        import re

        variables = {}
        root_pattern = r':root\s*\{([^}]+)\}'
        root_match = re.search(root_pattern, qss_content, re.DOTALL)

        if root_match:
            root_content = root_match.group(1)
            var_pattern = r'--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);'
            variables = dict(re.findall(var_pattern, root_content))

            qss_content = re.sub(root_pattern, '', qss_content)

        for var_name, var_value in variables.items():
            qss_content = qss_content.replace(f'var(--{var_name})', var_value.strip())

        return qss_content

    def replace_image_placeholders(self, qss_content):
        import re

        image_pattern = r'url\(["\']?([^"\')]+)["\']?\)'

        def replace_image(match):
            filename = match.group(1)
            filename = filename.strip('"\'').strip()
            filename_no_ext = os.path.splitext(filename)[0].lower()

            if filename_no_ext in self.theme_images:
                return f'url("{self.theme_images[filename_no_ext]}")'
            else:
                for img_key, img_path in self.theme_images.items():
                    if img_key in filename_no_ext or filename_no_ext in img_key:
                        return f'url("{img_path}")'
                return match.group(0)

        return re.sub(image_pattern, replace_image, qss_content)

    def apply_custom_checkboxes(self):
        if 'checkbox_checked' in self.theme_images and 'checkbox_unchecked' in self.theme_images:
            checkbox_style = f"""
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:unchecked {{
                image: url("{self.theme_images['checkbox_unchecked']}");
            }}
            QCheckBox::indicator:unchecked:hover {{
                image: url("{self.theme_images.get('checkbox_unchecked_hover', self.theme_images['checkbox_unchecked'])}");
            }}
            QCheckBox::indicator:checked {{
                image: url("{self.theme_images['checkbox_checked']}");
            }}
            QCheckBox::indicator:checked:hover {{
                image: url("{self.theme_images.get('checkbox_checked_hover', self.theme_images['checkbox_checked'])}");
            }}
            """

            for widget in QApplication.allWidgets():
                if isinstance(widget, QCheckBox):
                    widget.setStyleSheet(checkbox_style)
            print(f"theme system: applied custom checkbox style")

    def apply_custom_scrollbars(self):
        scrollbar_style = ""

        if 'scroll_handle' in self.theme_images:
            scrollbar_style += """
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop: 0 rgba(255, 255, 255, 100),
                    stop: 1 rgba(255, 255, 255, 50));
                border-radius: 6px;
            }
            """

        if scrollbar_style:
            for widget in QApplication.allWidgets():
                if hasattr(widget, 'verticalScrollBar') or hasattr(widget, 'horizontalScrollBar'):
                    current_style = widget.styleSheet()
                    widget.setStyleSheet(current_style + scrollbar_style)
            print(f"theme system: applied custom scrollbar style")

    def update_new_tab_theme(self):
        if not self.theme_path or not hasattr(self.browser, 'tabs'):
            return

        bg_image = None
        bg_keys = ['newtab_bg', 'background', 'bg']

        for bg_key in bg_keys:
            if bg_key in self.theme_images:
                bg_image = self.theme_images[bg_key]
                print(f"theme system: found background image: {os.path.basename(bg_image)}")
                self.current_background = bg_image
                break

        if not bg_image:
            print(f"theme system: no background image found in theme")
            self.current_background = None
            return

        for i in range(self.browser.tabs.count()):
            tab = self.browser.tabs.widget(i)
            if hasattr(tab, 'new_tab_page') and tab.new_tab_page:
                self.apply_background_to_tab(tab.new_tab_page, bg_image, i)

class CustomNewTabPage(QWidget):
    def __init__(self, parent=None, translator=None, theme_engine=None):
        super().__init__(parent)
        self.parent_browser = parent
        self.translator = translator
        self.theme_engine = theme_engine
        self.custom_bg_applied = False
        self.original_pixmap = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.bg_container = QWidget()
        self.bg_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.bg_layout = QVBoxLayout(self.bg_container)
        self.bg_layout.setContentsMargins(0, 0, 0, 0)

        self.bg_label = QLabel()
        self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bg_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.bg_layout.addWidget(self.bg_label)

        self.main_layout.addWidget(self.bg_container)

        self.overlay = QWidget(self)
        self.overlay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.overlay.setStyleSheet("background: transparent;")

        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.setContentsMargins(50, 50, 50, 50)

        self.title_label = QLabel(self.translator.tr("welcome_title", "cat browser (real)"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            color:white;
            font-size:32px;
            font-weight:bold;
            margin-bottom:30px;
        """)
        overlay_layout.addWidget(self.title_label)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(self.translator.tr("search_placeholder", "search google or enter url"))
        self.search_bar.setStyleSheet("""
            background-color: rgba(0,0,0,0.8);
            border: 2px solid #1b1c1c;
            border-radius: 25px;
            padding: 12px 20px;
            font-size: 18px;
            color: white;
            min-width: 400px;
            max-width: 600px;
            margin-bottom: 40px;
        """)
        overlay_layout.addWidget(self.search_bar, 0, Qt.AlignmentFlag.AlignCenter)

        self.quote_label = QLabel()
        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_label.setStyleSheet("color:#ccc; font-size:14px; font-style:italic; margin-top:30px;")
        overlay_layout.addWidget(self.quote_label)

        bottom_container = QWidget()
        bottom_container.setStyleSheet("background: transparent;")
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0,20,20,20)
        bottom_layout.addStretch()
        self.credits_btn = QPushButton(self.translator.tr("credits","Credits"))
        self.credits_btn.setFixedSize(70,25)
        self.credits_btn.setStyleSheet("""
            QPushButton {
                background: rgba(60,60,60,0.8);
                border: 1px solid #777;
                border-radius:4px;
                color:white;
                padding:4px 8px;
                font-size:11px;
                font-weight:bold;
            }
            QPushButton:hover {
                background: rgba(80,80,80,0.9);
                border:1px solid #0078d4;
            }
        """)
        self.credits_btn.clicked.connect(self.show_credits)
        bottom_layout.addWidget(self.credits_btn)
        overlay_layout.addWidget(bottom_container)

        self.load_fun_fact()

        self.search_bar.returnPressed.connect(self.perform_search)

        if self.theme_engine and getattr(self.theme_engine,"current_background",None):
            self.set_custom_background(self.theme_engine.current_background)
        else:
            self.set_default_background()

    def download_favicon(self, url):
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.netloc:
                domain = parsed.netloc.replace('www.', '')
                favicon_url = f"https://{domain}/favicon.ico"

                favicon_view = QWebEngineView()
                favicon_view.loadFinished.connect(
                    lambda ok, view=favicon_view, dom=domain: self.save_favicon(view, dom, ok)
                )
                favicon_view.load(QUrl(favicon_url))

        except Exception as e:
            print(f"error setting up favicon download: {e}")

    def save_favicon(self, view, domain, ok):
        try:
            if ok:
                icon = view.page().icon()
                if not icon.isNull():
                    pixmap = icon.pixmap(32, 32)
                    favicon_path = os.path.join(FAVICON_DIR, f"{domain}.png")
                    pixmap.save(favicon_path, "PNG")
                    self.display_shortcuts()
        except Exception as e:
            print(f"error saving favicon: {e}")
        finally:
            view.deleteLater()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.overlay.setGeometry(0, 0, self.width(), self.height())

        self.update_background_scaling()

    def update_background_scaling(self):
        if hasattr(self, 'original_pixmap') and self.original_pixmap and self.custom_bg_applied:
            scaled_pixmap = self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg_label.setPixmap(scaled_pixmap)

    def set_default_background(self):
        pixmap_path = None
        if os.path.exists(BG2_IMG) and random.randint(1,1000)==1:
            pixmap_path = BG2_IMG
        elif os.path.exists(BG_IMG):
            pixmap_path = BG_IMG

        self.set_custom_background(pixmap_path)

    def set_custom_background(self, pixmap_or_path):
        pixmap = None
        if isinstance(pixmap_or_path, QPixmap):
            pixmap = pixmap_or_path
        elif isinstance(pixmap_or_path, str) and os.path.exists(pixmap_or_path):
            pixmap = QPixmap(pixmap_or_path)

        if pixmap and not pixmap.isNull():
            self.original_pixmap = pixmap

            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.bg_label.setPixmap(scaled_pixmap)
            self.bg_label.setScaledContents(False)

            self.bg_label.setMinimumSize(1, 1)
            self.bg_label.setMaximumSize(16777215, 16777215)

            self.custom_bg_applied = True
        else:
            self.bg_label.setStyleSheet("background-color:#1e1e1e;")
            self.custom_bg_applied = False
            self.original_pixmap = None


    def load_fun_fact(self):
        if os.path.exists(FACTS_FILE):
            with open(FACTS_FILE, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
                if lines:
                    fact_text = random.choice(lines)
                    self.quote_label.setText(self.translator.tr("fun_fact", "{}").format(fact_text))
                    return
        self.quote_label.setText(self.translator.tr("fun_fact", "fun fact:").format(""))

    def perform_search(self):
        q = self.search_bar.text().strip()
        if not q:
            return

        parent_tab = self.parent()
        while parent_tab and not isinstance(parent_tab, Tab):
            parent_tab = parent_tab.parent()

        if not parent_tab:
            if self.parent_browser:
                search_url = self.parent_browser.get_search_url(q)
                self.parent_browser.add_tab(search_url)
            return

        if self.parent_browser:
            search_url = self.parent_browser.get_search_url(q)
        else:
            from urllib.parse import quote
            if '.' in q and ' ' not in q and not q.startswith(('http://','https://')):
                search_url = "https://" + q
            else:
                search_url = f"https://www.google.com/search?q={quote(q)}"

        layout = parent_tab.layout()
        if layout:
            if parent_tab.new_tab_page:
                parent_tab.new_tab_page.setParent(None)
                parent_tab.new_tab_page.deleteLater()
                parent_tab.new_tab_page = None

            parent_tab.web_view = InspectorWebView(parent_tab.profile, parent_tab, browser=self.parent_browser)
            parent_tab.web_view.setUrl(QUrl(search_url))

            if self.parent_browser:
                parent_tab.web_view.urlChanged.connect(
                    lambda u, t=parent_tab: self.parent_browser.on_url_change(t)
                )
                parent_tab.web_view.titleChanged.connect(
                    lambda t, i=self.parent_browser.tabs.indexOf(parent_tab):
                    self.parent_browser.on_title_change(t, i)
                )
                parent_tab.web_view.iconChanged.connect(
                    lambda icon, i=self.parent_browser.tabs.indexOf(parent_tab):
                    self.parent_browser.on_icon_change(icon, i)
                )
                parent_tab.web_view.urlChanged.connect(
                    lambda u: self.parent_browser.history.append(parent_tab.web_view.url().toString())
                )

            layout.addWidget(parent_tab.web_view)

            parent_tab.is_new_tab = False

            if self.parent_browser:
                self.parent_browser.tabs.setTabText(
                    self.parent_browser.tabs.indexOf(parent_tab),
                    self.parent_browser.translator.tr("loading", "Loading...")
                )

                self.parent_browser.tab_last_accessed[id(parent_tab)] = datetime.now()

    def show_credits(self):

        credits_dialog = QDialog(self)
        credits_dialog.setWindowTitle(self.translator.tr("credits_title", "cat browser credits"))
        credits_dialog.setFixedSize(600, 600)
        credits_dialog.setStyleSheet("""
            QDialog {
                background: #1a1a1a;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: #106ebe;
            }
        """)

        layout = QVBoxLayout(credits_dialog)

        title = QLabel(self.translator.tr("credits_title", "cat browser credits"))
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)


        credits_text = QLabel()
        credits_text.setTextFormat(Qt.TextFormat.RichText)
        credits_text.setWordWrap(True)
        credits_text.setText(f"""
        <div style='text-align: center;'>
        <h3>{self.translator.tr('development_team', 'Development Team')}</h3>
        <p><b>anameless_guy - Discord</b> - {self.translator.tr('developer', 'dev')}</p>
        <p><b>monoes1 - Discord</b> - {self.translator.tr('download manager dev', 'download_manager_dev')}</p>
        <h3>{self.translator.tr('translators', 'Translators')}</h3>
        <p><b>alex.ggiscool - Discord</b></p>
        <p><b>nmlsspersonn1033 - Discord / @nmlssperson1033 - Telegram</b></p>
        <p><b>monoes1 - Discord</b></p>
        <p><b>rizakai - Discord</b></p>


        <h3>{self.translator.tr('special_thanks', 'Special Thanks')}</h3>
        <p>PyQt6 Team  - {self.translator.tr('for_webengine', 'For the WebEngine')}</p>

        </div>
        """)
        credits_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credits_text)

        close_text = self.translator.tr("close", "Close")
        close_btn = QPushButton(close_text)
        close_btn.clicked.connect(credits_dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        credits_dialog.exec()

class InspectorWebPage(QWebEnginePage):
    def __init__(self, profile, parent):
        super().__init__(profile, parent)
        self.inspector_view = None
        self.parent_browser = None

    def set_parent_browser(self, browser):
        self.parent_browser = browser

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"js console: {message} (line {lineNumber})")

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if url.scheme() == "cat-browser":
            if self.parent_browser:
                from PyQt6.QtCore import QTimer
                url_str = url.toString()
                QTimer.singleShot(0, lambda: self.parent_browser._open_cat_browser_page(url_str))
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def createWindow(self, type):
        if type == QWebEnginePage.WebWindowType.WebBrowserTab:
            if self.parent_browser:
                new_tab = self.parent_browser.add_tab("about:blank")
                if hasattr(new_tab, 'web_view') and new_tab.web_view:
                    return new_tab.web_view.page()
            new_view = InspectorWebView(self.profile())
            return new_view.page()
        return super().createWindow(type)

def build_offline_game_html(soggy_path: str) -> str:
    soggy_url = QUrl.fromLocalFile(soggy_path).toString()
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>No Internet</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: #5c94fc;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    user-select: none;
    image-rendering: pixelated;
  }}
  canvas {{
    display: block;
    cursor: pointer;
    image-rendering: pixelated;
    position: absolute;
    top: 0; left: 0;
  }}
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

let W, H, S;
let PIPE_W, PIPE_GAP, PIPE_SPEED, PIPE_SPAWN, GROUND_H, CAT_X, CAT_W, CAT_H, BLOCK;
let GRAVITY, FLAP_VEL;

function resize() {{
  W = window.innerWidth;
  H = window.innerHeight;
  canvas.width  = W;
  canvas.height = H;
  ctx.imageSmoothingEnabled = false;

  S = Math.min(W, H) / 320;

  BLOCK      = Math.round(6 * S);
  PIPE_W     = Math.round(40 * S);
  PIPE_GAP   = Math.round(120 * S);
  PIPE_SPEED = 3.5 * S;
  PIPE_SPAWN = Math.round(160 * S);
  GROUND_H   = Math.round(52 * S);
  CAT_X      = Math.round(60 * S);
  CAT_W      = Math.round(34 * S);
  CAT_H      = Math.round(34 * S);
  GRAVITY    = 0.38 * S;
  FLAP_VEL   = -5 * S;

  if (state === 'idle') reset();
}}

const img = new Image();
img.src = "{soggy_url}";

const CLOUD_SHAPE = [
  [1,1],[2,1],[3,1],
  [0,2],[1,2],[2,2],[3,2],[4,2],
  [0,3],[1,3],[2,3],[3,3],[4,3],
];

let state = 'idle';
let catY, catVY, pipes, frame, bgOffset, clouds;

function makeCloud(x) {{
  return {{ x, y: Math.floor(20 * S + Math.random() * 80 * S) }};
}}

function reset() {{
  catY     = H / 2 - CAT_H / 2;
  catVY    = 0;
  pipes    = [];
  frame    = 0;
  bgOffset = 0;
  pipes.push(makePipe(W + Math.round(40 * S)));
  clouds = [
    makeCloud(Math.round(40 * S)),
    makeCloud(Math.round(160 * S)),
    makeCloud(Math.round(280 * S)),
  ];
}}

function makePipe(x) {{
  const minTop = Math.round(40 * S);
  const maxTop = H - GROUND_H - PIPE_GAP - Math.round(40 * S);
  const topH   = Math.floor(Math.random() * (maxTop - minTop) + minTop);
  return {{ x, topH }};
}}

function flap() {{
  if (state === 'dead') {{ state = 'idle'; reset(); return; }}
  if (state === 'idle') {{ state = 'running'; reset(); }}
  catVY = FLAP_VEL;
}}

document.addEventListener('keydown', e => {{
  if (e.code === 'Space' || e.code === 'ArrowUp') {{ e.preventDefault(); flap(); }}
}});
canvas.addEventListener('click', flap);
canvas.addEventListener('touchstart', e => {{ e.preventDefault(); flap(); }});
window.addEventListener('resize', resize);

function drawSky() {{
  ctx.fillStyle = '#5c94fc';
  ctx.fillRect(0, 0, W, H - GROUND_H);
}}

function drawCloud(cx, cy) {{
  ctx.fillStyle = '#ffffff';
  CLOUD_SHAPE.forEach(([col, row]) => {{
    ctx.fillRect(cx + col * BLOCK, cy + row * BLOCK, BLOCK, BLOCK);
  }});
}}

function drawClouds() {{
  clouds.forEach(c => {{
    drawCloud(c.x, c.y);
    if (state === 'running') c.x -= 0.5 * S;
    if (c.x < -5 * BLOCK) c.x = W + 10;
  }});
}}

function drawGround() {{
  ctx.fillStyle = '#c84b0c';
  ctx.fillRect(0, H - GROUND_H, W, GROUND_H);
  ctx.fillStyle = '#5da30e';
  ctx.fillRect(0, H - GROUND_H, W, Math.round(8 * S));
  ctx.fillStyle = '#4a8a0a';
  ctx.fillRect(0, H - GROUND_H + Math.round(8 * S), W, Math.round(4 * S));
  ctx.fillStyle = '#b04008';
  const tile = Math.round(16 * S);
  const off  = Math.floor(bgOffset * 0.6) % tile;
  for (let x = -off; x < W; x += tile) {{
    ctx.fillRect(x, H - GROUND_H + Math.round(18 * S), Math.round(8 * S), Math.round(4 * S));
    ctx.fillRect(x + Math.round(8 * S), H - GROUND_H + Math.round(30 * S), Math.round(8 * S), Math.round(4 * S));
  }}
}}

function drawPipe(p) {{
  const botY = p.topH + PIPE_GAP;
  const cap  = Math.round(14 * S);
  const edge = Math.round(6 * S);
  const ovr  = Math.round(4 * S);

  ctx.fillStyle = '#5aab17';
  ctx.fillRect(p.x, 0, PIPE_W, p.topH);
  ctx.fillStyle = '#4a9010';
  ctx.fillRect(p.x - ovr, p.topH - cap, PIPE_W + ovr * 2, cap);
  ctx.fillStyle = '#2d6008';
  ctx.fillRect(p.x, 0, edge, p.topH);
  ctx.fillRect(p.x - ovr, p.topH - cap, edge, cap);

  ctx.fillStyle = '#5aab17';
  ctx.fillRect(p.x, botY, PIPE_W, H - botY - GROUND_H);
  ctx.fillStyle = '#4a9010';
  ctx.fillRect(p.x - ovr, botY, PIPE_W + ovr * 2, cap);
  ctx.fillStyle = '#2d6008';
  ctx.fillRect(p.x, botY + cap, edge, H - botY - GROUND_H - cap);
  ctx.fillRect(p.x - ovr, botY, edge, cap);
}}

function drawCat() {{
  if (img.complete && img.naturalWidth > 0) {{
    ctx.drawImage(img, CAT_X, catY, CAT_W, CAT_H);
  }} else {{
    ctx.fillStyle = '#e74c3c';
    ctx.fillRect(CAT_X, catY, CAT_W, CAT_H);
  }}
}}

function drawHUD() {{
  ctx.textAlign = 'center';
  ctx.imageSmoothingEnabled = false;
  const fs = Math.round(13 * S);

  if (state === 'idle') {{
    const bw = Math.round(180 * S), bh = Math.round(48 * S);
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(W/2 - bw/2, H/2 - bh/2, bw, bh);
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = Math.round(2 * S);
    ctx.strokeRect(W/2 - bw/2, H/2 - bh/2, bw, bh);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold ' + fs + 'px monospace';
    ctx.fillText('CLICK TO START', W / 2, H / 2 + fs * 0.4);
  }}

  if (state === 'dead') {{
    const bw = Math.round(200 * S), bh = Math.round(64 * S);
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(W/2 - bw/2, H/2 - bh/2, bw, bh);
    ctx.strokeStyle = '#e74c3c';
    ctx.lineWidth = Math.round(2 * S);
    ctx.strokeRect(W/2 - bw/2, H/2 - bh/2, bw, bh);
    ctx.fillStyle = '#e74c3c';
    ctx.font = 'bold ' + Math.round(15 * S) + 'px monospace';
    ctx.fillText('GAME OVER', W / 2, H / 2 - fs * 0.4);
    ctx.fillStyle = '#aaaaaa';
    ctx.font = Math.round(11 * S) + 'px monospace';
    ctx.fillText('CLICK TO RETRY', W / 2, H / 2 + fs * 1.2);
  }}

  if (state === 'running') {{
  }}
}}

function update() {{
  if (state !== 'running') return;
  frame++; bgOffset += PIPE_SPEED;
  catVY += GRAVITY; catY += catVY;
  if (pipes.length === 0 || pipes[pipes.length - 1].x < W - PIPE_SPAWN)
    pipes.push(makePipe(W + 10));
  for (const p of pipes) {{
    p.x -= PIPE_SPEED;
  }}
  pipes = pipes.filter(p => p.x > -PIPE_W - 10);
  if (catY + CAT_H >= H - GROUND_H || catY <= 0) {{ state = 'dead'; return; }}
  const cx = CAT_X + Math.round(4 * S), cy = catY + Math.round(4 * S);
  const cw = CAT_W - Math.round(8 * S), ch = CAT_H - Math.round(8 * S);
  for (const p of pipes) {{
    if (cx + cw > p.x + Math.round(4 * S) && cx < p.x + PIPE_W - Math.round(4 * S))
      if (cy < p.topH || cy + ch > p.topH + PIPE_GAP) {{ state = 'dead'; return; }}
  }}
}}

function loop() {{
  drawSky();
  drawClouds();
  pipes.forEach(drawPipe);
  drawGround();
  drawCat();
  drawHUD();
  update();
  requestAnimationFrame(loop);
}}

resize();
loop();
</script>
</body></html>"""


class InspectorWebView(QWebEngineView):
    def __init__(self, profile, parent=None, browser=None):
        super().__init__(parent)
        self.parent_browser = browser
        self.inspector_page = InspectorWebPage(profile, self)
        self.inspector_page.set_parent_browser(browser)
        self.setPage(self.inspector_page)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._last_requested_url = ""
        self.loadStarted.connect(self._on_load_started)
        self.loadFinished.connect(self._on_load_finished)

    def _on_load_started(self):
        self._last_requested_url = self.url().toString()

    def _on_load_finished(self, ok):
        if ok:
            return
        current_url = self.url().toString()
        OFFLINE_ERRORS = (
            "ERR_NAME_NOT_RESOLVED",
            "ERR_INTERNET_DISCONNECTED",
            "ERR_NETWORK_CHANGED",
            "ERR_CONNECTION_REFUSED",
            "ERR_CONNECTION_TIMED_OUT",
            "ERR_CONNECTION_RESET",
            "ERR_ADDRESS_UNREACHABLE",
        )
        self.page().runJavaScript(
            "document.title + '|||' + (document.body ? document.body.innerText.substring(0, 300) : '')",
            lambda result, url=current_url: self._check_error_page(result, url)
        )

    def _check_error_page(self, result, url):
        if not result:
            return
        text = result.upper()
        OFFLINE_TRIGGERS = [
            "ERR_NAME_NOT_RESOLVED", "ERR_INTERNET_DISCONNECTED",
            "ERR_NETWORK_CHANGED", "ERR_CONNECTION_REFUSED",
            "ERR_CONNECTION_TIMED_OUT", "ERR_CONNECTION_RESET",
            "ERR_ADDRESS_UNREACHABLE", "ERR_EMPTY_RESPONSE",
            "NET::ERR", "DNS_PROBE", "CHROME-ERROR",
        ]
        if any(t in text for t in OFFLINE_TRIGGERS):
            soggy_path = os.path.join(BASE_PATH, "soggy.png")
            base_url = QUrl.fromLocalFile(BASE_PATH + os.sep)
            self.setHtml(build_offline_game_html(soggy_path), base_url)
            if self.parent_browser:
                tab_index = -1
                for i in range(self.parent_browser.tabs.count()):
                    tab = self.parent_browser.tabs.widget(i)
                    if hasattr(tab, 'web_view') and tab.web_view is self:
                        tab_index = i
                        break
                if tab_index >= 0:
                    self.parent_browser.tabs.setTabText(tab_index, "No Internet")
                self.parent_browser.url_bar.setText(url)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        inspect_action = QAction("Inspect Element", menu)
        inspect_action.triggered.connect(self.inspect_element)
        menu.addAction(inspect_action)

        menu.exec(event.globalPos())

    def inspect_element(self):
        self.page().runJavaScript("""
            (function() {
                if (!window.__cat_inspector) {
                    window.__cat_inspector = true;
                    var style = document.createElement('style');
                    style.innerHTML = `
                        *:hover {
                            outline: 2px solid red !important;
                            outline-offset: -2px;
                            cursor: crosshair;
                        }
                    `;
                    document.head.appendChild(style);

                    document.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        var element = e.target;
                        var html = element.outerHTML.substring(0, 200);
                        var info = {
                            tag: element.tagName,
                            id: element.id,
                            className: element.className,
                            html: html,
                            xpath: getXPath(element)
                        };
                        window.__cat_last_inspected = info;

                        style.remove();
                        window.__cat_inspector = false;

                        console.log('Inspected element:', info);
                    }, true);

                    function getXPath(element) {
                        if (element.id !== '')
                            return '//*[@id="' + element.id + '"]';
                        if (element === document.body)
                            return '/html/body';
                        var ix = 0;
                        var siblings = element.parentNode.childNodes;
                        for (var i = 0; i < siblings.length; i++) {
                            var sibling = siblings[i];
                            if (sibling === element)
                                return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                            if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                                ix++;
                        }
                    }
                }
            })();
        """)

        self.show_inspector_dialog()

    def show_inspector_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Element Inspector")
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet("""
            QDialog {
                background: #2b2b2b;
                color: white;
            }
            QTextEdit {
                background: #1a1a1a;
                color: #00ff00;
                font-family: 'Monospace';
                font-size: 12px;
                border: 1px solid #444;
            }
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #106ebe;
            }
        """)

        layout = QVBoxLayout(dialog)

        self.inspector_text = QTextEdit()
        self.inspector_text.setReadOnly(True)
        layout.addWidget(self.inspector_text)

        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(lambda: self.refresh_inspector(dialog))
        button_layout.addWidget(refresh_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.refresh_inspector(dialog)
        dialog.exec()

    def refresh_inspector(self, dialog):
        self.page().runJavaScript("""
            (function() {
                if (window.__cat_last_inspected) {
                    return window.__cat_last_inspected;
                }
                return null;
            })();
        """, lambda result: self.display_inspector_result(result, dialog))

    def display_inspector_result(self, result, dialog):
        if result:
            text = f"Tag: {result.get('tag', 'N/A')}\n"
            text += f"ID: {result.get('id', 'N/A')}\n"
            text += f"Class: {result.get('className', 'N/A')}\n"
            text += f"XPath: {result.get('xpath', 'N/A')}\n"
            text += f"HTML Preview:\n{result.get('html', 'N/A')}..."
            self.inspector_text.setText(text)
        else:
            self.inspector_text.setText("No element inspected yet.\nClick 'Inspect Element' and then click on any element on the page.")

class Tab(QWidget):
    def __init__(self, profile, url=None, is_new_tab=False, parent_browser=None, translator=None, theme_engine=None):
        super().__init__()
        self.is_new_tab = is_new_tab
        self.web_view = None
        self.profile = profile
        self.main_browser = parent_browser
        self.translator = translator
        self.theme_engine = theme_engine

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if not is_new_tab and self.web_view:
            self.web_view.urlChanged.connect(self.on_url_changed)
            self.web_view.loadFinished.connect(self.on_page_loaded)

        if is_new_tab:
            self.new_tab_page = CustomNewTabPage(self.main_browser, self.translator, theme_engine)
            layout.addWidget(self.new_tab_page)
            self.web_view = None

        elif url and url.startswith("settings://"):
            label = QLabel("Invalid tab type")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.web_view = None
            self.new_tab_page = None

        else:
            self.web_view = InspectorWebView(profile, self, browser=self.main_browser)
            self.web_view.setUrl(QUrl(url) if url else QUrl("https://www.google.com"))
            self.optimize_webview()
            if self.web_view.page():
                self.web_view.page().fullScreenRequested.connect(self.handle_fullscreen_request)

            layout.addWidget(self.web_view)
            self.new_tab_page = None

        self.setLayout(layout)

    def inject_password_detection(self):
        script = """
            document.addEventListener('submit', function(e) {
                const form = e.target;
                const inputs = form.querySelectorAll('input');
                let formData = {};

                inputs.forEach(input => {
                    if (input.type === 'password' && input.value) {
                        formData.password = input.value;
                        const usernameInput = form.querySelector('input[type="text"], input[type="email"], input[name*="user"]');
                        if (usernameInput) {
                            formData.username = usernameInput.value;
                        }
                    }
                });

                if (formData.password && formData.username) {
                    window.external.invoke(JSON.stringify({
                        type: 'password_submission',
                        data: formData
                    }));
                }
            }, true);
        """

        self.web_view.page().runJavaScript(script)

    def handle_fullscreen_request(self, request):
        request.accept()
        if request.toggleOn():
            self.main_browser.showFullScreen()
            if hasattr(self.main_browser, 'nav_toolbar'):
                self.main_browser.nav_toolbar.hide()
        else:
            self.main_browser.showNormal()
            if hasattr(self.main_browser, 'nav_toolbar'):
                self.main_browser.nav_toolbar.show()


    def optimize_webview(self):
        if not getattr(self, "web_view", None):
            return
        page = self.web_view.page()
        settings = page.settings()

        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)

        profile = QWebEngineProfile.defaultProfile()
        def clear_cache():
            profile.clearHttpCache()
            profile.clearAllVisitedLinks()
        QTimer.singleShot(1000 * 60 * 10, clear_cache)
        page.setBackgroundColor(Qt.GlobalColor.transparent)


class SetupWizard(QDialog):
    finished = Signal()

    def __init__(self, browser):
        super().__init__()
        print("setup: starting...")
        self.browser = browser
        self.translator = browser.translator
        self.setWindowTitle(self.translator.tr("setup_wizard", "Setup Cat Browser"))
        self.setFixedSize(600, 500)
        self.setStyleSheet("""
            QDialog {
                background: #1a1a1a;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 500;
            }
            QComboBox, QCheckBox {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #106ebe;
            }
            QPushButton:pressed {
                background: #005a9e;
            }
        """)

        self.setup_steps = []
        self.current_step = 0
        self.results = {}

        self.create_steps()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.show_step(0)

    def create_steps(self):
        step1_widget = QWidget()
        step1_layout = QVBoxLayout(step1_widget)
        step1_layout.setSpacing(20)

        if os.path.exists(WELCOME_IMG):
            image_label = QLabel()
            pixmap = QPixmap(WELCOME_IMG)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                step1_layout.addWidget(image_label)

        self.title1 = QLabel(self.translator.tr("welcome_title", "cat browser (real)"))
        self.title1.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        self.title1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step1_layout.addWidget(self.title1)

        self.desc1 = QLabel(self.translator.tr("setup_step1_desc", "Let's set up your browser. First, choose your preferred search engine:"))
        self.desc1.setWordWrap(True)
        step1_layout.addWidget(self.desc1)

        self.search_combo = QComboBox()
        self.search_combo.setStyleSheet("""
            QComboBox {
                background: #2d2d2d;
                color: white;
                border: 2px solid #404040;
                border-radius: 14px;
                padding: 10px;
                font-size: 16px;
            }
        """)
        for engine in self.browser.search_engines.keys():
            self.search_combo.addItem(engine)
        step1_layout.addWidget(self.search_combo)

        self.setup_steps.append(step1_widget)
        step2_widget = QWidget()
        step2_layout = QVBoxLayout(step2_widget)
        step2_layout.setSpacing(20)

        self.title2 = QLabel(self.translator.tr("setup_step2_title", "Choose Language"))
        self.title2.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        self.title2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step2_layout.addWidget(self.title2)

        self.desc2 = QLabel(self.translator.tr("setup_step2_desc", "Select your preferred language for the browser interface:"))
        self.desc2.setWordWrap(True)
        step2_layout.addWidget(self.desc2)

        self.language_combo = QComboBox()
        self.language_combo.setStyleSheet("""
            QComboBox {
                background: #2d2d2d;
                color: white;
                border: 2px solid #404040;
                border-radius: 14px;
                padding: 10px;
                font-size: 16px;
            }
        """)
        for lang in self.translator.languages.keys():
            self.language_combo.addItem(lang)


        current_index = self.language_combo.findText(self.translator.current_lang)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)


        self.language_combo.currentTextChanged.connect(self.update_language)

        step2_layout.addWidget(self.language_combo)
        step2_layout.addStretch()

        self.setup_steps.append(step2_widget)


        step3_widget = QWidget()
        step3_layout = QVBoxLayout(step3_widget)
        step3_layout.setSpacing(20)

        self.title3 = QLabel(self.translator.tr("setup_step3_title", "Password Import"))
        self.title3.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        self.title3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step3_layout.addWidget(self.title3)

        self.desc3 = QLabel(self.translator.tr("setup_step3_desc", "Would you like to import passwords from a CSV file?\n\nYou can skip this and do it later from Settings."))
        self.desc3.setWordWrap(True)
        step3_layout.addWidget(self.desc3)


        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.import_btn = QPushButton(self.translator.tr("import_csv", "Import CSV"))
        self.skip_btn = QPushButton(self.translator.tr("skip", "Skip"))

        self.import_btn.setStyleSheet("""
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #106ebe;
            }
            QPushButton:pressed {
                background: #005a9e;
            }
        """)

        self.skip_btn.setStyleSheet("""
            QPushButton {
                background: #555;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #666;
            }
            QPushButton:pressed {
                background: #444;
            }
        """)

        self.import_btn.clicked.connect(self.import_passwords_dialog)
        self.skip_btn.clicked.connect(self.skip_passwords)

        button_layout.addStretch()
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.skip_btn)
        button_layout.addStretch()

        step3_layout.addLayout(button_layout)
        step3_layout.addStretch()

        self.setup_steps.append(step3_widget)


        step4_widget = QWidget()
        step4_layout = QVBoxLayout(step4_widget)
        step4_layout.setSpacing(20)

        self.title4 = QLabel(self.translator.tr("setup_step4_title", "Welcome Screen"))
        self.title4.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        self.title4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step4_layout.addWidget(self.title4)

        self.desc4 = QLabel(self.translator.tr("setup_step4_desc", "Show welcome screen on startup?\n\nYou can change this later in Settings."))
        self.desc4.setWordWrap(True)
        step4_layout.addWidget(self.desc4)

        self.welcome_checkbox = QCheckBox(self.translator.tr("show_welcome", "Show welcome screen on startup"))
        self.welcome_checkbox.setChecked(True)
        self.welcome_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 16px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        step4_layout.addWidget(self.welcome_checkbox)
        step4_layout.addStretch()
        self.setup_steps.append(step4_widget)


        step5_widget = QWidget()
        step5_layout = QVBoxLayout(step5_widget)
        step5_layout.setSpacing(20)

        self.title5 = QLabel(self.translator.tr("setup_complete", "Setup Complete! "))
        self.title5.setStyleSheet("font-size: 28px; font-weight: bold; color: #00cc00;")
        self.title5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step5_layout.addWidget(self.title5)

        self.desc5 = QLabel(self.translator.tr("setup_ready", "Your browser is ready to use!\n\nEnjoy your stay with Cat Browser!"))
        self.desc5.setStyleSheet("font-size: 18px;")
        self.desc5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc5.setWordWrap(True)
        step5_layout.addWidget(self.desc5)




        self.credits_btn = QPushButton(self.translator.tr("see_credits", "See Credits"))
        self.credits_btn.setStyleSheet("""
            QPushButton {
                background: #555;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: #666;
            }
            QPushButton:pressed {
                background: #444;
            }
        """)
        self.credits_btn.clicked.connect(self.show_credits)
        step5_layout.addWidget(self.credits_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        step5_layout.addStretch()
        self.setup_steps.append(step5_widget)

    def update_language(self, lang_name):

        print(f"settings: updating language to {lang_name}")
        if self.translator.set_language(lang_name):

            self.setWindowTitle(self.translator.tr("setup_wizard", "Setup Cat Browser"))


            self.title1.setText(self.translator.tr("welcome_title", "cat browser (real)"))
            self.desc1.setText(self.translator.tr("setup_step1_desc", "Let's set up your browser. First, choose your preferred search engine:"))

            self.title2.setText(self.translator.tr("setup_step2_title", "Choose Language"))
            self.desc2.setText(self.translator.tr("setup_step2_desc", "Select your preferred language for the browser interface:"))

            self.title3.setText(self.translator.tr("setup_step3_title", "Password Import"))
            self.desc3.setText(self.translator.tr("setup_step3_desc", "Would you like to import passwords from a CSV file?\n\nYou can skip this and do it later from Settings."))
            self.import_btn.setText(self.translator.tr("import_csv", "Import CSV"))
            self.skip_btn.setText(self.translator.tr("skip", "Skip"))

            self.title4.setText(self.translator.tr("setup_step4_title", "Welcome Screen"))
            self.desc4.setText(self.translator.tr("setup_step4_desc", "Show welcome screen on startup?\n\nYou can change this later in Settings."))
            self.welcome_checkbox.setText(self.translator.tr("show_welcome", "Show welcome screen on startup"))

            self.title5.setText(self.translator.tr("setup_complete", "Setup Complete! "))
            self.desc5.setText(self.translator.tr("setup_ready", "Your browser is ready to use!\n\nEnjoy your stay with Cat Browser!"))
            self.credits_btn.setText(self.translator.tr("see_credits", "See Credits"))


            self.update_navigation_buttons()

    def update_navigation_buttons(self):

        pass

    def show_step(self, step_index):

        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                widget = child.widget()
                widget.setParent(None)


        if step_index < len(self.setup_steps):
            self.layout.addWidget(self.setup_steps[step_index])


        if step_index != 2:
            button_layout = QHBoxLayout()

            if step_index > 0:
                back_text = self.translator.tr("back", "Back")
                back_btn = QPushButton(back_text)
                back_btn.clicked.connect(lambda checked, idx=step_index-1: self.show_step(idx))
                button_layout.addWidget(back_btn)

            button_layout.addStretch()

            if step_index < len(self.setup_steps) - 1:
                if step_index < len(self.setup_steps) - 2:
                    next_text = self.translator.tr("next", "Next")
                else:
                    next_text = self.translator.tr("finish", "Finish")
                next_btn = QPushButton(next_text)
                next_btn.clicked.connect(lambda checked, idx=step_index: self.next_step(idx))
                button_layout.addWidget(next_btn)
            else:
                finish_text = self.translator.tr("start_browsing", "Start Browsing!")
                finish_btn = QPushButton(finish_text)
                finish_btn.clicked.connect(self.finish_setup)
                button_layout.addWidget(finish_btn)

            self.layout.addLayout(button_layout)

        self.current_step = step_index

    def next_step(self, current_step):
        if current_step == 0:
            self.results['search_engine'] = self.search_combo.currentText()
        elif current_step == 1:

            selected_lang = self.language_combo.currentText()
            self.results['language'] = selected_lang
        elif current_step == 3:
            self.results['show_welcome'] = self.welcome_checkbox.isChecked()

        if current_step != 2:
            self.show_step(current_step + 1)

    def skip_passwords(self):

        self.show_step(3)

    def show_credits(self):

        credits_dialog = QDialog(self)
        credits_dialog.setWindowTitle(self.translator.tr("credits_title", "cat browser credits"))
        credits_dialog.setFixedSize(600, 600)
        credits_dialog.setStyleSheet("""
            QDialog {
                background: #1a1a1a;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: #106ebe;
            }
        """)

        layout = QVBoxLayout(credits_dialog)

        title = QLabel(self.translator.tr("credits_title", "cat browser credits"))
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)


        credits_text = QLabel()
        credits_text.setTextFormat(Qt.TextFormat.RichText)
        credits_text.setWordWrap(True)
        credits_text.setText(f"""
        <div style='text-align: center;'>
        <h3>{self.translator.tr('development_team', 'Development Team')}</h3>
        <p><b>anameless_guy - Discord</b> - {self.translator.tr('developer', 'dev')}</p>
        <p><b>monoes1 - Discord</b> - {self.translator.tr('download manager dev', 'download_manager_dev')}</p>
        <h3>{self.translator.tr('translators', 'Translators')}</h3>
        <p><b>alex.ggiscool - Discord</b></p>
        <p><b>nmlsspersonn1033 - Discord / @nmlssperson1033 - Telegram</b></p>
        <p><b>monoes1 - Discord</b></p>
        <p><b>rizakai - Discord</b></p>


        <h3>{self.translator.tr('special_thanks', 'Special Thanks')}</h3>
        <p>PyQt6 Team  - {self.translator.tr('for_webengine', 'For the WebEngine')}</p>

        </div>
        """)
        credits_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credits_text)

        close_text = self.translator.tr("close", "Close")
        close_btn = QPushButton(close_text)
        close_btn.clicked.connect(credits_dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        credits_dialog.exec()

    def finish_setup(self):

        if 'search_engine' in self.results:
            self.browser.set_search_engine(self.results['search_engine'])

        if 'language' in self.results:
            self.browser.translator.set_language(self.results['language'])
            self.browser.settings['language'] = self.results['language']

        if 'show_welcome' in self.results:
            self.browser.settings['show_welcome_screen'] = self.results['show_welcome']

        self.browser.save_settings()


        with open(SETUP_FILE, 'w') as f:
            json.dump({'completed': True}, f)

        self.finished.emit()
        self.accept()

    def import_passwords_dialog(self):
        title = self.translator.tr("import_passwords", "Import Passwords")
        file_filter = self.translator.tr("csv_files", "CSV Files (*.csv)")
        path, _ = QFileDialog.getOpenFileName(self, title, "", file_filter)

        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if "name" in row and "username" in row and "password" in row:
                            self.browser.passwords[row["name"]] = {
                                "user": row["username"],
                                "pass": row["password"]
                            }
                self.browser.save_passwords()
                success_title = self.translator.tr("success", "Success")
                success_msg = self.translator.tr("passwords_imported", "Passwords imported successfully!")
                QMessageBox.information(self, success_title, success_msg)
            except Exception as e:
                error_title = self.translator.tr("error", "Error")
                error_msg = self.translator.tr("import_failed", "Failed to import passwords: {}").format(str(e))
                QMessageBox.warning(self, error_title, error_msg)


        self.show_step(3)

class Translator:
    def __init__(self):
        self.languages = {}
        self.current_lang = "English"
        self.load_languages()

    def load_languages(self):
        if os.path.exists(LANGUAGES_FILE):
            try:
                with open(LANGUAGES_FILE, 'r', encoding='utf-8') as f:
                    current_lang = None
                    current_dict = {}

                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        if line.startswith('[') and line.endswith(']'):
                            if current_lang and current_dict:
                                self.languages[current_lang] = current_dict
                            current_lang = line[1:-1]
                            current_dict = {}
                        elif '=' in line:
                            key, value = line.split('=', 1)
                            current_dict[key.strip()] = value.strip()

                    if current_lang and current_dict:
                        self.languages[current_lang] = current_dict

            except Exception as e:
                print(f"settings: error loading languages: {e}")

    def set_language(self, lang):
        if lang in self.languages:
            self.current_lang = lang
            return True
        return False

    def get(self, key, default=None):
        if self.current_lang in self.languages:
            return self.languages[self.current_lang].get(key, default)
        return default

    def tr(self, key, *args):
        text = self.get(key, key)
        if args:
            try:
                text = text.format(*args)
            except:
                pass
        return text

class ModernTabBar(QTabBar):
    def __init__(self):
        super().__init__()
        self.setDrawBase(False)
        self.setExpanding(False)
        self.setMovable(True)

    def tabSizeHint(self, index):
        return QSize(200, 35)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for index in range(self.count()):
            rect = self.tabRect(index)
            close_rect = QRect(rect.right() - 20, rect.center().y() - 6, 12, 12)
            if close_rect.contains(self.mapFromGlobal(self.cursor().pos())):
                painter.setBrush(Qt.GlobalColor.red)
                painter.setPen(Qt.GlobalColor.red)
                painter.drawEllipse(close_rect)
                painter.setPen(QPen(Qt.GlobalColor.white, 2))
            else:
                painter.setPen(QPen(Qt.GlobalColor.white, 1.5))
            painter.drawLine(close_rect.topLeft(), close_rect.bottomRight())
            painter.drawLine(close_rect.topRight(), close_rect.bottomLeft())

    def mousePressEvent(self, event):
        for index in range(self.count()):
            rect = self.tabRect(index)
            close_rect = QRect(rect.right() - 20, rect.center().y() - 6, 12, 12)
            if close_rect.contains(event.pos()):
                self.tabCloseRequested.emit(index)
                return
        super().mousePressEvent(event)

class WelcomeScreen(QWidget):
    finished = Signal()

    def __init__(self, duration=3000):
        super().__init__()
        print("splash screen: starting...")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #000000;")
        self.setFixedSize(659, 460)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(659, 460)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)

        video_path = os.path.join(BASE_PATH, "splash.mp4")
        print(f"splash screen: looking for video at {video_path}")
        if os.path.exists(video_path):
            print("splash screen: video found")
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.media_player.setVideoOutput(self.video_widget)
            self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
            self.media_player.play()
            print("splash screen: video playing")
        else:
            print(f"splash screen: error playing video {video_path}")
            self.finished.emit()
            QTimer.singleShot(100, self.close)
            return

        layout.addWidget(self.video_widget)
        self.setLayout(layout)
        self.duration = duration

        self.close_timer = QTimer()
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.close_splash)
        self.close_timer.start(duration)


    def on_media_status_changed(self, status):
        from PyQt6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.finished.emit()
            self.close_splash()

    def close_splash(self):

        print("splash screen:: video ended")
        if hasattr(self, 'close_timer'):
            self.close_timer.stop()
        if hasattr(self, 'media_player'):
            self.media_player.stop()
        self.finished.emit()
        self.close()

    def closeEvent(self, event):


        self.close_splash()
        event.accept()

class SettingsTab(QWidget):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.translator = browser.translator

        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
            }
        """)

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: #1a1a1a;")
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(10,10,10,10)
        self.main_layout.setSpacing(15)

        title = QLabel(self.translator.tr("settings", "Settings"))
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            background-color: transparent;
            padding: 5px;
        """)
        self.main_layout.addWidget(title)

        version_label = QLabel("version: 0.9.1")
        version_label.setStyleSheet("""
            color: #b0b0b0;
            font-size: 12px;
            font-weight: normal;
            background-color: transparent;
            padding: 2px;
        """)
        self.main_layout.addWidget(version_label)

        tab_count_label = QLabel(self.translator.tr("tabs_count", "{}").format(self.browser.tabs.count()))
        tab_count_label.setStyleSheet("""
            color: #e0e0e0;
            font-size: 16px;
            background-color: transparent;
        """)
        self.main_layout.addWidget(tab_count_label)

        self.ram_label = QLabel("RAM: 0 MB")
        self.ram_label.setStyleSheet("""
            color: #e0e0e0;
            font-size: 16px;
            background-color: transparent;
        """)
        self.main_layout.addWidget(self.ram_label)

        self.version = QLabel("0.9.1")
        self.version.setStyleSheet("""
            color: #e0e0e0;
            font-size: 16px;
            background-color: transparent;
        """)

        self.ram_timer = QTimer()
        self.ram_timer.timeout.connect(self.update_ram_usage)
        self.ram_timer.start(1000)

        group_box_style = """
            QGroupBox {
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2a2a2a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
                background-color: transparent;
            }
        """

        checkbox_style = """
            QCheckBox {
                color: #e0e0e0;
                font-size: 14px;
                spacing: 8px;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #555;
                border-radius: 14px;
                background: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background: #0078d4;
                border: 2px solid #0078d4;
            }
            QCheckBox::indicator:checked:hover {
                background: #106ebe;
                border: 2px solid #106ebe;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #777;
            }
        """

        general_group = QGroupBox(self.translator.tr("general", "General Settings"))
        general_group.setStyleSheet(group_box_style)
        general_layout = QFormLayout(general_group)
        general_layout.setSpacing(10)

        label_style = """
            QLabel {
                color: #e0e0e0;
                background-color: transparent;
                padding: 3px;
            }
        """

        language_label = QLabel(self.translator.tr("language", "Language:"))
        language_label.setStyleSheet(label_style)
        self.language_combo = QComboBox()
        self.language_combo.setStyleSheet("""
            QComboBox {
                background: #3c3c3c;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid #666;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background: #3c3c3c;
                color: white;
                border: 1px solid #555;
                selection-background-color: #0078d4;
            }
        """)

        for lang in self.translator.languages.keys():
            self.language_combo.addItem(lang)

        current_index = self.language_combo.findText(self.translator.current_lang)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)

        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        general_layout.addRow(language_label, self.language_combo)

        search_label = QLabel(self.translator.tr("search_engine", "Search Engine:"))
        search_label.setStyleSheet(label_style)
        self.search_combo = QComboBox()
        self.search_combo.setStyleSheet(self.language_combo.styleSheet())

        for engine_name in self.browser.search_engines.keys():
            self.search_combo.addItem(engine_name)

        current_engine = self.browser.current_search_engine
        engine_index = self.search_combo.findText(current_engine)
        if engine_index >= 0:
            self.search_combo.setCurrentIndex(engine_index)

        self.search_combo.currentTextChanged.connect(self.on_search_engine_changed)
        general_layout.addRow(search_label, self.search_combo)

        theme_label = QLabel(self.translator.tr("theme", "Theme:"))
        theme_label.setStyleSheet(label_style)
        theme_container = QWidget()
        theme_container.setStyleSheet("background-color: transparent;")
        theme_container_layout = QVBoxLayout(theme_container)
        theme_container_layout.setContentsMargins(0,0,0,0)
        theme_container_layout.setSpacing(5)

        self.theme_combo = QComboBox()
        self.theme_combo.setStyleSheet(self.language_combo.styleSheet())
        self.theme_combo.addItem(self.translator.tr("default_theme", "Default Theme"))

        for theme_name in self.browser.themes.keys():
            self.theme_combo.addItem(theme_name)

        current_theme = self.browser.settings.get("theme", self.translator.tr("default_theme", "Default Theme"))
        theme_index = self.theme_combo.findText(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)

        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_container_layout.addWidget(self.theme_combo)

        general_layout.addRow(theme_label, theme_container)
        self.main_layout.addWidget(general_group)

        sound_group = QGroupBox(self.translator.tr("sound_settings", "Sound Effects"))
        sound_group.setStyleSheet(group_box_style)
        sound_layout = QVBoxLayout(sound_group)
        sound_layout.setSpacing(8)

        self.sound_checkbox = QCheckBox(self.translator.tr("enable_sounds", "Enable Sound Effects"))
        self.sound_checkbox.setChecked(self.browser.settings.get("sound_enabled", True))
        self.sound_checkbox.setStyleSheet(checkbox_style)
        self.sound_checkbox.stateChanged.connect(self.on_sound_setting_changed)
        sound_layout.addWidget(self.sound_checkbox)

        self.main_layout.addWidget(sound_group)

        startup_group = QGroupBox(self.translator.tr("startup_settings", "Startup Settings"))
        startup_group.setStyleSheet(group_box_style)
        startup_layout = QVBoxLayout(startup_group)
        startup_layout.setSpacing(8)

        self.welcome_checkbox = QCheckBox(self.translator.tr("show_welcome", "Show welcome screen on startup"))
        self.welcome_checkbox.setChecked(self.browser.settings.get("show_welcome_screen", True))
        self.welcome_checkbox.setStyleSheet(checkbox_style)
        self.welcome_checkbox.stateChanged.connect(self.on_welcome_setting_changed)
        startup_layout.addWidget(self.welcome_checkbox)

        self.restore_session_checkbox = QCheckBox(self.translator.tr("restore_session", "Restore tabs from previous session"))
        self.restore_session_checkbox.setChecked(self.browser.settings.get("restore_session", True))
        self.restore_session_checkbox.setStyleSheet(checkbox_style)
        self.restore_session_checkbox.stateChanged.connect(self.on_restore_session_changed)
        startup_layout.addWidget(self.restore_session_checkbox)

        self.vertical_tabs_checkbox = QCheckBox(self.translator.tr("vertical_tabs", "Vertical tabs"))
        self.vertical_tabs_checkbox.setChecked(self.browser.settings.get("vertical_tabs", False))
        self.vertical_tabs_checkbox.setStyleSheet(checkbox_style)
        self.vertical_tabs_checkbox.stateChanged.connect(self.on_vertical_tabs_changed)
        startup_layout.addWidget(self.vertical_tabs_checkbox)

        self.main_layout.addWidget(startup_group)

        crash_group = QGroupBox(self.translator.tr("crash_handler_settings", "Crash Handler"))
        crash_group.setStyleSheet(group_box_style)
        crash_layout = QVBoxLayout(crash_group)
        crash_layout.setSpacing(8)

        self.crash_handler_checkbox = QCheckBox(self.translator.tr("enable_crash_handler", "Enable crash handler (catch crashes instead of closing)"))
        self.crash_handler_checkbox.setChecked(self.browser.settings.get("crash_handler_enabled", True))
        self.crash_handler_checkbox.setStyleSheet(checkbox_style)
        self.crash_handler_checkbox.stateChanged.connect(self.on_crash_handler_changed)
        crash_layout.addWidget(self.crash_handler_checkbox)

        crash_handler_desc = QLabel(self.translator.tr("crash_handler_desc", "When enabled, catches crashes and prevents the browser from closing unexpectedly. When disabled, browser will close on fatal errors."))
        crash_handler_desc.setWordWrap(True)
        crash_handler_desc.setStyleSheet("color: #999; font-size: 12px; background: transparent; margin-left: 24px;")
        crash_layout.addWidget(crash_handler_desc)

        crash_layout.addSpacing(10)

        self.crash_dialog_checkbox = QCheckBox(self.translator.tr("show_crash_dialog", "Show crash dialog popup"))
        self.crash_dialog_checkbox.setChecked(self.browser.settings.get("crash_dialog_enabled", True))
        self.crash_dialog_checkbox.setStyleSheet(checkbox_style)
        self.crash_dialog_checkbox.stateChanged.connect(self.on_crash_dialog_changed)
        crash_layout.addWidget(self.crash_dialog_checkbox)

        crash_dialog_desc = QLabel(self.translator.tr("crash_dialog_desc", "When enabled, shows a popup dialog with crash details and options to save logs. When disabled, crashes are only logged to console."))
        crash_dialog_desc.setWordWrap(True)
        crash_dialog_desc.setStyleSheet("color: #999; font-size: 12px; background: transparent; margin-left: 24px;")
        crash_layout.addWidget(crash_dialog_desc)

        self.main_layout.addWidget(crash_group)

        memory_group = QGroupBox(self.translator.tr("memory_settings", "Memory Settings"))
        memory_group.setStyleSheet(group_box_style)
        memory_layout = QVBoxLayout(memory_group)
        memory_layout.setSpacing(8)

        self.memory_saver_checkbox = QCheckBox(self.translator.tr("memory_saver", "Memory Saver (unloads inactive tabs after 5 minutes)"))
        self.memory_saver_checkbox.setChecked(self.browser.settings.get("memory_saver", False))
        self.memory_saver_checkbox.setStyleSheet(checkbox_style)
        self.memory_saver_checkbox.stateChanged.connect(self.on_memory_saver_changed)
        memory_layout.addWidget(self.memory_saver_checkbox)

        self.main_layout.addWidget(memory_group)

        extensions_group = QGroupBox(self.translator.tr("extensions", "Extensions"))
        extensions_group.setStyleSheet(group_box_style)
        extensions_layout = QVBoxLayout(extensions_group)
        extensions_layout.setSpacing(10)

        self.extensions_enabled_checkbox = QCheckBox(self.translator.tr("enable_extensions", "Enable Extensions"))
        extensions_enabled = self.browser.settings.get("extensions_enabled", True)
        self.extensions_enabled_checkbox.setChecked(extensions_enabled)
        self.extensions_enabled_checkbox.setStyleSheet(checkbox_style)
        self.extensions_enabled_checkbox.stateChanged.connect(self.on_extensions_enabled_changed)
        extensions_layout.addWidget(self.extensions_enabled_checkbox)

        self.ext_text = QTextEdit()
        self.ext_text.setReadOnly(True)
        self.ext_text.setMaximumHeight(150)
        self.ext_text.setStyleSheet("""
            QTextEdit {
                background: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                selection-background-color: #0078d4;
            }
            QScrollBar:vertical {
                background: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666;
            }
        """)
        extensions_layout.addWidget(self.ext_text)

        ext_buttons_layout = QHBoxLayout()

        self.reload_ext_btn = QPushButton(self.translator.tr("reload_extensions", "Reload Extensions"))

        button_style = """
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
                margin-right: 5px;
            }
            QPushButton:hover { background: #106ebe; }
            QPushButton:pressed { background: #005a9e; }
            QPushButton:disabled {
                background: #555;
                color: #999;
            }
        """

        self.reload_ext_btn.setStyleSheet(button_style)
        self.reload_ext_btn.clicked.connect(self.reload_extensions)

        ext_buttons_layout.addWidget(self.reload_ext_btn)
        ext_buttons_layout.addStretch()

        extensions_layout.addLayout(ext_buttons_layout)
        self.main_layout.addWidget(extensions_group)

        passwords_group = QGroupBox(self.translator.tr("passwords", "Passwords"))
        passwords_group.setStyleSheet(group_box_style)
        passwords_layout = QVBoxLayout(passwords_group)
        passwords_layout.setSpacing(10)

        pw_buttons_layout = QHBoxLayout()
        self.import_btn = QPushButton(self.translator.tr("import_csv", "Import CSV"))
        self.export_btn = QPushButton(self.translator.tr("export_csv", "Export CSV"))

        self.import_btn.setStyleSheet(button_style)
        self.export_btn.setStyleSheet(button_style)

        self.import_btn.clicked.connect(self.import_csv)
        self.export_btn.clicked.connect(self.export_csv)

        pw_buttons_layout.addWidget(self.import_btn)
        pw_buttons_layout.addWidget(self.export_btn)
        pw_buttons_layout.addStretch()
        passwords_layout.addLayout(pw_buttons_layout)

        self.pw_text = QTextEdit()
        self.pw_text.setReadOnly(True)
        self.pw_text.setMaximumHeight(150)
        self.pw_text.setStyleSheet(self.ext_text.styleSheet())
        passwords_layout.addWidget(self.pw_text)
        self.update_pw_view()
        self.main_layout.addWidget(passwords_group)

        history_group = QGroupBox(self.translator.tr("history", "History"))
        history_group.setStyleSheet(group_box_style)
        history_layout = QVBoxLayout(history_group)
        history_layout.setSpacing(10)
        self.clear_history_btn = QPushButton(self.translator.tr("clear_history", "Clear History"))
        self.clear_history_btn.setStyleSheet(button_style)
        self.clear_history_btn.clicked.connect(self.clear_history)
        self.clear_history_btn.setFixedWidth(190)
        history_layout.addWidget(self.clear_history_btn)
        self.view_history_btn = QPushButton(self.translator.tr("view_history", "View History"))
        self.view_history_btn.setStyleSheet(button_style)
        self.view_history_btn.setFixedWidth(190)
        self.view_history_btn.clicked.connect(lambda: self.browser._open_cat_browser_page("cat-browser://history"))
        history_layout.addWidget(self.view_history_btn)
        self.main_layout.addWidget(history_group)
        reset_group = QGroupBox("Reset")
        reset_group.setStyleSheet(group_box_style)
        reset_layout = QVBoxLayout(reset_group)
        reset_layout.setSpacing(8)

        self.reset_settings_btn = QPushButton(self.translator.tr("restore_default_settings", "Restore default settings"))
        self.reset_settings_btn.setStyleSheet(button_style)
        self.reset_settings_btn.clicked.connect(self.reset_settings)
        reset_layout.addWidget(self.reset_settings_btn)
        self.reset_settings_btn.setFixedWidth(340)
        self.clear_data_btn = QPushButton(self.translator.tr("clear_all_data", "Clear all data"))
        self.clear_data_btn.setStyleSheet("""
            QPushButton {
                background: #c0392b;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
                margin-right: 5px;
            }
            QPushButton:hover { background: #e74c3c; }
            QPushButton:pressed { background: #922b21; }
        """)
        self.clear_data_btn.clicked.connect(self.clear_all_data)
        reset_layout.addWidget(self.clear_data_btn)
        self.clear_data_btn.setFixedWidth(220)
        self.main_layout.addWidget(reset_group)
        self.main_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.main_widget)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

        self.update_extensions_view()
        self.update_extension_buttons_state()

    def on_crash_handler_changed(self, state):
        enabled = (state == Qt.CheckState.Checked.value)
        self.browser.settings["crash_handler_enabled"] = enabled
        self.browser.save_settings()
        print(f"settings: crash handler {'enabled' if enabled else 'disabled'}")
        if not enabled:
            QMessageBox.warning(
                self,
                "warning",
                "disabling the crash handler will make the browser close even when small errors happen"
        )

    def on_crash_dialog_changed(self, state):
        enabled = (state == Qt.CheckState.Checked.value)
        self.browser.settings["crash_dialog_enabled"] = enabled
        self.browser.save_settings()
        print(f"settings: crash dialog {'enabled' if enabled else 'disabled'}")

    def clear_history(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(self.translator.tr("clear_history", "Clear History"))
        msg.setText(self.translator.tr("clear_history_msg", "i bet you're doing this so that no one knows you gooned"))
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.browser.history = []
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)

    def reset_settings(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(self.translator.tr("restore_default_settings", "Restore Default Settings"))
        msg.setText(self.translator.tr("restore_default_settings_msg", "this will reset your settings to default, no data will be deleted, are you sure"))
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            for f in [SETTINGS_FILE, SEARCH_ENGINE_FILE]:
                if os.path.exists(f):
                    os.remove(f)
            self.browser.settings = self.browser.load_settings()
            self.browser.current_search_engine = self.browser.load_search_engine()
            self.browser.update_url_bar_placeholder()
            done = QMessageBox(self)
            done.setWindowTitle(self.translator.tr("done", "Done"))
            done.setText(self.translator.tr("settings_restored", "Settings restored to default."))
            done.exec()

    def clear_all_data(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(self.translator.tr("clear_all_data", "Clear All Data"))
        msg.setText(self.translator.tr("clear_all_data_msg", "this will delete basically everything, your cookies, your logged in accounts, and your extensions and themes and settings, are you sure vroo?"))
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            import shutil
            if os.path.exists(DATA_DIR):
                shutil.rmtree(DATA_DIR)
            done = QMessageBox(self)
            done.setWindowTitle(self.translator.tr("done", "Done"))
            done.setText(self.translator.tr("clear_all_data_done", "All data cleared. The browser will now close."))
            done.exec()
            self.browser.close()
    def on_sound_setting_changed(self, state):
        enabled = (state == Qt.CheckState.Checked.value)
        self.browser.settings["sound_enabled"] = enabled
        self.browser.save_settings()
        if hasattr(self.browser, 'sound_manager'):
            self.browser.sound_manager.set_enabled(enabled)

    def update_ram_usage(self):
        process = psutil.Process(os.getpid())
        ram_mb = process.memory_info().rss / 1024**2
        self.ram_label.setText(f"RAM: {ram_mb:.1f} MB")

    def on_language_changed(self, lang):
        if self.translator.set_language(lang):
            self.browser.save_settings()
            self.browser.update_language()

    def on_welcome_setting_changed(self, state):
        self.browser.settings["show_welcome_screen"] = (state == Qt.CheckState.Checked.value)
        self.browser.save_settings()

    def on_search_engine_changed(self, engine_name):
        self.browser.set_search_engine(engine_name)

    def on_theme_changed(self, theme_name):
        self.browser.set_theme(theme_name)

    def on_memory_saver_changed(self, state):
        self.browser.settings["memory_saver"] = (state == Qt.CheckState.Checked.value)
        self.browser.save_settings()
        self.browser.enable_memory_saver(state == Qt.CheckState.Checked.value)

    def on_restore_session_changed(self, state):
        self.browser.settings["restore_session"] = (state == Qt.CheckState.Checked.value)
        self.browser.save_settings()

    def on_vertical_tabs_changed(self, state):
        enabled = (state == Qt.CheckState.Checked.value)
        self.browser.settings["vertical_tabs"] = enabled
        self.browser.save_settings()
        if hasattr(self.browser, 'vtab_bar') and hasattr(self.browser, 'tabs'):
            vtab = self.browser.vtab_bar
            tabs = self.browser.tabs
            if enabled:
                for entry in list(vtab.entries):
                    entry.deleteLater()
                vtab.entries.clear()
                for i in range(tabs.count()):
                    label = tabs.tabText(i)
                    icon = tabs.tabIcon(i)
                    vtab.add_tab_entry(i, label, icon if not icon.isNull() else None)
                vtab.set_current(tabs.currentIndex())
            vtab.setVisible(enabled)
            tabs.tabBar().setVisible(not enabled)
    def on_extensions_enabled_changed(self, state):
        enabled = (state == Qt.CheckState.Checked.value)
        self.browser.settings["extensions_enabled"] = enabled
        self.browser.save_settings()
        self.browser.profile.scripts().clear()

        if enabled:
            self.browser.inject_extensions_into_profile()
            print("extension engine: extensions enabled and injected")
        else:
            print("extension engine: extensions disabled and cleared")

        self.update_extension_buttons_state()
        self.update_extensions_view()

        if enabled:
            self.show_status_message("Extensions enabled")
        else:
            self.show_status_message("Extensions disabled")

    def update_extension_buttons_state(self):
        enabled = self.browser.settings.get("extensions_enabled", True)
        self.reload_ext_btn.setEnabled(enabled)
        self.ext_text.setEnabled(enabled)

    def show_status_message(self, message):
        print(f"status: {message}")

    def update_extensions_view(self):
        enabled = self.browser.settings.get("extensions_enabled", True)

        if not self.browser.extensions:
            if enabled:
                self.ext_text.setText(self.translator.tr("no_extensions", "No extensions loaded."))
            else:
                self.ext_text.setText(self.translator.tr("extensions_disabled", "Extensions are currently disabled."))
        else:
            ext_info = ""
            if not enabled:
                ext_info += self.translator.tr("extensions_disabled_note", "Extensions are disabled (will not execute)\n\n")

            ext_info += self.translator.tr("loaded_extensions", "Loaded Extensions: \n\n")
            for ext_name, ext_data in self.browser.extensions.items():
                status = "✓" if enabled else "✗"
                ext_info += f"{status} {ext_name}\n"
                ext_info += self.translator.tr("description", "  Description: {}").format(ext_data.get('description', 'No description')) + "\n"
                ext_info += self.translator.tr("version", "  Version: {}").format(ext_data.get('version', '1.0')) + "\n"
                ext_info += f"  Script: {ext_data.get('script', 'No script')}\n\n"
            self.ext_text.setText(ext_info)

    def reload_extensions(self):
        if not self.browser.settings.get("extensions_enabled", True):
            return

        if hasattr(self.browser, 'reload_extensions'):
            self.browser.reload_extensions()
        self.update_extensions_view()
        self.show_status_message("Extensions reloaded")

    def update_pw_view(self):
        s = ""
        for site,info in self.browser.passwords.items():
            s += f"{site} - {info['user']} / {info['pass']}\n"
        self.pw_text.setText(s)

    def import_csv(self):
        path,_ = QFileDialog.getOpenFileName(self,
            self.translator.tr("import_passwords", "Import Passwords"),
            "",
            self.translator.tr("csv_files", "CSV Files (*.csv)"))
        if path:
            with open(path,"r",encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.browser.passwords[row["name"]] = {"user":row["username"], "pass":row["password"]}
            self.update_pw_view()

    def export_csv(self):
        path,_ = QFileDialog.getSaveFileName(self,
            self.translator.tr("export_passwords", "Export Passwords"),
            "",
            self.translator.tr("csv_files", "CSV Files (*.csv)"))
        if path:
            with open(path,"w",newline="",encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name","url","username","password","note"])
                for name,info in self.browser.passwords.items():
                    writer.writerow([name,"",info["user"],info["pass"],""])
            self.update_pw_view()

class VerticalTabEntry(QWidget):
    clicked = Signal(int)
    close_requested = Signal(int)

    def __init__(self, index, title, icon=None, parent=None):
        super().__init__(parent)
        self.tab_index = index
        self._selected = False
        self._hovered = False
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

        row = QHBoxLayout(self)
        row.setContentsMargins(8, 4, 4, 4)
        row.setSpacing(8)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(18, 18)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent; border: none;")
        row.addWidget(self.icon_label)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("background: transparent; border: none; color: #ccc; font-size: 12px;")
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        row.addWidget(self.title_label, 1)

        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #888; font-size: 14px; font-weight: bold; border-radius: 8px; padding: 0; }
            QPushButton:hover { background: #c0392b; color: white; }
        """)
        self.close_btn.clicked.connect(lambda: self.close_requested.emit(self.tab_index))
        row.addWidget(self.close_btn)

        if icon:
            self.set_icon(icon)
        else:
            self._set_fallback(title)
        self._refresh_style()

    def set_icon(self, icon):
        if not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(16, 16))
            self.icon_label.setText("")
            self.icon_label.setStyleSheet("background: transparent; border: none;")
        else:
            self._set_fallback(self.title_label.text())

    def set_title(self, title):
        self.title_label.setText(title)
        if not self.icon_label.pixmap() or self.icon_label.pixmap().isNull():
            self._set_fallback(title)

    def set_selected(self, selected):
        self._selected = selected
        self._refresh_style()

    def set_collapsed(self, collapsed):
        self.title_label.setVisible(not collapsed)
        self.close_btn.setVisible(not collapsed)

    def _set_fallback(self, title):
        letter = title[0].upper() if title else "?"
        self.icon_label.setText(letter)
        self.icon_label.setStyleSheet("background: #0078d4; color: white; font-size: 10px; font-weight: bold; border-radius: 9px; border: none;")

    def _refresh_style(self):
        if self._selected:
            bg, border = "#2a4a6a", "border-left: 3px solid #0078d4;"
        elif self._hovered:
            bg, border = "#3a3a3a", "border-left: 3px solid transparent;"
        else:
            bg, border = "transparent", "border-left: 3px solid transparent;"
        self.setStyleSheet(f"VerticalTabEntry {{ background: {bg}; {border} border-radius: 4px; }}")

    def enterEvent(self, e):
        self._hovered = True; self._refresh_style(); super().enterEvent(e)

    def leaveEvent(self, e):
        self._hovered = False; self._refresh_style(); super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.tab_index)
        super().mousePressEvent(e)


class VerticalTabBar(QWidget):
    tab_selected = Signal(int)
    tab_close_requested = Signal(int)
    new_tab_requested = Signal()

    EXPANDED_WIDTH = 220
    COLLAPSED_WIDTH = 42

    def __init__(self, parent=None):
        super().__init__(parent)
        self._collapsed = False
        self.entries = []
        self.setFixedWidth(self.EXPANDED_WIDTH)
        self.setStyleSheet("VerticalTabBar { background: #1e1e1e; border-right: 1px solid #333; }")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(0)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 6)
        top.setSpacing(4)

        self.toggle_btn = QPushButton("«")
        self.toggle_btn.setFixedSize(28, 28)
        self.toggle_btn.setToolTip("Collapse sidebar")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet(self._btn_style())
        self.toggle_btn.clicked.connect(self.toggle_collapsed)
        top.addWidget(self.toggle_btn)
        top.addStretch()

        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(28, 28)
        self.new_tab_btn.setToolTip("New tab (Ctrl+T)")
        self.new_tab_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_tab_btn.setStyleSheet(self._btn_style())
        self.new_tab_btn.clicked.connect(self.new_tab_requested)
        top.addWidget(self.new_tab_btn)
        outer.addLayout(top)

        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #333;")
        outer.addWidget(div)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #1e1e1e; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #444; border-radius: 3px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #555; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._vbox = QVBoxLayout(self._container)
        self._vbox.setContentsMargins(0, 4, 0, 4)
        self._vbox.setSpacing(2)
        self._vbox.addStretch()

        scroll.setWidget(self._container)
        outer.addWidget(scroll, 1)

    def add_tab_entry(self, index, title, icon=None):
        entry = VerticalTabEntry(index, title, icon)
        entry.clicked.connect(self._on_clicked)
        entry.close_requested.connect(self.tab_close_requested)
        self._vbox.insertWidget(self._vbox.count() - 1, entry)
        self.entries.append(entry)
        self._reindex()
        return entry

    def remove_tab_entry(self, index):
        entry = self._at(index)
        if entry:
            self.entries.remove(entry)
            entry.deleteLater()
            self._reindex()

    def set_current(self, index):
        for e in self.entries:
            e.set_selected(e.tab_index == index)

    def set_title(self, index, title):
        e = self._at(index)
        if e: e.set_title(title)

    def set_icon(self, index, icon):
        e = self._at(index)
        if e: e.set_icon(icon)

    def toggle_collapsed(self):
        self._collapsed = not self._collapsed
        w = self.COLLAPSED_WIDTH if self._collapsed else self.EXPANDED_WIDTH
        self.setFixedWidth(w)
        self.toggle_btn.setText("»" if self._collapsed else "«")
        self.toggle_btn.setToolTip("Expand sidebar" if self._collapsed else "Collapse sidebar")
        self.new_tab_btn.setVisible(not self._collapsed)
        for e in self.entries:
            e.set_collapsed(self._collapsed)

    def _at(self, index):
        for e in self.entries:
            if e.tab_index == index:
                return e
        return None

    def _reindex(self):
        pass 

    def _on_clicked(self, index):
        self.tab_selected.emit(index)

    @staticmethod
    def _btn_style():
        return """
            QPushButton { background: transparent; border: none; color: #aaa; font-size: 14px; font-weight: bold; border-radius: 6px; }
            QPushButton:hover { background: #333; color: white; }
            QPushButton:pressed { background: #444; }
        """


class _TopEdgeTracker(QWidget):
    def __init__(self, parent, browser):
        super().__init__(parent)
        self.browser = browser
        self.setMouseTracking(True)

    def enterEvent(self, e):
        if getattr(self.browser, '_tab_focused', False):
            self.browser._show_hover_bar()
        super().enterEvent(e)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("cat browser")
        self.resize(1280,800)
        self.watchdog_timer = QTimer()
        self.watchdog_timer.timeout.connect(self.check_browser_health)
        self.watchdog_timer.start(30000)
        self.translator = Translator()
        self.download_manager = DownloadManager(self, translator=self.translator)
        self.search_engines = {
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "DuckDuckGo": "https://duckduckgo.com/?q={}",
            "Yahoo": "https://search.yahoo.com/search?p={}",
            "Roblox (funni)": "https://www.roblox.com/discover/?Keyword={}",
            "Yandex": "https://yandex.com/search?text={}",
            "GPrivate": "https://gprivate.com/search/?q=#gsc.q={}",
            "YouTube (because yes)": "https://www.youtube.com/results?search_query={}"
        }

        self.themes = {}
        self.passwords = self.load_passwords()
        self.history = self.load_history()
        self.extensions = {}
        self.current_theme = None
        self.current_search_engine = self.load_search_engine()
        self.settings = self.load_settings()

        lang = self.settings.get("language", "English")
        self.translator.set_language(lang)

        self.rpc = None
        self.init_discord_rpc()

        self.profile = QWebEngineProfile("cat_profile")
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.profile.setPersistentStoragePath(DATA_DIR)
        self.profile.downloadRequested.connect(self.on_download)
        default_settings = self.profile.settings()
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        self.profile.setHttpUserAgent(self.profile.httpUserAgent())
        default_settings = self.profile.settings()
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        default_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        self.memory_saver_enabled = self.settings.get("memory_saver", False)
        self.tab_last_accessed = {}
        self.memory_saver_timer = QTimer()
        if self.memory_saver_enabled:
            self.memory_saver_timer.timeout.connect(self.cleanup_inactive_tabs)
            self.memory_saver_timer.start(60000)

        self.themes = {}
        self.load_themes()
        self.theme_engine = ThemeEngine(self)
        self.load_extensions()
        self.inject_extensions_into_profile()
        self.setup_ui()
        self.apply_current_theme()
        self.download_manager = DownloadManager(self, translator=self.translator)
        self.profile.downloadRequested.connect(self.on_download)
        if self.settings.get("restore_session", True):
            self.restore_session()
        else:
            self.add_tab(is_new_tab=True)
        app = QApplication.instance()
        app.installEventFilter(self)
        self.sound_manager = SoundManager()
        self.sound_manager.set_enabled(self.settings.get("sound_enabled", True))

    def reload_extensions(self):
        self.extensions = {}
        self.load_extensions()
        if self.settings.get("extensions_enabled", True):
            self.inject_extensions_into_profile()
        print("settings: extensions reloaded")

    def eventFilter(self, obj, event):
        if hasattr(self, 'sound_manager') and self.settings.get("sound_enabled", True):
            if event.type() == QMouseEvent.Type.MouseButtonPress:
                self.sound_manager.on_mouse_press()
            elif event.type() == QMouseEvent.Type.MouseButtonRelease:
                self.sound_manager.on_mouse_release()
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):    
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_T:
                self.add_tab(is_new_tab=True)
                event.accept()
            elif event.key() == Qt.Key.Key_W:
                self.close_tab_with_checks(self.tabs.currentIndex())
                event.accept()
            elif event.key() == Qt.Key.Key_L:
                self.url_bar.setFocus()
                self.url_bar.selectAll()
                event.accept()
            elif event.key() == Qt.Key.Key_R:
                if self.current_browser():
                    self.current_browser().reload()
                event.accept()
            elif event.key() == Qt.Key.Key_Tab:
                next_index = (self.tabs.currentIndex() + 1) % self.tabs.count()
                self.tabs.setCurrentIndex(next_index)
                event.accept()
            else:
                super().keyPressEvent(event)
        elif event.modifiers() == (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.AltModifier):
            if event.key() == Qt.Key.Key_E:
                self._crash_test_step = 1
                event.accept()
            elif event.key() == Qt.Key.Key_B and getattr(self, '_crash_test_step', 0) == 1:
                print("crash handler test")
                raise RuntimeError("this is a test crash caused by pressing shift + alt + e + b")
            else:
                self._crash_test_step = 0
                super().keyPressEvent(event)
        else:
            self._crash_test_step = 0
            super().keyPressEvent(event)

    def check_browser_health(self):
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            if memory_mb > 2000:
                print(f"browser: high memory usage {memory_mb:.2f} mb, cleaning up...")
                self.force_cleanup_tabs()

        except ImportError:
            pass
        except Exception as e:
            print(f"watchdog error: {e}")

    def force_cleanup_tabs(self):
        current_time = datetime.now()

        for i in range(self.tabs.count()):
            if i == self.tabs.currentIndex():
                continue

            tab = self.tabs.widget(i)
            if hasattr(tab, 'web_view') and tab.web_view:
                tab_id = id(tab)
                last_access = self.tab_last_accessed.get(tab_id)

                if last_access and (current_time - last_access).seconds > 60:
                    self.unload_tab_content(i)

    def cleanup_inactive_tabs(self):
        if not self.memory_saver_enabled:
            return

        current_time = datetime.now()
        inactive_threshold = timedelta(minutes=5)

        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)

            if hasattr(tab, 'web_view') and tab.web_view:
                tab_id = id(tab)
                last_access = self.tab_last_accessed.get(tab_id)

                if last_access:
                    if current_time - last_access > inactive_threshold:
                        if self.tabs.currentIndex() != i:
                            self.unload_tab_content(i)
                else:
                    self.tab_last_accessed[tab_id] = current_time


    def setup_webengine_crash_handler(self):
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-compositing --enable-gpu-rasterization --disable-software-rasterizer"

        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --max_old_space_size=4096"

        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=UseChromeOSDirectVideoDecoder"

        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --enable-vulkan"

    def setup_ui(self):
        central = QWidget()
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.nav_toolbar = QToolBar()
        self.nav_toolbar.setMovable(False)
        root_layout.addWidget(self.nav_toolbar)

        for text, func in [
            ("◀", lambda: self.current_browser().back()    if self.current_browser() else None),
            ("▶", lambda: self.current_browser().forward() if self.current_browser() else None),
            ("↻", lambda: self.current_browser().reload()  if self.current_browser() else None),
            ("⚙", self.open_settings_tab),
            ("+", lambda: self.add_tab(is_new_tab=True)),
        ]:
            btn = QPushButton(text)
            btn.setFixedSize(32, 32)
            btn.clicked.connect(func)
            self.nav_toolbar.addWidget(btn)

        self.url_bar = QLineEdit()
        self.update_url_bar_placeholder()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_toolbar.addWidget(self.url_bar)

        dl_btn = QPushButton("↓")
        dl_btn.setFixedSize(32, 32)
        dl_btn.setToolTip("Downloads")
        dl_btn.clicked.connect(self.show_downloads)
        self.nav_toolbar.addWidget(dl_btn)

        bm_btn = QPushButton("★")
        bm_btn.setFixedSize(32, 32)
        bm_btn.setToolTip("Bookmark this page")
        bm_btn.clicked.connect(self.bookmark_current_page)
        self.nav_toolbar.addWidget(bm_btn)

        self.focus_btn = QPushButton("⛶")
        self.focus_btn.setFixedSize(32, 32)
        self.focus_btn.setToolTip("Focus mode")
        self.focus_btn.clicked.connect(self.toggle_tab_focus)
        self.nav_toolbar.addWidget(self.focus_btn)

        self.bookmarks_bar_visible = True
        self.bookmarks_bar_wrapper = QWidget()
        self.bookmarks_bar_wrapper.setFixedHeight(30)
        self.bookmarks_bar_wrapper.setStyleSheet("background: #232323; border-top: 1px solid #3c3c3c;")
        wrapper_layout = QHBoxLayout(self.bookmarks_bar_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)

        self.bookmarks_scroll = QScrollArea()
        self.bookmarks_scroll.setWidgetResizable(True)
        self.bookmarks_scroll.setFixedHeight(30)
        self.bookmarks_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bookmarks_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bookmarks_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        def _bm_wheel(event):
            sb = self.bookmarks_scroll.horizontalScrollBar()
            sb.setValue(sb.value() - event.angleDelta().y())
        self.bookmarks_scroll.wheelEvent = _bm_wheel

        self.bookmarks_bar = QWidget()
        self.bookmarks_bar.setStyleSheet("background: transparent;")
        self.bookmarks_bar_layout = QHBoxLayout(self.bookmarks_bar)
        self.bookmarks_bar_layout.setContentsMargins(6, 2, 6, 2)
        self.bookmarks_bar_layout.setSpacing(2)
        self.bookmarks_bar_layout.addStretch()
        self.bookmarks_scroll.setWidget(self.bookmarks_bar)
        wrapper_layout.addWidget(self.bookmarks_scroll, 1)

        toggle_bm_btn = QPushButton("▾")
        toggle_bm_btn.setFixedSize(24, 30)
        toggle_bm_btn.setToolTip("Hide bookmarks bar")
        toggle_bm_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #888; border: none; font-size: 14px; }
            QPushButton:hover { color: white; background: #3c3c3c; }
        """)
        toggle_bm_btn.clicked.connect(self.toggle_bookmarks_bar)
        self.toggle_bm_btn = toggle_bm_btn
        wrapper_layout.addWidget(toggle_bm_btn)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.vtab_bar = VerticalTabBar()
        self.vtab_bar.tab_selected.connect(self._on_vtab_selected)
        self.vtab_bar.tab_close_requested.connect(self.close_tab_with_checks)
        self.vtab_bar.new_tab_requested.connect(lambda: self.add_tab(is_new_tab=True))
        self.vtab_bar.setVisible(self.settings.get("vertical_tabs", False))
        body.addWidget(self.vtab_bar)

        tabs_and_bm = QVBoxLayout()
        tabs_and_bm.setContentsMargins(0, 0, 0, 0)
        tabs_and_bm.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setTabBar(ModernTabBar())
        self.tabs.setTabsClosable(True)
        self.tabs.setStyleSheet("QTabBar::close-button {width:0;height:0;image:none;}")
        self.tabs.tabCloseRequested.connect(self.close_tab_with_checks)
        self.tabs.currentChanged.connect(self._on_tab_changed_internal)
        self.tabs.tabBar().setVisible(not self.settings.get("vertical_tabs", False))
        tabs_and_bm.addWidget(self.tabs, 1)
        tabs_and_bm.addWidget(self.bookmarks_bar_wrapper)

        tabs_and_bm_widget = QWidget()
        tabs_and_bm_widget.setLayout(tabs_and_bm)
        body.addWidget(tabs_and_bm_widget, 1)

        body_widget = QWidget()
        body_widget.setLayout(body)
        root_layout.addWidget(body_widget, 1)

        self.refresh_bookmarks_bar()

        self.setCentralWidget(central)

        self._hover_bar = QWidget(central)
        self._hover_bar.setFixedHeight(36)
        self._hover_bar.setStyleSheet("background: rgba(30,30,30,220); border-bottom: 1px solid #444;")
        hb_layout = QHBoxLayout(self._hover_bar)
        hb_layout.setContentsMargins(8, 2, 8, 2)
        hb_layout.addStretch()
        hb_exit_btn = QPushButton("x")
        hb_exit_btn.setFixedHeight(24)
        hb_exit_btn.setStyleSheet("QPushButton { background: #333; color: #ccc; border: 0px solid #555; border-radius: 14px; padding: 0 10px; } QPushButton:hover { background: #444; color: white; }")
        hb_exit_btn.clicked.connect(self.toggle_tab_focus)
        hb_layout.addWidget(hb_exit_btn)
        hb_layout.addStretch()
        self._hover_bar.hide()
        self._hover_bar.raise_()

        self._focus_tracker = _TopEdgeTracker(central, self)
        self._focus_tracker.setGeometry(0, 0, central.width(), 4)
        self._focus_tracker.raise_()

    def _on_tab_changed_internal(self, index):
        self.update_url_bar()
        if hasattr(self, 'vtab_bar'):
            self.vtab_bar.set_current(index)
        tab = self.tabs.widget(index)
        if tab:
            self.tab_last_accessed[id(tab)] = datetime.now()

    def _on_vtab_selected(self, index):
        self.tabs.setCurrentIndex(index)

    def load_themes(self):
        print(f"theme system: loading themes")
        print(f"themes directory: {THEMES_DIR}")

        if not os.path.exists(THEMES_DIR):
            print("theme system: themes directory doesnt exist")
            return
        try:
            if hasattr(self, 'theme_engine'):
                self.theme_engine.update_new_tab_theme()
        except Exception as e:
            print(f"theme system: could not update new tab for the theme: {e}")


        for theme_folder in os.listdir(THEMES_DIR):
            theme_path = os.path.join(THEMES_DIR, theme_folder)
            if os.path.isdir(theme_path):
                manifest_path = os.path.join(theme_path, "manifest.json")

                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)

                        theme_name = manifest.get('name', theme_folder)
                        theme_type = manifest.get('type', 'full')
                        theme_file = manifest.get('theme_file', 'theme.qss')

                        qss_path = os.path.join(theme_path, theme_file)
                        has_qss = os.path.exists(qss_path)

                        font_path = os.path.join(theme_path, "font.ttf")
                        has_font = os.path.exists(font_path)

                        has_images = False
                        image_files = ['back.png', 'forward.png', 'reload.png', 'settings.png',
                                    'plus.png', 'magnify.png', 'checkbox_checked.png',
                                    'checkbox_unchecked.png']
                        for img in image_files:
                            if os.path.exists(os.path.join(theme_path, img)):
                                has_images = True
                                break

                        theme_data = {
                            'name': theme_name,
                            'path': theme_path,
                            'has_qss': has_qss,
                            'has_font': has_font,
                            'has_images': has_images,
                            'type': theme_type,
                            'theme_file': theme_file
                        }

                        if has_qss:
                            try:
                                with open(qss_path, 'r', encoding='utf-8') as f:
                                    theme_data['css_content'] = f.read()
                                print(f"theme system: loaded theme {theme_name} (QSS: {has_qss}, Font: {has_font}, Images: {has_images})")
                            except Exception as e:
                                theme_data['has_qss'] = False
                        else:
                            print(f"theme system: theme {theme_name} has no qss file at: {qss_path}")

                        self.themes[theme_name] = theme_data

                    except Exception as e:
                        print(f"theme system: error loading theme {theme_folder}: {e}")

        print(f"theme system: themes loaded: {len(self.themes)}")
        print(f"theme system: theme names: {list(self.themes.keys())}")

    def enable_memory_saver(self, enabled):
        self.memory_saver_enabled = enabled
        self.settings["memory_saver"] = enabled
        self.save_settings()

        if enabled:
            if not self.memory_saver_timer.isActive():
                self.memory_saver_timer.timeout.connect(self.cleanup_inactive_tabs)
                self.memory_saver_timer.start(60000)
        else:
            self.memory_saver_timer.stop()

    def close_tab_with_checks(self, i):
        tab = self.tabs.widget(i)

        if isinstance(tab, SettingsTab):
            if self.tabs.count() <= 1:
                self.add_tab(is_new_tab=True)
            if hasattr(self, 'vtab_bar') and self.settings.get("vertical_tabs", True):
                self.vtab_bar.remove_tab_entry(i)
            self.tabs.removeTab(i)
        else:
            self.close_tab(i)

    def cleanup_inactive_tabs(self):
        if not self.memory_saver_enabled:
            return

        current_time = datetime.now()
        inactive_threshold = timedelta(minutes=5)

        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)

            if hasattr(tab, 'web_view') and tab.web_view:
                tab_id = id(tab)
                last_access = self.tab_last_accessed.get(tab_id)

                if last_access:
                    if current_time - last_access > inactive_threshold:
                        if self.tabs.currentIndex() != i:
                            self.unload_tab_content(i)
                else:
                    self.tab_last_accessed[tab_id] = current_time

    def unload_tab_content(self, tab_index):
        tab = self.tabs.widget(tab_index)
        if hasattr(tab, 'web_view') and tab.web_view:
            try:
                url = ""
                if hasattr(tab.web_view, 'url'):
                    url_obj = tab.web_view.url()
                    if url_obj:
                        url = url_obj.toString()

                title = self.tabs.tabText(tab_index)

                if url:
                    self.save_tab_state(tab_index, url, title)

                try:
                    if hasattr(tab.web_view, 'page') and tab.web_view.page():
                        tab.web_view.page().runJavaScript("""
                            (function() {
                                var audios = document.getElementsByTagName('audio');
                                for (var i = 0; i < audios.length; i++) {
                                    audios[i].pause();
                                    audios[i].currentTime = 0;
                                }

                                var videos = document.getElementsByTagName('video');
                                for (var i = 0; i < videos.length; i++) {
                                    videos[i].pause();
                                    videos[i].currentTime = 0;
                                }
                            })();
                        """)
                except:
                    pass

                layout = tab.layout()
                if layout:
                    for i in reversed(range(layout.count())):
                        widget = layout.itemAt(i).widget()
                        if widget:
                            widget.deleteLater()

                    placeholder_text = "Tab unloaded to save memory"
                    if url:
                        placeholder_text += f"\n\nURL: {url}\nClick anywhere to reload"

                    placeholder = QLabel(placeholder_text)
                    placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    placeholder.setStyleSheet("""
                        QLabel {
                            color: white;
                            background: #2b2b2b;
                            font-size: 14px;
                            padding: 40px;
                            border: 1px solid #444;
                            border-radius: 8px;
                        }
                    """)

                    placeholder.mousePressEvent = lambda event, idx=tab_index: self.restore_tab_content(idx)
                    layout.addWidget(placeholder)

                tab.web_view.deleteLater()
                tab.web_view = None

            except Exception as e:
                print(f"browser: error unloading tab {tab_index}: {e}")


    def restore_tab_content(self, tab_index):
        tab = self.tabs.widget(tab_index)
        if not hasattr(tab, 'web_view') or tab.web_view is None:
            tab_states = self.load_tab_states()
            if str(tab_index) in tab_states:
                state = tab_states[str(tab_index)]

                layout = tab.layout()
                if layout:
                    for i in reversed(range(layout.count())):
                        widget = layout.itemAt(i).widget()
                        if widget:
                            widget.deleteLater()

                try:
                    tab.web_view = InspectorWebView(self.profile, tab, browser=self)
                    if state['url']:
                        tab.web_view.setUrl(QUrl(state['url']))
                    else:
                        tab.web_view.setUrl(QUrl("about:blank"))

                    tab.web_view.urlChanged.connect(lambda u, t=tab: self.on_url_change(t))
                    tab.web_view.titleChanged.connect(lambda t, i=tab_index: self.on_title_change(t, i))
                    tab.web_view.iconChanged.connect(lambda icon, i=tab_index: self.on_icon_change(icon, i))

                    layout.addWidget(tab.web_view)
                    self.tab_last_accessed[id(tab)] = datetime.now()

                    self.remove_tab_state(tab_index)

                except Exception as e:
                    print(f"browser: error restoring tab {tab_index}: {e}")
                    layout.addWidget(QLabel("failed to restore tab"))

    def save_tab_state(self, tab_index, url, title):
        try:
            tab_states = {}
            if os.path.exists(TAB_STATE_FILE):
                with open(TAB_STATE_FILE, 'r', encoding='utf-8') as f:
                    tab_states = json.load(f)

            tab_states[str(tab_index)] = {
                'url': url,
                'title': title,
                'timestamp': datetime.now().isoformat()
            }

            with open(TAB_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(tab_states, f, indent=2)
        except:
            pass

    def load_tab_states(self):
        try:
            if os.path.exists(TAB_STATE_FILE):
                with open(TAB_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_session(self):
        try:
            session_data = {
                'tabs': [],
                'current_tab': self.tabs.currentIndex(),
                'timestamp': datetime.now().isoformat()
            }

            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)

                if isinstance(tab, SettingsTab):
                    session_data['tabs'].append({
                        'type': 'settings',
                        'title': self.translator.tr("settings", "Settings")
                    })
                elif hasattr(tab, 'new_tab_page') and tab.new_tab_page:
                    session_data['tabs'].append({
                        'type': 'newtab',
                        'title': self.translator.tr("new_tab", "New Tab")
                    })
                elif hasattr(tab, 'browser') and tab.web_view:
                    url = tab.web_view.url().toString()
                    title = self.tabs.tabText(i)
                    session_data['tabs'].append({
                        'type': 'web',
                        'url': url,
                        'title': title
                    })

            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"browser: error saving session {e}")

    def restore_session(self):
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                while self.tabs.count() > 0:
                    self.tabs.removeTab(0)

                restored_count = 0
                for tab_data in session_data['tabs']:
                    if tab_data.get('type') == 'settings':
                        st = SettingsTab(self)
                        i = self.tabs.addTab(st, self.translator.tr("settings", "Settings"))
                        if hasattr(self, 'vtab_bar') and self.settings.get("vertical_tabs", True):
                            self.vtab_bar.add_tab_entry(i, self.translator.tr("settings", "Settings"))
                        restored_count += 1
                    elif tab_data.get('type') == 'newtab':
                        self.add_tab(is_new_tab=True)
                        restored_count += 1
                    elif tab_data.get('url'):
                        self.add_tab(tab_data['url'])
                        restored_count += 1

                if restored_count == 0:
                    self.add_tab(is_new_tab=True)

                if 'current_tab' in session_data:
                    current_index = min(session_data['current_tab'], self.tabs.count() - 1)
                    if current_index >= 0:
                        self.tabs.setCurrentIndex(current_index)
            else:
                self.add_tab(is_new_tab=True)
        except Exception as e:
            print(f"browser: error restoring session {e}")
            self.add_tab(is_new_tab=True)

    def close_tab(self, i):
        if self.tabs.count() <= 1:
            return

        tab = self.tabs.widget(i)
        if hasattr(tab, 'web_view') and tab.web_view:
            try:
                if hasattr(tab.web_view, 'page') and tab.web_view.page():
                    tab.web_view.page().runJavaScript("""
                        (function() {
                            var audios = document.getElementsByTagName('audio');
                            for (var i = 0; i < audios.length; i++) {
                                audios[i].pause();
                                audios[i].currentTime = 0;
                            }

                            var videos = document.getElementsByTagName('video');
                            for (var i = 0; i < videos.length; i++) {
                                videos[i].pause();
                                videos[i].currentTime = 0;
                            }
                        })();
                    """)
            except Exception as e:
                print(f"browser: error stopping media: {e}")

            try:
                if hasattr(tab.web_view, 'setHtml'):
                    tab.web_view.setHtml("")
            except:
                pass

            tab.web_view.deleteLater()
            tab.web_view = None

        tab_id = id(tab)
        if tab_id in self.tab_last_accessed:
            del self.tab_last_accessed[tab_id]

        self.remove_tab_state(i)

        if hasattr(self, 'vtab_bar') and self.settings.get("vertical_tabs", True):
            self.vtab_bar.remove_tab_entry(i)

        self.tabs.removeTab(i)


    def add_tab(self, url=None, is_new_tab=False):
        if url and url.startswith("settings://"):
            self.open_settings_tab()
            return None

        new_tab = Tab(self.profile, url, is_new_tab, self, self.translator, self.theme_engine)

        if is_new_tab:
            label = self.translator.tr("new_tab", "New Tab")
        else:
            label = self.translator.tr("loading", "Loading...")

        i = self.tabs.addTab(new_tab, label)
        self.tabs.setCurrentIndex(i)

        if hasattr(self, 'vtab_bar') and self.settings.get("vertical_tabs", True):
            self.vtab_bar.add_tab_entry(i, label)
            self.vtab_bar.set_current(i)

        if hasattr(self, 'sound_manager'):
            self.sound_manager.play('tab_open')

        if is_new_tab:
            if hasattr(self.theme_engine, 'apply_theme_to_new_tab') and new_tab.new_tab_page:
                self.theme_engine.apply_theme_to_new_tab(new_tab.new_tab_page)
        else:
            if new_tab.web_view:
                new_tab.web_view.parent_browser = self
                new_tab.web_view.urlChanged.connect(lambda u, t=new_tab: self.on_url_change(t))
                new_tab.web_view.titleChanged.connect(lambda t, idx=i: self.on_title_change(t, idx))
                new_tab.web_view.iconChanged.connect(lambda icon, idx=i: self.on_icon_change(icon, idx))
                new_tab.web_view.urlChanged.connect(lambda u: self.history.append(new_tab.web_view.url().toString()))
                self.tab_last_accessed[id(new_tab)] = datetime.now()

        return new_tab

    def remove_tab_state(self, tab_index):
        try:
            if os.path.exists(TAB_STATE_FILE):
                with open(TAB_STATE_FILE, 'r', encoding='utf-8') as f:
                    tab_states = json.load(f)

                if str(tab_index) in tab_states:
                    del tab_states[str(tab_index)]

                    new_states = {}
                    for key, value in tab_states.items():
                        old_index = int(key)
                        if old_index > tab_index:
                            new_states[str(old_index - 1)] = value
                        else:
                            new_states[key] = value

                    with open(TAB_STATE_FILE, 'w', encoding='utf-8') as f:
                        json.dump(new_states, f, indent=2)
        except:
            pass

    def apply_current_theme(self):
        theme_name = self.settings.get("theme", self.translator.tr("default_theme", "Default Theme"))
        self.theme_engine.apply_theme(theme_name)

    def load_settings(self):
        settings = {
            "show_welcome_screen": True,
            "language": "English",
            "theme": self.translator.tr("default_theme", "Default Theme"),
            "memory_saver": False,
            "restore_session": True,
            "sound_enabled": True,
            "vertical_tabs": False,
            "crash_handler_enabled": True,
            "crash_dialog_enabled": False,
            "extensions_enabled": True,
        }
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    settings.update(loaded_settings)
            except Exception as e:
                print(f"settings: error loading user settings {e}")
        return settings

    def save_settings(self):
        self.settings["language"] = self.translator.current_lang
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"settings: error saving user settings {e}")

    def update_language(self):
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, SettingsTab):
                self.tabs.setTabText(i, self.translator.tr("settings", "Settings"))
                widget.update_extensions_view()
            elif hasattr(widget, 'new_tab_page') and widget.new_tab_page:
                widget.new_tab_page.search_bar.setPlaceholderText(
                    self.translator.tr("search_placeholder", "search google or enter url")
                )

        self.update_url_bar_placeholder()

    def init_discord_rpc(self):
        if DISCORD_RPC_AVAILABLE:
            try:
                self.rpc = Presence(DISCORD_APP_ID)
                self.rpc.connect()
                self.rpc.update(state="browsing the web", details="made by anameless_guy on discord")
                print("discord rpc: connected")

            except Exception as e:
                print(f"discord rpc: failed {e}")
                self.rpc = None

    def update_url_bar_placeholder(self):
        self.url_bar.setPlaceholderText(
            self.translator.tr("search_placeholder", "search {} or type a URL").format(self.current_search_engine)
        )

    def get_search_url(self, query):
        from urllib.parse import quote
        if query.startswith(('http://', 'https://', 'cat-browser://', 'file://', 'about:')):
            return query
        if '.' in query and ' ' not in query:
            return "https://" + query
        search_template = self.search_engines.get(self.current_search_engine, "https://www.google.com/search?q={}")
        return search_template.format(quote(query))


    CAT_BROWSER_PAGES = {
        "newtab":    "new_tab",
        "settings":  "settings",
        "history":   "history",
        "version":   "version",
    }

    def _open_cat_browser_page(self, url: str):
        page = url.replace("cat-browser://", "").strip("/").lower()

        if page in ("settings", ""):
            self.open_settings_tab()
            self.url_bar.setText("cat-browser://settings")
            return

        if page in ("newtab", "new-tab", "new_tab"):
            self.add_tab(is_new_tab=True)
            return

        if page in ("history",):
            self._show_cat_browser_html_page("cat-browser://history", self._build_history_page(), "History")
            return

        if page in ("version", "about"):
            self._show_cat_browser_html_page("cat-browser://version", self._build_version_page(), "about cat browser")
            return

        if page in ("offline",):
            soggy_path = os.path.join(BASE_PATH, "soggy.png")
            base_url = QUrl.fromLocalFile(BASE_PATH + os.sep)
            html = build_offline_game_html(soggy_path)
            self._show_cat_browser_html_page_with_base("cat-browser://offline", html, "No Internet", base_url)
            return

        html = self._build_error_page(page)
        self._show_cat_browser_html_page(url, html, f"cat-browser://{page}")

    def _show_cat_browser_html_page(self, url: str, html: str, title: str):
        current_tab = self.tabs.currentWidget()

        if current_tab and hasattr(current_tab, 'new_tab_page') and current_tab.new_tab_page:
            layout = current_tab.layout()
            if layout:
                current_tab.new_tab_page.setParent(None)
                current_tab.new_tab_page.deleteLater()
                current_tab.new_tab_page = None
                current_tab.web_view = InspectorWebView(current_tab.profile, current_tab, browser=self)
                current_tab.web_view.setHtml(html, QUrl(url))
                tab_index = self.tabs.indexOf(current_tab)
                self.tabs.setTabText(tab_index, title)
                self.url_bar.setText(url)
                layout.addWidget(current_tab.web_view)
                return

        browser = self.current_browser()
        if browser:
            browser.setHtml(html, QUrl(url))
            self.url_bar.setText(url)
            tab_index = self.tabs.currentIndex()
            self.tabs.setTabText(tab_index, title)
            return

        new_tab = Tab(self.profile, None, False, self, self.translator, self.theme_engine)
        i = self.tabs.addTab(new_tab, title)
        self.tabs.setCurrentIndex(i)
        if new_tab.web_view:
            new_tab.web_view.setHtml(html, QUrl(url))
        self.url_bar.setText(url)

    def _show_cat_browser_html_page_with_base(self, url: str, html: str, title: str, base_url: QUrl):
        current_tab = self.tabs.currentWidget()

        if current_tab and hasattr(current_tab, 'new_tab_page') and current_tab.new_tab_page:
            layout = current_tab.layout()
            if layout:
                current_tab.new_tab_page.setParent(None)
                current_tab.new_tab_page.deleteLater()
                current_tab.new_tab_page = None
                current_tab.web_view = InspectorWebView(current_tab.profile, current_tab, browser=self)
                current_tab.web_view.setHtml(html, base_url)
                tab_index = self.tabs.indexOf(current_tab)
                self.tabs.setTabText(tab_index, title)
                self.url_bar.setText(url)
                layout.addWidget(current_tab.web_view)
                return

        browser = self.current_browser()
        if browser:
            browser.setHtml(html, base_url)
            self.url_bar.setText(url)
            self.tabs.setTabText(self.tabs.currentIndex(), title)
            return

        new_tab = Tab(self.profile, None, False, self, self.translator, self.theme_engine)
        i = self.tabs.addTab(new_tab, title)
        self.tabs.setCurrentIndex(i)
        if new_tab.web_view:
            new_tab.web_view.setHtml(html, base_url)
        self.url_bar.setText(url)

    def _build_history_page(self) -> str:
        items_html = ""
        for entry in reversed(self.history[-200:]):
            if entry and not entry.startswith("about:"):
                safe = entry.replace("&", "&amp;").replace("<", "&lt;")
                items_html += f'<li><a href="{safe}" onclick="window.location.href=this.href;return false;">{safe}</a></li>\n'
        if not items_html:
            items_html = "<li style='color:#888'>no history</li>"
        return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <title>History</title>
        <style>
          body {{ background:#1a1a1a; color:white; font-family:sans-serif; padding:40px; }}
          h1 {{ color:#0078d4; }}
          ul {{ list-style:none; padding:0; }}
          li {{ padding:6px 0; border-bottom:1px solid #333; }}
          a {{ color:#7ec8ff; text-decoration:none; font-size:14px; }}
          a:hover {{ text-decoration:underline; }}
        </style></head><body>
        <h1>history</h1>
        <ul>{items_html}</ul>
        </body></html>"""

    def _build_version_page(self) -> str:
        return """<!DOCTYPE html><html><head><meta charset="utf-8">
        <title>about cat browser</title>
        <style> 
          body {{ background:#1a1a1a; color:white; font-family:sans-serif;
                 display:flex; flex-direction:column; align-items:center;
                 justify-content:center; height:100vh; margin:0; }}
          h1 {{ color:#0078d4; font-size:48px; margin-bottom:8px; }}
          .ver {{ color:#aaa; font-size:20px; }}
          .sub {{ color:#666; font-size:14px; margin-top:20px; }}
          table {{ margin-top:30px; border-collapse:collapse; }}
          td {{ padding:8px 20px; border-bottom:1px solid #333; color:#ccc; font-size:14px; }}
          td:first-child {{ color:#0078d4; font-weight:bold; }}
        </style></head><body>
        <h1>cat browser</h1>
        <div class="ver">version 0.9.1</div>
        </body></html>"""

    def _build_error_page(self, page: str) -> str:
        known = ["settings", "newtab", "history", "version", "about", "offline"]
        links = "".join(f'<li><a href="cat-browser://{p}">cat-browser://{p}</a></li>' for p in known)
        return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <title>Unknown Page</title>
        <style>
          body {{ background:#1a1a1a; color:white; font-family:sans-serif; padding:60px; }}
          h1 {{ color:#ff6b6b; }}
          a {{ color:#7ec8ff; }}
          ul {{ margin-top:20px; line-height:2; }}
        </style></head><body>
        <h1>Unknown page: cat-browser://{page}</h1>
        <p>Available internal pages:</p>
        <ul>{links}</ul>
        </body></html>"""

    def set_search_engine(self, engine_name):
        if engine_name in self.search_engines:
            self.current_search_engine = engine_name
            self.update_url_bar_placeholder()
            self.save_search_engine()
            print(f"settings: search engine changed to {engine_name}")

    def load_search_engine(self):
        if os.path.exists(SEARCH_ENGINE_FILE):
            try:
                with open(SEARCH_ENGINE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    engine = data.get("engine", "Google")
                    if engine in self.search_engines:
                        return engine
            except Exception as e:
                print(f"settings: error loading search engine {e}")
        return "Google"

    def save_search_engine(self):
        try:
            with open(SEARCH_ENGINE_FILE, "w", encoding="utf-8") as f:
                json.dump({"engine": self.current_search_engine}, f, indent=2)
        except Exception as e:
            print(f"settings: error saving search engine {e}")

    def set_theme(self, theme_name):
        self.settings["theme"] = theme_name
        self.save_settings()
        previous_font = self.theme_engine.current_font
        self.theme_engine.apply_theme(theme_name)
        self.style().unpolish(self)
        self.style().polish(self)

        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, 'new_tab_page') and tab.new_tab_page:
                tab.new_tab_page.set_default_background()

    def load_extensions(self):
        if not os.path.exists(EXTENSIONS_DIR):
            return

        for ext_folder in os.listdir(EXTENSIONS_DIR):
            ext_path = os.path.join(EXTENSIONS_DIR, ext_folder)
            if os.path.isdir(ext_path):
                manifest_path = os.path.join(ext_path, "manifest.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)

                        ext_name = manifest.get('name', ext_folder)
                        ext_description = manifest.get('description', 'No description provided')
                        ext_version = manifest.get('version', '1.0')
                        script_file = manifest.get('script', 'script.js')

                        script_path = os.path.join(ext_path, script_file)
                        if os.path.exists(script_path):
                            with open(script_path, 'r', encoding='utf-8') as f:
                                script_content = f.read()

                            self.extensions[ext_name] = {
                                'name': ext_name,
                                'description': ext_description,
                                'version': ext_version,
                                'script': script_file,
                                'script_content': script_content,
                                'folder': ext_folder
                            }

                            print(f"extension engine: loaded extension {ext_name} v{ext_version}")

                    except Exception as e:
                        print(f"extension engine: error loading extension {ext_folder}: {e}")

        if self.settings.get("extensions_enabled", True):
            self.inject_extensions_into_profile()

    def inject_extensions_into_profile(self):
        self.profile.scripts().clear()
        if not self.settings.get("extensions_enabled", True):
            print("extension engine: extensions are disabled, skipping injection")
            return

        for ext_name, ext_data in self.extensions.items():
            script_content = ext_data.get('script_content', '')
            if script_content:
                script = QWebEngineScript()
                script.setSourceCode(script_content)
                script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
                script.setRunsOnSubFrames(True)
                script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
                self.profile.scripts().insert(script)
                print(f"extension engine: injected {ext_name}")

    def load_passwords(self):
        passwords = {}
        if os.path.exists(PASSWORDS_FILE):
            try:
                with open(PASSWORDS_FILE, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if "name" in row and "username" in row and "password" in row:
                            passwords[row["name"]] = {"user": row["username"], "pass": row["password"]}
            except Exception as e:
                print(f"settings: error loading passwords {e}")
        return passwords

    def save_passwords(self):
        try:
            with open(PASSWORDS_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "username", "password"])
                for name, info in self.passwords.items():
                    writer.writerow([name, info["user"], info["pass"]])
        except Exception as e:
            print(f"settings: error saving passwords: {e}")

    def load_history(self):
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                print(f"settings: error loading history {e}")
        return history

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"settings: error saving history {e}")

    def create_tab_view(self):
        web_view = InspectorWebView(self.profile, browser=self)
        return web_view

    def on_title_change(self, title, index):
        tab_text = title[:20] + "..." if len(title) > 23 else title
        display = tab_text if title else self.translator.tr("new_tab", "New Tab")
        self.tabs.setTabText(index, display)
        if hasattr(self, 'vtab_bar') and self.settings.get("vertical_tabs", True):
            self.vtab_bar.set_title(index, display)

    def on_icon_change(self, icon, index):
        if not icon.isNull():
            self.tabs.setTabIcon(index, icon)
            if hasattr(self, 'vtab_bar') and self.settings.get("vertical_tabs", True):
                self.vtab_bar.set_icon(index, icon)
        else:
            self.tabs.setTabIcon(index, QIcon())

    def open_settings_tab(self):
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, SettingsTab):
                self.tabs.setCurrentIndex(i)
                if hasattr(self, 'vtab_bar') and self.settings.get("vertical_tabs", True):
                    self.vtab_bar.set_current(i)
                w.update_extensions_view()
                return

        st = SettingsTab(self)
        i = self.tabs.addTab(st, self.translator.tr("settings", "Settings"))
        self.tabs.setCurrentIndex(i)
        if hasattr(self, 'vtab_bar') and self.settings.get("vertical_tabs", True):
            self.vtab_bar.add_tab_entry(i, self.translator.tr("settings", "Settings"))
            self.vtab_bar.set_current(i)

    def current_browser(self):
        tab = self.tabs.currentWidget()
        if hasattr(tab,"web_view") and tab.web_view:
            return tab.web_view
        return None

    def inspect_current_page(self):
        browser = self.current_browser()
        if browser and hasattr(browser, 'inspect_element'):
            browser.inspect_element()
        else:
            QMessageBox.information(self, "Inspect Element", "No web page to inspect.")

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return

        if url.startswith("cat-browser://"):
            self._open_cat_browser_page(url)
            return

        url = self.get_search_url(url)

        current_tab = self.tabs.currentWidget()

        if current_tab and hasattr(current_tab, 'new_tab_page') and current_tab.new_tab_page:
            layout = current_tab.layout()
            if layout:
                current_tab.new_tab_page.setParent(None)
                current_tab.new_tab_page.deleteLater()
                current_tab.new_tab_page = None

                current_tab.web_view = InspectorWebView(current_tab.profile, current_tab, browser=self)
                current_tab.web_view.setUrl(QUrl(url))

                tab_index = self.tabs.indexOf(current_tab)
                current_tab.web_view.urlChanged.connect(lambda u, t=current_tab: self.on_url_change(t))
                current_tab.web_view.titleChanged.connect(lambda t, i=tab_index: self.on_title_change(t, i))
                current_tab.web_view.iconChanged.connect(lambda icon, i=tab_index: self.on_icon_change(icon, i))
                current_tab.web_view.urlChanged.connect(lambda u: self.history.append(current_tab.web_view.url().toString()))
                layout.addWidget(current_tab.web_view)
                self.tab_last_accessed[id(current_tab)] = datetime.now()
                self.tabs.setTabText(tab_index, self.translator.tr("loading", "Loading..."))
            return

        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl(url))
            return

        self.add_tab(url)

    def on_url_change(self, tab):
        if self.tabs.currentWidget() == tab and hasattr(tab, 'web_view') and tab.web_view:
            self.url_bar.setText(tab.web_view.url().toString())

        tab_id = id(tab)
        self.tab_last_accessed[tab_id] = datetime.now()

    def update_url_bar(self, *args):
        tab = self.tabs.currentWidget()
        if hasattr(tab, "browser") and isinstance(tab.browser, QWebEngineView):
            self.url_bar.setText(tab.browser.url().toString())
        else:
            self.url_bar.setText("")

    def on_download(self, item: QWebEngineDownloadRequest):
        if hasattr(item, '_being_handled') and item._being_handled:
            return

        item._being_handled = True

        suggested = item.suggestedFileName()
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")

        path, _ = QFileDialog.getSaveFileName(
            self,
            self.translator.tr("save_as", "Save File As"),
            os.path.join(downloads_dir, suggested)
        )

        if path:
            item.setDownloadDirectory(os.path.dirname(path))
            item.setDownloadFileName(os.path.basename(path))
            item.accept()

            self.download_manager.add_download(item)
        else:
            item.cancel()

    def show_downloads(self):
        self.download_manager.show()
        self.download_manager.raise_()

    def load_bookmarks(self):
        try:
            if os.path.exists(BOOKMARKS_FILE):
                with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_bookmarks(self, bookmarks):
        try:
            with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
                json.dump(bookmarks, f, indent=2)
        except:
            pass

    def refresh_bookmarks_bar(self):
        while self.bookmarks_bar_layout.count():
            item = self.bookmarks_bar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        bookmarks = self.load_bookmarks()

        if not bookmarks:
            self.bookmarks_bar_wrapper.hide()
            return

        if self.bookmarks_bar_visible:
            self.bookmarks_bar_wrapper.show()

        btn_style = """
            QPushButton {
                background: transparent;
                color: #ccc;
                border: none;
                padding: 2px 6px;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background: #3c3c3c; color: white; }
            QPushButton:pressed { background: #4a4a4a; }
        """
        x_style = """
            QPushButton {
                background: transparent;
                color: #666;
                border: none;
                padding: 0px 3px;
                font-size: 11px;
                border-radius: 3px;
            }
            QPushButton:hover { background: #c0392b; color: white; }
        """

        for bm in bookmarks:
            pair = QWidget()
            pair.setStyleSheet("background: transparent;")
            pair_layout = QHBoxLayout(pair)
            pair_layout.setContentsMargins(0, 0, 0, 0)
            pair_layout.setSpacing(0)

            name_btn = QPushButton(bm['name'][:24])
            name_btn.setToolTip(bm['url'])
            name_btn.setStyleSheet(btn_style)
            name_btn.clicked.connect(lambda checked, u=bm['url']: self.navigate_to_url_direct(u))

            x_btn = QPushButton("✕")
            x_btn.setFixedSize(16, 20)
            x_btn.setToolTip(f"Remove {bm['name']}")
            x_btn.setStyleSheet(x_style)
            x_btn.clicked.connect(lambda checked, u=bm['url']: self._remove_bookmark(u))

            pair_layout.addWidget(name_btn)
            pair_layout.addWidget(x_btn)
            self.bookmarks_bar_layout.addWidget(pair)

        self.bookmarks_bar_layout.addStretch()

    def toggle_bookmarks_bar(self):
        bookmarks = self.load_bookmarks()
        if not bookmarks:
            return
        self.bookmarks_bar_visible = not self.bookmarks_bar_visible
        self.bookmarks_scroll.setVisible(self.bookmarks_bar_visible)
        if self.bookmarks_bar_visible:
            self.toggle_bm_btn.setText("▾")
            self.toggle_bm_btn.setToolTip("Hide bookmarks bar")
            self.bookmarks_bar_wrapper.setFixedHeight(27)
        else:
            self.toggle_bm_btn.setText("▸")
            self.toggle_bm_btn.setToolTip("Show bookmarks bar")
            self.bookmarks_bar_wrapper.setFixedHeight(27)

    def _remove_bookmark(self, url):
        bookmarks = self.load_bookmarks()
        bookmarks = [b for b in bookmarks if b['url'] != url]
        self.save_bookmarks(bookmarks)
        self.refresh_bookmarks_bar()

    def navigate_to_url_direct(self, url):
        self.url_bar.setText(url)
        self.navigate_to_url()

    def bookmark_current_page(self):
        browser = self.current_browser()
        if not browser:
            return
        url = browser.url().toString()
        if not url or url.startswith("about:"):
            return
        title = self.tabs.tabText(self.tabs.currentIndex()).replace("...", "").strip()
        if not title:
            title = url
        bookmarks = self.load_bookmarks()
        if not any(b['url'] == url for b in bookmarks):
            bookmarks.append({'name': title, 'url': url})
            self.save_bookmarks(bookmarks)
            self.refresh_bookmarks_bar()

    def toggle_tab_focus(self):
        focused = getattr(self, '_tab_focused', False)
        if focused:
            self.nav_toolbar.show()
            if self.load_bookmarks():
                self.bookmarks_bar_wrapper.show()
            if hasattr(self, 'vtab_bar'):
                self.vtab_bar.setVisible(self.settings.get("vertical_tabs", False))
            self.tabs.tabBar().setVisible(not self.settings.get("vertical_tabs", False))
            self.focus_btn.setText("⛶")
            self.focus_btn.setToolTip("focus mode")
            self._tab_focused = False
            self._hide_hover_bar()
        else:
            self.nav_toolbar.hide()
            self.bookmarks_bar_wrapper.hide()
            if hasattr(self, 'vtab_bar'):
                self.vtab_bar.hide()
            self.tabs.tabBar().hide()
            self.focus_btn.setText("⛶")
            self.focus_btn.setToolTip("exit focus mode")
            self._tab_focused = True

    def _show_hover_bar(self):
        if hasattr(self, '_hover_bar'):
            cw = self.centralWidget()
            if cw:
                self._hover_bar.setGeometry(0, 0, cw.width(), 36)
            self._hover_bar.show()
            self._hover_bar.raise_()
            if hasattr(self, '_hover_hide_timer'):
                self._hover_hide_timer.stop()
            self._hover_hide_timer = QTimer(self)
            self._hover_hide_timer.setSingleShot(True)
            self._hover_hide_timer.timeout.connect(self._hide_hover_bar)
            self._hover_bar.enterEvent = lambda e: self._hover_hide_timer.stop()
            self._hover_bar.leaveEvent = lambda e: self._hover_hide_timer.start(800)
            self._hover_hide_timer.start(2000)

    def _hide_hover_bar(self):
        if hasattr(self, '_hover_bar'):
            self._hover_bar.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cw = self.centralWidget()
        if cw:
            if hasattr(self, '_focus_tracker'):
                self._focus_tracker.setGeometry(0, 0, cw.width(), 4)
            if hasattr(self, '_hover_bar'):
                self._hover_bar.setGeometry(0, 0, cw.width(), 36)


    def closeEvent(self, event):
        print(f"cat browser closing (plz use it again)")
        if hasattr(self, 'sound_manager'):
            self.sound_manager.cleanup_all()
        self.save_passwords()
        self.save_history()
        self.save_search_engine()
        self.save_settings()

        if self.settings.get("restore_session", True):
            self.save_session()
            if os.path.exists(TAB_STATE_FILE):
                try:
                    os.remove(TAB_STATE_FILE)
                except:
                    pass

        if self.rpc:
            try:
                self.rpc.close()
            except:
                pass

        event.accept()

    def extract_domain(self, url):
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return url

def global_exception_handler(exc_type, exc_value, exc_traceback):
    import traceback
    
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print("=" * 80)
    print("UNHANDLED EXCEPTION CAUGHT BY CRASH HANDLER")
    print("=" * 80)
    print(error_msg)
    print("=" * 80)
    
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        crash_handler_enabled = True
        crash_dialog_enabled = True

        for widget in app.topLevelWidgets():
            try:
                if isinstance(widget, Browser):
                    crash_handler_enabled = widget.settings.get("crash_handler_enabled", True)
                    crash_dialog_enabled = widget.settings.get("crash_dialog_enabled", True)
                    break
            except:
                pass

        if not crash_handler_enabled:
            print("crash handler disabled - using default exception handling")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        if crash_dialog_enabled:
            dialog = CrashDialog(error_msg)
            dialog.exec()
        else:
            print("crash dialog off, the logs will only be visible in the console")

    except Exception as e:
        print("failed to show crash dialog which isnt very good")
        print(f"dialog error: {e}")
        traceback.print_exception(exc_type, exc_value, exc_traceback)

if __name__ == "__main__":
    sys.excepthook = global_exception_handler
    
    try:
        app = QApplication(sys.argv)
        main_window = Browser()

        startup_url = None
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            if arg.startswith("http://") or arg.startswith("https://"):
                startup_url = arg
            else:
                startup_url = "https://" + arg

        startup_url_opened = False

        def open_startup_url():
            global startup_url_opened
            if startup_url and not startup_url_opened:
                startup_url_opened = True
                main_window.add_tab(startup_url)

        if not os.path.exists(SETUP_FILE):
            splash = WelcomeScreen(3000)
            splash.show()

            class SetupController:
                def __init__(self):
                    self.setup_shown = False
                    self.timer = QTimer()
                    self.timer.setSingleShot(True)
                    self.timer.timeout.connect(self.show_setup)

                def show_setup(self):
                    if not self.setup_shown:
                        self.setup_shown = True
                        setup_wizard = SetupWizard(main_window)
                        setup_wizard.finished.connect(main_window.show)
                        setup_wizard.finished.connect(open_startup_url)
                        setup_wizard.exec()

                def start_timer(self):
                    self.timer.start(3500)

            controller = SetupController()
            splash.finished.connect(controller.show_setup)
            controller.start_timer()

        else:
            if main_window.settings.get("show_welcome_screen", True):
                splash = WelcomeScreen(3000)
                splash.show()
                splash.finished.connect(main_window.show)
                splash.finished.connect(open_startup_url)
                QTimer.singleShot(3500, main_window.show)
            else:
                main_window.show()
                open_startup_url()

        sys.exit(app.exec())
    
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print("CRITICAL ERROR DURING STARTUP")
        print(error_msg)
        
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            dialog = CrashDialog(error_msg)
            dialog.exec()
        except:
            print("dawg how can you even break the browser this bad")        
        sys.exit(1)

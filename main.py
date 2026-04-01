import sys
import os
import ctypes
import ctypes.wintypes as wintypes
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QWidget, QFileDialog,
    QLabel, QScrollArea, QGridLayout, QVBoxLayout,
)
from PyQt5.QtCore import Qt, QRect, QTimer, QAbstractNativeEventFilter, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QFont

from config import get_save_dir, set_save_dir
from editor import AnnotationEditor


DELAY_SECONDS = 3

# Windows hotkey sabitleri
WM_HOTKEY = 0x0312
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
VK_SNAPSHOT = 0x2C
HOTKEY_ID_CAPTURE = 1      # Ctrl+Shift+S
HOTKEY_ID_PRTSCN = 2       # Print Screen
HOTKEY_ID_DELAYED = 3      # Ctrl+Shift+D


# ---------------------------------------------------------------------------
# Global hotkey (Windows RegisterHotKey API)
# ---------------------------------------------------------------------------

class GlobalHotkeyFilter(QAbstractNativeEventFilter):
    """Windows WM_HOTKEY mesajlarını yakalayan native event filtresi."""

    def __init__(self, on_capture, on_delayed):
        super().__init__()
        self.on_capture = on_capture
        self.on_delayed = on_delayed

    def nativeEventFilter(self, eventType, message):
        try:
            if eventType == b"windows_generic_MSG":
                msg = wintypes.MSG.from_address(int(message))
                if msg.message == WM_HOTKEY:
                    if msg.wParam in (HOTKEY_ID_CAPTURE, HOTKEY_ID_PRTSCN):
                        self.on_capture()
                        return True, 0
                    elif msg.wParam == HOTKEY_ID_DELAYED:
                        self.on_delayed()
                        return True, 0
        except Exception:
            pass
        return False, 0


# ---------------------------------------------------------------------------
# Ekran seçim overlay'ı
# ---------------------------------------------------------------------------

class ScreenshotOverlay(QWidget):
    def __init__(self, on_capture, pre_captured_bg=None):
        super().__init__()
        self.on_capture = on_capture
        self.origin = None
        self.current = None
        self.ready = False

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)

        screen = QApplication.primaryScreen()
        vg = screen.virtualGeometry()
        self.setGeometry(vg)
        self.bg = pre_captured_bg if pre_captured_bg else screen.grabWindow(
            0, vg.x(), vg.y(), vg.width(), vg.height()
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.setFocus(Qt.ActiveWindowFocusReason)
        self.raise_()
        QTimer.singleShot(200, self._enable)

    def _enable(self):
        self.ready = True
        self.activateWindow()
        self.setFocus(Qt.ActiveWindowFocusReason)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.drawPixmap(0, 0, self.bg)
        p.fillRect(self.rect(), QColor(0, 0, 0, 80))
        if self.origin and self.current:
            rect = QRect(self.origin, self.current).normalized()
            p.drawPixmap(rect, self.bg, rect)
            p.setPen(QPen(QColor(0, 120, 215), 2))
            p.drawRect(rect)
            label = f"{rect.width()} x {rect.height()}"
            p.setPen(QColor(255, 255, 255))
            p.drawText(rect.x(), rect.y() - 6, label)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._capture(self.bg)

    def mousePressEvent(self, event):
        if not self.ready or event.button() != Qt.LeftButton:
            return
        self.origin = event.pos()
        self.current = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        if self.origin:
            self.current = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if not self.ready or event.button() != Qt.LeftButton or not self.origin:
            return
        self.current = event.pos()
        rect = QRect(self.origin, self.current).normalized()
        if rect.width() > 5 and rect.height() > 5:
            self._capture(self.bg.copy(rect))
        else:
            self._capture(self.bg)

    def _capture(self, pixmap):
        self.on_capture(pixmap)
        self.close()


# ---------------------------------------------------------------------------
# Geri sayım overlay'ı
# ---------------------------------------------------------------------------

class CountdownOverlay(QWidget):
    """Küçük yüzen sayaç — ekranı kapatmaz, mouse/klavye geçirir."""

    def __init__(self, seconds, on_done):
        super().__init__()
        self.remaining = seconds
        self.on_done = on_done

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput  # Mouse/klavye olaylarını geçir
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Küçük sayaç — ekranın ortasında
        size = 120
        screen = QApplication.primaryScreen().availableGeometry()
        self.setFixedSize(size, size)
        self.move(
            screen.x() + (screen.width() - size) // 2,
            screen.y() + (screen.height() - size) // 2,
        )

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

    def showEvent(self, event):
        super().showEvent(event)
        self.timer.start(1000)

    def _tick(self):
        self.remaining -= 1
        self.update()
        if self.remaining <= 0:
            self.timer.stop()
            self.close()
            self.on_done()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # Yarı saydam koyu daire
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 180))
        p.drawEllipse(self.rect().adjusted(4, 4, -4, -4))
        # Sayı
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Segoe UI", 48, QFont.Bold))
        p.drawText(self.rect(), Qt.AlignCenter, str(self.remaining))


# ---------------------------------------------------------------------------
# Galeri penceresi
# ---------------------------------------------------------------------------

def _apply_dark_titlebar(hwnd):
    try:
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4
        )
    except Exception:
        pass


class GalleryWindow(QWidget):
    def __init__(self, save_dir):
        super().__init__()
        self.save_dir = Path(save_dir)
        self.setWindowTitle("SnapForge — Galeri")
        self.setMinimumSize(700, 500)
        self.setStyleSheet("QWidget { background: #1a1a1a; }")
        _apply_dark_titlebar(int(self.winId()))

        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(8)
        scroll.setWidget(container)

        self._load_thumbnails()

    def _load_thumbnails(self):
        files = sorted(self.save_dir.glob("*.png"), reverse=True)[:50]
        col_count = 4
        for i, f in enumerate(files):
            row, col = divmod(i, col_count)
            thumb = self._make_thumb(f)
            self.grid.addWidget(thumb, row, col)

    def _make_thumb(self, filepath):
        px = QPixmap(str(filepath))
        scaled = px.scaled(QSize(220, 160), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        lbl = QLabel()
        lbl.setPixmap(scaled)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setToolTip(str(filepath))
        lbl.setStyleSheet(
            "QLabel { border: 2px solid #555; padding: 4px; background: #222; }"
            "QLabel:hover { border-color: #0078d7; }"
        )
        lbl.setCursor(Qt.PointingHandCursor)
        lbl.mousePressEvent = lambda e, p=filepath: os.startfile(str(p))
        return lbl


# ---------------------------------------------------------------------------
# Ana uygulama
# ---------------------------------------------------------------------------

def _create_app_icon():
    """SnapForge ikonu — gradient arka plan, vizör köşe işaretleri, kıvılcım."""
    from PyQt5.QtGui import QLinearGradient, QPainterPath
    sizes = [16, 32, 48, 64, 128, 256]
    icon = QIcon()
    for s in sizes:
        px = QPixmap(s, s)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)

        m = s * 0.04  # margin

        # Gradient arka plan: koyu mavi → cyan
        grad = QLinearGradient(0, 0, s, s)
        grad.setColorAt(0.0, QColor(15, 52, 120))
        grad.setColorAt(0.5, QColor(0, 100, 200))
        grad.setColorAt(1.0, QColor(0, 180, 220))
        p.setPen(Qt.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(int(m), int(m), int(s - m * 2), int(s - m * 2),
                          s * 0.22, s * 0.22)

        # Vizör köşe işaretleri (L-bracket'lar)
        t = max(s * 0.07, 1.5)  # çizgi kalınlığı
        arm = s * 0.18          # kol uzunluğu
        inset = s * 0.2         # kenara mesafe
        pen = QPen(QColor(255, 255, 255, 230), t, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)

        # Sol üst
        x0, y0 = inset, inset
        p.drawLine(int(x0), int(y0), int(x0 + arm), int(y0))
        p.drawLine(int(x0), int(y0), int(x0), int(y0 + arm))

        # Sağ üst
        x1 = s - inset
        p.drawLine(int(x1), int(y0), int(x1 - arm), int(y0))
        p.drawLine(int(x1), int(y0), int(x1), int(y0 + arm))

        # Sol alt
        y1 = s - inset
        p.drawLine(int(x0), int(y1), int(x0 + arm), int(y1))
        p.drawLine(int(x0), int(y1), int(x0), int(y1 - arm))

        # Sağ alt
        p.drawLine(int(x1), int(y1), int(x1 - arm), int(y1))
        p.drawLine(int(x1), int(y1), int(x1), int(y1 - arm))

        # Kıvılcım / yıldırım (forge teması) — ortada
        if s >= 32:
            cx, cy = s * 0.5, s * 0.5
            spark_h = s * 0.28
            spark_w = s * 0.12

            path = QPainterPath()
            path.moveTo(cx + spark_w * 0.3, cy - spark_h * 0.5)
            path.lineTo(cx - spark_w * 0.2, cy + spark_h * 0.05)
            path.lineTo(cx + spark_w * 0.15, cy + spark_h * 0.05)
            path.lineTo(cx - spark_w * 0.3, cy + spark_h * 0.5)

            spark_pen = QPen(QColor(255, 220, 60), max(t * 0.9, 1.5), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            p.setPen(spark_pen)
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)

            # Parıltı noktaları
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 240, 100, 200))
            dot = max(s * 0.04, 1.5)
            p.drawEllipse(int(cx + spark_w * 0.5), int(cy - spark_h * 0.3), int(dot), int(dot))
            p.drawEllipse(int(cx - spark_w * 0.6), int(cy + spark_h * 0.2), int(dot * 0.8), int(dot * 0.8))

        p.end()
        icon.addPixmap(px)
    return icon


class SnapForge:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("SnapForge")
        self.app.setApplicationDisplayName("SnapForge")
        self.app.setQuitOnLastWindowClosed(False)

        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("snapforge.app")
        except Exception:
            pass

        self.overlay = None
        self.editor = None
        self.gallery = None
        self.countdown = None

        get_save_dir().mkdir(parents=True, exist_ok=True)

        self._setup_tray()
        self._setup_hotkey()

    def _setup_tray(self):
        self.tray = QSystemTrayIcon()
        self.app_icon = _create_app_icon()
        self.app.setWindowIcon(self.app_icon)
        self.tray.setIcon(self.app_icon)
        self.tray.setToolTip("SnapForge (Ctrl+Shift+S | Ctrl+Shift+D gecikmeli)")

        menu = QMenu()
        menu.addAction("Ekran Görüntüsü Al", self._start_capture)
        menu.addAction(f"Gecikmeli Al ({DELAY_SECONDS} sn)", self._start_delayed)
        menu.addSeparator()
        menu.addAction("Galeri", self._show_gallery)
        menu.addAction("Klasörü Aç", self._open_folder)
        menu.addAction("Kayıt Klasörünü Değiştir...", self._change_save_dir)
        menu.addSeparator()
        menu.addAction("Çıkış", self._quit)
        self.tray.setContextMenu(menu)

        self.tray.activated.connect(self._on_tray_click)
        self.tray.show()

        self.tray.showMessage(
            "SnapForge",
            "Hazır.\nCtrl+Shift+S → çekim\nCtrl+Shift+D → gecikmeli çekim",
            QSystemTrayIcon.Information,
            2000,
        )

    def _setup_hotkey(self):
        # Önceki crash'ten kalan kayıtları temizle
        ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_CAPTURE)
        ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_PRTSCN)

        # Ctrl+Shift+S
        ctypes.windll.user32.RegisterHotKey(
            None, HOTKEY_ID_CAPTURE,
            MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT,
            ord("S"),
        )

        # Print Screen — tooltip'leri kaçırmaz
        prtscn_ok = ctypes.windll.user32.RegisterHotKey(
            None, HOTKEY_ID_PRTSCN,
            MOD_NOREPEAT,
            VK_SNAPSHOT,
        )
        if not prtscn_ok:
            self.tray.showMessage(
                "SnapForge",
                "Print Screen kaydedilemedi.\n"
                "Ayarlar > Erişilebilirlik > Klavye > 'Print Screen tuşuyla Ekran Alıntısı Aracı aç' kapatın.",
                QSystemTrayIcon.Warning,
                5000,
            )

        # Ctrl+Shift+D — gecikmeli çekim (tooltip modu)
        ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_DELAYED)
        ctypes.windll.user32.RegisterHotKey(
            None, HOTKEY_ID_DELAYED,
            MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT,
            ord("D"),
        )

        self._hotkey_filter = GlobalHotkeyFilter(self._start_capture, self._start_delayed)
        self.app.installNativeEventFilter(self._hotkey_filter)

    def _on_tray_click(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._start_capture()

    # -- Çekim modları --

    def _start_capture(self):
        # Editor açıksa öne getir
        if self.editor and self.editor.isVisible():
            self.editor.raise_()
            self.editor.activateWindow()
            return
        if self.overlay and self.overlay.isVisible():
            return
        if self.countdown and self.countdown.isVisible():
            return

        # Ekranı HEMEN yakala
        screen = QApplication.primaryScreen()
        vg = screen.virtualGeometry()
        self._pre_bg = screen.grabWindow(0, vg.x(), vg.y(), vg.width(), vg.height())
        QTimer.singleShot(50, self._show_overlay)

    def _show_overlay(self):
        if self.overlay:
            self.overlay.deleteLater()
            self.overlay = None
        if self.editor:
            self.editor.deleteLater()
            self.editor = None
        self.overlay = ScreenshotOverlay(self._open_editor, self._pre_bg)
        self._pre_bg = None
        self.overlay.show()

    def _start_delayed(self):
        if self.countdown:
            self.countdown.deleteLater()
        self.countdown = CountdownOverlay(DELAY_SECONDS, self._delayed_capture)
        self.countdown.show()

    def _delayed_capture(self):
        # Geri sayım bitti — ekranı şimdi yakala (tooltip'ler görünür)
        screen = QApplication.primaryScreen()
        vg = screen.virtualGeometry()
        self._pre_bg = screen.grabWindow(0, vg.x(), vg.y(), vg.width(), vg.height())
        QTimer.singleShot(50, self._show_overlay)

    # -- Editör --

    def _open_editor(self, pixmap):
        if self.overlay:
            self.overlay.deleteLater()
            self.overlay = None

        # Kırpılan görüntüyü hemen clipboard'a kopyala
        QApplication.clipboard().setPixmap(pixmap)

        self.editor = AnnotationEditor(
            pixmap, get_save_dir(), self.tray,
            on_delayed=self._start_delayed,
            on_new=self._new_capture,
        )
        self.editor.show()

    def _new_capture(self):
        """Editörü kapat, yeni çekim başlat."""
        if self.editor:
            self.editor.close()
            self.editor.deleteLater()
            self.editor = None
        QTimer.singleShot(200, self._show_overlay)

    # -- Galeri --

    def _show_gallery(self):
        self.gallery = GalleryWindow(get_save_dir())
        self.gallery.show()

    # -- Ayarlar --

    def _change_save_dir(self):
        current = str(get_save_dir())
        folder = QFileDialog.getExistingDirectory(None, "Kayıt Klasörü Seç", current)
        if folder:
            set_save_dir(folder)
            Path(folder).mkdir(parents=True, exist_ok=True)
            self.tray.showMessage(
                "Klasör Değiştirildi",
                folder,
                QSystemTrayIcon.Information,
                2000,
            )

    def _open_folder(self):
        os.startfile(str(get_save_dir()))

    def _quit(self):
        ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_CAPTURE)
        ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_PRTSCN)
        ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_DELAYED)
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    # Tek örnek kontrolü — zaten çalışıyorsa sessizce çık
    _mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "SnapForge_SingleInstance")
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        sys.exit(0)

    app = SnapForge()
    app.run()

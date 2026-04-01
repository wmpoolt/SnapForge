import math
import subprocess
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QToolBar, QAction, QActionGroup,
    QColorDialog, QLineEdit, QHBoxLayout, QVBoxLayout, QPushButton,
    QFrame, QLabel, QComboBox, QGraphicsDropShadowEffect, QSizePolicy,
)
from PyQt5.QtCore import Qt, QRect, QPoint, QTimer, QSize
from PyQt5.QtGui import (
    QPixmap, QPainter, QColor, QPen, QFont, QPolygon, QIcon, QBrush,
    QFontMetrics, QPainterPath,
)


# ---------------------------------------------------------------------------
# Toolbar ikonları
# ---------------------------------------------------------------------------

def _icon(draw_func, size=24):
    """24x24 ikon oluştur."""
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    draw_func(p, size)
    p.end()
    return QIcon(px)


def icon_select():
    def draw(p, s):
        pen = QPen(QColor(220, 220, 220), 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(QBrush(QColor(220, 220, 220)))
        path = QPainterPath()
        path.moveTo(s * 0.2, s * 0.15)
        path.lineTo(s * 0.2, s * 0.7)
        path.lineTo(s * 0.38, s * 0.55)
        path.lineTo(s * 0.55, s * 0.8)
        path.lineTo(s * 0.65, s * 0.72)
        path.lineTo(s * 0.48, s * 0.48)
        path.lineTo(s * 0.7, s * 0.45)
        path.closeSubpath()
        p.drawPath(path)
    return _icon(draw)


def icon_pen():
    def draw(p, s):
        pen = QPen(QColor(220, 220, 220), 2, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        # Kalem gövdesi
        p.drawLine(int(s * 0.25), int(s * 0.75), int(s * 0.7), int(s * 0.3))
        # Ucu
        p.setBrush(QBrush(QColor(220, 220, 220)))
        p.drawEllipse(int(s * 0.18), int(s * 0.74), int(s * 0.1), int(s * 0.1))
        # Kalem üst
        p.drawLine(int(s * 0.7), int(s * 0.3), int(s * 0.78), int(s * 0.18))
    return _icon(draw)


def icon_arrow():
    def draw(p, s):
        pen = QPen(QColor(220, 220, 220), 2, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(int(s * 0.2), int(s * 0.8), int(s * 0.7), int(s * 0.25))
        # Ok ucu
        p.setBrush(QBrush(QColor(220, 220, 220)))
        p.setPen(Qt.NoPen)
        poly = QPolygon([
            QPoint(int(s * 0.75), int(s * 0.18)),
            QPoint(int(s * 0.55), int(s * 0.28)),
            QPoint(int(s * 0.68), int(s * 0.42)),
        ])
        p.drawPolygon(poly)
    return _icon(draw)


def icon_rect():
    def draw(p, s):
        pen = QPen(QColor(220, 220, 220), 2)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRect(int(s * 0.18), int(s * 0.22), int(s * 0.64), int(s * 0.56))
    return _icon(draw)


def icon_text():
    def draw(p, s):
        p.setPen(QColor(220, 220, 220))
        f = QFont("Segoe UI", int(s * 0.55), QFont.Bold)
        p.setFont(f)
        p.drawText(QRect(0, 0, s, s), Qt.AlignCenter, "T")
    return _icon(draw)


def icon_blur():
    def draw(p, s):
        # Mozaik grid
        p.setPen(Qt.NoPen)
        colors = [QColor(180, 180, 180), QColor(120, 120, 120)]
        cell = s * 0.18
        for row in range(3):
            for col in range(3):
                c = colors[(row + col) % 2]
                p.setBrush(c)
                x = s * 0.16 + col * cell
                y = s * 0.16 + row * cell
                p.drawRect(int(x), int(y), int(cell - 1), int(cell - 1))
    return _icon(draw)


def icon_color():
    def draw(p, s):
        p.setPen(QPen(QColor(180, 180, 180), 1.5))
        p.setBrush(QBrush(QColor(255, 60, 60)))
        p.drawEllipse(int(s * 0.2), int(s * 0.2), int(s * 0.6), int(s * 0.6))
    return _icon(draw)


def icon_delete():
    def draw(p, s):
        pen = QPen(QColor(240, 80, 80), 2.5, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(int(s * 0.25), int(s * 0.25), int(s * 0.75), int(s * 0.75))
        p.drawLine(int(s * 0.75), int(s * 0.25), int(s * 0.25), int(s * 0.75))
    return _icon(draw)


def icon_undo():
    def draw(p, s):
        pen = QPen(QColor(220, 220, 220), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        path = QPainterPath()
        path.moveTo(s * 0.65, s * 0.3)
        path.cubicTo(s * 0.75, s * 0.5, s * 0.65, s * 0.75, s * 0.35, s * 0.65)
        p.drawPath(path)
        # Ok ucu
        p.setBrush(QBrush(QColor(220, 220, 220)))
        p.setPen(Qt.NoPen)
        poly = QPolygon([
            QPoint(int(s * 0.28), int(s * 0.6)),
            QPoint(int(s * 0.38), int(s * 0.72)),
            QPoint(int(s * 0.42), int(s * 0.55)),
        ])
        p.drawPolygon(poly)
    return _icon(draw)


def icon_new():
    def draw(p, s):
        pen = QPen(QColor(220, 220, 220), 1.8, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        # Kare çerçeve
        p.setBrush(Qt.NoBrush)
        p.drawRect(int(s * 0.2), int(s * 0.2), int(s * 0.55), int(s * 0.6))
        # Artı işareti
        cx, cy = s * 0.7, s * 0.3
        arm = s * 0.12
        p.setPen(QPen(QColor(100, 220, 100), 2.5, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(int(cx - arm), int(cy), int(cx + arm), int(cy))
        p.drawLine(int(cx), int(cy - arm), int(cx), int(cy + arm))
    return _icon(draw)


def icon_timer():
    def draw(p, s):
        pen = QPen(QColor(220, 220, 220), 1.8)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        cx, cy = s * 0.5, s * 0.52
        r = s * 0.32
        p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
        # Akrep + yelkovan
        p.setPen(QPen(QColor(220, 220, 220), 2, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(int(cx), int(cy), int(cx), int(cy - r * 0.65))
        p.drawLine(int(cx), int(cy), int(cx + r * 0.5), int(cy + r * 0.15))
        # Üst düğme
        p.drawLine(int(cx - s * 0.06), int(cy - r - s * 0.06), int(cx + s * 0.06), int(cy - r - s * 0.06))
    return _icon(draw)


def icon_width(w):
    def draw(p, s):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(220, 220, 220)))
        thickness = max(w * 1.2, 2)
        y = s / 2 - thickness / 2
        p.drawRoundedRect(int(s * 0.15), int(y), int(s * 0.7), int(thickness), 2, 2)
    return _icon(draw)


# ---------------------------------------------------------------------------
# Floating text input panel
# ---------------------------------------------------------------------------

class TextInputPanel(QFrame):
    """Tıklanan noktada açılan mini yazı düzenleme paneli."""

    def __init__(self, parent_canvas, image_pos, widget_pos):
        super().__init__(parent_canvas)
        self.canvas = parent_canvas
        self.image_pos = image_pos

        self.color = QColor(parent_canvas.pen_color)
        self.bg_color = QColor(parent_canvas.text_bg_color) if parent_canvas.text_bg_color else None
        self.font_size = parent_canvas.font_size

        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("""
            TextInputPanel {
                background: #2b2b2b;
                border: 1px solid #555;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Üst satır: renk, arka plan, boyut
        top = QHBoxLayout()
        top.setSpacing(4)

        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(28, 28)
        self.color_btn.setCursor(Qt.PointingHandCursor)
        self.color_btn.setToolTip("Yazı Rengi")
        self.color_btn.clicked.connect(self._pick_color)
        self._update_color_btn()
        top.addWidget(self.color_btn)

        self.bg_btn = QPushButton()
        self.bg_btn.setFixedSize(28, 28)
        self.bg_btn.setCursor(Qt.PointingHandCursor)
        self.bg_btn.setToolTip("Arka Plan Rengi (tıkla aç/kapat)")
        self.bg_btn.clicked.connect(self._pick_bg)
        self._update_bg_btn()
        top.addWidget(self.bg_btn)

        self.size_combo = QComboBox()
        self.size_combo.setStyleSheet("QComboBox { color: white; background: #3c3c3c; border: 1px solid #555; border-radius: 4px; padding: 2px 6px; }")
        for s in (12, 14, 18, 24, 32, 48):
            self.size_combo.addItem(f"{s}pt", s)
        idx = self.size_combo.findData(self.font_size)
        if idx >= 0:
            self.size_combo.setCurrentIndex(idx)
        self.size_combo.currentIndexChanged.connect(self._size_changed)
        top.addWidget(self.size_combo)

        top.addStretch()

        ok_btn = QPushButton("Tamam")
        ok_btn.setStyleSheet("QPushButton { color: white; background: #0078d7; border: none; border-radius: 4px; padding: 4px 12px; } QPushButton:hover { background: #1a8ae8; }")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(self._commit)
        top.addWidget(ok_btn)

        layout.addLayout(top)

        # Metin girişi
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Metni buraya yaz...")
        self._update_text_style()
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.returnPressed.connect(self._commit)
        layout.addWidget(self.text_edit)

        # Pozisyon
        self.setFixedWidth(320)
        self.adjustSize()
        x = max(0, min(widget_pos.x(), parent_canvas.width() - self.width()))
        y = max(0, widget_pos.y() + 10)
        if y + self.height() > parent_canvas.height():
            y = widget_pos.y() - self.height() - 10
        self.move(x, y)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        self.show()
        self.text_edit.setFocus()

    def _update_color_btn(self):
        self.color_btn.setStyleSheet(
            f"QPushButton {{ background: {self.color.name()}; border: 2px solid #888; border-radius: 14px; }}"
            f"QPushButton:hover {{ border-color: white; }}"
        )

    def _update_bg_btn(self):
        if self.bg_color:
            bg = self.bg_color.name()
            self.bg_btn.setStyleSheet(
                f"QPushButton {{ background: {bg}; border: 2px solid #888; border-radius: 14px; }}"
                f"QPushButton:hover {{ border-color: white; }}"
            )
        else:
            self.bg_btn.setStyleSheet(
                "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #444, stop:1 #666); border: 2px dashed #888; border-radius: 14px; }"
                "QPushButton:hover { border-color: white; }"
            )

    def _update_text_style(self):
        bg = self.bg_color.name() if self.bg_color else "#3c3c3c"
        self.text_edit.setStyleSheet(
            f"QLineEdit {{ color: {self.color.name()}; background: {bg}; "
            f"font-size: {self.font_size}px; border: 1px solid #555; "
            f"border-radius: 4px; padding: 4px; }}"
        )

    def _pick_color(self):
        c = QColorDialog.getColor(self.color, self, "Yazı Rengi")
        if c.isValid():
            self.color = c
            self._update_color_btn()
            self._update_text_style()
            self.canvas.update()

    def _pick_bg(self):
        if self.bg_color:
            self.bg_color = None
        else:
            c = QColorDialog.getColor(
                QColor(255, 255, 100, 200), self, "Arka Plan Rengi",
                QColorDialog.ShowAlphaChannel,
            )
            if c.isValid():
                self.bg_color = c
            else:
                return
        self._update_bg_btn()
        self._update_text_style()
        self.canvas.update()

    def _size_changed(self):
        self.font_size = self.size_combo.currentData()
        self._update_text_style()
        self.canvas.update()

    def _on_text_changed(self):
        self.canvas.update()

    def get_preview_annotation(self):
        text = self.text_edit.text()
        if not text:
            return None
        return {
            "type": "text",
            "start": self.image_pos,
            "end": self.image_pos,
            "color": self.color,
            "bg_color": QColor(self.bg_color) if self.bg_color else None,
            "font_size": self.font_size,
            "width": 3,
            "text": text,
        }

    def _commit(self):
        ann = self.get_preview_annotation()
        if ann:
            self.canvas.annotations.append(ann)
            self.canvas.pen_color = self.color
            self.canvas.text_bg_color = self.bg_color
            self.canvas.font_size = self.font_size
        self.canvas.text_panel = None
        self.canvas.update()
        if ann:
            self.canvas._sync_clipboard()
        self.deleteLater()

    def cancel(self):
        self.canvas.text_panel = None
        self.canvas.update()
        self.deleteLater()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancel()
        else:
            super().keyPressEvent(event)


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------

class AnnotationCanvas(QWidget):

    # Handle sabitleri
    H_NONE = 0
    H_BODY = 1
    H_TL = 2
    H_TR = 3
    H_BL = 4
    H_BR = 5
    H_START = 6   # ok başlangıcı
    H_END = 7     # ok ucu

    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.base = pixmap
        self.annotations = []
        self.current_tool = "select"
        self.pen_color = QColor(255, 40, 40)
        self.text_bg_color = None
        self.font_size = 18
        self.pen_width = 3

        # Çizim durumu
        self.drawing = False
        self.start = None
        self.end = None
        self.pen_points = []  # Kalem aracı için nokta listesi

        # Metin paneli
        self.text_panel = None

        # Seçim / taşıma / boyutlandırma
        self.selected_index = -1
        self.active_handle = self.H_NONE
        self.drag_start = None
        self.resize_fixed = None  # boyutlandırmada sabit köşe

        # Ölçekleme
        self.scale = 1.0
        self.offset = QPoint(0, 0)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    # -- Koordinat --

    def _recalc_transform(self):
        if self.base.isNull():
            return
        w_scale = self.width() / self.base.width()
        h_scale = self.height() / self.base.height()
        self.scale = min(w_scale, h_scale, 1.0)
        sw = self.base.width() * self.scale
        sh = self.base.height() * self.scale
        self.offset = QPoint(int((self.width() - sw) / 2),
                             int((self.height() - sh) / 2))

    def _to_image(self, widget_pos):
        return QPoint(
            int((widget_pos.x() - self.offset.x()) / self.scale),
            int((widget_pos.y() - self.offset.y()) / self.scale),
        )

    def resizeEvent(self, event):
        self._recalc_transform()
        super().resizeEvent(event)

    # -- Çizim --

    def paintEvent(self, _event):
        self._recalc_transform()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.fillRect(self.rect(), QColor(30, 30, 30))

        p.save()
        p.translate(self.offset)
        p.scale(self.scale, self.scale)

        p.drawPixmap(0, 0, self.base)
        for ann in self.annotations:
            _draw(p, ann, self.base)

        # Devam eden çizim
        if self.drawing:
            if self.current_tool == "pen" and len(self.pen_points) > 1:
                _draw(p, {
                    "type": "pen",
                    "points": self.pen_points,
                    "color": self.pen_color,
                    "width": self.pen_width,
                    "text": "",
                }, self.base)
            elif self.start and self.end:
                _draw(p, {
                    "type": self.current_tool,
                    "start": self.start,
                    "end": self.end,
                    "color": self.pen_color,
                    "width": self.pen_width,
                    "text": "",
                }, self.base)

        # Seçili annotation vurgusu
        if 0 <= self.selected_index < len(self.annotations):
            _draw_selection(p, self.annotations[self.selected_index])

        # Metin önizleme
        if self.text_panel:
            preview = self.text_panel.get_preview_annotation()
            if preview:
                _draw(p, preview, self.base)

        p.restore()

    # -- Hit test --

    def _find_at(self, image_pos):
        for i in range(len(self.annotations) - 1, -1, -1):
            if self._hit_test(self.annotations[i], image_pos):
                return i
        return -1

    def _hit_test(self, ann, pos):
        t = ann["type"]
        if t == "text":
            return _text_rect(ann).contains(pos)
        elif t in ("rectangle", "blur"):
            rect = QRect(ann["start"], ann["end"]).normalized()
            return rect.adjusted(-10, -10, 10, 10).contains(pos)
        elif t in ("arrow", "line"):
            return _point_near_line(pos, ann["start"], ann["end"], 12)
        elif t == "pen":
            points = ann.get("points", [])
            for i in range(1, len(points)):
                if _point_near_line(pos, points[i - 1], points[i], 12):
                    return True
            return False
        return False

    def _detect_handle(self, ann, pos):
        """Seçili annotation üzerinde hangi tutamaca tıklandığını belirle."""
        hs = 10  # tutamaç yakalama yarıçapı
        t = ann["type"]

        if t in ("rectangle", "blur"):
            rect = QRect(ann["start"], ann["end"]).normalized()
            corners = [
                (self.H_TL, rect.topLeft()),
                (self.H_TR, rect.topRight()),
                (self.H_BL, rect.bottomLeft()),
                (self.H_BR, rect.bottomRight()),
            ]
            for h, corner in corners:
                if abs(pos.x() - corner.x()) <= hs and abs(pos.y() - corner.y()) <= hs:
                    return h

        elif t in ("arrow", "line"):
            if abs(pos.x() - ann["start"].x()) <= hs and abs(pos.y() - ann["start"].y()) <= hs:
                return self.H_START
            if abs(pos.x() - ann["end"].x()) <= hs and abs(pos.y() - ann["end"].y()) <= hs:
                return self.H_END

        elif t == "text":
            rect = _text_rect(ann)
            corners = [
                (self.H_TL, rect.topLeft()),
                (self.H_TR, rect.topRight()),
                (self.H_BL, rect.bottomLeft()),
                (self.H_BR, rect.bottomRight()),
            ]
            for h, corner in corners:
                if abs(pos.x() - corner.x()) <= hs and abs(pos.y() - corner.y()) <= hs:
                    return h

        # Gövdeye tıklama
        if self._hit_test(ann, pos):
            return self.H_BODY

        return self.H_NONE

    # -- Mouse --

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        # Metin paneli açıksa ve dışına tıklandıysa commit et
        if self.text_panel and not self.text_panel.geometry().contains(event.pos()):
            self.text_panel._commit()

        pos = self._to_image(event.pos())

        # Seç modu
        if self.current_tool == "select":
            self._select_press(pos, event)
            return

        if self.current_tool == "text":
            self._open_text_panel(event.pos(), pos)
            return

        # Çizim araçları
        self.selected_index = -1
        self.drawing = True
        self.start = pos
        self.end = pos
        if self.current_tool == "pen":
            self.pen_points = [pos]
        self.update()

    def _select_press(self, pos, event):
        # Önce seçili annotation'ın tutamaçlarını kontrol et
        if 0 <= self.selected_index < len(self.annotations):
            ann = self.annotations[self.selected_index]
            handle = self._detect_handle(ann, pos)
            if handle != self.H_NONE:
                self.active_handle = handle
                self.drag_start = pos

                # Boyutlandırma için başlangıç değerlerini kaydet
                if handle in (self.H_TL, self.H_TR, self.H_BL, self.H_BR):
                    if ann["type"] in ("rectangle", "blur"):
                        rect = QRect(ann["start"], ann["end"]).normalized()
                        opposites = {
                            self.H_TL: rect.bottomRight(),
                            self.H_TR: rect.bottomLeft(),
                            self.H_BL: rect.topRight(),
                            self.H_BR: rect.topLeft(),
                        }
                        self.resize_fixed = QPoint(opposites[handle])
                    elif ann["type"] == "text":
                        self._text_resize_initial_font = ann.get("font_size", 18)
                        rect = _text_rect(ann)
                        center = rect.center()
                        dist = math.sqrt((pos.x() - center.x())**2 + (pos.y() - center.y())**2)
                        self._text_resize_initial_dist = max(dist, 1)
                        self._text_resize_center = center

                self.setCursor(Qt.ClosedHandCursor)
                self.update()
                return

        # Yeni annotation seç
        idx = self._find_at(pos)
        self.selected_index = idx
        if idx >= 0:
            self.active_handle = self.H_BODY
            self.drag_start = pos
            self.setCursor(Qt.ClosedHandCursor)
        else:
            self.active_handle = self.H_NONE
        self.update()

    def mouseMoveEvent(self, event):
        pos = self._to_image(event.pos())

        # Seç modu - sürükleme
        if self.current_tool == "select" and self.active_handle != self.H_NONE:
            self._select_drag(pos)
            return

        # Seç modu - hover cursor
        if self.current_tool == "select" and self.active_handle == self.H_NONE:
            self._update_select_cursor(pos)
            return

        # Çizim sürükleme
        if self.drawing:
            self.end = pos
            if self.current_tool == "pen":
                self.pen_points.append(pos)
            self.update()

    def _select_drag(self, pos):
        if self.selected_index < 0:
            return
        ann = self.annotations[self.selected_index]
        dx = pos.x() - self.drag_start.x()
        dy = pos.y() - self.drag_start.y()

        if self.active_handle == self.H_BODY:
            # Taşıma
            ann["start"] = QPoint(ann["start"].x() + dx, ann["start"].y() + dy)
            ann["end"] = QPoint(ann["end"].x() + dx, ann["end"].y() + dy)
            if ann["type"] == "pen" and "points" in ann:
                ann["points"] = [QPoint(p.x() + dx, p.y() + dy) for p in ann["points"]]
            self.drag_start = pos

        elif self.active_handle in (self.H_TL, self.H_TR, self.H_BL, self.H_BR):
            if ann["type"] in ("rectangle", "blur"):
                # Boyutlandırma: sabit köşe + sürüklenen köşe
                ann["start"] = QPoint(self.resize_fixed)
                ann["end"] = pos
            elif ann["type"] == "text":
                # Metin boyutlandırma: merkeze uzaklık oranı ile font_size değiştir
                center = self._text_resize_center
                dist = math.sqrt((pos.x() - center.x())**2 + (pos.y() - center.y())**2)
                ratio = dist / max(self._text_resize_initial_dist, 1)
                new_size = int(self._text_resize_initial_font * ratio)
                ann["font_size"] = max(8, min(new_size, 120))

        elif self.active_handle == self.H_START:
            ann["start"] = pos
        elif self.active_handle == self.H_END:
            ann["end"] = pos

        self.update()

    def _update_select_cursor(self, pos):
        if 0 <= self.selected_index < len(self.annotations):
            ann = self.annotations[self.selected_index]
            handle = self._detect_handle(ann, pos)
            if handle in (self.H_TL, self.H_BR):
                self.setCursor(Qt.SizeFDiagCursor)
                return
            elif handle in (self.H_TR, self.H_BL):
                self.setCursor(Qt.SizeBDiagCursor)
                return
            elif handle in (self.H_START, self.H_END):
                self.setCursor(Qt.CrossCursor)
                return
            elif handle == self.H_BODY:
                self.setCursor(Qt.OpenHandCursor)
                return

        if self._find_at(pos) >= 0:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        # Seç modu bırak
        if self.current_tool == "select" and self.active_handle != self.H_NONE:
            self.active_handle = self.H_NONE
            self.drag_start = None
            self.resize_fixed = None
            self._update_select_cursor(self._to_image(event.pos()))
            self.update()
            self._sync_clipboard()
            return

        if not self.drawing:
            return
        self.end = self._to_image(event.pos())
        self.drawing = False

        if self.current_tool == "pen":
            if len(self.pen_points) > 1:
                self.annotations.append({
                    "type": "pen",
                    "points": list(self.pen_points),
                    "start": self.pen_points[0],
                    "end": self.pen_points[-1],
                    "color": QColor(self.pen_color),
                    "width": self.pen_width,
                    "text": "",
                })
            self.pen_points = []
        else:
            rect = QRect(self.start, self.end).normalized()
            if rect.width() > 3 or rect.height() > 3:
                self.annotations.append({
                    "type": self.current_tool,
                    "start": QPoint(self.start),
                    "end": QPoint(self.end),
                    "color": QColor(self.pen_color),
                    "width": self.pen_width,
                    "text": "",
                })
        self.update()
        self._sync_clipboard()

    def mouseDoubleClickEvent(self, event):
        """Seç modunda metin'e çift tıkla → düzenle."""
        if self.current_tool != "select":
            return
        pos = self._to_image(event.pos())
        idx = self._find_at(pos)
        if idx >= 0 and self.annotations[idx]["type"] == "text":
            ann = self.annotations[idx]
            # Mevcut annotation'ı sil, paneli aç
            self.selected_index = -1
            self.annotations.pop(idx)
            self._open_text_panel(event.pos(), ann["start"])
            # Panel'e mevcut değerleri yükle
            self.text_panel.text_edit.setText(ann["text"])
            self.text_panel.color = ann["color"]
            self.text_panel.bg_color = ann.get("bg_color")
            self.text_panel.font_size = ann.get("font_size", 18)
            self.text_panel._update_color_btn()
            self.text_panel._update_bg_btn()
            idx2 = self.text_panel.size_combo.findData(self.text_panel.font_size)
            if idx2 >= 0:
                self.text_panel.size_combo.setCurrentIndex(idx2)
            self.text_panel._update_text_style()
            self.update()

    # -- Klavye --

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and 0 <= self.selected_index < len(self.annotations):
            self.annotations.pop(self.selected_index)
            self.selected_index = -1
            self.update()
        else:
            super().keyPressEvent(event)

    # -- Metin paneli --

    def _open_text_panel(self, widget_pos, image_pos):
        if self.text_panel:
            self.text_panel._commit()
        self.text_panel = TextInputPanel(self, image_pos, widget_pos)

    def commit_pending_text(self):
        if self.text_panel:
            self.text_panel._commit()

    def undo(self):
        if self.text_panel:
            self.text_panel.cancel()
            return
        if 0 <= self.selected_index < len(self.annotations):
            self.annotations.pop(self.selected_index)
            self.selected_index = -1
            self.update()
            self._sync_clipboard()
            return
        if self.annotations:
            self.annotations.pop()
            self.update()
            self._sync_clipboard()

    def delete_selected(self):
        if 0 <= self.selected_index < len(self.annotations):
            self.annotations.pop(self.selected_index)
            self.selected_index = -1
            self.update()
            self._sync_clipboard()

    def _sync_clipboard(self):
        """Her değişiklikte clipboard'ı güncelle."""
        from PyQt5.QtWidgets import QApplication
        result = QPixmap(self.base)
        p = QPainter(result)
        p.setRenderHint(QPainter.Antialiasing)
        for ann in self.annotations:
            _draw(p, ann, self.base)
        p.end()
        QApplication.clipboard().setPixmap(result)

    def render_final(self):
        self.commit_pending_text()
        result = QPixmap(self.base)
        p = QPainter(result)
        p.setRenderHint(QPainter.Antialiasing)
        for ann in self.annotations:
            _draw(p, ann, self.base)
        p.end()
        return result


# ---------------------------------------------------------------------------
# Annotation çizim fonksiyonları
# ---------------------------------------------------------------------------

def _draw(painter, ann, base_pixmap):
    t = ann["type"]
    c = ann["color"]
    w = ann["width"]
    s = ann.get("start", QPoint(0, 0))
    e = ann.get("end", QPoint(0, 0))

    if t == "arrow":
        _draw_arrow(painter, s, e, c, w)
    elif t == "line":
        painter.setPen(QPen(c, w, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(s, e)
    elif t == "pen":
        _draw_pen(painter, ann)
    elif t == "rectangle":
        painter.setPen(QPen(c, w))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QRect(s, e).normalized())
    elif t == "blur":
        _draw_blur(painter, s, e, base_pixmap)
    elif t == "text":
        _draw_text(painter, ann)


def _draw_arrow(painter, start, end, color, width):
    painter.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(start, end)

    dx = end.x() - start.x()
    dy = end.y() - start.y()
    length = math.sqrt(dx * dx + dy * dy)
    if length < 1:
        return

    angle = math.atan2(dy, dx)
    size = max(width * 4, 14)
    p1 = QPoint(int(end.x() - size * math.cos(angle - math.pi / 6)),
                int(end.y() - size * math.sin(angle - math.pi / 6)))
    p2 = QPoint(int(end.x() - size * math.cos(angle + math.pi / 6)),
                int(end.y() - size * math.sin(angle + math.pi / 6)))

    painter.setBrush(QBrush(color))
    painter.setPen(Qt.NoPen)
    painter.drawPolygon(QPolygon([end, p1, p2]))


def _draw_pen(painter, ann):
    points = ann.get("points", [])
    if len(points) < 2:
        return
    painter.setPen(QPen(ann["color"], ann["width"], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    for i in range(1, len(points)):
        painter.drawLine(points[i - 1], points[i])


def _draw_blur(painter, start, end, base_pixmap):
    rect = QRect(start, end).normalized()
    if rect.width() < 2 or rect.height() < 2:
        return
    region = base_pixmap.copy(rect)
    tiny = region.scaled(
        max(region.width() // 10, 1),
        max(region.height() // 10, 1),
        Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
    )
    blurred = tiny.scaled(region.size(), Qt.IgnoreAspectRatio, Qt.FastTransformation)
    painter.drawPixmap(rect.topLeft(), blurred)


def _text_rect(ann):
    """Metin annotation'ının sınır kutusunu hesapla."""
    font = QFont("Segoe UI", ann.get("font_size", 18))
    metrics = QFontMetrics(font)
    s = ann["start"]
    tw = metrics.horizontalAdvance(ann["text"]) if ann.get("text") else 40
    th = metrics.height()
    return QRect(s.x() - 8, s.y() - metrics.ascent() - 8, tw + 16, th + 16)


def _point_near_line(pt, start, end, threshold):
    """Noktanın çizgiye yakın olup olmadığını kontrol et."""
    dx = end.x() - start.x()
    dy = end.y() - start.y()
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        dist = math.sqrt((pt.x() - start.x())**2 + (pt.y() - start.y())**2)
        return dist <= threshold
    t = max(0, min(1, ((pt.x() - start.x()) * dx + (pt.y() - start.y()) * dy) / length_sq))
    proj_x = start.x() + t * dx
    proj_y = start.y() + t * dy
    dist = math.sqrt((pt.x() - proj_x)**2 + (pt.y() - proj_y)**2)
    return dist <= threshold


def _draw_selection(painter, ann):
    """Seçili annotation etrafına kesikli mavi çerçeve çiz."""
    t = ann["type"]
    if t == "text":
        rect = _text_rect(ann)
    elif t in ("rectangle", "blur"):
        rect = QRect(ann["start"], ann["end"]).normalized().adjusted(-4, -4, 4, 4)
    elif t in ("arrow", "line"):
        rect = QRect(ann["start"], ann["end"]).normalized().adjusted(-8, -8, 8, 8)
    elif t == "pen":
        points = ann.get("points", [])
        if not points:
            return
        xs = [p.x() for p in points]
        ys = [p.y() for p in points]
        rect = QRect(min(xs) - 6, min(ys) - 6, max(xs) - min(xs) + 12, max(ys) - min(ys) + 12)
    else:
        return

    pen = QPen(QColor(0, 120, 215), 2, Qt.DashLine)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawRect(rect)

    # Köşe tutamaçları
    handle = 6
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(QColor(0, 120, 215)))
    for corner in [rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight()]:
        painter.drawRect(corner.x() - handle // 2, corner.y() - handle // 2, handle, handle)


def _draw_text(painter, ann):
    s = ann["start"]
    c = ann["color"]
    text = ann["text"]
    font_size = ann.get("font_size", 18)
    bg_color = ann.get("bg_color")

    font = QFont("Segoe UI", font_size)
    font.setWeight(QFont.Medium)
    painter.setFont(font)

    metrics = QFontMetrics(font)
    text_width = metrics.horizontalAdvance(text)
    text_height = metrics.height()
    padding = 6

    bg_rect = QRect(
        s.x() - padding,
        s.y() - metrics.ascent() - padding,
        text_width + padding * 2,
        text_height + padding * 2,
    )

    if bg_color:
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(bg_rect, 6, 6)

    painter.setBrush(Qt.NoBrush)
    painter.setPen(c)
    painter.drawText(s, text)


# ---------------------------------------------------------------------------
# Modern alt bar (Snipping Tool tarzı)
# ---------------------------------------------------------------------------

BOTTOM_BAR_STYLE = """
    QFrame#bottomBar {
        background: rgba(32, 32, 32, 230);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    QPushButton {
        color: #e0e0e0;
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-size: 13px;
        font-family: 'Segoe UI';
    }
    QPushButton:hover {
        background: rgba(255, 255, 255, 0.12);
        color: white;
    }
    QPushButton:pressed {
        background: rgba(255, 255, 255, 0.08);
    }
    QPushButton#primary {
        background: #0078d7;
        color: white;
        font-weight: bold;
    }
    QPushButton#primary:hover {
        background: #1a8ae8;
    }
    QFrame#separator {
        background: rgba(255, 255, 255, 0.15);
        max-width: 1px;
        min-height: 24px;
    }
"""


class BottomBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("bottomBar")
        self.setStyleSheet(BOTTOM_BAR_STYLE)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        self.buttons = {}
        items = [
            ("save", "Kaydet", True),
            ("sep1", None, False),
            ("copy_img", "Kopyala", False),
            ("copy_path", "Yolu Kopyala", False),
            ("sep2", None, False),
            ("explorer", "Dosyayı Göster", False),
        ]
        for key, label, primary in items:
            if label is None:
                sep = QFrame()
                sep.setObjectName("separator")
                sep.setFixedWidth(1)
                sep.setFixedHeight(28)
                layout.addWidget(sep)
                continue
            btn = QPushButton(label)
            if primary:
                btn.setObjectName("primary")
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)
            self.buttons[key] = btn

        self.adjustSize()


# ---------------------------------------------------------------------------
# Editor penceresi
# ---------------------------------------------------------------------------

TOOLBAR_STYLE = """
    QToolBar {
        background: #1e1e1e;
        border: none;
        border-bottom: 1px solid #333;
        spacing: 2px;
        padding: 4px;
    }
    QToolButton {
        color: #ccc;
        background: transparent;
        border: none;
        border-radius: 6px;
        padding: 8px 10px;
        font-size: 12px;
        font-family: 'Segoe UI';
    }
    QToolButton:hover {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    QToolButton:checked {
        background: #0078d7;
        color: white;
    }
"""


def _apply_dark_titlebar(hwnd):
    """Windows 10/11'de koyu başlık çubuğu."""
    try:
        import ctypes
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4
        )
    except Exception:
        pass


class AnnotationEditor(QMainWindow):
    def __init__(self, pixmap, save_dir, tray=None, on_delayed=None, on_new=None):
        super().__init__()
        self.save_dir = Path(save_dir)
        self.tray = tray
        self.on_delayed = on_delayed
        self.on_new = on_new
        self.saved_path = None

        self.setWindowTitle("SnapForge")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("QMainWindow { background: #1a1a1a; }")

        # Ana uygulama ikonu
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app and app.windowIcon():
            self.setWindowIcon(app.windowIcon())

        # Canvas
        self.canvas = AnnotationCanvas(pixmap, self)
        self.setCentralWidget(self.canvas)

        self._build_toolbar()
        self._build_bottom_bar()
        self._fit_window(pixmap)

        # Koyu başlık çubuğu
        _apply_dark_titlebar(int(self.winId()))

    def _fit_window(self, pixmap):
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().availableGeometry()
        w = min(pixmap.width() + 40, screen.width() - 100)
        h = min(pixmap.height() + 140, screen.height() - 100)
        self.resize(w, h)
        self.move((screen.width() - w) // 2, (screen.height() - h) // 2)

    # -- Araç çubuğu --

    def _build_toolbar(self):
        tb = QToolBar("Araçlar")
        tb.setMovable(False)
        tb.setIconSize(QSize(22, 22))
        tb.setToolButtonStyle(Qt.ToolButtonIconOnly)
        tb.setStyleSheet(TOOLBAR_STYLE)
        self.addToolBar(tb)

        # Yeni çekim — en başta
        if self.on_new:
            new_action = QAction(icon_new(), "Yeni Çekim", self)
            new_action.setToolTip("Yeni çekim (Ctrl+N)")
            new_action.setShortcut("Ctrl+N")
            new_action.triggered.connect(self._trigger_new)
            tb.addAction(new_action)
            tb.addSeparator()

        group = QActionGroup(self)
        tools = [
            ("Seç", "select", icon_select()),
            ("Kalem", "pen", icon_pen()),
            ("Ok", "arrow", icon_arrow()),
            ("Dikdörtgen", "rectangle", icon_rect()),
            ("Yazı", "text", icon_text()),
            ("Bulanıklaştır", "blur", icon_blur()),
        ]
        for label, tool_id, ico in tools:
            action = QAction(ico, label, self)
            action.setCheckable(True)
            action.setToolTip(label)
            action.triggered.connect(lambda checked, t=tool_id: self._set_tool(t))
            group.addAction(action)
            tb.addAction(action)
            if tool_id == "select":
                action.setChecked(True)

        tb.addSeparator()

        # Renk
        self.color_action = QAction(icon_color(), "Renk", self)
        self.color_action.setToolTip("Renk")
        self.color_action.triggered.connect(self._pick_color)
        tb.addAction(self.color_action)

        tb.addSeparator()

        # Kalınlık
        for w in (2, 4, 6):
            a = QAction(icon_width(w), f"{w}px", self)
            a.setToolTip(f"Kalınlık {w}px")
            a.triggered.connect(lambda checked, pw=w: self._set_width(pw))
            tb.addAction(a)

        tb.addSeparator()

        # Sil
        delete_action = QAction(icon_delete(), "Sil", self)
        delete_action.setShortcut("Delete")
        delete_action.setToolTip("Seçili öğeyi sil (Delete)")
        delete_action.triggered.connect(self.canvas.delete_selected)
        tb.addAction(delete_action)

        # Geri al
        undo_action = QAction(icon_undo(), "Geri Al", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setToolTip("Geri al (Ctrl+Z)")
        undo_action.triggered.connect(self.canvas.undo)
        tb.addAction(undo_action)

        tb.addSeparator()

        # Gecikmeli çekim
        if self.on_delayed:
            delay_action = QAction(icon_timer(), "Gecikmeli Çekim", self)
            delay_action.setToolTip("3 saniye sonra yeni çekim")
            delay_action.triggered.connect(self._trigger_delayed)
            tb.addAction(delay_action)

    def _trigger_new(self):
        self.close()
        if self.on_new:
            self.on_new()

    def _trigger_delayed(self):
        self.close()
        if self.on_delayed:
            self.on_delayed()

    def _set_tool(self, tool_id):
        self.canvas.current_tool = tool_id
        self.canvas.selected_index = -1
        self.canvas.active_handle = self.canvas.H_NONE
        if tool_id == "select":
            self.canvas.setCursor(Qt.ArrowCursor)
        else:
            self.canvas.setCursor(Qt.CrossCursor)
        self.canvas.update()

    def _pick_color(self):
        color = QColorDialog.getColor(self.canvas.pen_color, self)
        if color.isValid():
            self.canvas.pen_color = color

    def _set_width(self, w):
        self.canvas.pen_width = w

    # -- Alt bar --

    def _build_bottom_bar(self):
        self.bottom_bar = BottomBar(self)
        self.bottom_bar.buttons["save"].clicked.connect(self._save)
        self.bottom_bar.buttons["copy_img"].clicked.connect(self._copy_image)
        self.bottom_bar.buttons["copy_path"].clicked.connect(self._copy_path)
        self.bottom_bar.buttons["explorer"].clicked.connect(self._show_in_explorer)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_bottom_bar()

    def _position_bottom_bar(self):
        bar = self.bottom_bar
        bar.adjustSize()
        x = (self.width() - bar.width()) // 2
        y = self.height() - bar.height() - 20
        bar.move(x, y)
        bar.raise_()

    # -- Aksiyonlar --

    def _ensure_saved(self):
        """Dosyayı kaydet ama pencereyi kapatma."""
        if self.saved_path and self.saved_path.exists():
            return
        self.save_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = self.save_dir / f"{ts}.png"

        final = self.canvas.render_final()
        final.save(str(path))
        self.saved_path = path

    def _save(self):
        self._ensure_saved()
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setPixmap(self.canvas.render_final())

        if self.tray:
            self.tray.showMessage(
                "Kaydedildi",
                f"{self.saved_path}\nGörüntü clipboard'a kopyalandı — Ctrl+V ile yapıştır",
                2000,
            )
        self.close()

    def _copy_image(self):
        from PyQt5.QtWidgets import QApplication
        final = self.canvas.render_final()
        QApplication.clipboard().setPixmap(final)
        if self.tray:
            self.tray.showMessage("Kopyalandı", "Ctrl+V ile yapıştırabilirsin", 1500)

    def _copy_path(self):
        self._ensure_saved()
        if self.saved_path:
            from PyQt5.QtWidgets import QApplication
            QApplication.clipboard().setText(str(self.saved_path))
            if self.tray:
                self.tray.showMessage("Yol Kopyalandı", str(self.saved_path), 1500)

    def _show_in_explorer(self):
        self._ensure_saved()
        if self.saved_path and self.saved_path.exists():
            subprocess.Popen(["explorer", "/select,", str(self.saved_path)])

    def closeEvent(self, event):
        # Kapanırken güncel halini clipboard'a kopyala
        from PyQt5.QtWidgets import QApplication
        final = self.canvas.render_final()
        QApplication.clipboard().setPixmap(final)
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

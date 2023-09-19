##
##
##

import math
from typing import Any

from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QColor, QImage, QKeyEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from hoi.structs import Action, Entity, Sample, SampleID


class HOIScene(QGraphicsScene):
    """Scene for displaying an HOI sample.

    This scene displays the image of an HOI sample with the bounding boxes of the
    entities in the sample.
    """

    def __init__(self, sample: Sample, parent: QWidget | None = None):
        super().__init__(parent=parent)

        image = QImage(sample.image_path)
        self.setSceneRect(0, 0, image.width(), image.height())
        self.addPixmap(QPixmap.fromImage(image))

        self._add_entities(sample.entities)

    def _add_entities(self, entities: list[Entity]) -> None:
        """Adds the entities to the scene.

        For each entity, a bounding box is drawn on the scene. On the top left corner
        of the bounding box, the index of the entity is drawn. The color of the
        bounding box is determined by the category of the entity.

        Parameters
        ----------
        entities : list[Entity]
            The entities to add to the scene.
        """

        categories = set(entity.category for entity in entities)
        pens = {
            category: QPen(
                QColor.fromHsv(int(360 / len(categories) * idx), 255, 255),
                2,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
            for idx, category in enumerate(categories)
        }

        for idx, entity in enumerate(entities):
            pen = pens[entity.category]
            # draw the bounding box
            bbox = entity.bbox.denormalize((self.width(), self.height())).to_xywh()
            x, y, w, h = bbox.coordinates
            self.addRect(x, y, w, h, pen=pen)

            # draw the index of the entity on the top left corner of the bounding box
            text = self.addText(str(idx))
            text.setPos(x, y)
            text.setDefaultTextColor(Qt.GlobalColor.black)
            text.setZValue(1)

            # draw a rectangle behind the text with the same color as the bounding box
            text_rect = text.boundingRect()
            text_rect.moveTopLeft(text.sceneBoundingRect().topLeft())
            self.addRect(text_rect, pen=pen, brush=pen.color())


class HOIWidget(QWidget):
    """Widget for displaying an HOI sample.

    On the left side of this widget, the image with the bounding boxes of the entities
    in the sample is displayed. On the right side of this widget, a table with the
    entities and actions in the sample is displayed.
    """

    def __init__(self, sample: Sample, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        layout = QHBoxLayout(self)

        layout.addWidget(self._create_scene(sample))
        layout.addLayout(self._create_tables(sample))

    def _create_scene(self, sample: Sample) -> QGraphicsView:
        scene = HOIScene(sample)
        view = QGraphicsView()
        view.setScene(scene)
        view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        return view

    def _create_tables(self, sample: Sample) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self._create_entity_table(sample.entities))
        layout.addWidget(self._create_action_table(sample.actions))

        return layout

    def _create_entity_table(self, entities: list[Entity]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Index", "Category"])
        table.setRowCount(len(entities))

        for idx, entity in enumerate(entities):
            table.setItem(idx, 0, QTableWidgetItem(str(idx)))
            table.setItem(idx, 1, QTableWidgetItem(entity.category))

        return table

    def _create_action_table(self, actions: list[Action]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Subject", "Verb", "Target", "Instrument"])
        table.setRowCount(len(actions))

        for idx, action in enumerate(actions):
            table.setItem(idx, 0, QTableWidgetItem(str(action.subject)))
            table.setItem(idx, 1, QTableWidgetItem(action.verb))
            table.setItem(
                idx, 2, QTableWidgetItem(str(action.target) if action.target else "")
            )
            table.setItem(
                idx,
                3,
                QTableWidgetItem(str(action.instrument) if action.instrument else ""),
            )

        return table


class HOISlider(QWidget):
    left = Signal(name="left")
    right = Signal(name="right")
    up = Signal(name="up")
    down = Signal(name="down")
    close = Signal(name="close")

    def __init__(self, sample=Sample, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        layout = QHBoxLayout(self)
        hoi_widget = HOIWidget(sample)
        layout.addWidget(hoi_widget)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        match event.key():
            case Qt.Key.Key_Right:
                self.right.emit()
            case Qt.Key.Key_Up:
                self.up.emit()
            case Qt.Key.Key_Down:
                self.down.emit()
            case Qt.Key.Key_Left:
                self.left.emit()
            case Qt.Key.Key_Escape:
                self.close.emit()
            case _:
                return super().keyReleaseEvent(event)


class MainWindow(QMainWindow):
    """Main window of the application.

    The window displays a grid where each cell displays a small version of a sample
    image. When a cell is clicked, an overlay is displayed with the image of the
    sample and a table with the entities and actions in the sample.
    """

    def __init__(self, samples: list[tuple[SampleID, Sample]]) -> None:
        super().__init__()

        self.samples = samples

        self.setWindowTitle("HOI Dataset Viewer")

        self.table = self._create_table()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.table)
        self.setCentralWidget(self.stack)

    def _create_table(self) -> QTableView:
        table = QTableView()
        table.setItemDelegate(ThumbnailDelegate())

        vertical_header = table.verticalHeader()
        vertical_header.hide()
        vertical_header.setDefaultSectionSize(350)

        horizontal_header = table.horizontalHeader()
        horizontal_header.hide()
        horizontal_header.setDefaultSectionSize(350)

        table.setShowGrid(False)
        table.doubleClicked.connect(self.on_doubleClicked)

        model = SampleTableModel(self.samples)
        table.setModel(model)

        return table

    @Slot(QModelIndex)
    def on_doubleClicked(self, index: QModelIndex) -> None:
        if not index.isValid():
            return

        if index.row() * 5 + index.column() >= len(self.samples):
            return

        if self.stack.count() == 2:
            self.stack.removeWidget(self.stack.widget(1))

        _, sample = self.samples[index.row() * 5 + index.column()]

        overlay = HOISlider(sample)
        overlay.close.connect(lambda: self.stack.removeWidget(overlay))
        overlay.left.connect(
            lambda: self.on_doubleClicked(index.siblingAtColumn(index.column() - 1))
        )
        overlay.right.connect(
            lambda: self.on_doubleClicked(index.siblingAtColumn(index.column() + 1))
        )
        overlay.up.connect(
            lambda: self.on_doubleClicked(index.siblingAtRow(index.row() - 1))
        )
        overlay.down.connect(
            lambda: self.on_doubleClicked(index.siblingAtRow(index.row() + 1))
        )

        self.stack.insertWidget(1, overlay)
        self.stack.setCurrentIndex(1)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        indexes = self.table.selectedIndexes()
        if not indexes:
            return super().keyPressEvent(event)

        index = indexes[0]
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.on_doubleClicked(index)
        else:
            super().keyPressEvent(event)


class SampleTableModel(QAbstractTableModel):
    def __init__(self, samples: list[tuple[SampleID, Sample]]) -> None:
        super().__init__()

        self.samples = samples

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
        return 0 if parent.isValid() else math.ceil(len(self.samples) / 5)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
        return 0 if parent.isValid() else 5

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        if index.row() * 5 + index.column() >= len(self.samples):
            return None

        if role == Qt.ItemDataRole.DecorationRole:
            sample = self.samples[index.row() * 5 + index.column()][1]
            image = Image.open(sample.image_path).convert("RGB")
            image.thumbnail((300, 300))
            return QPixmap.fromImage(ImageQt(image))
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        return None

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlags:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


class ThumbnailDelegate(QStyledItemDelegate):
    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        self.initStyleOption(option, index)

        painter.save()

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        pixmap: QPixmap = index.data(Qt.ItemDataRole.DecorationRole)
        rect = option.rect
        w, h = pixmap.width(), pixmap.height()
        cx, cy = rect.center().x(), rect.center().y()

        x, y = cx - w / 2, cy - h / 2

        painter.drawPixmap(x, y, pixmap)

        painter.restore()

    def sizeHint(
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        return QSize(350, 350)

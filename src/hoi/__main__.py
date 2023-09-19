##
##
##

from PySide6.QtWidgets import QApplication

from hoi.datasets import H2ODataset
from hoi.widgets import MainWindow


def main() -> None:
    dataset = H2ODataset("datasets/h2o")
    samples = list(iter(dataset))

    app = QApplication([])
    window = MainWindow(samples)
    window.setMinimumSize(800, 600)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

import sys
import requests
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QFrame,
    QTableWidget, QTableWidgetItem, QSizePolicy,
    QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages


API_BASE = "http://127.0.0.1:8000"


# ---------------- CARD ----------------
class Card(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 14px;
                padding: 18px;
            }
        """)


# ---------------- CHART CANVAS ----------------
class ChartCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


# ---------------- MAIN APP ----------------
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment CSV Analyzer")
        self.resize(1300, 800)
        self.file_path = None
        self.last_data = None
        self.last_history = []
        self.init_ui()
        self.fetch_history()

    # ---------------- UI ----------------
    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6fb;
                font-family: Segoe UI;
            }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                padding: 12px 26px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
        """)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        main = QVBoxLayout(container)
        main.setSpacing(24)
        main.setContentsMargins(24, 24, 24, 24)

        # ---------- TITLE ----------
        title = QLabel("🧪 Chemical Equipment CSV Analyzer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        main.addWidget(title)

        # ---------- UPLOAD ----------
        upload_card = Card()
        upload_layout = QHBoxLayout()

        choose_btn = QPushButton("Choose CSV")
        choose_btn.clicked.connect(self.choose_file)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color:#666; padding-left:12px;")

        upload_btn = QPushButton("Upload")
        upload_btn.clicked.connect(self.upload_file)

        pdf_btn = QPushButton("Download PDF")
        pdf_btn.clicked.connect(self.download_pdf)

        upload_layout.addWidget(choose_btn)
        upload_layout.addWidget(self.file_label, 1)
        upload_layout.addWidget(upload_btn)
        upload_layout.addWidget(pdf_btn)

        upload_card.setLayout(upload_layout)
        main.addWidget(upload_card)

        # ---------- SUMMARY ----------
        summary_card = Card()
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(40)

        self.s_total = QLabel("Total Equipment: —")
        self.s_flow = QLabel("Avg Flowrate: —")
        self.s_pressure = QLabel("Max Pressure: —")
        self.s_temp = QLabel("Temperature Range: —")

        for lbl in (self.s_total, self.s_flow, self.s_pressure, self.s_temp):
            lbl.setStyleSheet("font-size:16px; font-weight:600;")

        summary_layout.addWidget(self.s_total)
        summary_layout.addWidget(self.s_flow)
        summary_layout.addWidget(self.s_pressure)
        summary_layout.addWidget(self.s_temp)

        summary_card.setLayout(summary_layout)
        main.addWidget(summary_card)

        # ---------- CHARTS ----------
        charts = QHBoxLayout()
        charts.setSpacing(20)

        self.bar_chart = ChartCanvas()
        self.pie_chart = ChartCanvas()

        bar_card = Card()
        bar_layout = QVBoxLayout()
        bar_layout.addWidget(self.bar_chart)
        bar_card.setLayout(bar_layout)

        pie_card = Card()
        pie_layout = QVBoxLayout()
        pie_layout.addWidget(self.pie_chart)
        pie_card.setLayout(pie_layout)

        charts.addWidget(bar_card, 1)
        charts.addWidget(pie_card, 1)
        main.addLayout(charts)

        # ---------- HISTORY ----------
        history_card = Card()
        history_layout = QVBoxLayout()

        history_title = QLabel("Upload History (Last 5)")
        history_title.setStyleSheet("font-size:16px; font-weight:bold;")

        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(
            ["Filename", "Total", "Avg Flowrate", "Max Pressure", "Uploaded At"]
        )
        self.history_table.horizontalHeader().setStretchLastSection(True)

        history_layout.addWidget(history_title)
        history_layout.addWidget(self.history_table)
        history_card.setLayout(history_layout)
        main.addWidget(history_card)

        scroll.setWidget(container)
        root = QVBoxLayout(self)
        root.addWidget(scroll)

    # ---------------- FILE PICK ----------------
    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if path:
            self.file_path = path
            self.file_label.setText(path.split("/")[-1])

    # ---------------- UPLOAD ----------------
    def upload_file(self):
        if not self.file_path:
            return

        try:
            with open(self.file_path, "rb") as f:
                r = requests.post(f"{API_BASE}/api/upload/", files={"file": f})

            self.last_data = r.json()
            summary = self.last_data["summary"]
            types = self.last_data["type_distribution"]

            self.s_total.setText(f"Total Equipment: {summary['total_equipment']}")
            self.s_flow.setText(f"Avg Flowrate: {summary['avg_flowrate']}")
            self.s_pressure.setText(f"Max Pressure: {summary['max_pressure']}")
            self.s_temp.setText(
                f"Temperature Range: {summary['temperature_range'][0]} – {summary['temperature_range'][1]}"
            )

            self.bar_chart.ax.clear()
            self.bar_chart.ax.bar(
                ["Flowrate", "Pressure", "Temperature"],
                [
                    summary["avg_flowrate"],
                    summary["max_pressure"],
                    sum(summary["temperature_range"]) / 2,
                ],
                color=["#4CAF50", "#2196F3", "#FF9800"]
            )
            self.bar_chart.ax.set_title("Equipment Metrics")
            self.bar_chart.draw()

            self.pie_chart.ax.clear()
            wedges, _ = self.pie_chart.ax.pie(types.values(), startangle=90)
            self.pie_chart.ax.legend(
                wedges, types.keys(),
                loc="center left", bbox_to_anchor=(1, 0.5)
            )
            self.pie_chart.ax.set_title("Equipment Type Distribution")
            self.pie_chart.draw()

            self.fetch_history()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------------- PDF DOWNLOAD ----------------
    def download_pdf(self):
        if not self.last_data:
            QMessageBox.warning(self, "No Data", "Upload a CSV first.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        if not path:
            return

        with PdfPages(path) as pdf:
            pdf.savefig(self.bar_chart.fig)
            pdf.savefig(self.pie_chart.fig)

        QMessageBox.information(self, "Success", "PDF downloaded successfully.")

    # ---------------- HISTORY ----------------
    def fetch_history(self):
        try:
            r = requests.get(f"{API_BASE}/api/history/", timeout=2)
            self.last_history = r.json()[:5]

            self.history_table.setRowCount(len(self.last_history))
            for row, item in enumerate(self.last_history):
                self.history_table.setItem(row, 0, QTableWidgetItem(item["filename"]))
                self.history_table.setItem(row, 1, QTableWidgetItem(str(item["total_equipment"])))
                self.history_table.setItem(row, 2, QTableWidgetItem(str(item["avg_flowrate"])))
                self.history_table.setItem(row, 3, QTableWidgetItem(str(item["max_pressure"])))
                self.history_table.setItem(row, 4, QTableWidgetItem(item["uploaded_at"]))

        except Exception:
            pass


# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())

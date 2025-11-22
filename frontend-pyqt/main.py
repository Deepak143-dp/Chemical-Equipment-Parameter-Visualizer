from PyQt5.QtCore import Qt
import sys
import os
import json
import requests
import pandas as pd
from datetime import datetime
import argparse
import shutil
import webbrowser
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QTextEdit, QHBoxLayout,
    QTableWidget, QTableWidgetItem
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config import API_BASE


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chemical Equipment Visualizer')
        self.resize(1000, 700)

        # storage directory for cached/archived datasets
        self.storage_dir = os.path.join(os.path.dirname(__file__), 'stored_data')
        os.makedirs(self.storage_dir, exist_ok=True)

        layout = QVBoxLayout()

        # Upload button
        self.upload_btn = QPushButton('Upload your data or CSV')
        self.upload_btn.clicked.connect(self.upload)
        layout.addWidget(self.upload_btn)

        # Status label
        self.status = QLabel('')
        layout.addWidget(self.status)

        # (no toggle button) — desktop will always show Given Data, Summary and Chart

        # Text box (shows raw summary JSON)
        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        layout.addWidget(self.summary)

        # Plot area (created now, added into content area when rendering)
        self.fig = Figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self.fig)

        # area where tables / other output will be placed; cleared between uploads
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        # cached last-rendered payload (kept for potential future use)
        self._last_summary = None
        self._last_rows = None

        self.setLayout(layout)

    # ----------------- cached data helpers -----------------
    def _cache_path(self):
        return os.path.join(self.storage_dir, 'latest.json')

    def _archive_path(self):
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        return os.path.join(self.storage_dir, f'archive_{ts}.json')

    def _load_and_display_cached(self):
        path = self._cache_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    payload = json.load(f)
                summary = payload.get('summary', {})
                rows = payload.get('rows', [])
                name = payload.get('name', 'cached')
                uploaded_at = payload.get('uploaded_at')
                # render the cached summary + rows into the UI (chart + tables)
                self.display_summary_and_rows(summary, rows)
                if uploaded_at:
                    self.status.setText(f'Loaded cached dataset: {name} (uploaded {uploaded_at})')
                else:
                    self.status.setText(f'Loaded cached dataset: {name}')
            except Exception as e:
                # don't block startup on cache errors
                print('Failed to load cached data:', e)

    def _save_cache(self, name, summary, rows):
        """Archive existing cache and write new latest.json"""
        latest = self._cache_path()
        # archive old cache if exists
        if os.path.exists(latest):
            try:
                os.replace(latest, self._archive_path())
            except Exception:
                # best-effort: if rename fails continue
                pass

        payload = {
            'name': name,
            'uploaded_at': datetime.utcnow().isoformat() + 'Z',
            'summary': summary,
            'rows': rows
        }
        try:
            with open(latest, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print('Failed to write cache:', e)

    def display_summary_and_rows(self, summary, rows):
        # Clear previous tables/chart before rendering new output
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
            else:
                l = item.layout()
                if l:
                    while l.count():
                        it = l.takeAt(0)
                        w2 = it.widget()
                        if w2:
                            w2.setParent(None)
                    del l
        """Render the chart and two tables (summary & raw rows) in the UI.

        summary: dict mapping column -> stats
        rows: list of row dicts
        """
        # remember last payload so toggle can re-render without refetch
        self._last_summary = summary
        self._last_rows = rows

        # Update textual summary box
        try:
            self.summary.setPlainText(json.dumps(summary, indent=2))
        except Exception:
            self.summary.setPlainText(str(summary))

        # Prepare DataFrames
        try:
            df_summary = pd.DataFrame(summary).T
            df_summary.reset_index(inplace=True)
            df_summary.rename(columns={'index': 'Parameter'}, inplace=True)
        except Exception:
            df_summary = pd.DataFrame()

        try:
            df_raw = pd.DataFrame(rows)
        except Exception:
            df_raw = pd.DataFrame()

        # --- Plot: grouped bar of mean and median (if available) ---
        try:
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            if df_summary.shape[0] > 0:
                params = df_summary['Parameter'].astype(str).tolist()
                x = list(range(len(params)))

                # prepare the four statistics if available, else fill with NaN
                def col_or_nan(colname):
                    if colname in df_summary.columns:
                        return pd.to_numeric(df_summary[colname], errors='coerce').tolist()
                    return [float('nan')] * len(params)

                means = col_or_nan('mean')
                medians = col_or_nan('median')
                mins = col_or_nan('min')
                maxs = col_or_nan('max')

                # width and positions for 4 grouped bars
                width = 0.18
                bars_mean = ax.bar([xi - 1.5*width for xi in x], means, width=width, label='mean', color='#1f77b4')
                bars_median = ax.bar([xi - 0.5*width for xi in x], medians, width=width, label='median', color='#ff7f0e')
                bars_min = ax.bar([xi + 0.5*width for xi in x], mins, width=width, label='min', color='#2ca02c')
                bars_max = ax.bar([xi + 1.5*width for xi in x], maxs, width=width, label='max', color='#d62728')

                # annotate bar values on top
                try:
                    import math
                    for barset in (bars_mean, bars_median, bars_min, bars_max):
                        for bar in barset:
                            h = bar.get_height()
                            if h is None or (isinstance(h, float) and math.isnan(h)):
                                continue
                            ax.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', color='white', fontsize=8)
                except Exception:
                    pass

                ax.set_xticks(x)
                ax.set_xticklabels(params, rotation=45, ha='right')
                ax.set_ylabel('Value')
                ax.set_title('Summary statistics per Numeric Parameter')
                ax.legend()
            else:
                ax.text(0.5, 0.5, 'No numeric columns to plot', ha='center', va='center')
            self.canvas.draw()
        except Exception as e:
            print('Plot error:', e)

        # ---- Build tables & chart (stacked vertically) ----
        vbox = QVBoxLayout()

        # --- Given Data (raw table) ---
        table_raw = QTableWidget()
        if not df_raw.empty:
            table_raw.setRowCount(df_raw.shape[0])
            table_raw.setColumnCount(df_raw.shape[1])
            headers_raw = [str(c) for c in df_raw.columns]
            table_raw.setHorizontalHeaderLabels(headers_raw)
            for i in range(df_raw.shape[0]):
                for j in range(df_raw.shape[1]):
                    table_raw.setItem(i, j, QTableWidgetItem(str(df_raw.iat[i, j])))
        else:
            table_raw.setRowCount(0)
            table_raw.setColumnCount(0)

        raw_label = QLabel("Given Data")
        vbox.addWidget(raw_label)
        vbox.addWidget(table_raw)

        # --- Summary / Output table (if present) ---
        if not df_summary.empty:
            table_summary = QTableWidget()
            table_summary.setRowCount(df_summary.shape[0])
            table_summary.setColumnCount(df_summary.shape[1])
            headers = [str(c) for c in df_summary.columns]
            table_summary.setHorizontalHeaderLabels(headers)
            for i in range(df_summary.shape[0]):
                for j in range(df_summary.shape[1]):
                    table_summary.setItem(i, j, QTableWidgetItem(str(df_summary.iat[i, j])))

            summary_label = QLabel("Output (Summary Statistics)")
            vbox.addWidget(summary_label)
            vbox.addWidget(table_summary)

        # --- Chart (always shown) ---
        chart_label = QLabel("Output Chart")
        vbox.addWidget(chart_label)
        # ensure the canvas widget is reparented into the content area
        vbox.addWidget(self.canvas)

        # place into content area (clear previous)
        try:
            # clear existing content
            while self.content_layout.count():
                item = self.content_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.setParent(None)
                else:
                    l = item.layout()
                    if l:
                        # remove widgets in sublayout
                        while l.count():
                            it = l.takeAt(0)
                            w2 = it.widget()
                            if w2:
                                w2.setParent(None)
                        del l
            # replace content with our new vertical stack
            self.content_layout.addLayout(vbox)
        except Exception as e:
            print('Failed to place tables in content area:', e)

    def upload(self):
        """Upload the CSV file to the Django backend"""
        path, _ = QFileDialog.getOpenFileName(self, 'Select CSV', '', 'CSV Files (*.csv)')
        if not path:
            return

        files = {'file': open(path, 'rb')}
        r = requests.post(API_BASE + '/upload/', files=files)

        if r.status_code == 201:
            resp = r.json()
            self.status.setText('Uploaded: ' + resp.get('name',''))
            ds_id = resp.get('id')
            if ds_id:
                # call dataset-specific summary endpoint
                self.fetch_summary(ds_id)
            else:
                self.status.setText('Uploaded but backend did not return dataset id')
        else:
            self.status.setText('Error: ' + str(r.text))

    def fetch_summary(self, ds_id):
        """Fetch dataset-specific summary and show a short result in the UI.

        This uses the backend endpoint `/api/datasets/<id>/summary/`. We also
        attempt to fetch a sample of rows from `/api/datasets/<id>/rows/`.
        """
        try:
            r = requests.get(f"{API_BASE}/datasets/{ds_id}/summary/")
            if r.status_code != 200:
                try:
                    body = r.json()
                except Exception:
                    body = r.text
                self.status.setText(f"Failed to fetch summary: {r.status_code} {body}")
                return

            data = r.json()
            # try to fetch a small sample of rows to show count and to cache
            rows = []
            rows_resp = requests.get(f"{API_BASE}/datasets/{ds_id}/rows/?page=1&page_size=50")
            if rows_resp.status_code == 200:
                rows_json = rows_resp.json()
                rows = rows_json.get('rows', [])
                total = rows_json.get('total', None)
                if total is not None:
                    self.status.setText(f"Summary fetched — rows: {total}")
                else:
                    self.status.setText('Summary fetched')
            else:
                self.status.setText('Summary fetched (rows unavailable)')

            # render the fetched summary and rows into the UI
            try:
                self.display_summary_and_rows(data.get('summary', {}), rows)
            except Exception as e:
                print('Failed to render fetched data:', e)

            # fetch dataset detail to obtain a name for caching
            name = f'dataset_{ds_id}'
            try:
                detail_resp = requests.get(f"{API_BASE}/datasets/{ds_id}/")
                if detail_resp.status_code == 200:
                    detail_json = detail_resp.json()
                    name = detail_json.get('name', name)
            except Exception:
                pass

            # save summary + sample rows to local cache so it's available when user is not uploading
            try:
                self._save_cache(name, data.get('summary', {}), rows)
            except Exception as e:
                print('Failed to save cache:', e)

        except Exception as e:
            self.status.setText(f"Error fetching summary: {e}")

    def toggle_summary(self):
        """Toggle visibility of the Summary Statistics table on the desktop UI.

        When toggled, re-render the last-known payload (if any) so the
        summary table appears or disappears immediately without requiring a
        backend refetch.
        """
        try:
            self._summary_visible = bool(self.summary_toggle_btn.isChecked())
            if self._summary_visible:
                self.summary_toggle_btn.setText('Hide Summary Statistics')
            else:
                self.summary_toggle_btn.setText('Show Summary Statistics')

            # re-render last payload if present
            if self._last_summary is not None or self._last_rows is not None:
                self.display_summary_and_rows(self._last_summary or {}, self._last_rows or [])
        except Exception as e:
            print('Error toggling summary view:', e)


def _open_website(url: str):
    """Try to open the given URL in Chrome (if available) otherwise fall back to
    the system default browser.
    """
    # Prefer Google Chrome/Chromium if available
    candidates = [
        'google-chrome',
        'google-chrome-stable',
        'chrome',
        'chromium',
        'chromium-browser'
    ]

    for name in candidates:
        path = shutil.which(name)
        if path:
            try:
                # Launch the browser in a non-blocking way
                subprocess.Popen([path, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f'Opened {url} in {name} ({path})')
                return
            except Exception:
                # try next candidate
                pass

    # Fallback to Python's default browser opener
    try:
        webbrowser.open(url)
        print(f'Opened {url} in the default browser')
    except Exception as e:
        print(f'Failed to open browser for {url}: {e}')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Launch the Chemical Equipment Visualizer (desktop or website)')
    parser.add_argument('--run', choices=['Desktop', 'Website', 'desktop', 'website'], help="Which UI to run: 'Desktop' or 'Website'", default='Desktop')
    args = parser.parse_args(argv)

    choice = args.run.lower()
    if choice == 'website':
        # Attempt to open the React dev server. Default CRA dev server runs on port 3000.
        url = 'http://localhost:3000'
        # If the repo contains a build, we could open the built index.html instead; for now assume dev server
        _open_website(url)
        return 0

    # Default: run the desktop PyQt application
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec_()


if __name__ == '__main__':
    # Use main() so we can call it from tests if needed
    sys.exit(main())

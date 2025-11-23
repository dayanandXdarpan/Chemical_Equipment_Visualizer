import sys
import os
import requests
import pandas as pd
import io
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QFileDialog, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QListWidget, QSplitter, QGroupBox,
                             QFormLayout, QTabWidget, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


API_BASE_URL = 'http://localhost:8000/api'


class LoginWindow(QWidget):
    """Login/Register Window"""
    login_successful = pyqtSignal(str, str)  # token, username

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Chemical Equipment Visualizer - Login')
        self.setGeometry(100, 100, 400, 350)
        
        # Set window icon
        from PyQt5.QtGui import QIcon, QPixmap
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'public', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout()
        
        # Logo
        if os.path.exists(icon_path):
            logo_label = QLabel()
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # Title
        title = QLabel('🧪 Chemical Equipment Visualizer')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel('Hybrid Web + Desktop Application')
        subtitle.setFont(QFont('Arial', 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('color: #666; margin-bottom: 10px;')
        layout.addWidget(subtitle)
        
        # Login form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter username')
        form_layout.addRow('Username:', self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Enter password')
        form_layout.addRow('Password:', self.password_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Enter email (for registration)')
        form_layout.addRow('Email:', self.email_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet('background-color: #2a5298; color: white; padding: 10px;')
        btn_layout.addWidget(login_btn)
        
        register_btn = QPushButton('Register')
        register_btn.clicked.connect(self.register)
        register_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 10px;')
        btn_layout.addWidget(register_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter username and password')
            return
        
        try:
            response = requests.post(f'{API_BASE_URL}/auth/login/', 
                                    json={'username': username, 'password': password})
            
            if response.status_code == 200:
                data = response.json()
                token = data['token']
                self.login_successful.emit(token, username)
                self.close()
            else:
                QMessageBox.warning(self, 'Error', response.json().get('error', 'Login failed'))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Connection error: {str(e)}')

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter username and password')
            return
        
        try:
            response = requests.post(f'{API_BASE_URL}/auth/register/', 
                                    json={'username': username, 'password': password, 'email': email})
            
            if response.status_code == 201:
                data = response.json()
                token = data['token']
                self.login_successful.emit(token, username)
                self.close()
            else:
                QMessageBox.warning(self, 'Error', response.json().get('error', 'Registration failed'))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Connection error: {str(e)}')


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for charts"""
    def __init__(self, parent=None):
        fig = Figure(figsize=(8, 6))
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class MainWindow(QMainWindow):
    """Main Application Window"""
    def __init__(self, token, username):
        super().__init__()
        self.token = token
        self.username = username
        self.current_dataset = None
        self.init_ui()
        self.load_datasets()

    def init_ui(self):
        self.setWindowTitle(f'Chemical Equipment Visualizer - {self.username}')
        self.setGeometry(100, 100, 1400, 800)
        
        # Set window icon
        from PyQt5.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'public', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # Left panel - Upload and Dataset list
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Upload section
        upload_group = QGroupBox('📤 Upload CSV File')
        upload_layout = QVBoxLayout()
        
        self.file_label = QLabel('No file selected')
        upload_layout.addWidget(self.file_label)
        
        btn_layout = QHBoxLayout()
        select_btn = QPushButton('Select File')
        select_btn.clicked.connect(self.select_file)
        btn_layout.addWidget(select_btn)
        
        upload_btn = QPushButton('Upload')
        upload_btn.clicked.connect(self.upload_file)
        upload_btn.setStyleSheet('background-color: #4CAF50; color: white;')
        btn_layout.addWidget(upload_btn)
        
        upload_layout.addLayout(btn_layout)
        upload_group.setLayout(upload_layout)
        left_layout.addWidget(upload_group)
        
        # Dataset list
        dataset_group = QGroupBox('📊 Dataset History')
        dataset_layout = QVBoxLayout()
        
        self.dataset_list = QListWidget()
        self.dataset_list.itemClicked.connect(self.load_dataset_details)
        dataset_layout.addWidget(self.dataset_list)
        
        dataset_group.setLayout(dataset_layout)
        left_layout.addWidget(dataset_group)
        
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(300)
        
        # Right panel - Data visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # Summary tab
        self.summary_widget = QWidget()
        summary_layout = QVBoxLayout()
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        self.summary_widget.setLayout(summary_layout)
        
        # Table tab
        self.table_widget = QTableWidget()
        
        # Charts tab
        self.charts_widget = QWidget()
        charts_layout = QVBoxLayout()
        self.canvas1 = MatplotlibCanvas(self)
        self.canvas2 = MatplotlibCanvas(self)
        charts_layout.addWidget(self.canvas1)
        charts_layout.addWidget(self.canvas2)
        self.charts_widget.setLayout(charts_layout)
        
        self.tabs.addTab(self.summary_widget, '📋 Summary')
        self.tabs.addTab(self.table_widget, '📊 Data Table')
        self.tabs.addTab(self.charts_widget, '📈 Charts')
        
        right_layout.addWidget(self.tabs)
        
        # PDF export button
        pdf_btn = QPushButton('📄 Export PDF Report')
        pdf_btn.clicked.connect(self.export_pdf)
        pdf_btn.setStyleSheet('background-color: #e74c3c; color: white; padding: 10px;')
        right_layout.addWidget(pdf_btn)
        
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Footer with website link
        footer_widget = QWidget()
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 5, 10, 5)
        
        footer_label = QLabel('© 2025 Chemical Equipment Visualizer | Hybrid Web + Desktop App')
        footer_label.setStyleSheet('color: #666; font-size: 11px;')
        footer_layout.addWidget(footer_label)
        
        footer_layout.addStretch()
        
        website_label = QLabel('<a href="https://www.dayananddarpan.me/" style="color: #2a5298; text-decoration: none; font-weight: bold;">🌐 Developed by Dayanand Darpan</a>')
        website_label.setOpenExternalLinks(True)
        website_label.setStyleSheet('font-size: 11px;')
        footer_layout.addWidget(website_label)
        
        footer_widget.setLayout(footer_layout)
        footer_widget.setStyleSheet('background: #f0f0f0; border-top: 1px solid #ccc; padding: 5px;')
        
        main_layout.addWidget(footer_widget)
        central_widget.setLayout(main_layout)

    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if filename:
            self.selected_file = filename
            self.file_label.setText(os.path.basename(filename))

    def upload_file(self):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, 'Error', 'Please select a file first')
            return
        
        try:
            with open(self.selected_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(f'{API_BASE_URL}/datasets/upload/', files=files)
                
                if response.status_code == 201:
                    QMessageBox.information(self, 'Success', 'File uploaded successfully!')
                    self.file_label.setText('No file selected')
                    self.load_datasets()
                else:
                    QMessageBox.warning(self, 'Error', response.json().get('error', 'Upload failed'))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Upload error: {str(e)}')

    def load_datasets(self):
        try:
            response = requests.get(f'{API_BASE_URL}/datasets/')
            if response.status_code == 200:
                datasets = response.json()
                self.dataset_list.clear()
                for dataset in datasets:
                    item_text = f"{dataset['name']} ({dataset['total_count']} items)"
                    item = self.dataset_list.addItem(item_text)
                    # Store dataset ID in item data
                    self.dataset_list.item(self.dataset_list.count() - 1).setData(Qt.UserRole, dataset['id'])
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load datasets: {str(e)}')

    def load_dataset_details(self, item):
        dataset_id = item.data(Qt.UserRole)
        try:
            response = requests.get(f'{API_BASE_URL}/datasets/{dataset_id}/summary/')
            if response.status_code == 200:
                self.current_dataset = response.json()
                self.display_data()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load dataset: {str(e)}')

    def display_data(self):
        if not self.current_dataset:
            return
        
        # Display summary
        summary_html = f"""
        <h2>{self.current_dataset['dataset_name']}</h2>
        <p><b>Total Equipment:</b> {self.current_dataset['total_count']}</p>
        <h3>Average Values:</h3>
        <ul>
            <li><b>Flowrate:</b> {self.current_dataset['averages']['flowrate']}</li>
            <li><b>Pressure:</b> {self.current_dataset['averages']['pressure']}</li>
            <li><b>Temperature:</b> {self.current_dataset['averages']['temperature']}</li>
        </ul>
        <h3>Equipment Type Distribution:</h3>
        <ul>
        """
        for item in self.current_dataset['type_distribution']:
            summary_html += f"<li><b>{item['equipment_type']}:</b> {item['count']}</li>"
        summary_html += "</ul>"
        self.summary_text.setHtml(summary_html)
        
        # Display table
        equipment_list = self.current_dataset['equipment_list']
        self.table_widget.setRowCount(len(equipment_list))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        
        for row, item in enumerate(equipment_list):
            self.table_widget.setItem(row, 0, QTableWidgetItem(item['equipment_name']))
            self.table_widget.setItem(row, 1, QTableWidgetItem(item['equipment_type']))
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(round(item['flowrate'], 2))))
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(round(item['pressure'], 2))))
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(round(item['temperature'], 2))))
        
        self.table_widget.resizeColumnsToContents()
        
        # Display charts
        self.plot_charts()

    def plot_charts(self):
        if not self.current_dataset:
            return
        
        # Chart 1: Average values bar chart
        self.canvas1.axes.clear()
        averages = self.current_dataset['averages']
        labels = ['Flowrate', 'Pressure', 'Temperature']
        values = [averages['flowrate'], averages['pressure'], averages['temperature']]
        colors_list = ['#36a2eb', '#ff6384', '#ffce56']
        
        self.canvas1.axes.bar(labels, values, color=colors_list)
        self.canvas1.axes.set_title('Average Parameter Values', fontsize=14, fontweight='bold')
        self.canvas1.axes.set_ylabel('Value')
        self.canvas1.draw()
        
        # Chart 2: Equipment type distribution pie chart
        self.canvas2.axes.clear()
        type_dist = self.current_dataset['type_distribution']
        labels = [item['equipment_type'] for item in type_dist]
        sizes = [item['count'] for item in type_dist]
        
        self.canvas2.axes.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.canvas2.axes.set_title('Equipment Type Distribution', fontsize=14, fontweight='bold')
        self.canvas2.draw()

    def export_pdf(self):
        if not self.current_dataset:
            QMessageBox.warning(self, 'Error', 'No dataset loaded')
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, 'Save PDF Report', 
                                                  f"report_{self.current_dataset['dataset_id']}.pdf",
                                                  'PDF Files (*.pdf)')
        if not filename:
            return
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph(f"<b>Chemical Equipment Analysis Report</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary
            summary_text = f"""
            <b>Dataset:</b> {self.current_dataset['dataset_name']}<br/>
            <b>Total Equipment:</b> {self.current_dataset['total_count']}<br/>
            <b>Average Flowrate:</b> {self.current_dataset['averages']['flowrate']}<br/>
            <b>Average Pressure:</b> {self.current_dataset['averages']['pressure']}<br/>
            <b>Average Temperature:</b> {self.current_dataset['averages']['temperature']}
            """
            elements.append(Paragraph(summary_text, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Equipment table
            table_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
            for item in self.current_dataset['equipment_list']:
                table_data.append([
                    item['equipment_name'],
                    item['equipment_type'],
                    f"{item['flowrate']:.2f}",
                    f"{item['pressure']:.2f}",
                    f"{item['temperature']:.2f}"
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            
            doc.build(elements)
            QMessageBox.information(self, 'Success', f'PDF report saved to {filename}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to generate PDF: {str(e)}')


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Show login window
    login_window = LoginWindow()
    
    def on_login(token, username):
        main_window = MainWindow(token, username)
        main_window.show()
    
    login_window.login_successful.connect(on_login)
    login_window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

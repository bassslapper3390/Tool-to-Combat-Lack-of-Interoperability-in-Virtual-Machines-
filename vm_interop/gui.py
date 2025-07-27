import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QTabWidget,
    QTextEdit, QProgressBar, QMessageBox, QGroupBox, QLineEdit,
    QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from .converter import VMConverter
from .network_analyzer import NetworkAnalyzer
from .vm_manager import VMManager, get_machine_info
from .connectivity_verifier import ConnectivityVerifier
from .file_transfer import send_file
from .messaging import send_message, TCPServer
from .monitoring import send_stats, MonitoringAgent
from .network_orchestrator import assign_static_ip
import platform
import socket

class ConversionWorker(QThread):
    """Worker thread for VM conversion."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, input_path, output_path, input_format, output_format, options=None):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.input_format = input_format
        self.output_format = output_format
        self.options = options or {}
        
    def run(self):
        try:
            converter = VMConverter()
            success = converter.convert(
                self.input_path,
                self.output_path,
                self.input_format,
                self.output_format,
                **self.options
            )
            self.finished.emit(success, "Conversion completed successfully" if success else "Conversion failed")
        except Exception as e:
            self.finished.emit(False, str(e))

class NetworkCaptureWorker(QThread):
    """Worker thread for network capture."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, interface, duration, output_file):
        super().__init__()
        self.interface = interface
        self.duration = duration
        self.output_file = output_file
        
    def run(self):
        try:
            analyzer = NetworkAnalyzer(interface=self.interface)
            df = analyzer.capture_traffic(
                duration=self.duration,
                output_file=self.output_file
            )
            self.finished.emit(True, f"Captured {len(df)} packets")
        except Exception as e:
            self.finished.emit(False, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VM Interoperability Tool")
        self.setMinimumSize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Add conversion tab
        conversion_tab = QWidget()
        tabs.addTab(conversion_tab, "VM Conversion")
        self.setup_conversion_tab(conversion_tab)
        
        # Add interop dashboard tab
        interop_tab = QWidget()
        tabs.addTab(interop_tab, "Interop Dashboard")
        self.setup_interop_tab(interop_tab)
        
        # Add status bar
        self.statusBar().showMessage("Ready")
        
    def setup_conversion_tab(self, tab):
        """Setup the VM conversion tab."""
        layout = QVBoxLayout(tab)
        
        # Input file selection
        input_group = QGroupBox("Input VM")
        input_layout = QVBoxLayout()
        
        input_file_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)
        input_file_btn = QPushButton("Browse")
        input_file_btn.clicked.connect(self.select_input_file)
        input_file_layout.addWidget(QLabel("Input File:"))
        input_file_layout.addWidget(self.input_path)
        input_file_layout.addWidget(input_file_btn)
        
        input_format_layout = QHBoxLayout()
        self.input_format = QComboBox()
        self.input_format.addItems(["vmdk", "vdi", "vhd", "vhdx", "qcow2", "raw", "ova", "ovf"])
        self.input_format.currentTextChanged.connect(self.update_input_format)
        input_format_layout.addWidget(QLabel("Input Format:"))
        input_format_layout.addWidget(self.input_format)
        
        input_layout.addLayout(input_file_layout)
        input_layout.addLayout(input_format_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Output file selection
        output_group = QGroupBox("Output VM")
        output_layout = QVBoxLayout()
        
        # Output format selection
        output_format_layout = QHBoxLayout()
        self.output_format = QComboBox()
        self.output_format.addItems(["vmdk", "vdi", "vhd", "vhdx", "qcow2", "raw", "ova", "ovf"])
        self.output_format.currentTextChanged.connect(self.update_output_format)
        output_format_layout.addWidget(QLabel("Output Format:"))
        output_format_layout.addWidget(self.output_format)
        
        # Output file selection
        output_file_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)
        self.output_path.textChanged.connect(self.validate_output_path)
        output_file_btn = QPushButton("Browse")
        output_file_btn.clicked.connect(self.select_output_file)
        output_file_layout.addWidget(QLabel("Output File:"))
        output_file_layout.addWidget(self.output_path)
        output_file_layout.addWidget(output_file_btn)
        
        output_layout.addLayout(output_format_layout)
        output_layout.addLayout(output_file_layout)
        
        # Status label for output validation
        self.output_status = QLabel()
        self.output_status.setStyleSheet("color: gray;")
        output_layout.addWidget(self.output_status)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Progress bar
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Convert button
        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self.start_conversion)
        layout.addWidget(convert_btn)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
    def update_input_format(self, format_name):
        """Update input format and validate input file."""
        if self.input_path.text():
            self.validate_input_path()
            
    def update_output_format(self, format_name):
        """Update output format and validate output path."""
        if self.output_path.text():
            self.validate_output_path()
            
    def validate_input_path(self):
        """Validate input file path and format."""
        input_path = self.input_path.text()
        if not input_path:
            return
            
        if not os.path.exists(input_path):
            self.log_display.append(f"Error: Input file not found: {input_path}")
            return False
            
        # Check if file extension matches selected format
        ext = os.path.splitext(input_path)[1].lower().lstrip('.')
        if ext != self.input_format.currentText():
            self.log_display.append(f"Warning: File extension ({ext}) doesn't match selected format ({self.input_format.currentText()})")
            
        return True
        
    def validate_output_path(self):
        """Validate output file path and format."""
        output_path = self.output_path.text()
        if not output_path:
            self.output_status.setText("")
            return False
            
        # Check if output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            self.output_status.setText("Output directory will be created")
            self.output_status.setStyleSheet("color: orange;")
        else:
            self.output_status.setText("")
            
        # Check if output file already exists
        if os.path.exists(output_path):
            self.output_status.setText("Warning: Output file already exists")
            self.output_status.setStyleSheet("color: red;")
            return False
            
        return True
        
    def select_input_file(self):
        """Handle input file selection."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input VM",
            "",
            "VM Files (*.vmdk *.vdi *.vhd *.vhdx *.qcow2 *.raw *.ova *.ovf);;All Files (*.*)"
        )
        if file_name:
            self.input_path.setText(file_name)
            
    def select_output_file(self):
        # Get the selected output format
        output_format = self.output_format.currentText()
        # Get the input filename (without extension)
        input_filename = os.path.splitext(os.path.basename(self.input_path.text()))[0] if self.input_path.text() else "output"
        # Open folder picker
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder:
            output_path = os.path.join(folder, f"{input_filename}.{output_format}")
            self.output_path.setText(output_path)
            self.validate_output_path()
            
    def start_conversion(self):
        """Start VM conversion process (refactored for clarity and robustness)."""
        input_path = self.input_path.text()
        output_path = self.output_path.text()
        input_format = self.input_format.currentText()
        output_format = self.output_format.currentText()

        # Clear previous log
        self.log_display.clear()

        # Validate input
        if not input_path or not output_path:
            self.log_display.append("Error: Please select input and output files.")
            QMessageBox.warning(self, "Error", "Please select input and output files")
            return
        if not self.validate_input_path():
            self.log_display.append("Error: Invalid input file.")
            QMessageBox.warning(self, "Error", "Invalid input file")
            return
        if not self.validate_output_path():
            reply = QMessageBox.question(
                self,
                "Confirm Overwrite",
                "Output file already exists. Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                self.log_display.append("Conversion cancelled by user.")
                return
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                self.log_display.append(f"Failed to create output directory: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to create output directory: {str(e)}")
                return
        self.progress.setValue(0)
        self.log_display.append(f"Starting conversion: {input_path} ({input_format}) → {output_path} ({output_format})")
        self.worker = ConversionWorker(
            input_path,
            output_path,
            input_format,
            output_format
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.start()

    def conversion_finished(self, success, message):
        """Handle conversion completion."""
        self.progress.setValue(100 if success else 0)
        if success:
            self.log_display.append(f"Success: {message}")
            QMessageBox.information(self, "Success", message)
        else:
            self.log_display.append(f"Error: {message}")
            QMessageBox.warning(self, "Error", message)
            
    def setup_interop_tab(self, tab):
        """Setup the interoperability dashboard tab with all stages wired."""
        from .network_orchestrator import NetworkOrchestrator
        from .connectivity_verifier import ConnectivityVerifier
        from .file_transfer import FileTransferAgent
        from .messaging import MessagingConsole
        from .auth import AuthManager
        from .monitoring import MonitoringDashboard
        from .vm_manager import VMManager
        import os

        layout = QVBoxLayout(tab)

        # --- Environment Info Section ---
        self.env_info_label = QLabel()
        self.env_info_label.setStyleSheet("font-weight: bold; color: white;")
        self.env_info_label.setToolTip("Shows the detected OS, architecture, and available VM tool.")
        layout.addWidget(self.env_info_label)

        # --- Machine Info Section ---
        machine_info = get_machine_info()
        machine_info_text = "Detected Environment:\n" + "\n".join(f"{k}: {v}" for k, v in machine_info.items())
        self.machine_info_label = QLabel(machine_info_text)
        self.machine_info_label.setStyleSheet("font-weight: bold; color: white;")
        layout.addWidget(self.machine_info_label)

        # --- VM List Section ---
        vm_group = QGroupBox("Virtual Machines")
        vm_group.setStyleSheet("color: white; font-weight: bold;")
        vm_layout = QVBoxLayout()
        self.vm_manager = VMManager()
        self.vm_list = QTextEdit()
        self.vm_list.setReadOnly(True)
        self.vm_list.setStyleSheet("color: white; background-color: #2a2a2a;")
        self.load_vm_list()
        vm_layout.addWidget(self.vm_list)
        reload_btn = QPushButton("Reload VM List")
        reload_btn.setStyleSheet("color: white;")
        reload_btn.clicked.connect(self.load_vm_list)
        vm_layout.addWidget(reload_btn)
        vm_group.setLayout(vm_layout)
        layout.addWidget(vm_group)

        # --- Connectivity Verifier Section ---
        conn_group = QGroupBox("Connectivity Verifier")
        conn_group.setStyleSheet("color: white; font-weight: bold;")
        conn_layout = QHBoxLayout()
        self.source_ip_field = QLineEdit()
        self.source_ip_field.setPlaceholderText("Source IP")
        self.source_ip_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        self.dest_ip_field = QLineEdit()
        self.dest_ip_field.setPlaceholderText("Destination IP")
        self.dest_ip_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        verify_btn = QPushButton("Verify Connectivity (Ping)")
        verify_btn.setStyleSheet("color: white;")
        verify_btn.clicked.connect(self.on_verify_connectivity)
        self.connectivity_status = QLabel()
        self.connectivity_status.setStyleSheet("color: white;")
        conn_layout.addWidget(self.source_ip_field)
        conn_layout.addWidget(self.dest_ip_field)
        conn_layout.addWidget(verify_btn)
        conn_layout.addWidget(self.connectivity_status)
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # --- File Transfer Section ---
        file_group = QGroupBox("File Transfer")
        file_group.setStyleSheet("color: white; font-weight: bold;")
        file_layout = QHBoxLayout()
        self.file_path_field = QLineEdit()
        self.file_path_field.setPlaceholderText("Local File Path")
        self.file_path_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        file_browse_btn = QPushButton("Browse")
        file_browse_btn.setStyleSheet("color: white;")
        file_browse_btn.clicked.connect(self.on_browse_file)
        self.file_dest_ip_field = QLineEdit()
        self.file_dest_ip_field.setPlaceholderText("Destination IP")
        self.file_dest_ip_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        self.file_user_field = QLineEdit()
        self.file_user_field.setPlaceholderText("Username")
        self.file_user_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        self.file_pass_field = QLineEdit()
        self.file_pass_field.setPlaceholderText("Password")
        self.file_pass_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.file_pass_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        file_send_btn = QPushButton("Send File")
        file_send_btn.setStyleSheet("color: white;")
        file_send_btn.clicked.connect(self.on_send_file_clicked)
        self.transfer_log = QLabel()
        self.transfer_log.setStyleSheet("color: white;")
        file_layout.addWidget(self.file_path_field)
        file_layout.addWidget(file_browse_btn)
        file_layout.addWidget(self.file_dest_ip_field)
        file_layout.addWidget(self.file_user_field)
        file_layout.addWidget(self.file_pass_field)
        file_layout.addWidget(file_send_btn)
        file_layout.addWidget(self.transfer_log)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # --- Messaging Console Section ---
        msg_group = QGroupBox("Messaging Console")
        msg_group.setStyleSheet("color: white; font-weight: bold;")
        msg_layout = QHBoxLayout()
        self.message_ip_field = QLineEdit()
        self.message_ip_field.setPlaceholderText("Destination IP")
        self.message_ip_field.setToolTip("Enter the IP address of the recipient VM.")
        self.message_ip_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Message")
        self.message_input.setToolTip("Type your message here.")
        self.message_input.setStyleSheet("color: white; background-color: #2a2a2a;")
        msg_send_btn = QPushButton("Send Message")
        msg_send_btn.setToolTip("Send the message to the specified IP.")
        msg_send_btn.setStyleSheet("color: white;")
        msg_send_btn.clicked.connect(self.on_send_message_clicked)
        self.message_log = QTextEdit()
        self.message_log.setReadOnly(True)
        self.message_log.setToolTip("Received and sent messages will appear here.")
        self.message_log.setStyleSheet("color: white; background-color: #2a2a2a;")
        # TCP Server controls
        self.msg_server_status = QLabel("Server stopped")
        self.msg_server_status.setToolTip("Shows the status of the built-in messaging server.")
        self.msg_server_status.setStyleSheet("color: white;")
        self.msg_server_start_btn = QPushButton("Start Server")
        self.msg_server_start_btn.setToolTip("Start the built-in messaging server to receive messages.")
        self.msg_server_start_btn.setStyleSheet("color: white;")
        self.msg_server_stop_btn = QPushButton("Stop Server")
        self.msg_server_stop_btn.setToolTip("Stop the built-in messaging server.")
        self.msg_server_stop_btn.setStyleSheet("color: white;")
        self.msg_server_start_btn.clicked.connect(self.on_start_msg_server)
        self.msg_server_stop_btn.clicked.connect(self.on_stop_msg_server)
        msg_layout.addWidget(self.message_ip_field)
        msg_layout.addWidget(self.message_input)
        msg_layout.addWidget(msg_send_btn)
        msg_layout.addWidget(self.msg_server_start_btn)
        msg_layout.addWidget(self.msg_server_stop_btn)
        msg_layout.addWidget(self.msg_server_status)
        msg_layout.addWidget(self.message_log)
        msg_group.setLayout(msg_layout)
        layout.addWidget(msg_group)

        # --- Monitoring Dashboard Section ---
        mon_group = QGroupBox("Monitoring Dashboard")
        mon_group.setStyleSheet("color: white; font-weight: bold;")
        mon_layout = QHBoxLayout()
        self.cpu_label = QLabel("CPU: N/A")
        self.cpu_label.setToolTip("Shows the current CPU usage.")
        self.cpu_label.setStyleSheet("color: white;")
        self.ram_label = QLabel("RAM: N/A")
        self.ram_label.setToolTip("Shows the current RAM usage.")
        self.ram_label.setStyleSheet("color: white;")
        self.disk_label = QLabel("Disk: N/A")
        self.disk_label.setToolTip("Shows the current Disk usage.")
        self.disk_label.setStyleSheet("color: white;")
        self.mon_agent_status = QLabel("Agent stopped")
        self.mon_agent_status.setToolTip("Shows the status of the monitoring agent.")
        self.mon_agent_status.setStyleSheet("color: white;")
        self.mon_agent_start_btn = QPushButton("Start Agent")
        self.mon_agent_start_btn.setToolTip("Start the monitoring agent to display real-time stats.")
        self.mon_agent_start_btn.setStyleSheet("color: white;")
        self.mon_agent_stop_btn = QPushButton("Stop Agent")
        self.mon_agent_stop_btn.setToolTip("Stop the monitoring agent.")
        self.mon_agent_stop_btn.setStyleSheet("color: white;")
        self.mon_agent_start_btn.clicked.connect(self.on_start_mon_agent)
        self.mon_agent_stop_btn.clicked.connect(self.on_stop_mon_agent)
        mon_layout.addWidget(self.cpu_label)
        mon_layout.addWidget(self.ram_label)
        mon_layout.addWidget(self.disk_label)
        mon_layout.addWidget(self.mon_agent_start_btn)
        mon_layout.addWidget(self.mon_agent_stop_btn)
        mon_layout.addWidget(self.mon_agent_status)
        mon_group.setLayout(mon_layout)
        layout.addWidget(mon_group)

        # --- Network Orchestration Section ---
        net_group = QGroupBox("Network Orchestration")
        net_group.setStyleSheet("color: white; font-weight: bold;")
        net_layout = QHBoxLayout()
        self.net_ip_field = QLineEdit()
        self.net_ip_field.setPlaceholderText("VM IP")
        self.net_ip_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        self.net_user_field = QLineEdit()
        self.net_user_field.setPlaceholderText("Username")
        self.net_user_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        self.net_pass_field = QLineEdit()
        self.net_pass_field.setPlaceholderText("Password")
        self.net_pass_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.net_pass_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        self.net_target_ip_field = QLineEdit()
        self.net_target_ip_field.setPlaceholderText("Assign Static IP")
        self.net_target_ip_field.setStyleSheet("color: white; background-color: #2a2a2a;")
        net_assign_btn = QPushButton("Assign Static IP")
        net_assign_btn.setStyleSheet("color: white;")
        net_assign_btn.clicked.connect(self.on_assign_static_ip_clicked)
        self.net_status = QLabel()
        self.net_status.setStyleSheet("color: white;")
        net_layout.addWidget(self.net_ip_field)
        net_layout.addWidget(self.net_user_field)
        net_layout.addWidget(self.net_pass_field)
        net_layout.addWidget(self.net_target_ip_field)
        net_layout.addWidget(net_assign_btn)
        net_layout.addWidget(self.net_status)
        net_group.setLayout(net_layout)
        layout.addWidget(net_group)

        self.msg_server = None
        self.mon_agent = None

        self.update_env_info()

    def load_vm_list(self):
        """Load and display the list of VMs."""
        vms = self.vm_manager.list_vms()
        if vms:
            headers = ["Name", "Status", "Platform"]
            vm_text = "\t".join(headers) + "\n"
            for vm in vms:
                row = [vm.get('name', ''), vm.get('status', ''), vm.get('platform', '')]
                vm_text += "\t".join(row) + "\n"
        else:
            vm_text = "No VMs found."
        self.vm_list.setText(vm_text)

    def on_verify_connectivity(self):
        """Ping destination IP and show result."""
        ip1 = self.source_ip_field.text()
        ip2 = self.dest_ip_field.text()
        if not ip2:
            self.connectivity_status.setText("Destination IP required.")
            return
        verifier = ConnectivityVerifier()
        result = verifier.ping_vm(ip2)
        if result:
            self.connectivity_status.setText(f"{ip1} can reach {ip2} ✅")
        else:
            self.connectivity_status.setText(f"{ip1} cannot reach {ip2} ❌")

    def on_browse_file(self):
        """Open file dialog to select a file for transfer."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File to Send", "", "All Files (*.*)")
        if file_name:
            self.file_path_field.setText(file_name)

    def on_send_file_clicked(self):
        """Send file to another VM using SFTP."""
        file_path = self.file_path_field.text()
        ip = self.file_dest_ip_field.text()
        user = self.file_user_field.text()
        pwd = self.file_pass_field.text()
        if not all([file_path, ip, user, pwd]):
            self.transfer_log.setText("All fields required.")
            return
        # Check SSH server availability
        try:
            sock = socket.create_connection((ip, 22), timeout=5)
            sock.close()
        except Exception:
            self.transfer_log.setText("SSH server not available on target. Ensure SSH is enabled (OpenSSH on Windows, sshd on Linux/Mac).")
            return
        remote_path = os.path.join("/home", user, os.path.basename(file_path))
        success, msg = send_file(ip, user, pwd, file_path, remote_path)
        self.transfer_log.setText(msg if not success else "File sent!")

    def on_send_message_clicked(self):
        """Send a message to another VM."""
        ip = self.message_ip_field.text()
        msg = self.message_input.text()
        if not ip or not msg:
            self.message_log.append("IP and message required.")
            return
        port = 12345  # Default port for demo
        success, errmsg = send_message(ip, port, msg)
        if success:
            self.message_log.append(f"To {ip}: {msg}")
        else:
            self.message_log.append(f"Failed to send to {ip}: {errmsg}")

    def update_monitor_data(self, stats_dict):
        """Update monitoring dashboard with stats."""
        try:
            self.cpu_label.setText(f"CPU: {stats_dict.get('cpu', 'N/A')}%")
            self.ram_label.setText(f"RAM: {stats_dict.get('ram', 'N/A')}%")
            self.disk_label.setText(f"Disk: {stats_dict.get('disk', 'N/A')}%")
        except Exception as e:
            self.cpu_label.setText("CPU: Error")
            self.ram_label.setText("RAM: Error")
            self.disk_label.setText("Disk: Error")
            QMessageBox.warning(self, "Monitoring Error", f"Error updating stats: {e}")

    def on_assign_static_ip_clicked(self):
        """Assign a static IP to a VM via SSH."""
        ip = self.net_ip_field.text()
        user = self.net_user_field.text()
        pwd = self.net_pass_field.text()
        target_ip = self.net_target_ip_field.text()
        if not all([ip, user, pwd, target_ip]):
            self.net_status.setText("All fields required.")
            return
        # Detect remote OS (simple check via SSH)
        try:
            import paramiko
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=user, password=pwd, timeout=10)
            stdin, stdout, stderr = ssh.exec_command('uname -s')
            os_type = stdout.read().decode().strip()
            ssh.close()
        except Exception as e:
            self.net_status.setText(f"SSH error: {e}")
            return
        if os_type.lower().startswith('linux'):
            # Optionally, check for NetworkManager
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=user, password=pwd, timeout=10)
                stdin, stdout, stderr = ssh.exec_command('pgrep NetworkManager')
                nm_running = stdout.read().decode().strip()
                ssh.close()
                if nm_running:
                    self.net_status.setText("NetworkManager detected. Static IP assignment may not work. Use NetworkManager tools instead.")
                    return
            except Exception:
                pass
            success, msg = assign_static_ip(ip, user, pwd, target_ip)
            self.net_status.setText(msg if not success else "Static IP assigned!")
        else:
            self.net_status.setText("Static IP assignment only supported on Linux VMs with /etc/network/interfaces.")

    def on_start_msg_server(self):
        """Start the built-in TCP messaging server."""
        if self.msg_server and self.msg_server.is_alive():
            self.msg_server_status.setText("Server already running")
            return
        def on_message(addr, msg):
            self.message_log.append(f"From {addr[0]}:{addr[1]}: {msg}")
        try:
            self.msg_server = TCPServer(port=12345, on_message=on_message)
            self.msg_server.start()
            self.msg_server_status.setText("Server running on port 12345")
        except Exception as e:
            self.msg_server_status.setText(f"Error: {e}")

    def on_stop_msg_server(self):
        """Stop the built-in TCP messaging server."""
        if self.msg_server and self.msg_server.is_alive():
            try:
                self.msg_server.stop()
                self.msg_server.join(timeout=2)
                self.msg_server_status.setText("Server stopped")
            except Exception as e:
                self.msg_server_status.setText(f"Error: {e}")
        else:
            self.msg_server_status.setText("Server not running")

    def on_start_mon_agent(self):
        """Start the monitoring agent in a background thread."""
        if self.mon_agent and self.mon_agent.is_alive():
            self.mon_agent_status.setText("Agent already running")
            return
        def on_stats(stats):
            self.update_monitor_data(stats)
        try:
            self.mon_agent = MonitoringAgent(interval=2, on_stats=on_stats)
            self.mon_agent.start()
            self.mon_agent_status.setText("Agent running")
        except Exception as e:
            self.mon_agent_status.setText(f"Error: {e}")

    def on_stop_mon_agent(self):
        """Stop the monitoring agent."""
        if self.mon_agent and self.mon_agent.is_alive():
            try:
                self.mon_agent.stop()
                self.mon_agent.join(timeout=2)
                self.mon_agent_status.setText("Agent stopped")
            except Exception as e:
                self.mon_agent_status.setText(f"Error: {e}")
        else:
            self.mon_agent_status.setText("Agent not running")

    def update_env_info(self):
        """Update the environment info label with detected platform/tool."""
        if hasattr(self, 'vm_manager'):
            info = self.vm_manager.get_environment_info()
            self.env_info_label.setText(info)

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            color: white;
        }
        QLabel, QLineEdit, QPushButton, QGroupBox, QTextEdit, QComboBox, QProgressBar, QTabWidget, QMainWindow {
            color: white;
        }
        QLabel {
            color: white;
        }
        QLineEdit {
            color: white;
            background-color: #2a2a2a;
        }
        QTextEdit {
            color: white;
            background-color: #2a2a2a;
        }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 
from typing import Optional
import os
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from .ThermalUnitWidget import ThermalUnitWidget
from .AppColors import Colors
from src.Backend.FanControl import FanControl
from src.Backend.FanProfile import FanProfile
from .ProfileDialog import ProfileDialog
from src.Backend.AutoStart import AutoStart
from src.Backend.HotkeyManager import HotkeyManager
from .HotkeyDialog import HotkeyDialog
from src.Backend.GlobalHotkey import GlobalHotkey
import json
from src.translations.translations import Translator
from .LoaderDialog import LoaderDialog
import sys
import requests
from packaging import version

# Profile constants
PROFILE_SILENT = "Silent"
PROFILE_BALANCED = "Balanced"
PROFILE_PERFORMANCE = "Performance"
PROFILE_CUSTOM = "Custom"
PROFILE_GMODE = "G Mode"  # New profile

DEFAULT_PROFILES = [PROFILE_SILENT, PROFILE_BALANCED, PROFILE_PERFORMANCE, PROFILE_GMODE]  # Add G Mode

class FanControlGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Get correct icon path
        if getattr(sys, 'frozen', False):
            # PyInstaller packaged exe
            base_path = sys._MEIPASS
        else:
            # Python script
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Look for icon path under assets folder
        self._icon_path = os.path.join(base_path, "src", "assets", "app.ico")
        self._app_icon = QtGui.QIcon(self._icon_path)
        
        # Set icon for both window and application
        self.setWindowIcon(self._app_icon)
        QtWidgets.QApplication.instance().setWindowIcon(self._app_icon)
        
        # Normal initialization
        self.setWindowTitle("Fan Control Center")
        
        # Create Translator first
        self.translator = Translator()
        
        # System tray icon setup
        self._setupSystemTray()
        
        # Window size
        window_width = 900
        window_height = 400
        
        # Get screen geometry
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        
        # Center window on screen
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        
        # Set window geometry
        self.setGeometry(x, y, window_width, window_height)
        
        # Sidebar width
        self.sidebar_width = 250
        
        # Backend and flags
        self._fanControl = FanControl()
        self._ignoreSliderChanges = False
        self._suppressNotification = False
        self._autostart = AutoStart("Fan Control Center")
        self._hotkey_manager = HotkeyManager()
        self._hotkey_manager.initialize_default_hotkeys()
        self._global_hotkey = GlobalHotkey()
        self._global_hotkey.start()
        
        # Load saved hotkeys
        self._registerSavedHotkeys()
        
        # Hotkey listener
        self.installEventFilter(self)
        
        # Main widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QtWidgets.QWidget()
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #303030;
                color: #DDDDDD;
            }
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                margin: 2px 8px;
                font-size: 14px;
                color: #DDDDDD;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:checked {
                background-color: #1A6497;
            }
        """)
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(4)
        
        # Logo
        self.logo = QtWidgets.QLabel("Fan Control Center")
        self.logo.setStyleSheet("""
            font-size: 24px;
            padding: 20px;
            background-color: #303030;
            color: #DDDDDD;
        """)
        self.sidebar_layout.addWidget(self.logo)
        
        # Main content area
        self.content = QtWidgets.QWidget()
        self.content.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: #DDDDDD;
            }
            QLabel {
                color: #DDDDDD;
            }
            QComboBox {
                background-color: #505050;
                color: #DDDDDD;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox:hover {
                background-color: #606060;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QPushButton {
                background-color: #505050;
                color: #DDDDDD;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QCheckBox {
                color: #DDDDDD;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background-color: #505050;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
            }
            QSpinBox {
                background-color: #505050;
                color: #DDDDDD;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
            QSpinBox:hover {
                background-color: #606060;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #404040;
                border: none;
                border-radius: 2px;
                margin: 1px;
                width: 16px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #505050;
            }
            QSpinBox::up-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #DDDDDD;
            }
            QSpinBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #DDDDDD;
            }
        """)
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        
        # Top menu bar widget
        top_bar = QtWidgets.QWidget()
        top_bar_layout = QtWidgets.QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Container for hamburger menu
        hamburger_container = QtWidgets.QWidget()
        hamburger_container.setFixedWidth(50)  # Only icon width
        hamburger_layout = QtWidgets.QHBoxLayout(hamburger_container)
        hamburger_layout.setContentsMargins(10, 0, 10, 0)
        
        # Hamburger menu
        self.hamburger_button = QtWidgets.QPushButton("▶")  # Right arrow icon
        self.hamburger_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 10px;
                background-color: transparent;
                border: none;
                color: #DDDDDD;
                max-width: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: #505050;
                border-radius: 15px;
            }
        """)
        self.hamburger_button.clicked.connect(self.toggle_sidebar)
        hamburger_layout.addWidget(self.hamburger_button, 0, QtCore.Qt.AlignLeft)
        
        # Container for content
        content_container = QtWidgets.QWidget()
        content_container_layout = QtWidgets.QVBoxLayout(content_container)
        content_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Page title
        self.page_title = QtWidgets.QLabel("Dashboard")
        self.page_title.setStyleSheet("""
            font-size: 18px;
            color: #DDDDDD;
            padding: 10px;
        """)
        self.page_title.setAlignment(QtCore.Qt.AlignCenter)
        
        # Add title to content container
        content_container_layout.addWidget(self.page_title)
        
        # Stacked widget to content container
        self.stacked_widget = QtWidgets.QStackedWidget()
        content_container_layout.addWidget(self.stacked_widget)
        
        # Add widgets to top bar
        top_bar_layout.addWidget(hamburger_container)
        top_bar_layout.addWidget(content_container)
        
        # Add top bar to content layout
        self.content_layout.addWidget(top_bar)
        
        # Timer
        self._updateTimer = QtCore.QTimer(self)
        self._updateTimer.timeout.connect(self._updateStats)
        # Set default interval value
        self._updateTimer.setInterval(1000)  # Default value is 1 second
        
        # System tray setup - translator should be called after
        self._setupSystemTray()
        
        # Create pages and menu buttons
        self.create_pages()
        self.create_menu_buttons()
        
        # Add widgets to main layout
        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.content)
        
        # Load settings
        self._loadSettings()
        
        # Start update timer
        self._startUpdateTimer()
        
        # Sidebar settings
        self.sidebar_visible = False
        self.sidebar.setMinimumWidth(0)
        self.sidebar.setMaximumWidth(0)
        
        # Animations
        self.sidebar_animation = QtCore.QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_animation.setDuration(300)
        self.sidebar_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        
        self.max_animation = QtCore.QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.max_animation.setDuration(300)
        self.max_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        
        # Load last profile
        last_profile = self._hotkey_manager.get_last_profile()
        if last_profile and last_profile in self._fanControl.profile_manager.profiles:
            self._suppressNotification = True  # Suppress notification
            self._profileCombo.setCurrentText(last_profile)
            self._fanControl.apply_profile(last_profile)
            self._suppressNotification = False

    def _registerSavedHotkeys(self):
        """Load and activate saved hotkeys"""
        for profile_name, hotkey in self._hotkey_manager.hotkeys.items():
            if hotkey:
                self._global_hotkey.register(
                    hotkey,
                    lambda p=profile_name: self._onHotkeyTriggered(p)
                )

    def _onHotkeyTriggered(self, profile_name: str):
        """Called when hotkey is pressed"""
        # Prepare profile translations
        profile_translations = {
            'Silent': self.translator.get_text('profile_silent'),
            'Balanced': self.translator.get_text('profile_balanced'),
            'Performance': self.translator.get_text('profile_performance'),
            'G Mode': self.translator.get_text('profile_gmode'),
            'Custom': self.translator.get_text('profile_custom')
        }
        
        # Translate profile name
        translated_name = profile_translations.get(profile_name, profile_name)
        self._profileCombo.setCurrentText(translated_name)

    def create_pages(self):
        # Dashboard page (Main page)
        dashboard_page = QtWidgets.QWidget()
        dashboard_layout = QtWidgets.QVBoxLayout(dashboard_page)
        dashboard_layout.setSpacing(10)  # Reduce space between widgets
        
        # Profile selector - Top and compact
        profile_widget = QtWidgets.QWidget()
        profile_layout = QtWidgets.QHBoxLayout(profile_widget)
        profile_layout.setContentsMargins(10, 5, 10, 5)
        
        # Profile label
        self.profile_label = QtWidgets.QLabel(self.translator.get_text('active_profile'))
        self.profile_label.setStyleSheet("font-size: 12px;")
        
        # Profile combo box
        self._profileCombo = QtWidgets.QComboBox()
        self._profileCombo.setFixedWidth(150)  # Fixed width and small
        self._profileCombo.setStyleSheet("""
            QComboBox {
                font-size: 12px;
                padding: 3px;
            }
        """)
        
        # Prepare profile translations
        profile_translations = {
            'Silent': self.translator.get_text('profile_silent'),
            'Balanced': self.translator.get_text('profile_balanced'),
            'Performance': self.translator.get_text('profile_performance'),
            'G Mode': self.translator.get_text('profile_gmode'),
            'Custom': self.translator.get_text('profile_custom')
        }
        
        # Add translated profiles
        for profile in self._fanControl.profile_manager.profiles.keys():
            translated = profile_translations.get(profile, profile)
            self._profileCombo.addItem(translated, userData=profile)
        
        # Set active profile and configure
        current_profile = self._hotkey_manager.get_last_profile()
        if current_profile in self._fanControl.profile_manager.profiles:
            # Find and set translated profile
            translated_current = profile_translations.get(current_profile, current_profile)
            self._profileCombo.setCurrentText(translated_current)
            self._fanControl.profile_manager.current_profile = current_profile
        
        self._profileCombo.currentTextChanged.connect(self._onProfileChanged)
        
        profile_layout.addWidget(self.profile_label)
        profile_layout.addWidget(self._profileCombo)
        profile_layout.addStretch()  # Leave right side empty
        
        dashboard_layout.addWidget(profile_widget)
        
        # Fan control widgets
        self._cpuFan = ThermalUnitWidget("CPU Fan")
        self._gpuFan = ThermalUnitWidget("GPU Fan")
        dashboard_layout.addWidget(self._cpuFan)
        dashboard_layout.addWidget(self._gpuFan)
        
        self.stacked_widget.addWidget(dashboard_page)
        
        # Profile Management page
        profile_page = self.create_profile_management_page()
        self.stacked_widget.addWidget(profile_page)
        
        # Settings page
        settings_page = QtWidgets.QWidget()
        settings_layout = QtWidgets.QVBoxLayout(settings_page)
        
        # Autostart setting
        autostart_widget = QtWidgets.QWidget()
        autostart_layout = QtWidgets.QHBoxLayout(autostart_widget)
        autostart_layout.setContentsMargins(10, 5, 10, 5)
        
        self.autostart_label = QtWidgets.QLabel(self.translator.get_text('start_with_windows'))
        self.autostart_check = QtWidgets.QCheckBox("")
        self.autostart_check.setChecked(self._autostart.is_enabled())
        self.autostart_check.toggled.connect(self._toggleAutoStart)
        
        autostart_layout.addWidget(self.autostart_label)
        autostart_layout.addStretch()
        autostart_layout.addWidget(self.autostart_check)
        
        settings_layout.addWidget(autostart_widget)
        
        # Minimize to tray setting
        tray_widget = QtWidgets.QWidget()
        tray_layout = QtWidgets.QHBoxLayout(tray_widget)
        tray_layout.setContentsMargins(10, 5, 10, 5)
        
        self.tray_label = QtWidgets.QLabel(self.translator.get_text('minimize_to_tray'))
        self.tray_check = QtWidgets.QCheckBox("")
        self.tray_check.setChecked(self._loadTraySettings())
        self.tray_check.toggled.connect(self._toggleTrayMinimize)
        
        tray_layout.addWidget(self.tray_label)
        tray_layout.addStretch()
        tray_layout.addWidget(self.tray_check)
        
        settings_layout.addWidget(tray_widget)
        
        # Language setting - Text left, combobox right
        language_widget = QtWidgets.QWidget()
        language_layout = QtWidgets.QHBoxLayout(language_widget)
        language_layout.setContentsMargins(10, 5, 10, 5)
        
        self.language_label = QtWidgets.QLabel(self.translator.get_text('language'))
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(['English', 'Türkçe', 'Español', 'Français', 'Português', 'العربية', '中文', 'Русский'])
        self.language_combo.currentTextChanged.connect(self._onLanguageChanged)
        self.language_combo.setFixedWidth(150)
        
        language_layout.addWidget(self.language_label)
        language_layout.addStretch()
        language_layout.addWidget(self.language_combo)
        
        settings_layout.addWidget(language_widget)
        
        # Monitoring interval setting - Text left, spinbox and unit right
        interval_widget = QtWidgets.QWidget()
        interval_layout = QtWidgets.QHBoxLayout(interval_widget)
        interval_layout.setContentsMargins(10, 5, 10, 5)
        
        self.interval_label = QtWidgets.QLabel(self.translator.get_text('monitoring_interval'))
        
        # Container for spinbox and unit
        spinbox_container = QtWidgets.QWidget()
        spinbox_layout = QtWidgets.QHBoxLayout(spinbox_container)
        spinbox_layout.setContentsMargins(0, 0, 0, 0)
        spinbox_layout.setSpacing(5)
        
        self.interval_spinbox = QtWidgets.QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(60)
        self.interval_spinbox.setValue(int(self._updateTimer.interval() / 1000))
        self.interval_spinbox.valueChanged.connect(self._onIntervalChanged)
        self.interval_spinbox.setFixedWidth(70)
        
        self.seconds_label = QtWidgets.QLabel(self.translator.get_text('seconds'))
        
        spinbox_layout.addWidget(self.interval_spinbox)
        spinbox_layout.addWidget(self.seconds_label)
        
        interval_layout.addWidget(self.interval_label)
        interval_layout.addStretch()
        interval_layout.addWidget(spinbox_container)
        
        settings_layout.addWidget(interval_widget)
        
        # Güncelleme kontrolü butonu
        update_layout = QtWidgets.QHBoxLayout()
        self.check_update_btn = QtWidgets.QPushButton("🔄 " + self.translator.get_text('check_update'))
        self.check_update_btn.clicked.connect(self._checkForUpdates)
        self.update_status_label = QtWidgets.QLabel("")
        update_layout.addWidget(self.check_update_btn)
        update_layout.addWidget(self.update_status_label)
        update_layout.addStretch()
        settings_layout.addLayout(update_layout)
        
        self.stacked_widget.addWidget(settings_page)

    def create_profile_management_page(self):
        """Create profile management page"""
        profile_page = QtWidgets.QWidget()
        profile_layout = QtWidgets.QVBoxLayout(profile_page)
        
        # Profile selector
        profile_selector = QtWidgets.QWidget()
        selector_layout = QtWidgets.QHBoxLayout(profile_selector)
        
        # Profile label - Keep it for _updateTexts access
        self.profile_selector_label = QtWidgets.QLabel(self.translator.get_text('profile'))
        self._profileManagerCombo = QtWidgets.QComboBox()
        
        # Add "Please select" option with None userData
        self._profileManagerCombo.addItem(self.translator.get_text('please_select'), userData=None)
        
        # Add profiles with their original names as userData
        for profile in self._fanControl.profile_manager.profiles.keys():
            # Prepare profile translations
            profile_translations = {
                'Silent': self.translator.get_text('profile_silent'),
                'Balanced': self.translator.get_text('profile_balanced'),
                'Performance': self.translator.get_text('profile_performance'),
                'G Mode': self.translator.get_text('profile_gmode'),
                'Custom': self.translator.get_text('profile_custom')
            }
            # Add translated name but keep original name as userData
            translated_name = profile_translations.get(profile, profile)
            self._profileManagerCombo.addItem(translated_name, userData=profile)
        
        self._profileManagerCombo.currentTextChanged.connect(self._updateProfileInfo)
        
        selector_layout.addWidget(self.profile_selector_label)
        selector_layout.addWidget(self._profileManagerCombo)
        selector_layout.addStretch()
        
        # Profile information
        info_widget = QtWidgets.QWidget()
        info_layout = QtWidgets.QVBoxLayout(info_widget)
        
        self._profileCpuLabel = QtWidgets.QLabel(f"{self.translator.get_text('cpu_fan')}: --")
        self._profileGpuLabel = QtWidgets.QLabel(f"{self.translator.get_text('gpu_fan')}: --")
        
        info_layout.addWidget(self._profileCpuLabel)
        info_layout.addWidget(self._profileGpuLabel)
        
        # Hotkey settings
        hotkey_widget = QtWidgets.QWidget()
        hotkey_layout = QtWidgets.QHBoxLayout(hotkey_widget)
        
        hotkey_label = QtWidgets.QLabel(self.translator.get_text('hotkey'))
        self.current_hotkey_label = QtWidgets.QLabel(self.translator.get_text('not_set'))
        self.set_hotkey_btn = QtWidgets.QPushButton("⌨️ " + self.translator.get_text('set_hotkey'))
        self.set_hotkey_btn.clicked.connect(self._onSetHotkey)
        
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addWidget(self.current_hotkey_label)
        hotkey_layout.addWidget(self.set_hotkey_btn)
        hotkey_layout.addStretch()
        
        # Button group
        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout(button_widget)
        
        # Add emojis to buttons
        self.add_profile_btn = QtWidgets.QPushButton("➕ " + self.translator.get_text('add_profile'))
        self.edit_profile_btn = QtWidgets.QPushButton("✏️ " + self.translator.get_text('edit_profile'))
        self.delete_profile_btn = QtWidgets.QPushButton("🗑️ " + self.translator.get_text('delete_profile'))
        
        self.add_profile_btn.clicked.connect(self._onAddProfile)
        self.edit_profile_btn.clicked.connect(lambda: self._onEditProfile(self._profileManagerCombo.currentText()))
        self.delete_profile_btn.clicked.connect(lambda: self._onDeleteProfile(self._profileManagerCombo.currentText()))
        
        button_layout.addWidget(self.add_profile_btn)
        button_layout.addWidget(self.edit_profile_btn)
        button_layout.addWidget(self.delete_profile_btn)
        
        # Add widgets to main layout
        profile_layout.addWidget(profile_selector)
        profile_layout.addWidget(info_widget)
        profile_layout.addWidget(hotkey_widget)
        profile_layout.addWidget(button_widget)
        profile_layout.addStretch()
        
        return profile_page

    def create_menu_buttons(self):
        # Menu buttons
        self.dashboard_btn = QtWidgets.QPushButton("📊 " + self.translator.get_text('dashboard'))
        self.profiles_btn = QtWidgets.QPushButton("🔧 " + self.translator.get_text('profiles'))
        self.settings_btn = QtWidgets.QPushButton("⚙️ " + self.translator.get_text('settings'))
        
        # Add buttons to group
        button_group = QtWidgets.QButtonGroup(self)
        button_group.addButton(self.dashboard_btn)
        button_group.addButton(self.profiles_btn)
        button_group.addButton(self.settings_btn)
        
        # Select first button
        self.dashboard_btn.setChecked(True)
        
        # Add buttons to sidebar
        self.sidebar_layout.addWidget(self.dashboard_btn)
        self.sidebar_layout.addWidget(self.profiles_btn)
        self.sidebar_layout.addWidget(self.settings_btn)
        self.sidebar_layout.addStretch()
        
        # Button connections
        self.dashboard_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.profiles_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

    def switch_page(self, index):
        """Called when page changes"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Reset ComboBox when profile management page is accessed
        if index == 1:  # Profile management page
            self._profileManagerCombo.setCurrentText(self.translator.get_text('please_select'))
            self._updateProfileInfo(self.translator.get_text('please_select'))

    def toggle_sidebar(self):
        width = self.sidebar.width()
        target_width = 0 if width > 0 else self.sidebar_width
        
        # Update icon
        if target_width == 0:  # Menu closing
            self.hamburger_button.setText("▶")  # Right arrow
        else:  # Menu opening
            self.hamburger_button.setText("◀")  # Left arrow
        
        self.sidebar_animation.setStartValue(width)
        self.sidebar_animation.setEndValue(target_width)
        self.max_animation.setStartValue(width)
        self.max_animation.setEndValue(target_width)
        
        self.sidebar_animation.start()
        self.max_animation.start()
        
        self.sidebar_visible = not self.sidebar_visible

    def _setupSystemTray(self) -> None:
        """Setup system tray icon"""
        # Remove previous tray icon if exists
        if hasattr(self, '_trayIcon'):
            self._trayIcon.hide()
            del self._trayIcon
        
        self._trayIcon = QtWidgets.QSystemTrayIcon(self)
        self._trayIcon.setIcon(self._app_icon)
        self._trayIcon.setToolTip("Fan Control Center")
        
        # Tray menu
        self._trayMenu = QtWidgets.QMenu()
        
        # Profile selection submenu
        self._profilesMenu = self._trayMenu.addMenu(self.translator.get_text('profiles'))
        
        # Add profiles and create tray actions dictionary
        self._trayActions = {}
        profile_translations = {
            'Silent': self.translator.get_text('profile_silent'),
            'Balanced': self.translator.get_text('profile_balanced'),
            'Performance': self.translator.get_text('profile_performance'),
            'G Mode': self.translator.get_text('profile_gmode'),
            'Custom': self.translator.get_text('profile_custom')
        }
        
        for profile in DEFAULT_PROFILES:
            action = QAction(profile_translations.get(profile, profile), self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, p=profile: self._onProfileChanged(p))
            self._profilesMenu.addAction(action)
            self._trayActions[profile] = action
        
        # Separator
        self._trayMenu.addSeparator()
        
        # Show/Hide
        self._showAction = QAction(self.translator.get_text('show'), self)
        self._showAction.triggered.connect(self.show)
        self._trayMenu.addAction(self._showAction)
        
        # Exit
        self._exitAction = QAction(self.translator.get_text('quit'), self)
        self._exitAction.triggered.connect(self._cleanup)
        self._trayMenu.addAction(self._exitAction)
        
        # Connect menu to tray icon
        self._trayIcon.setContextMenu(self._trayMenu)
        
        # Show tray icon
        self._trayIcon.show()

    def _updateTrayTexts(self) -> None:
        """Update system tray menu texts"""
        try:
            if not hasattr(self, '_trayIcon'):
                return
            
            # Update profiles menu title
            self._profilesMenu.setTitle(self.translator.get_text('profiles'))
            
            # Update profile actions
            profile_translations = {
                'Silent': self.translator.get_text('profile_silent'),
                'Balanced': self.translator.get_text('profile_balanced'),
                'Performance': self.translator.get_text('profile_performance'),
                'G Mode': self.translator.get_text('profile_gmode'),
                'Custom': self.translator.get_text('profile_custom')
            }
            
            for profile_name, action in self._trayActions.items():
                action.setText(profile_translations.get(profile_name, profile_name))
            
            # Update Show and Exit buttons
            self._showAction.setText(self.translator.get_text('show'))
            self._exitAction.setText(self.translator.get_text('exit'))
            
        except Exception as e:
            print(f"Error in _updateTrayTexts: {e}")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Called when window is closed"""
        settings = QtCore.QSettings("Nova Web", "Fan Control Center")
        minimize_to_tray = settings.value("minimize_to_tray", True, type=bool)
        
        if minimize_to_tray and self._trayIcon.isVisible():
            event.ignore()
            self.hide()
        else:
            self._cleanup()
            event.accept()

    def _cleanup(self) -> None:
        """Clean up resources and exit application"""
        try:
            # 1. Stop timer
            if hasattr(self, '_updateTimer'):
                self._updateTimer.stop()
            
            # 2. Clean up global hotkeys
            if hasattr(self, '_global_hotkey'):
                self._global_hotkey.cleanup()
                del self._global_hotkey
            
            # 3. Clean up hotkey manager
            if hasattr(self, '_hotkey_manager'):
                del self._hotkey_manager
            
            # 4. Close FanControl and WMI connections
            if hasattr(self, '_fanControl'):
                # Save last profile
                self._fanControl.profile_manager._save_profiles()
                # Close WMI connection
                if hasattr(self._fanControl, '_awcc'):
                    del self._fanControl._awcc
                del self._fanControl
            
            # 5. Clean up system tray icon
            if hasattr(self, '_trayIcon'):
                self._trayIcon.hide()
                self._trayIcon.deleteLater()
            
            # 6. Save final settings
            self._saveSettings()
            
            # 7. Exit application completely
            QtWidgets.QApplication.quit()
            
        except Exception as e:
            print(f"Cleanup error: {e}")

    @QtCore.Slot()
    def _updateStats(self) -> None:
        """Update fan RPM and temperature values"""
        try:
            # Update RPM values
            rpms = self._fanControl.getAllFanRPM()
            if len(rpms) >= 2:
                self._cpuFan.updateRPM(rpms[0])
                self._gpuFan.updateRPM(rpms[1])
            
            # Update temperature values
            cpu_temp = self._fanControl.getSensorTemp(self._fanControl.CPU_SENSOR_ID)
            gpu_temp = self._fanControl.getSensorTemp(self._fanControl.GPU_SENSOR_ID)
            
            self._cpuFan.updateTemp(cpu_temp)
            self._gpuFan.updateTemp(gpu_temp)
            
            # Update system tray tooltip
            tooltip = f"CPU: {cpu_temp if cpu_temp else 'N/A'}°C ({rpms[0] if rpms[0] else '0'} RPM)\n"
            tooltip += f"GPU: {gpu_temp if gpu_temp else 'N/A'}°C ({rpms[1] if rpms[1] else '0'} RPM)"
            self._trayIcon.setToolTip(tooltip)
        except Exception as e:
            print(f"Update error: {e}")

    def _onProfileChanged(self, profile_name: str) -> None:
        """Called when profile changes"""
        try:
            # Convert profile name to original form
            profile_translations = {
                self.translator.get_text('profile_silent'): 'Silent',
                self.translator.get_text('profile_balanced'): 'Balanced',
                self.translator.get_text('profile_performance'): 'Performance',
                self.translator.get_text('profile_gmode'): 'G Mode',
                self.translator.get_text('profile_custom'): 'Custom'
            }
            original_name = profile_translations.get(profile_name, profile_name)
            
            # Apply profile
            if self._fanControl.apply_profile(original_name):
                # Update existing profile
                self._fanControl.profile_manager.current_profile = original_name
                self._fanControl.profile_manager._save_profiles()
                
                # Update sliders
                profile = self._fanControl.profile_manager.get_profile(original_name)
                if profile:
                    self._ignoreSliderChanges = True  # Temporarily disable slider change events
                    self._cpuFan.setSpeed(profile.cpu_speed)
                    self._gpuFan.setSpeed(profile.gpu_speed)
                    self._ignoreSliderChanges = False
                
                # Update window title
                self._updateWindowTitle()
                
                # Save settings
                self._saveSettings()
                
                # Show only one notification
                if not self._suppressNotification:
                    self.showNotification(
                        self.translator.get_text('success'),
                        self.translator.get_text('profile_applied').format(profile_name)
                    )
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    self.translator.get_text('error'),
                    self.translator.get_text('failed_apply')
                )
        except Exception as e:
            print(f"Error in _onProfileChanged: {e}")

    def _onAddProfile(self) -> None:
        """Add new profile"""
        dialog = ProfileDialog(self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            profile = dialog.getProfile()
            if self._fanControl.profile_manager.add_profile(profile):
                # Add to profile combo
                self._profileCombo.addItem(profile.name)
                
                # Add to profile management combo
                if hasattr(self, '_profileManagerCombo'):
                    current_selection = self._profileManagerCombo.currentText()
                    self._profileManagerCombo.addItem(profile.name)
                    self._profileManagerCombo.setCurrentText(current_selection)
                
                # Add to system tray menu
                if hasattr(self, '_profilesMenu'):
                    action = QAction(profile.name, self)
                    action.triggered.connect(lambda checked, p=profile.name: self._onProfileChanged(p))
                    self._trayActions[profile.name] = action
                    self._profilesMenu.addAction(action)
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    self.translator.get_text('error'),
                    self.translator.get_text('profile_exists')
                )

    def _onEditProfile(self, profile_name: str) -> None:
        """Edit existing profile"""
        if profile_name in DEFAULT_PROFILES:
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                "Default profiles cannot be edited!"
            )
            return
        
        profile = self._fanControl.profile_manager.get_profile(profile_name)
        if not profile:
            return
        
        dialog = ProfileDialog(self, profile)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            new_profile = dialog.getProfile()
            # Update profile
            self._fanControl.profile_manager.remove_profile(profile_name)
            self._fanControl.profile_manager.add_profile(new_profile)
            
            # Update combo boxes
            for combo in [self._profileCombo, self._profileManagerCombo]:
                idx = combo.findText(profile_name)
                if idx >= 0:
                    combo.removeItem(idx)
                    combo.addItem(new_profile.name)
                    if combo.currentText() == profile_name:
                        combo.setCurrentText(new_profile.name)

    def _onDeleteProfile(self, profile_name: str) -> None:
        """Delete existing profile"""
        if profile_name in DEFAULT_PROFILES:
            QtWidgets.QMessageBox.warning(
                self,
                self.translator.get_text('error'),
                self.translator.get_text('default_profile_delete')
            )
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            self.translator.get_text('warning'),
            self.translator.get_text('delete_confirm').format(profile_name),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            if self._fanControl.profile_manager.remove_profile(profile_name):
                # Remove from both combo boxes
                for combo in [self._profileCombo, self._profileManagerCombo]:
                    idx = combo.findText(profile_name)
                    if idx >= 0:
                        combo.removeItem(idx)
                
                # Set default profile
                self._profileCombo.setCurrentText(PROFILE_BALANCED)
                self._profileManagerCombo.setCurrentText(PROFILE_BALANCED)

    def _toggleAutoStart(self, checked: bool) -> None:
        """Turn automatic startup on/off"""
        if checked:
            if not self._autostart.enable():
                QtWidgets.QMessageBox.warning(
                    self,
                    self.translator.get_text('error'),
                    self.translator.get_text('failed_autostart')
                )
        else:
            if not self._autostart.disable():
                QtWidgets.QMessageBox.warning(
                    self,
                    self.translator.get_text('error'),
                    self.translator.get_text('failed_autostart_disable')
                )

    def _updateWindowTitle(self):
        """Update window title"""
        try:
            # Get profile name and translate
            current_profile = self._fanControl.profile_manager.current_profile
            
            # Prepare profile translations
            profile_translations = {
                'Silent': self.translator.get_text('profile_silent'),
                'Balanced': self.translator.get_text('profile_balanced'),
                'Performance': self.translator.get_text('profile_performance'),
                'G Mode': self.translator.get_text('profile_gmode'),
                'Custom': self.translator.get_text('profile_custom')
            }
            
            # Get translated profile name
            translated_profile = profile_translations.get(current_profile, current_profile)
            
            # Set title
            self.setWindowTitle(f"Fan Control Center - {translated_profile}")
        except Exception as e:
            print(f"Error updating window title: {e}")
            self.setWindowTitle("Fan Control Center")

    def _onManualSpeedChange(self, fanId: int, speed: int) -> None:
        """Called when manual fan speed change occurs"""
        # Ignore slider changes
        if hasattr(self, '_ignoreSliderChanges') and self._ignoreSliderChanges:
            return
        
        # Set fan speed
        if self._fanControl.setFanSpeed(fanId, speed):
            # Get existing speeds
            cpu_speed = self._cpuFan._speedSlider.value()
            gpu_speed = self._gpuFan._speedSlider.value()
            
            # Update custom profile or create
            custom_profile = FanProfile(PROFILE_CUSTOM, cpu_speed, gpu_speed)
            self._fanControl.profile_manager.profiles[PROFILE_CUSTOM] = custom_profile
            
            # Add "Custom" profile to ComboBox if not exists
            if self._profileCombo.findText(PROFILE_CUSTOM) == -1:
                self._profileCombo.addItem(PROFILE_CUSTOM)
            
            # Temporarily disable notification
            self._suppressNotification = True
            
            # Switch ComboBox to "Custom" profile
            if self._profileCombo.currentText() != PROFILE_CUSTOM:
                self._profileCombo.setCurrentText(PROFILE_CUSTOM)
            else:
                # If profile is already "Custom", call manual update method
                self._fanControl.profile_manager.current_profile = PROFILE_CUSTOM
                self._fanControl.profile_manager._save_profiles()
                self._updateWindowTitle()
            
            # Re-enable notification
            self._suppressNotification = False 

    def _startUpdateTimer(self):
        """Start timer and set fan callbacks"""
        # Set fan callbacks
        self._cpuFan.setSpeedChangeCallback(
            lambda speed: self._onManualSpeedChange(self._fanControl.CPU_FAN_ID, speed)
        )
        self._gpuFan.setSpeedChangeCallback(
            lambda speed: self._onManualSpeedChange(self._fanControl.GPU_FAN_ID, speed)
        )
        
        # Start timer (interval will be set after settings load)
        self._updateTimer.start()
        
        # Check hotkey queue
        def check_hotkey_queue():
            try:
                while not self._global_hotkey.message_queue.empty():
                    callback = self._global_hotkey.message_queue.get_nowait()
                    callback()
            except:
                pass
        
        # Add hotkey control to timer
        self._updateTimer.timeout.connect(check_hotkey_queue)

    def _updateProfileInfo(self, profile_name: str) -> None:
        """Update profile information"""
        # Get original profile name from userData
        current_index = self._profileManagerCombo.currentIndex()
        original_name = self._profileManagerCombo.itemData(current_index)
        
        if original_name is None:  # "Please select" option
            self._profileCpuLabel.setText(f"{self.translator.get_text('cpu_fan')}: -")
            self._profileGpuLabel.setText(f"{self.translator.get_text('gpu_fan')}: -")
            self.current_hotkey_label.setText(self.translator.get_text('not_set'))
            return
        
        profile = self._fanControl.profile_manager.get_profile(original_name)
        if profile:
            self._profileCpuLabel.setText(f"{self.translator.get_text('cpu_fan')}: {profile.cpu_speed}%")
            self._profileGpuLabel.setText(f"{self.translator.get_text('gpu_fan')}: {profile.gpu_speed}%")
            
            # Update hotkey
            hotkey = self._hotkey_manager.get_hotkey(original_name) or self.translator.get_text('not_set')
            self.current_hotkey_label.setText(hotkey)
        else:
            self._profileCpuLabel.setText(f"{self.translator.get_text('cpu_fan')}: --")
            self._profileGpuLabel.setText(f"{self.translator.get_text('gpu_fan')}: --")
            self.current_hotkey_label.setText(self.translator.get_text('not_set'))

    def updateHotkeysTable(self):
        """Update hotkeys table"""
        self.hotkeys_table.setRowCount(len(self._fanControl.profile_manager.profiles))
        
        # Prepare profile translations
        profile_translations = {
            'Silent': self.translator.get_text('profile_silent'),
            'Balanced': self.translator.get_text('profile_balanced'),
            'Performance': self.translator.get_text('profile_performance'),
            'G Mode': self.translator.get_text('profile_gmode'),
            'Custom': self.translator.get_text('profile_custom')
        }
        
        for row, profile_name in enumerate(self._fanControl.profile_manager.profiles.keys()):
            # Profile name
            translated_name = profile_translations.get(profile_name, profile_name)
            profile_item = QtWidgets.QTableWidgetItem(translated_name)
            profile_item.setFlags(profile_item.flags() & ~Qt.ItemIsEditable)
            self.hotkeys_table.setItem(row, 0, profile_item)
            
            # Hotkey
            hotkey = self._hotkey_manager.get_hotkey(profile_name) or self.translator.get_text('not_set')
            hotkey_item = QtWidgets.QTableWidgetItem(hotkey)
            hotkey_item.setFlags(hotkey_item.flags() & ~Qt.ItemIsEditable)
            self.hotkeys_table.setItem(row, 1, hotkey_item)

    def _onSetHotkey(self):
        """Set hotkey for selected profile"""
        # Get original profile name from userData
        current_index = self._profileManagerCombo.currentIndex()
        profile_name = self._profileManagerCombo.itemData(current_index)
        
        if profile_name is None:  # "Please select" option seçiliyse
            QtWidgets.QMessageBox.warning(
                self,
                self.translator.get_text('error'),
                self.translator.get_text('select_profile')
            )
            return
        
        # Wait for hotkey dialog
        dialog = HotkeyDialog(self)
        if dialog.exec() == QtWidgets.QDialog.Accepted and dialog.key_sequence:
            # Remove old hotkey
            old_hotkey = self._hotkey_manager.get_hotkey(profile_name)
            if old_hotkey:
                self._global_hotkey.unregister(old_hotkey)
            
            # Save and activate new hotkey
            self._hotkey_manager.set_hotkey(profile_name, dialog.key_sequence)
            self._global_hotkey.register(
                dialog.key_sequence,
                lambda: self._onHotkeyTriggered(profile_name)
            )
            
            # Update hotkey label
            self.current_hotkey_label.setText(dialog.key_sequence)

    def _onIntervalChanged(self, value: int):
        """Update performance monitoring interval"""
        # Convert to milliseconds
        interval_ms = value * 1000
        
        # Update timer
        self._updateTimer.setInterval(interval_ms)
        
        # Save setting
        self._saveSettings()

    def _saveSettings(self):
        """Save settings"""
        try:
            settings = {
                'monitoring_interval': self.interval_spinbox.value(),
                'language': self.translator.current_language,
                'last_profile': self._fanControl.profile_manager.current_profile,
                'minimize_to_tray': self.tray_check.isChecked()
            }
            
            # Save settings as JSON
            settings_path = os.path.join(
                os.getenv('APPDATA', os.path.expanduser('~')),
                'FanControl',
                'settings.json'
            )
            
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def _loadSettings(self):
        """Load settings"""
        try:
            settings_path = os.path.join(
                os.getenv('APPDATA', os.path.expanduser('~')),
                'FanControl',
                'settings.json'
            )
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    
                # Load monitoring interval setting
                if 'monitoring_interval' in settings:
                    interval = max(1, int(settings['monitoring_interval']))  # Minimum 1 second
                    self.interval_spinbox.setValue(interval)
                    self._updateTimer.setInterval(interval * 1000)
                    
                # Load language setting
                if 'language' in settings:
                    lang_map = {
                        'en': 'English',
                        'tr': 'Türkçe',
                        'es': 'Español',
                        'fr': 'Français',
                        'pt': 'Português',
                        'ar': 'العربية',
                        'zh': '中文',
                        'ru': 'Русский'
                    }
                    if settings['language'] in lang_map:
                        self.language_combo.setCurrentText(lang_map[settings['language']])
                    
                # Load last used profile and apply
                if 'last_profile' in settings:
                    last_profile = settings['last_profile']
                    if last_profile in self._fanControl.profile_manager.profiles:
                        # Temporarily disable notification
                        self._suppressNotification = True
                        # Set profile and apply
                        self._profileCombo.setCurrentText(last_profile)
                        self._onProfileChanged(last_profile)
                        # Re-enable notification
                        self._suppressNotification = False
                        
        except Exception as e:
            print(f"Failed to load settings: {e}") 

    def _onLanguageChanged(self, language: str):
        """Called when language changes"""
        lang_map = {
            'English': 'en',
            'Türkçe': 'tr',
            'Español': 'es',
            'Français': 'fr',
            'Português': 'pt',
            'العربية': 'ar',  # Arabic
            '中文': 'zh',      # Chinese
            'Русский': 'ru'  # Russian
        }
        
        if language in lang_map:
            # Temporarily disable notification
            self._suppressNotification = True
            
            # Change language and update texts
            self.translator.set_language(lang_map[language])
            self._updateTexts()
            self._saveSettings()
            
            # Re-enable notification
            self._suppressNotification = False

    def _updateTexts(self):
        """Update all texts"""
        try:
            # Page titles
            self.page_title.setText(self.translator.get_text('dashboard'))
            
            # Profile selector
            self.profile_label.setText(self.translator.get_text('active_profile'))
            
            # Fan widgets
            self._cpuFan.setTitle(self.translator.get_text('cpu_fan'))
            self._gpuFan.setTitle(self.translator.get_text('gpu_fan'))
            
            # Menu buttons (with emojis)
            self.dashboard_btn.setText("📊 " + self.translator.get_text('dashboard'))
            self.profiles_btn.setText("🔧 " + self.translator.get_text('profiles'))
            self.settings_btn.setText("⚙️ " + self.translator.get_text('settings'))
            
            # Logo
            self.logo.setText(self.translator.get_text('fan_control'))
            
            # Settings page
            if hasattr(self, 'autostart_label'):
                self.autostart_label.setText(self.translator.get_text('start_with_windows'))
            if hasattr(self, 'tray_label'):
                self.tray_label.setText(self.translator.get_text('minimize_to_tray'))
            if hasattr(self, 'language_label'):
                self.language_label.setText(self.translator.get_text('language'))
            if hasattr(self, 'interval_label'):
                self.interval_label.setText(self.translator.get_text('monitoring_interval'))
            if hasattr(self, 'seconds_label'):
                self.seconds_label.setText(self.translator.get_text('seconds'))
            if hasattr(self, 'hotkeys_group'):
                self.hotkeys_group.setTitle(self.translator.get_text('profile_hotkeys'))
            
            # Hotkeys table
            if hasattr(self, 'hotkeys_table'):
                self.hotkeys_table.setHorizontalHeaderLabels([
                    self.translator.get_text('profile'),
                    self.translator.get_text('hotkey')
                ])
            
            # Hotkey setting button
            if hasattr(self, 'set_hotkey_btn'):
                self.set_hotkey_btn.setText(self.translator.get_text('set_hotkey'))
            
            # Profile management buttons
            if hasattr(self, 'add_profile_btn'):
                self.add_profile_btn.setText("➕ " + self.translator.get_text('add_profile'))
            if hasattr(self, 'edit_profile_btn'):
                self.edit_profile_btn.setText("✏️ " + self.translator.get_text('edit_profile'))
            if hasattr(self, 'delete_profile_btn'):
                self.delete_profile_btn.setText("🗑️ " + self.translator.get_text('delete_profile'))
            
            # Profile management page
            if hasattr(self, '_profileCpuLabel'):
                current_speed = self._profileCpuLabel.text().split(':')[1] if ':' in self._profileCpuLabel.text() else ''
                self._profileCpuLabel.setText(f"{self.translator.get_text('cpu_fan')}: {current_speed}")
            if hasattr(self, '_profileGpuLabel'):
                current_speed = self._profileGpuLabel.text().split(':')[1] if ':' in self._profileGpuLabel.text() else ''
                self._profileGpuLabel.setText(f"{self.translator.get_text('gpu_fan')}: {current_speed}")
            
            # Profile names
            self._updateProfileNames()
            
            # Window title
            self._updateWindowTitle()
            
            # Profile management page labels
            if hasattr(self, 'profile_selector_label'):
                self.profile_selector_label.setText(self.translator.get_text('profile'))
            
            # System tray menu
            if hasattr(self, '_trayIcon'):
                # Directly call _updateTrayTexts
                self._updateTrayTexts()
                
        except Exception as e:
            print(f"Error in _updateTexts: {e}")

    def _updateProfileNames(self):
        """Translate and update profile names"""
        # Translate default profile names
        profile_translations = {
            'Silent': self.translator.get_text('profile_silent'),
            'Balanced': self.translator.get_text('profile_balanced'),
            'Performance': self.translator.get_text('profile_performance'),
            'Custom': self.translator.get_text('profile_custom'),
            'G Mode': self.translator.get_text('profile_gmode')
        }
        
        # Reverse translation dictionary
        reverse_translations = {v: k for k, v in profile_translations.items()}
        
        # Update main ComboBox
        if hasattr(self, '_profileCombo'):
            current = self._profileCombo.currentText()
            current_original = reverse_translations.get(current, current)
            
            self._profileCombo.blockSignals(True)
            self._profileCombo.clear()
            for profile in self._fanControl.profile_manager.profiles.keys():
                translated = profile_translations.get(profile, profile)
                self._profileCombo.addItem(translated, userData=profile)
            
            translated_current = profile_translations.get(current_original, current_original)
            self._profileCombo.setCurrentText(translated_current)
            self._profileCombo.blockSignals(False)
        
        # Profile management ComboBox
        if hasattr(self, '_profileManagerCombo'):
            current = self._profileManagerCombo.currentText()
            current_original = reverse_translations.get(current, current)
            
            self._profileManagerCombo.blockSignals(True)
            self._profileManagerCombo.clear()
            self._profileManagerCombo.addItem(self.translator.get_text('please_select'))
            for profile in self._fanControl.profile_manager.profiles.keys():
                translated = profile_translations.get(profile, profile)
                self._profileManagerCombo.addItem(translated, userData=profile)
            
            if current != self.translator.get_text('please_select'):
                translated_current = profile_translations.get(current_original, current_original)
                self._profileManagerCombo.setCurrentText(translated_current)
            self._profileManagerCombo.blockSignals(False)

    def showNotification(self, title: str, message: str):
        """Show notification in system tray"""
        self._trayIcon.showMessage(
            title,
            message,
            self._app_icon,
            1000  # Show for 1 second
        ) 

    def _loadTraySettings(self) -> bool:
        """Load tray settings"""
        try:
            settings_path = os.path.join(
                os.getenv('APPDATA', os.path.expanduser('~')),
                'FanControl',
                'settings.json'
            )
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    return settings.get('minimize_to_tray', True)  # Default active
        except:
            pass
        return True

    def _toggleTrayMinimize(self, checked: bool) -> None:
        """Change system tray setting"""
        try:
            settings_path = os.path.join(
                os.getenv('APPDATA', os.path.expanduser('~')),
                'FanControl',
                'settings.json'
            )
            
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            
            settings['minimize_to_tray'] = checked
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
            
        except Exception as e:
            print(f"Failed to save tray settings: {e}") 

    def _onTrayIconActivated(self, reason):
        """Called when system tray icon is clicked"""
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.show() 

    def _onProfileChange(self, index: int) -> None:
        """Called when profile changes"""
        try:
            # Get profile name
            profile_name = self._profileCombo.itemData(index)  # Get original name from userData
            
            # Apply profile
            if self._fanControl.apply_profile(profile_name):
                # Save last profile
                self._hotkey_manager.set_last_profile(profile_name)
                
                # Update existing profile in FanControl
                self._fanControl.profile_manager.current_profile = profile_name
                
                # Update window title
                self._updateWindowTitle()
                
                if not self._suppressNotification:
                    # Get translated profile name
                    translated_name = self._profileCombo.itemText(index)
                    # Show notification only once
                    self.showNotification(
                        self.translator.get_text('success'),
                        self.translator.get_text('profile_applied', translated_name)
                    )
            else:
                QtWidgets.QMessageBox.critical(
                    self,
                    self.translator.get_text('error'),
                    self.translator.get_text('failed_apply')
                )
        except Exception as e:
            print(f"Profile change error: {e}") 

    def _checkForUpdates(self):
        """Güncellemeleri kontrol et"""
        try:
            self.check_update_btn.setEnabled(False)
            self.update_status_label.setText(self.translator.get_text('checking_updates'))
            
            # GitHub API'den son sürümü kontrol et
            response = requests.get('https://api.github.com/repos/mre31/fan-control-center/releases/latest')
            if response.status_code == 200:
                latest_version = version.parse(response.json()['tag_name'].lstrip('v'))
                current_version = version.parse('1.1.0')  # Mevcut sürüm
                
                if latest_version > current_version:
                    self.update_status_label.setText(
                        self.translator.get_text('update_available', str(latest_version))
                    )
                    # Güncelleme linkini aç
                    download_url = response.json()['html_url']
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl(download_url))
                else:
                    self.update_status_label.setText(self.translator.get_text('no_updates'))
            else:
                self.update_status_label.setText(self.translator.get_text('update_check_failed'))
                
        except Exception as e:
            print(f"Update check failed: {e}")
            self.update_status_label.setText(self.translator.get_text('update_check_failed'))
        finally:
            self.check_update_btn.setEnabled(True) 
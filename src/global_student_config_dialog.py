"""
Global student configuration dialog for the Sheets2Anki addon.

This module implements an interface for globally configuring which students
should be synchronized across all remote decks.
"""

from .compat import CustomContextMenu
from .compat import DialogAccepted
from .compat import Horizontal
from .compat import MessageBox_Yes
from .compat import Palette_Window
from .compat import QAction
from .compat import QCheckBox
from .compat import QDialog
from .compat import QFrame
from .compat import QGroupBox
from .compat import QHBoxLayout
from .compat import QInputDialog
from .compat import QLabel
from .compat import QListWidget
from .compat import QMenu
from .compat import QPushButton
from .styled_messages import StyledMessageBox
from .compat import QSplitter
from .compat import QVBoxLayout
from .compat import QWidget
from .compat import safe_exec_dialog
from .compat import safe_exec_menu
from .templates_and_definitions import DEFAULT_STUDENT
from .config_manager import get_global_student_config
from .config_manager import save_global_student_config
from .config_manager import update_available_students_from_discovery


class GlobalStudentConfigDialog(QDialog):
    """
    Dialog for global student configuration.

    Allows the user to:
    - Select which students to synchronize
    - Add/remove students manually
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Student Configuration - Sheets2Anki")
        self.setMinimumSize(650, 550)
        self.resize(750, 600)

        # List of available students (loaded from configuration)
        self.available_students = set()

        # Detect dark mode
        palette = self.palette()
        bg_color = palette.color(Palette_Window)
        self.is_dark_mode = bg_color.lightness() < 128

        self._setup_colors()
        self._setup_ui()
        self._apply_styles()
        self._load_current_config()

    def _setup_colors(self):
        """Sets up color scheme based on theme."""
        if self.is_dark_mode:
            self.colors = {
                'bg': '#1e1e1e',
                'card_bg': '#2d2d2d',
                'text': '#ffffff',
                'text_secondary': '#b0b0b0',
                'border': '#404040',
                'accent_primary': '#2196F3',
                'accent_success': '#4CAF50',
                'accent_danger': '#e53935',
                'accent_warning': '#FF9800',
                'button_bg': '#3d3d3d',
                'button_hover': '#4a4a4a',
                'list_bg': '#252525',
            }
        else:
            self.colors = {
                'bg': '#f5f5f5',
                'card_bg': '#ffffff',
                'text': '#1a1a1a',
                'text_secondary': '#666666',
                'border': '#d0d0d0',
                'accent_primary': '#1976D2',
                'accent_success': '#4CAF50',
                'accent_danger': '#d32f2f',
                'accent_warning': '#FF9800',
                'button_bg': '#e0e0e0',
                'button_hover': '#d0d0d0',
                'list_bg': '#fafafa',
            }

    def _apply_styles(self):
        """Applies styles to the dialog."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.colors['bg']};
                color: {self.colors['text']};
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: 12pt;
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding: 12px;
                padding-top: 28px;
                background-color: {self.colors['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                top: 4px;
                padding: 2px 10px;
                background-color: {self.colors['card_bg']};
                border-radius: 4px;
                color: {self.colors['text_secondary']};
                font-size: 12pt;
            }}
            QListWidget {{
                background-color: {self.colors['list_bg']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 5px;
                font-size: 12pt;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['accent_primary']};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {self.colors['button_hover']};
            }}

        """)

    def _setup_ui(self):
        """Sets up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet(f"""
            QFrame#headerFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['accent_primary']}, 
                    stop:1 {self.colors['accent_success']});
                border-radius: 12px;
                padding: 5px;
            }}
            QFrame#headerFrame QLabel {{
                background: transparent;
                color: white;
                border: none;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        title_label = QLabel("👥 Global Student Configuration")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        desc_label = QLabel(
            "Select which students should be synchronized across all remote decks. "
            "Notes will be created for each selected student."
        )
        desc_label.setStyleSheet("font-size: 12pt; opacity: 0.9;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)

        layout.addWidget(header_frame)

        # Options section
        options_group = QGroupBox("Sync Options")
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)

        # Auto-remove checkbox
        self.auto_remove_checkbox = QCheckBox(
            "⚠️ Automatically remove data from students removed from synchronization"
        )
        self.auto_remove_checkbox.setToolTip(
            "CAUTION: If enabled, when a student is removed from the sync list,\n"
            "all their data (notes, cards, note types and decks) will be PERMANENTLY deleted\n"
            "on the next synchronization. This action is irreversible!"
        )
        self.auto_remove_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {self.colors['accent_danger']};
                font-weight: bold;
                padding: 10px;
                background-color: rgba(229, 57, 53, 0.1);
                border-radius: 6px;
            }}
        """)
        options_layout.addWidget(self.auto_remove_checkbox)

        # Sync missing checkbox
        self.sync_missing_checkbox = QCheckBox(
            f"📋 Synchronize notes without specific students to {DEFAULT_STUDENT} deck"
        )
        self.sync_missing_checkbox.setToolTip(
            "If enabled, notes that don't have defined students (empty STUDENTS column)\n"
            f"will be synchronized to a subdeck called {DEFAULT_STUDENT} inside the remote deck.\n"
            "If disabled, these notes will stop being synchronized and will be removed."
        )
        self.sync_missing_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {self.colors['accent_primary']};
                font-weight: bold;
                padding: 10px;
                background-color: rgba(33, 150, 243, 0.1);
                border-radius: 6px;
            }}
        """)
        options_layout.addWidget(self.sync_missing_checkbox)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Students section with splitter
        students_frame = QFrame()
        students_frame.setObjectName("studentsFrame")
        students_frame.setStyleSheet(f"""
            QFrame#studentsFrame {{
                background-color: {self.colors['card_bg']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        students_layout = QVBoxLayout(students_frame)

        splitter = QSplitter(Horizontal)

        # Left panel - Available students
        left_panel = self._create_available_students_panel()
        splitter.addWidget(left_panel)

        # Right panel - Selected students
        right_panel = self._create_selected_students_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 300])
        students_layout.addWidget(splitter)

        layout.addWidget(students_frame, 1)  # Give stretch factor

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        btn_style = f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_hover']};
                border-color: {self.colors['accent_primary']};
            }}
        """

        auto_discover_btn = QPushButton("🔍 Auto-Discover Students")
        auto_discover_btn.setStyleSheet(btn_style)
        auto_discover_btn.setToolTip("Discover students from all configured remote decks")
        auto_discover_btn.clicked.connect(self._auto_discover_students)
        action_layout.addWidget(auto_discover_btn)

        add_manual_btn = QPushButton("➕ Add Student...")
        add_manual_btn.setStyleSheet(btn_style)
        add_manual_btn.setToolTip("Add a student not listed automatically")
        add_manual_btn.clicked.connect(self._add_manual_student)
        action_layout.addWidget(add_manual_btn)

        action_layout.addStretch()

        # OK/Cancel buttons
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_hover']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        action_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("✓ Save")
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_success']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        ok_btn.clicked.connect(self.accept)
        action_layout.addWidget(ok_btn)

        layout.addLayout(action_layout)
        self.setLayout(layout)

    def _create_available_students_panel(self):
        """Creates the available students panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)

        title = QLabel("📄 Available Students")
        title.setStyleSheet(f"font-weight: bold; font-size: 12pt; color: {self.colors['text']};")
        layout.addWidget(title)

        self.available_list = QListWidget()
        self.available_list.setToolTip(
            "Double-click to add to selected list\n"
            "Right-click for edit/delete options"
        )
        self.available_list.itemDoubleClicked.connect(self._move_to_selected)
        self.available_list.setContextMenuPolicy(CustomContextMenu)
        self.available_list.customContextMenuRequested.connect(
            self._show_available_context_menu
        )
        layout.addWidget(self.available_list, 1)

        add_btn = QPushButton("Add Selected →")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_success']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        add_btn.clicked.connect(self._move_to_selected)
        layout.addWidget(add_btn)

        panel.setLayout(layout)
        return panel

    def _create_selected_students_panel(self):
        """Creates the selected students panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)

        title = QLabel("✅ Selected for Sync")
        title.setStyleSheet(f"font-weight: bold; font-size: 12pt; color: {self.colors['accent_success']};")
        layout.addWidget(title)

        self.selected_list = QListWidget()
        self.selected_list.setToolTip(
            "Double-click to remove from selection\n"
            "Right-click for edit/delete options"
        )
        self.selected_list.itemDoubleClicked.connect(self._move_to_available)
        self.selected_list.setContextMenuPolicy(CustomContextMenu)
        self.selected_list.customContextMenuRequested.connect(
            self._show_selected_context_menu
        )
        layout.addWidget(self.selected_list, 1)

        remove_btn = QPushButton("← Remove Selected")
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_danger']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: #c62828;
            }}
        """)
        remove_btn.clicked.connect(self._move_to_available)
        layout.addWidget(remove_btn)

        panel.setLayout(layout)
        return panel

    def _auto_discover_students(self):
        """Automatically discovers students from all remote decks."""
        try:
            discovered_students, new_count = update_available_students_from_discovery()
            self._load_current_config()

            if new_count > 0:
                message = f"Search completed!\nFound {new_count} new students.\nTotal available students: {len(discovered_students)}"
            else:
                message = f"Search completed!\nNo new students found.\nTotal available students: {len(discovered_students)}"

            StyledMessageBox.information(
                self, 
                "Automatic Search", 
                "Search completed!", 
                detailed_text=message.replace("Search completed!\n", "")
            )

        except Exception as e:
            StyledMessageBox.warning(
                self, "Search Error", f"Error discovering students: {str(e)}"
            )

    def _load_current_config(self):
        """Loads current configuration."""
        self.available_list.clear()
        self.selected_list.clear()

        config = get_global_student_config()

        available_students = set(config.get("available_students", []))
        enabled_students = set(config.get("enabled_students", []))

        auto_remove = config.get("auto_remove_disabled_students", False)
        self.auto_remove_checkbox.setChecked(auto_remove)

        sync_missing = config.get("sync_missing_students_notes", False)
        self.sync_missing_checkbox.setChecked(sync_missing)

        self.available_students = available_students.copy()

        for student in sorted(available_students - enabled_students):
            self.available_list.addItem(student)

        for student in sorted(enabled_students):
            self.selected_list.addItem(student)

    def _move_to_selected(self):
        """Moves student from available to selected list."""
        current_item = self.available_list.currentItem()
        if current_item:
            student_name = current_item.text()
            row = self.available_list.row(current_item)
            self.available_list.takeItem(row)
            self._add_to_selected_sorted(student_name)

    def _move_to_available(self):
        """Moves student from selected to available list."""
        current_item = self.selected_list.currentItem()
        if current_item:
            student_name = current_item.text()
            row = self.selected_list.row(current_item)
            self.selected_list.takeItem(row)
            self._add_to_available_sorted(student_name)

    def _add_to_selected_sorted(self, student_name):
        """Adds student to selected list maintaining alphabetical order."""
        insert_pos = 0
        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            if item and item.text() > student_name:
                insert_pos = i
                break
            insert_pos = i + 1
        self.selected_list.insertItem(insert_pos, student_name)

    def _add_to_available_sorted(self, student_name):
        """Adds student to available list maintaining alphabetical order."""
        insert_pos = 0
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if item and item.text() > student_name:
                insert_pos = i
                break
            insert_pos = i + 1
        self.available_list.insertItem(insert_pos, student_name)

    def _add_manual_student(self):
        """Allows adding a student manually."""
        student_name, ok = QInputDialog.getText(
            self, "Add Student", "Student name:"
        )

        if ok and student_name.strip():
            clean_name = student_name.strip()

            if self._student_name_exists(clean_name):
                StyledMessageBox.warning(
                    self, "Student Exists", f"Student '{clean_name}' is already in the list."
                )
                return

            self.available_students.add(clean_name)
            self._add_to_available_sorted(clean_name)

    def _show_available_context_menu(self, position):
        """Shows context menu for available students list."""
        item = self.available_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        add_action = QAction("Add to Selected", self)
        add_action.triggered.connect(self._move_to_selected)
        menu.addAction(add_action)

        menu.addSeparator()

        delete_action = QAction("Delete Student", self)
        delete_action.triggered.connect(
            lambda: self._delete_student(self.available_list)
        )
        menu.addAction(delete_action)

        safe_exec_menu(menu, self.available_list.mapToGlobal(position))

    def _show_selected_context_menu(self, position):
        """Shows context menu for selected students list."""
        item = self.selected_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        remove_action = QAction("Remove from Selected", self)
        remove_action.triggered.connect(self._move_to_available)
        menu.addAction(remove_action)

        menu.addSeparator()

        delete_action = QAction("Delete Student", self)
        delete_action.triggered.connect(
            lambda: self._delete_student(self.selected_list)
        )
        menu.addAction(delete_action)

        safe_exec_menu(menu, self.selected_list.mapToGlobal(position))

    def _delete_student(self, list_widget):
        """Allows deleting a student from the list."""
        current_item = list_widget.currentItem()
        if not current_item:
            return

        student_name = current_item.text()

        if StyledMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete student '{student_name}'?",
            yes_text="Delete",
            no_text="Cancel",
            destructive=True
        ):
            self.available_students.discard(student_name)
            row = list_widget.row(current_item)
            list_widget.takeItem(row)

    def _student_name_exists(self, name):
        """Checks if a student name already exists in any list."""
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if item and item.text() == name:
                return True

        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            if item and item.text() == name:
                return True

        return False

    def get_selected_config(self):
        """Gets the configuration selected by the user."""
        selected_students = []
        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            if item:
                selected_students.append(item.text())

        filter_enabled = True
        return selected_students, filter_enabled

    def accept(self):
        """Saves configuration and closes dialog."""
        selected_students, filter_enabled = self.get_selected_config()

        available_students = []
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if item:
                available_students.append(item.text())

        available_students.extend(selected_students)

        auto_remove_enabled = self.auto_remove_checkbox.isChecked()
        sync_missing_enabled = self.sync_missing_checkbox.isChecked()

        save_global_student_config(
            selected_students,
            available_students,
            auto_remove_enabled,
            sync_missing_enabled,
        )

        super().accept()


def show_global_student_config_dialog(parent=None):
    """
    Shows the global student configuration dialog.

    Args:
        parent: Parent widget (optional)

    Returns:
        bool: True if user confirmed, False if cancelled
    """
    dialog = GlobalStudentConfigDialog(parent)
    return safe_exec_dialog(dialog) == DialogAccepted

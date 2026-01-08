"""
Centralized module for generating data removal confirmation messages.

This module provides a single and consistent interface for generating
confirmation messages when student data needs to be removed.
"""

from typing import List, Optional
from .compat import MessageBox_No, MessageBox_Yes, MessageBox_Cancel, safe_exec_dialog
from .styled_messages import StyledMessageBox
from .templates_and_definitions import DEFAULT_STUDENT


def generate_data_removal_confirmation_message(students_to_remove: List[str]) -> str:
    """
    Generates the standard confirmation message for student data removal.
    
    This function centralizes message generation to ensure consistency
    throughout the system.
    
    Args:
        students_to_remove: List of student/feature names to be removed
        
    Returns:
        str: Formatted message for display
    """
    if not students_to_remove:
        return ""
    
    # Remove duplicates and sort
    unique_students = sorted(list(set(students_to_remove)))
    students_list = "\n".join([f"• {student}" for student in unique_students])
    
    message = (
        f"⚠️ WARNING: PERMANENT DATA REMOVAL ⚠️\n\n"
        f"The following students have been removed from the sync list:\n\n"
        f"{students_list}\n\n"
        f"🗑️ DATA THAT WILL BE PERMANENTLY DELETED:\n"
        f"• All student notes\n"
        f"• All student cards\n"
        f"• All student decks\n"
        f"• All student note types\n\n"
        f"❌ THIS ACTION IS IRREVERSIBLE!\n\n"
        f"Do you want to continue with the data removal?"
    )
    
    return message


def show_data_removal_confirmation_dialog(
    students_to_remove: List[str], 
    window_title: str = "Confirm Permanent Data Removal",
    parent=None
) -> bool:
    """
    Shows the confirmation dialog for student data removal.
    
    This function centralizes all dialog display logic to ensure
    consistent behavior throughout the system.
    
    Args:
        students_to_remove: List of student/feature names to be removed
        window_title: Window title (optional)
        parent: Parent widget (optional)
        
    Returns:
        int: Dialog result code (MessageBox_Yes, MessageBox_No, MessageBox_Cancel)
    """
    if not students_to_remove:
        return False
    
    # Generate message using centralized function
    message = generate_data_removal_confirmation_message(students_to_remove)
    
    # Create custom buttons
    buttons = [
        {
            "text": "🗑️ YES, DELETE DATA",
            "role": "custom",
            "result_code": MessageBox_Yes,
            "primary": True,
            "destructive": True
        },
        {
            "text": "🛡️ NO, KEEP DATA",
            "role": "custom",
            "result_code": MessageBox_No,
            "primary": True
        },
        {
            "text": "🚫 CANCEL SYNC",
            "role": "custom",
            "result_code": MessageBox_Cancel,
            "primary": False
        }
    ]
    
    # Create and show dialog
    dlg = StyledMessageBox(
        parent,
        window_title,
        message,
        message_type=StyledMessageBox.WARNING,
        buttons=buttons
    )
    
    # Execute dialog and return result
    return dlg.exec()


def collect_students_for_removal(
    disabled_students: List[str], 
    missing_functionality_disabled: bool = False
) -> List[str]:
    """
    Collects and organizes the list of students/features for removal.
    
    This function centralizes collection logic to ensure no
    duplications or inconsistencies.
    
    Args:
        disabled_students: List of disabled students
        missing_functionality_disabled: If True, adds DEFAULT_STUDENT to the list
        
    Returns:
        List[str]: Unique and sorted list of students/features for removal
    """
    all_students_to_remove = list(disabled_students) if disabled_students else []
    
    # Add DEFAULT_STUDENT if functionality was disabled
    if missing_functionality_disabled:
        if DEFAULT_STUDENT not in all_students_to_remove:
            all_students_to_remove.append(DEFAULT_STUDENT)
    
    # Remove duplicates and return sorted list
    return sorted(list(set(all_students_to_remove)))


# Convenience function for most common case
def confirm_students_removal(
    disabled_students: List[str], 
    missing_functionality_disabled: bool = False,
    window_title: str = "Confirm Permanent Data Removal",
    parent=None
) -> int:
    """
    Convenience function that combines collection and confirmation.
    
    Args:
        disabled_students: List of disabled students
        missing_functionality_disabled: If True, includes DEFAULT_STUDENT in removal
        window_title: Window title (optional)
        parent: Parent widget (optional)
        
    Returns:
        int: Dialog result code (MessageBox_Yes, MessageBox_No, MessageBox_Cancel)
    """
    students_to_remove = collect_students_for_removal(
        disabled_students, missing_functionality_disabled
    )
    
    if not students_to_remove:
        return MessageBox_No
    
    return show_data_removal_confirmation_dialog(
        students_to_remove, window_title, parent
    )

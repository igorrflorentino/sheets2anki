#!/usr/bin/env python3
"""
Simplified Backup System for Sheets2Anki

This module provides the following functionalities:
1. Generate Backup: Creates a full backup (.apkg + configurations)
2. Recover Backup: Restores everything to the original state
3. Safety Backup: Automatically creates a backup before restore operations
4. List Available Backups: Returns list of available backup files
"""

import glob
import json
import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from aqt import mw
from .styled_messages import StyledMessageBox

try:
    from .compat import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, WINDOW_MODAL
    from .config_manager import get_meta, save_meta, get_remote_decks, save_remote_decks, get_auto_backup_config, get_auto_backup_directory
    from .utils import add_debug_message
except ImportError:
    # For standalone testing
    from compat import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, WINDOW_MODAL
    from config_manager import get_meta, save_meta, get_remote_decks, save_remote_decks, get_auto_backup_config, get_auto_backup_directory
    def add_debug_message(message, category="DEBUG"):
        print(f"[{category}] {message}")


@dataclass
class BackupInfo:
    """Information about a backup file"""
    filename: str
    path: str
    size: int
    created_at: datetime
    backup_type: str  # 'full', 'config_only', or 'safety'
    version: str
    apkg_included: bool
    
    @property
    def size_human(self) -> str:
        """Returns human-readable file size"""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary"""
        return {
            "filename": self.filename,
            "path": self.path,
            "size": self.size,
            "size_human": self.size_human,
            "created_at": self.created_at.isoformat(),
            "backup_type": self.backup_type,
            "version": self.version,
            "apkg_included": self.apkg_included
        }


class SimplifiedBackupManager:
    """Simplified backup manager - Generate Full Backup, Recover Full Backup and Recover Settings"""

    def __init__(self):
        self.backup_version = "2.0"
        self.sheets2anki_deck_name = "Sheets2Anki"
        self._safety_backup_prefix = "sheets2anki_safety_"
        self._auto_backup_prefix = "sheets2anki_auto_config_"
        self._manual_backup_prefix = "sheets2anki_backup_"

    def create_backup(self, backup_path: str) -> bool:
        """Creates a full backup of the Sheets2Anki system"""
        try:
            if not mw or not mw.col:
                StyledMessageBox.critical(mw, "Error", "Anki is not available for backup.")
                return False

            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Export main deck as .apkg
                apkg_success = self._export_main_deck_apkg(temp_path)
                if not apkg_success:
                    StyledMessageBox.warning(mw, "Warning", "Deck 'Sheets2Anki' not found. Creating a backup of settings only.")
                
                # 2. Save all settings
                self._save_configurations(temp_path)
                
                # 3. Save backup information
                self._save_backup_info(temp_path, apkg_success, config_only=False)
                
                # 4. Create final ZIP file
                self._create_backup_zip(temp_path, backup_path)
                
            return True
            
        except Exception as e:
            StyledMessageBox.critical(mw, "Error", f"Error creating backup: {str(e)}")
            return False

    def create_config_backup(self, backup_path: str) -> bool:
        """Creates a backup of addon settings only"""
        try:
            if not mw or not mw.col:
                StyledMessageBox.critical(mw, "Error", "Anki is not available for backup.")
                return False

            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Save only settings
                self._save_configurations(temp_path)
                
                # 2. Save backup information (no deck)
                self._save_backup_info(temp_path, apkg_included=False, config_only=True)
                
                # 3. Create final ZIP file
                self._create_backup_zip(temp_path, backup_path)
                
            return True
            
        except Exception as e:
            StyledMessageBox.critical(mw, "Error", f"Error creating configuration backup: {str(e)}")
            return False

    def create_safety_backup(self) -> Optional[str]:
        """
        Creates a safety backup of the current state before restore operations.
        
        This is automatically called before any restore operation to prevent
        data loss in case the restoration is not what was desired.
        
        Returns:
            str: Path to the safety backup file, or None if failed
        """
        try:
            add_debug_message("Creating safety backup before restore operation...", "SAFETY_BACKUP")
            
            # Get backup directory
            backup_dir = get_auto_backup_directory()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{self._safety_backup_prefix}{timestamp}.zip"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Create full backup (includes deck if exists)
            success = self.create_backup(backup_path)
            
            if success:
                add_debug_message(f"✅ Safety backup created: {backup_path}", "SAFETY_BACKUP")
                return backup_path
            else:
                add_debug_message("❌ Failed to create safety backup", "SAFETY_BACKUP")
                return None
                
        except Exception as e:
            add_debug_message(f"❌ Error creating safety backup: {e}", "SAFETY_BACKUP")
            return None

    def restore_backup(self, backup_path: str, create_safety: bool = True) -> bool:
        """Restores a full backup of the Sheets2Anki system
        
        Args:
            backup_path: Path to the backup file to restore
            create_safety: If True, creates a safety backup before restoring (default: True)
        """
        try:
            if not os.path.exists(backup_path):
                showCritical("Backup file not found.")
                return False

            if not mw or not mw.col:
                showCritical("Anki is not available for restoration.")
                return False

            # Confirm operation
            if not StyledMessageBox.question(
                mw,
                "Confirm Restoration",
                "Are you sure you want to restore this backup?",
                detailed_text=(
                    "This operation will:\n"
                    "• Create a safety backup of your current state\n"
                    "• Remove the current 'Sheets2Anki' deck and all its subdecks\n"
                    "• Restore settings from the backup\n"
                    "• Import the deck from the backup\n"
                    "• Recreate all links between remote and local decks"
                ),
                yes_text="Restore",
                no_text="Cancel",
                destructive=True
            ):
                return False

            # Create safety backup before restoring
            safety_backup_path = None
            if create_safety:
                safety_backup_path = self.create_safety_backup()
                if safety_backup_path:
                    add_debug_message(f"Safety backup created at: {safety_backup_path}", "BACKUP")
                else:
                    # Ask user if they want to continue without safety backup
                    if not StyledMessageBox.question(
                        mw,
                        "Safety Backup Failed",
                        "Could not create safety backup.",
                        detailed_text="Do you want to continue anyway?\n(This is not recommended as you may lose current data)",
                        yes_text="Continue Anyway",
                        no_text="Cancel",
                        destructive=True
                    ):
                        return False

            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Extract backup
                self._extract_backup_zip(backup_path, temp_path)
                
                # 2. Validate backup
                if not self._validate_backup(temp_path):
                    StyledMessageBox.critical(mw, "Error", "Invalid or corrupted backup file.")
                    return False
                
                # 3. Remove current deck
                self._remove_current_sheets2anki_deck()
                
                # 4. Restore settings
                self._restore_configurations(temp_path)
                
                # 5. Import deck from backup
                apkg_path = temp_path / "sheets2anki_deck.apkg"
                if apkg_path.exists():
                    self._import_deck_apkg(str(apkg_path))
                
                # 6. Recreate links
                self._recreate_deck_links()
            
            # Show success message with safety backup info
            success_msg = "Backup restored successfully!\n\n"
            if safety_backup_path:
                success_msg += f"📦 Safety backup saved at:\n{safety_backup_path}\n\n"
            success_msg += "Restart Anki to ensure all settings are applied."
            StyledMessageBox.success(mw, "Restore Complete", success_msg)
            return True
            
        except Exception as e:
            StyledMessageBox.critical(mw, "Error", f"Error restoring backup: {str(e)}")
            return False

    def restore_config_only(self, backup_path: str, create_safety: bool = True) -> bool:
        """Restores settings only from the backup, without affecting Anki data
        
        Args:
            backup_path: Path to the backup file to restore
            create_safety: If True, creates a safety backup before restoring (default: True)
        """
        try:
            if not os.path.exists(backup_path):
                StyledMessageBox.critical(mw, "Error", "Backup file not found.")
                return False

            if not mw or not mw.col:
                StyledMessageBox.critical(mw, "Error", "Anki is not available for restoration.")
                return False

            # Confirm operation
            if not StyledMessageBox.question(
                mw,
                "Confirm Configuration Recovery",
                "Are you sure you want to restore the configuration?",
                detailed_text=(
                    "This operation will:\n"
                    "• Create a safety backup of your current settings\n"
                    "• Restore all addon settings\n"
                    "• Restore remote deck information\n"
                    "• Recreate links between remote and local decks\n"
                    "• NOT change any Anki data (notes, cards, etc.)"
                ),
                yes_text="Restore",
                no_text="Cancel",
                destructive=True
            ):
                return False

            # Create safety backup before restoring (config only)
            safety_backup_path = None
            if create_safety:
                safety_backup_path = self._create_config_safety_backup()
                if safety_backup_path:
                    add_debug_message(f"Safety config backup created at: {safety_backup_path}", "BACKUP")
                else:
                    # Ask user if they want to continue without safety backup
                    if not StyledMessageBox.question(
                        mw,
                        "Safety Backup Failed",
                        "Could not create safety backup of current settings.",
                        detailed_text="Do you want to continue anyway?",
                        yes_text="Continue Anyway",
                        no_text="Cancel",
                        destructive=True
                    ):
                        return False

            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Extract backup
                self._extract_backup_zip(backup_path, temp_path)
                
                # 2. Validate backup
                backup_info = self._get_backup_info(temp_path)
                if not backup_info:
                    StyledMessageBox.critical(mw, "Error", "Invalid or corrupted backup file.")
                    return False
                
                # 3. Check if it's a valid backup (full or config only)
                if backup_info.get("version") != self.backup_version:
                    StyledMessageBox.critical(mw, "Error", "Incompatible backup version.")
                    return False
                
                # 4. Restore settings only
                self._restore_configurations(temp_path)
                
                # 5. Recreate links between remote and local decks
                self._recreate_deck_links()
            
            # Show success message with safety backup info
            success_msg = "Settings restored successfully!\n\n"
            if safety_backup_path:
                success_msg += f"📦 Safety backup saved at:\n{safety_backup_path}\n\n"
            success_msg += (
                "• Addon settings have been restored\n"
                "• Remote decks have been relinked to local decks\n"
                "• No Anki data was modified\n\n"
                "Restart Anki to ensure all\n"
                "settings are applied correctly."
            )
            StyledMessageBox.success(mw, "Restore Complete", success_msg)
            return True
            
        except Exception as e:
            StyledMessageBox.critical(mw, "Error", f"Error restoring configurations: {str(e)}")
            return False

    def _create_config_safety_backup(self) -> Optional[str]:
        """
        Creates a safety backup of current settings only (lighter than full backup).
        
        Returns:
            str: Path to the safety backup file, or None if failed
        """
        try:
            add_debug_message("Creating config-only safety backup...", "SAFETY_BACKUP")
            
            # Get backup directory
            backup_dir = get_auto_backup_directory()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{self._safety_backup_prefix}config_{timestamp}.zip"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Create config-only backup
            success = self.create_config_backup(backup_path)
            
            if success:
                add_debug_message(f"✅ Config safety backup created: {backup_path}", "SAFETY_BACKUP")
                return backup_path
            else:
                return None
                
        except Exception as e:
            add_debug_message(f"❌ Error creating config safety backup: {e}", "SAFETY_BACKUP")
            return None

    def _export_main_deck_apkg(self, temp_path: Path) -> bool:
        """Exports the main Sheets2Anki deck as .apkg"""
        try:
            if not mw or not mw.col:
                return False
                
            # Find main Sheets2Anki deck
            deck_id = None
            all_decks = mw.col.decks.all()
            for deck_dict in all_decks:
                if deck_dict['name'] == self.sheets2anki_deck_name:
                    deck_id = deck_dict['id']
                    break
            
            if deck_id is None:
                add_debug_message("Main deck 'Sheets2Anki' not found for backup", "BACKUP")
                return False
            
            # Export using Anki API
            from anki.exporting import AnkiPackageExporter
            apkg_path = temp_path / "sheets2anki_deck.apkg"
            
            # Configure exporter with null check
            col = mw.col
            if col is None:
                return False
                
            exporter = AnkiPackageExporter(col)
            exporter.did = deck_id
            exporter.includeSched = True  # Include scheduling information
            exporter.includeMedia = True  # Include media
            
            # Export
            exporter.exportInto(str(apkg_path))
            
            add_debug_message(f"Deck '{self.sheets2anki_deck_name}' exported successfully", "BACKUP")
            return True
            
        except Exception as e:
            add_debug_message(f"Error exporting main deck: {e}", "BACKUP")
            return False

    def _save_configurations(self, temp_path: Path) -> None:
        """Saves all addon settings"""
        config_dir = temp_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Save meta.json
        meta = get_meta()
        with open(config_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        
        # Save config.json if it exists
        addon_path = Path(__file__).parent.parent
        config_path = addon_path / "config.json"
        if config_path.exists():
            shutil.copy2(config_path, config_dir / "config.json")

    def _save_backup_info(self, temp_path: Path, apkg_included: bool, config_only: bool = False) -> None:
        """Saves information about the backup"""
        backup_info = {
            "version": self.backup_version,
            "created_at": datetime.now().isoformat(),
            "anki_version": getattr(mw, "version", "unknown") if mw else "unknown",
            "addon_version": "2.0",
            "apkg_included": apkg_included,
            "config_only": config_only,
            "deck_name": self.sheets2anki_deck_name,
            "contents": ["configurations"] if config_only else (["configurations", "deck_apkg"] if apkg_included else ["configurations"])
        }
        
        with open(temp_path / "backup_info.json", "w", encoding="utf-8") as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)

    def _create_backup_zip(self, temp_path: Path, backup_path: str) -> None:
        """Creates the backup ZIP file"""
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_path)
                    zipf.write(file_path, arcname)

    def _extract_backup_zip(self, backup_path: str, temp_path: Path) -> None:
        """Extracts the backup ZIP file"""
        with zipfile.ZipFile(backup_path, "r") as zipf:
            zipf.extractall(temp_path)

    def _validate_backup(self, temp_path: Path) -> bool:
        """Validates if the backup is valid"""
        backup_info = self._get_backup_info(temp_path)
        return backup_info is not None and backup_info.get("version") == self.backup_version

    def _get_backup_info(self, temp_path: Path) -> Optional[Dict[str, Any]]:
        """Gets backup information"""
        backup_info_path = temp_path / "backup_info.json"
        if not backup_info_path.exists():
            return None
        
        try:
            with open(backup_info_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None

    def _remove_current_sheets2anki_deck(self) -> None:
        """Removes the current Sheets2Anki deck and all subdecks"""
        try:
            if not mw or not mw.col:
                return
                
            # Find and remove main deck
            deck_id = None
            all_decks = mw.col.decks.all()
            for deck_dict in all_decks:
                if deck_dict['name'] == self.sheets2anki_deck_name:
                    deck_id = deck_dict['id']
                    break
            
            if deck_id is not None:
                # Remove deck and all subdecks
                col = mw.col
                if col is not None:
                    col.decks.rem(deck_id, cardsToo=True)
                    add_debug_message(f"Deck '{self.sheets2anki_deck_name}' removed for restoration", "BACKUP")
            
        except Exception as e:
            add_debug_message(f"Error removing current deck: {e}", "BACKUP")

    def _restore_configurations(self, temp_path: Path) -> None:
        """Restores all addon settings from backup"""
        config_dir = temp_path / "config"
        
        # Restore meta.json
        meta_path = config_dir / "meta.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            save_meta(meta)
        
        # Restore config.json if it exists
        backup_config_path = config_dir / "config.json"
        if backup_config_path.exists():
            addon_path = Path(__file__).parent.parent
            target_config_path = addon_path / "config.json"
            shutil.copy2(backup_config_path, target_config_path)

    def _import_deck_apkg(self, apkg_path: str) -> None:
        """Imports the deck from the .apkg file using modern Anki API"""
        try:
            if not mw or not mw.col:
                raise Exception("Anki is not available")
            
            # Method 1: Try using AnkiPackageImporter (modern API)
            try:
                from anki.importing.apkg import AnkiPackageImporter
                
                importer = AnkiPackageImporter(mw.col, apkg_path)
                importer.run()
                mw.col.save()
                
                add_debug_message("Deck imported successfully (modern API)", "BACKUP")
                StyledMessageBox.success(mw, "Import Successful", "Deck imported successfully from backup!")
                return
                
            except Exception as e:
                add_debug_message(f"Modern method failed: {e}", "BACKUP")
            
            # Method 2: Try using UI import (more compatible)
            try:
                from aqt.importing import importFile
                
                # Use UI import function
                importFile(mw, apkg_path)
                
                add_debug_message("Deck imported successfully (UI method)", "BACKUP")
                StyledMessageBox.success(mw, "Import Successful", "Deck imported successfully from backup!")
                return
                
            except Exception as e:
                add_debug_message(f"UI method failed: {e}", "BACKUP")
            
            # Method 3: Fallback for older versions
            try:
                from aqt.importing import doImport
                doImport(mw, apkg_path)
                
                add_debug_message("Deck imported successfully (legacy method)", "BACKUP")
                StyledMessageBox.success(mw, "Import Successful", "Deck imported successfully from backup!")
                return
                
            except Exception as e:
                add_debug_message(f"Legacy method failed: {e}", "BACKUP")
            
            # If all methods failed
            raise Exception("All import methods failed")
            
        except Exception as e:
            add_debug_message(f"Error importing deck: {e}", "BACKUP")
            StyledMessageBox.critical(mw, "Import Error", f"Error importing deck from backup:\n{e}\n\nTry manually importing the .apkg file via Anki's File > Import menu.")

    def _import_deck_manual(self, apkg_path: str) -> None:
        """Manual import method as a last resort"""
        # This method was removed as it is too complex and risky
        # Instead, we guide the user to import manually
        StyledMessageBox.warning(
            mw,
            "Import Failed",
            "Automatic import failed.",
            detailed_text=(
                "To recover your data:\n"
                "1. Open Anki\n"
                "2. Go to File > Import\n"
                f"3. Select file: {apkg_path}\n"
                "4. Follow the on-screen instructions\n\n"
                "Your data is safe in the backup file!"
            )
        )

    def _recreate_deck_links(self) -> None:
        """Recreates links between remote and local decks"""
        try:
            if not mw or not mw.col:
                return
                
            remote_decks = get_remote_decks()
            
            # For each remote deck, find the corresponding local deck
            for deck_key, deck_info in remote_decks.items():
                local_deck_name = deck_info.get("local_deck_name", "")
                if local_deck_name:
                    # Find deck in Anki
                    all_decks = mw.col.decks.all()
                    for deck_dict in all_decks:
                        if deck_dict['name'] == local_deck_name:
                            # Update local deck ID
                            deck_info["local_deck_id"] = deck_dict['id']
                            add_debug_message(f"Deck '{local_deck_name}' relinked with ID {deck_dict['id']}", "BACKUP")
                            break
            
            # Save updated settings
            save_remote_decks(remote_decks)
            
        except Exception as e:
            add_debug_message(f"Error recreating deck links: {e}", "BACKUP")


    def create_auto_backup(self) -> bool:
        """
        Creates an automatic backup during synchronization.
        
        The backup type (simple or complete) is determined by user configuration.
        - Simple: Configuration files only (fast, small size)
        - Complete: Configuration + deck data with cards (slower, larger size)
        
        Returns:
            bool: True if backup was successfully created
        """
        try:
            # Check if automatic backup is enabled
            auto_config = get_auto_backup_config()
            if not auto_config.get("enabled", True):
                add_debug_message("Automatic backup disabled", "AUTO_BACKUP")
                return False
            
            # Get backup type setting
            backup_type = auto_config.get("type", "simple")
            
            # Get backup directory
            backup_dir = get_auto_backup_directory()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Use different filename prefixes based on backup type
            if backup_type == "complete":
                backup_filename = f"{self._auto_backup_prefix}full_{timestamp}.zip"
                add_debug_message("Creating COMPLETE automatic backup (config + deck)...", "AUTO_BACKUP")
                success = self.create_backup(os.path.join(backup_dir, backup_filename))
            else:
                backup_filename = f"{self._auto_backup_prefix}{timestamp}.zip"
                add_debug_message("Creating SIMPLE automatic backup (config only)...", "AUTO_BACKUP")
                success = self.create_config_backup(os.path.join(backup_dir, backup_filename))
            
            backup_path = os.path.join(backup_dir, backup_filename)
            
            if success:
                add_debug_message(f"✅ Automatic backup created: {backup_path}", "AUTO_BACKUP")
                
                # Perform file rotation (keep only the last N)
                self._rotate_auto_backup_files(backup_dir, auto_config.get("max_files", 50))
                
                return True
            else:
                add_debug_message("❌ Failed to create automatic backup", "AUTO_BACKUP")
                return False
                
        except Exception as e:
            add_debug_message(f"❌ Error creating automatic backup: {e}", "AUTO_BACKUP")
            return False

    # Keep old method name for backward compatibility
    def create_auto_config_backup(self) -> bool:
        """Deprecated: Use create_auto_backup() instead. Kept for backward compatibility."""
        return self.create_auto_backup()

    def _rotate_auto_backup_files(self, backup_dir: str, max_files: int) -> None:
        """
        Removes old backup files, keeping only the most recent ones.
        
        Args:
            backup_dir (str): Backup directory
            max_files (int): Maximum number of files to keep
        """
        try:
            import glob
            
            # Find all automatic backup files
            pattern = os.path.join(backup_dir, "sheets2anki_auto_config_*.zip")
            backup_files = glob.glob(pattern)
            
            # Sort by modification time (most recent first)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Remove excess files
            files_to_remove = backup_files[max_files:]
            
            for file_path in files_to_remove:
                try:
                    os.remove(file_path)
                    add_debug_message(f"🗑️ Removed old backup: {os.path.basename(file_path)}", "AUTO_BACKUP")
                except Exception as e:
                    add_debug_message(f"⚠️ Error removing {file_path}: {e}", "AUTO_BACKUP")
            
            if files_to_remove:
                add_debug_message(f"📁 Rotation completed: {len(files_to_remove)} file(s) removed, {len(backup_files) - len(files_to_remove)} kept", "AUTO_BACKUP")
            
        except Exception as e:
            add_debug_message(f"❌ Error in file rotation: {e}", "AUTO_BACKUP")

    def get_auto_backup_info(self) -> Dict[str, Any]:
        """
        Gets information about automatic backups.
        
        Returns:
            dict: Automatic backup information
        """
        try:
            auto_config = get_auto_backup_config()
            backup_dir = get_auto_backup_directory()
            
            # Count existing backup files
            import glob
            pattern = os.path.join(backup_dir, "sheets2anki_auto_config_*.zip")
            backup_files = glob.glob(pattern)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Latest backup info
            latest_backup = None
            if backup_files:
                latest_file = backup_files[0]
                latest_backup = {
                    "filename": os.path.basename(latest_file),
                    "path": latest_file,
                    "size": os.path.getsize(latest_file),
                    "created": datetime.fromtimestamp(os.path.getmtime(latest_file)).isoformat()
                }
            
            return {
                "enabled": auto_config.get("enabled", True),
                "directory": backup_dir,
                "max_files": auto_config.get("max_files", 50),
                "total_files": len(backup_files),
                "latest_backup": latest_backup,
                "all_backups": [
                    {
                        "filename": os.path.basename(f),
                        "path": f,
                        "size": os.path.getsize(f),
                        "created": datetime.fromtimestamp(os.path.getmtime(f)).isoformat()
                    }
                    for f in backup_files[:10]  # Show only the 10 most recent
                ]
            }
            
        except Exception as e:
            add_debug_message(f"❌ Error getting info: {e}", "AUTO_BACKUP")
            return {
                "enabled": False,
                "directory": "",
                "max_files": 50,
                "total_files": 0,
                "latest_backup": None,
                "all_backups": [],
                "error": str(e)
            }

    def list_available_backups(self, backup_dir: Optional[str] = None) -> List[BackupInfo]:
        """
        Lists all available backup files with their metadata.
        
        Args:
            backup_dir: Optional directory to search. If None, uses default backup directory.
            
        Returns:
            List[BackupInfo]: List of BackupInfo objects sorted by creation date (newest first)
        """
        backups: List[BackupInfo] = []
        
        try:
            # Use provided directory or default
            if backup_dir is None:
                backup_dir = get_auto_backup_directory()
            
            if not os.path.exists(backup_dir):
                add_debug_message(f"Backup directory does not exist: {backup_dir}", "BACKUP")
                return []
            
            # Find all backup files (*.zip)
            patterns = [
                os.path.join(backup_dir, f"{self._safety_backup_prefix}*.zip"),
                os.path.join(backup_dir, f"{self._auto_backup_prefix}*.zip"),
                os.path.join(backup_dir, f"{self._manual_backup_prefix}*.zip"),
                os.path.join(backup_dir, "sheets2anki_*.zip"),  # Catch-all for other formats
            ]
            
            found_files = set()
            for pattern in patterns:
                found_files.update(glob.glob(pattern))
            
            for backup_path in found_files:
                try:
                    backup_info = self._get_backup_info_from_file(backup_path)
                    if backup_info:
                        backups.append(backup_info)
                except Exception as e:
                    add_debug_message(f"Error reading backup {backup_path}: {e}", "BACKUP")
                    continue
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x.created_at, reverse=True)
            
            add_debug_message(f"Found {len(backups)} available backups", "BACKUP")
            return backups
            
        except Exception as e:
            add_debug_message(f"Error listing backups: {e}", "BACKUP")
            return []

    def _get_backup_info_from_file(self, backup_path: str) -> Optional[BackupInfo]:
        """
        Extracts BackupInfo from a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            BackupInfo object or None if file is invalid
        """
        try:
            if not os.path.exists(backup_path) or not backup_path.endswith('.zip'):
                return None
            
            filename = os.path.basename(backup_path)
            file_size = os.path.getsize(backup_path)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
            
            # Determine backup type from filename
            if self._safety_backup_prefix in filename:
                backup_type = "safety"
            elif self._auto_backup_prefix in filename:
                backup_type = "auto"
            else:
                backup_type = "manual"
            
            # Try to read backup_info.json from the zip
            version = "unknown"
            apkg_included = False
            config_only = True
            
            try:
                with zipfile.ZipFile(backup_path, 'r') as zf:
                    if 'backup_info.json' in zf.namelist():
                        with zf.open('backup_info.json') as f:
                            info_data = json.load(f)
                            version = info_data.get('version', 'unknown')
                            apkg_included = info_data.get('apkg_included', False)
                            config_only = info_data.get('config_only', True)
                            
                            # Update backup type based on content
                            if not config_only and apkg_included:
                                if backup_type == "manual":
                                    backup_type = "full"
                            elif config_only:
                                if backup_type == "manual":
                                    backup_type = "config_only"
            except Exception:
                # If we can't read the zip, use defaults
                pass
            
            return BackupInfo(
                filename=filename,
                path=backup_path,
                size=file_size,
                created_at=file_mtime,
                backup_type=backup_type,
                version=version,
                apkg_included=apkg_included
            )
            
        except Exception as e:
            add_debug_message(f"Error extracting backup info from {backup_path}: {e}", "BACKUP")
            return None

    def get_backup_summary(self, backup_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Gets a summary of all available backups.
        
        Args:
            backup_dir: Optional directory to search.
            
        Returns:
            Dict with backup statistics and lists
        """
        try:
            backups = self.list_available_backups(backup_dir)
            
            # Categorize backups
            safety_backups = [b for b in backups if b.backup_type == "safety"]
            auto_backups = [b for b in backups if b.backup_type == "auto"]
            manual_backups = [b for b in backups if b.backup_type in ("manual", "full", "config_only")]
            full_backups = [b for b in backups if b.apkg_included]
            
            # Calculate total size
            total_size = sum(b.size for b in backups)
            
            return {
                "total_count": len(backups),
                "total_size": total_size,
                "total_size_human": self._format_size(total_size),
                "safety_count": len(safety_backups),
                "auto_count": len(auto_backups),
                "manual_count": len(manual_backups),
                "full_count": len(full_backups),
                "latest_backup": backups[0].to_dict() if backups else None,
                "latest_safety": safety_backups[0].to_dict() if safety_backups else None,
                "latest_auto": auto_backups[0].to_dict() if auto_backups else None,
                "all_backups": [b.to_dict() for b in backups]
            }
            
        except Exception as e:
            add_debug_message(f"Error getting backup summary: {e}", "BACKUP")
            return {
                "total_count": 0,
                "total_size": 0,
                "total_size_human": "0 B",
                "error": str(e)
            }

    def _format_size(self, size: int) -> str:
        """Formats size in bytes to human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def cleanup_old_safety_backups(self, max_keep: int = 10) -> int:
        """
        Removes old safety backups, keeping only the most recent ones.
        
        Args:
            max_keep: Maximum number of safety backups to keep (default: 10)
            
        Returns:
            int: Number of files removed
        """
        try:
            backup_dir = get_auto_backup_directory()
            pattern = os.path.join(backup_dir, f"{self._safety_backup_prefix}*.zip")
            safety_files = glob.glob(pattern)
            
            # Sort by modification time (most recent first)
            safety_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Remove excess files
            files_to_remove = safety_files[max_keep:]
            removed_count = 0
            
            for file_path in files_to_remove:
                try:
                    os.remove(file_path)
                    add_debug_message(f"🗑️ Removed old safety backup: {os.path.basename(file_path)}", "BACKUP")
                    removed_count += 1
                except Exception as e:
                    add_debug_message(f"⚠️ Error removing {file_path}: {e}", "BACKUP")
            
            if removed_count > 0:
                add_debug_message(f"📁 Cleanup completed: {removed_count} safety backup(s) removed", "BACKUP")
            
            return removed_count
            
        except Exception as e:
            add_debug_message(f"Error cleaning up safety backups: {e}", "BACKUP")
            return 0


# Maintain compatibility with old code
BackupManager = SimplifiedBackupManager

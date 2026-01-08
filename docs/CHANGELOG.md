# 📋 CHANGELOG - Sheets2Anki

## Complete History of Updates and Modifications

---

## 🚀 **v2.3.0** - January 2026 *(Current Version)*

### ✨ **New Features**
- **Debug Mode UI**: Dedicated interface (`Ctrl+Shift+L`) to manage debug mode, view logs, and reset configurations.
- **Sync Cancellation**: Added "CANCEL SYNC" button in data removal warning dialogs to prevent accidental data loss.

### 🎨 **UI/UX Improvements**
- **Modernized Configuration Dialogs**: Global Student, Deck Options, and AnkiWeb Sync dialogs updated with gradient headers, improved styling, and full dark mode support.
- **Localization**: Standardized column names to Portuguese (`PERGUNTA`, `ALUNOS`, `LEVAR PARA PROVA`) in documentation and sample data.
- **Sample Data**: Translated `sample_sheet.tsv` content to English while maintaining Portuguese column headers.

### 🔧 **Fixes & Optimization**
- **AnkiWeb Timeout**: Fixed persistence issue where timeout settings were not being saved.
- **Documentation**: Updated README to reflect support for 23 columns.
- **Code Cleanup**: Removed dead code directories (`config_pkg`, `sync_pkg`, `utils_pkg`) and consolidated imports.

---

## 🚀 **v2.2.0** - August 2025

### ✨ **Revolutionary URL System Simplification**

#### 🎯 **Unified URLs**
- **ONLY Edit URLs**: Simplified system works exclusively with edit URLs (`/edit?usp=sharing`)
- **Elimination of Published Format**: Completely removed support for published URLs (`/pub?output=tsv`)
- **Automatic Conversion**: Edit URLs are automatically converted to TSV download format
- **Simplified Process**: A single URL type for all use cases

#### 🆔 **Real ID Identification System**
- **Spreadsheet ID**: Uses the actual Google Sheets spreadsheet ID as identifier
- **End of Hashes**: Completely eliminates the MD5 hash system for identification
- **Clearer Configuration**: `meta.json` now uses real spreadsheet IDs as keys
- **Total Transparency**: Users can see exactly which spreadsheet is configured

#### 🔧 **Complete API Refactoring**
- **New Functions**:
  - `extract_spreadsheet_id_from_url()`: Extracts spreadsheet ID from edit URLs
  - `get_spreadsheet_id_from_url()`: Gets ID with validation
  - `convert_edit_url_to_tsv()`: Converts edit URL to TSV
- **Removed Functions**:
  - `extract_publication_key_from_url()`: ❌ Removed
  - `get_publication_key_hash()`: ❌ Removed
  - `convert_google_sheets_url_to_tsv()`: ❌ Removed

### 🗂️ **Automatic Configuration Migration**
- **Compatibility**: Existing configurations continue working
- **Transparent Migration**: System automatically detects and migrates old configurations
- **Data Preservation**: All decks and preferences are maintained
- **No Intervention**: Completely automatic process for the user

### 🧪 **New Test Suite**
- **Specific Tests**: 18 new tests for simplified functionalities
- **Complete Coverage**: Validation of all new functions
- **Error Tests**: Robust validation of error cases
- **Dedicated File**: `test_url_simplification.py` for new functionality tests

---

## 🚀 **v2.1.0** - August 2025

### ✨ **New Features**

#### 💾 **Advanced Backup System**
- **Automatic Configuration Backup**: Automatic backup on each synchronization with file rotation (keeps only the 50 most recent)
- **Configuration-Only Backup**: New backup mode that preserves only addon settings, ideal for reinstallation
- **3-Column Interface**: Side-by-side layout for full backup, recovery and automatic settings
- **Flexible Configuration**: Customizable directory for automatic backups
- **Sync Integration**: Automatic trigger after each successful synchronization

#### 🔧 **Automatic Name Consistency System**
- **Automatic Correction**: Automatically detects and corrects inconsistencies in note type names
- **Intelligent Synchronization**: Checks name alignment during each synchronization
- **Transparent Update**: Corrects differences between remote and local names without manual intervention
- **Data Preservation**: Maintains study history and settings during corrections
- **Standardized Names**: Implements consistent standards for decks, note types and configurations

#### 📊 **Enhanced Sync Summary**
- **Dual Visualization**: "Simplified" and "Complete" modes for different needs
- **Optimized Order**: In "Complete" mode, aggregated general summary appears first
- **Detailed Metrics**: Complete spreadsheet statistics and results per deck
- **Responsive Interface**: Automatic support for dark mode and adaptive layout

#### 🖼️ **Multimedia Field Support**
- **Media Fields**: "IMAGE HTML" for images/illustrations and "VIDEO HTML" for embedded videos
- **Automatic Template Update**: Automatically adds fields to existing note types
- **Intelligent Positioning**: Media appears on the back of the card for better pedagogy
- **Safe Templates**: Doesn't duplicate fields and preserves existing data

### 🔄 **Improvements and Optimizations**

#### 🌐 **Complete Google Sheets URL Support**
- **Edit URLs**: Native support for `/edit?usp=sharing` URLs
- **Automatic Conversion**: Automatically converts edit URLs to TSV format
- **GID Auto-discovery**: Automatically detects the correct spreadsheet gid
- **Backward Compatibility**: Maintains compatibility with published TSV URLs
- **Bug Fix**: Eliminates HTTP 400 "Bad Request" error with edit URLs

#### 👥 **Advanced Student Management**
- **Global Configuration**: Define once which students to sync across all decks
- **Personalized Subdecks**: Each student has their own organized hierarchy
- **Unique Note Types**: Personalized card templates for each student
- **Intelligent Filtering**: Syncs only the chosen students

#### 🏷️ **Complete Hierarchical Tag System**
- **8 Categories**: Students, Topics, Exam Boards, Years, Careers, Importance, Extra Tags
- **Hierarchical Structure**: Automatic organization in levels (`Sheets2Anki::Category::Item`)
- **Custom Tags**: Support for additional custom tags

### 🐛 **Bug Fixes**
- **HTTP 400 with Edit URLs**: Resolved through GID auto-discovery
- **Name Inconsistency**: Automatically corrected by consistency system
- **Count Calculation**: Fixed to use notes instead of questions
- **Empty Subdecks**: Automatic removal after synchronization
- **Error Reports**: Updated link to correct GitHub repository

### 🧪 **Testing and Quality**
- **Comprehensive Test Suite**: Tests for backup, dialog, name consistency
- **Complete Coverage**: 100% of new features tested
- **Integration Tests**: End-to-end functionality validation
- **Compatibility Tests**: Verification with PyQt5/PyQt6

---

## 🏗️ **v2.0.0** - July 2025

### ✨ **Main Features**
- **Selective Synchronization**: `SYNC` column for individual card control
- **Basic Backup System**: Manual backup and deck restoration
- **AnkiWeb Synchronization**: Automatic after updates
- **Cloze Card Support**: Automatic detection of `{{c1::text}}` patterns
- **Personalized Note Types**: One for each student automatically

### 🔧 **Base Architecture**
- **19 Required Columns**: Standardized structure for spreadsheets
- **TSV Processing**: Robust engine for Google Sheets data
- **Configuration Management**: `meta.json` system for persistence
- **Qt Interface**: Modern dialogs for configuration and status

---

## 📋 **v1.1.0** - June 2025

### ✨ **Basic Features**
- **Google Sheets Synchronization**: Direct connection with TSV spreadsheets
- **Automatic Deck Creation**: Based on spreadsheet data
- **Basic Note Types**: Support for basic and cloze cards
- **Simple Tags**: Basic categorization system

### 🔧 **Infrastructure**
- **Anki Add-on**: Native integration with Anki 2.1+
- **Data Processing**: Basic TSV engine
- **Simple Interface**: Basic configuration dialogs

---

## 📊 **Project Statistics**

### 📁 **Current Structure**
- **Python Modules**: 15+ main modules
- **Tests**: 10+ test files with comprehensive coverage
- **Documentation**: 6 specialized documents
- **Scripts**: 4 build and validation scripts

### 🏷️ **Features by Version**
- **v1.1.0**: 4 basic features
- **v2.0.0**: +8 advanced features
- **v2.1.0**: +12 premium features

### 🧪 **Quality and Testing**
- **Test Coverage**: 95%+ of features
- **Compatibility**: Anki 2.1.60+ to 2.1.66+
- **Qt Support**: PyQt5 and PyQt6
- **Platforms**: Windows, macOS, Linux

---

## 🎯 **Planned Future Versions**

### 🚀 **v2.4.0** - Planned
- **Real-Time Synchronization**: WebSocket for instant updates
- **Advanced Templates**: Visual card template editor
- **Advanced Statistics**: Complete performance dashboard
- **REST API**: Endpoints for integration with other tools

### 🌟 **v3.0.0** - Roadmap
- **Artificial Intelligence**: Automatic AI card generation
- **Real-Time Collaboration**: Simultaneous spreadsheet editing
- **Versioning**: Version control for spreadsheets
- **Mobile Support**: Companion app for mobile devices

---

## 📚 **Related Documentation**

### 📖 **Technical Documents**
- [Developer Documentation](./README.md) - Comprehensive technical documentation
- [User Guide](../README.md) - Feature explanations and usage instructions

### 🛠️ **For Developers**
- [`README.md`](../README.md) - Main user documentation
- [`tests/README.md`](../tests/README.md) - Testing and development guide
- [`scripts/README.md`](../scripts/README.md) - Build and deploy scripts

---

## 🤝 **Contributions**

### 👥 **Core Team**
- **Igor Florentino** - Lead Developer and Maintainer
- **Email**: igorlopesc@gmail.com
- **GitHub**: [@igorrflorentino](https://github.com/igorrflorentino)

### 🐛 **Report Bugs**
- **Issues**: [GitHub Issues](https://github.com/igorrflorentino/sheets2anki/issues)
- **Discussions**: [GitHub Discussions](https://github.com/igorrflorentino/sheets2anki/discussions)

### 🌟 **Acknowledgments**
- Anki community for the robust platform
- Users who provided valuable feedback
- Code and documentation contributors

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [`LICENSE`](../LICENSE) file for details.

---

## 🔗 **Useful Links**

- **🏠 Homepage**: [Sheets2Anki](https://github.com/igorrflorentino/sheets2anki)
- **📦 AnkiWeb**: [Add-on Page](https://ankiweb.net/shared/info/sheets2anki)
- **📖 Documentation**: [Wiki](https://github.com/igorrflorentino/sheets2anki/wiki)
- **💬 Support**: [Discord/Telegram](https://t.me/sheets2anki)

---

*Last updated: January 08, 2026*
*CHANGELOG Version: 1.0.0*

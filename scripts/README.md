# Scripts Directory

This directory contains utility scripts for Sheets2Anki development and image processing.

## 📸 Image Processor Tool

**New!** Process images from Google Sheets cells and convert them to HTML tags.

See [`IMAGE_PROCESSOR_README.md`](IMAGE_PROCESSOR_README.md) for full documentation.

**Quick Start**: [`QUICKSTART.md`](QUICKSTART.md)

```bash
# Setup
./setup_image_processor.sh

# Run
python3 process_sheet_images.py
```

---

## 🔧 Build and Packaging Scripts

Python scripts to build and validate Sheets2Anki add-on packages.

## Available Scripts

### `build_packages.py`
**Main script and most recommended for general use.**

Unified interactive menu that allows you to:
- Build package for AnkiWeb (`.ankiaddon`)
- Build standalone package (`.ankiaddon` with complete manifest)
- Validate existing packages
- Clean up temporary files

```bash
python scripts/build_packages.py
```

### `create_ankiweb_package.py`
Specifically builds the package for AnkiWeb upload.

- Removes optional fields from the manifest (keeps only mandatory ones)
- Cleans all cache files (`__pycache__`, `.pyc`, `.pyo`)
- Generates `build/sheets2anki.ankiaddon` ready for upload
- Validates the package structure

```bash
python scripts/create_ankiweb_package.py
```

### `create_standalone_package.py`
Builds a standalone package for independent distribution.

- Keeps the complete manifest with all fields
- Cleans cache files
- Generates `build/sheets2anki-standalone.ankiaddon`
- Validates the package structure

```bash
python scripts/create_standalone_package.py
```

### `validate_packages.py`
Validates existing `.ankiaddon` packages.

- Verifies ZIP structure
- Validates manifest.json
- Verifies absence of cache files
- Lists all included files

```bash
python scripts/validate_packages.py build/sheets2anki.ankiaddon
```

## Recommended Workflow

1. **For development and testing**: Use `build_packages.py` for quick access to all functions
2. **For AnkiWeb upload**: Use `create_ankiweb_package.py` or the corresponding menu option
3. **For independent distribution**: Use `create_standalone_package.py` or the corresponding menu option
4. **For validation**: Use `validate_packages.py` or the corresponding menu option

## Package Structure

The scripts ensure that `.ankiaddon` packages follow AnkiWeb specifications:

- ✅ Files at the root of the ZIP (no parent folder)
- ✅ Valid and present `manifest.json`
- ✅ Absence of `__pycache__`, `.pyc`, `.pyo` files
- ✅ Preserved directory structure (`src/`, `libs/`, etc.)

## Requirements

- Python 3.6+
- Standard modules: `json`, `zipfile`, `os`, `shutil`, `tempfile`

All scripts are self-contained and do not require external dependencies.

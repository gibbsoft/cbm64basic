# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-06

### Added

- **Modular architecture**: Split monolithic `cbm_basic.py` (2000+ lines) into focused modules:
  - `interpreter.py` - Core BASIC interpreter with match/case dispatch
  - `commands.py` - Statement handlers (PRINT, GOTO, FOR, INPUT, etc.)
  - `functions.py` - BASIC functions with dict dispatch (ABS, CHR$, LEFT$, etc.)
  - `screen.py` - Virtual screen memory emulation
  - `charset.py` - PETSCII and screen code Unicode mappings
  - `colors.py` - ANSI terminal color support (256-color)
  - `constants.py` - Memory addresses and screen dimensions
  - `prg_file.py` - PRG file format load/save support

- **Comprehensive test suite**: 96 pytest tests covering all BASIC features

- **Documentation**:
  - API documentation generated with pdoc
  - `CONTRIBUTING.md` with code style guidelines
  - Updated `AGENTS.md` for AI coding assistants
  - `Makefile` with targets: install, test, docs, lint, run, clean

- **Code style guidelines**:
  - PEP 8 compliant
  - Small files (<500 lines per module)
  - Modern Python 3.10+ (match/case, type hints)
  - Dict dispatch for function lookups
  - match/case for command dispatch

### Changed

- **Python version**: Minimum Python 3.10 (for match/case support)
- **Project structure**: All modules now under 500 lines for easier maintenance
- `cbm_basic.py` is now a re-export module for backward compatibility

### Developer Experience

- `make docs` - Generate HTML documentation with pdoc
- `make test` - Run all 96 tests
- `make run` - Start the BASIC editor
- Optional dev dependencies: `pip install -e ".[dev]"`

## [0.0.0] - Initial

- Initial monolithic implementation
- Basic BASIC interpreter functionality
- Interactive editor with syntax highlighting

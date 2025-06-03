# Fault Editor - Modular Architecture

## Overview
This is a complete refactoring of the AGV Fault Editor application into a modular architecture with proper separation of concerns. The application manages JSON fault code files for AGV (Automated Guided Vehicle) systems with translation capabilities between French, English, and Spanish.

The refactoring has transformed the monolithic application into a well-structured, modular system with enhanced features and improved maintainability.

## Features

### Core Features
- Manage fault codes in JSON format for AGV systems
- Support for multi-language fault descriptions (French, English, Spanish)
- Flat file editing with real-time search and navigation
- Hierarchical file structure navigation
- Batch translation between languages

### Advanced Features
- **Theme System**: Switch between dark, light, and high-contrast themes
- **Keyboard Navigation**: Enhanced keyboard shortcuts and focus group navigation
- **Plugin System**: Dynamically load and activate plugins to extend functionality
- **Statistics Plugin**: View detailed statistics about fault code files
- **Responsive UI**: Modern interface with proper layout management
- **Type Safety**: Improved type annotations throughout the codebase

## Architecture

The application has been refactored into a modular architecture with the following components:

### Core Modules
- `config/`: Application-wide configuration and constants
- `models/`: Data models and state management
- `file_ops/`: File operations and management
- `search/`: Search functionality
- `translation/`: Translation services
- `ui/`: User interface components
- `script_ops/`: Script operations and automation
- `plugins/`: Plugin system and extensions

### Key Components
- **MainController**: Orchestrates all application components
- **ThemeManager**: Manages application theming
- **PluginManager**: Handles plugin discovery and activation
- **FlatEditor**: Manages flat JSON file editing
- **HierarchicalEditor**: Handles hierarchical file structure
- **KeyboardNavigator**: Enhances keyboard accessibility

## How to Use

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application
```
python app_latest.py
```

Use `app_latest.py` for the fully modular version with all advanced features.

### Keyboard Shortcuts

- **Ctrl+O**: Open directory
- **Ctrl+R**: Refresh files
- **Ctrl+F**: Search
- **F1**: Help
- **Ctrl+T**: Change theme
- **F12**: Plugin manager
- **F6**: Next focus group
- **Shift+F6**: Previous focus group

## Theme Support
The application includes three themes:
- **Dark**: Default dark theme
- **Light**: Bright theme for high visibility
- **High Contrast**: Accessibility-focused theme

## Plugin Development
Plugins can be created by:
1. Creating a Python file in the `plugins/` directory
2. Extending the `Plugin` base class
3. Implementing the required methods (activate, deactivate)

Example:
```python
from plugins.plugin_system import Plugin

class MyPlugin(Plugin):
    name = "My Plugin"
    version = "1.0.0"
    description = "This is a custom plugin"
    author = "Your Name"

    def activate(self):
        # Plugin activation code
        pass

    def deactivate(self):
        # Plugin cleanup code
        pass
```

## Contributors
- Original application: Noovelia team
- Refactoring and modular architecture: AI Assistant

## License
[License information]

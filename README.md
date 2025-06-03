# AGVConfig-Traduction

A comprehensive Python-based tool for translating and managing AGV (Automated Guided Vehicle) configuration fault codes. This project provides a GUI application and command-line utilities for translating JSON configuration files between French, English, and Spanish using OpenAI's translation API.

## 🚀 Features

- **Multi-language Support**: Translate between French (fr), English (en), and Spanish (es)
- **GUI Application**: User-friendly Tkinter interface for browsing and editing fault codes
- **Batch Translation**: Automatic generation of missing translation files
- **File Synchronization**: Keep translation files synchronized across languages
- **Coherence Checking**: Validate consistency across different language versions
- **OpenAI Integration**: High-quality translations using GPT models
- **Language Detection**: Optional automatic language detection for improved accuracy
- **Plugin Architecture**: Extend the editor with optional plugins

## 📋 Prerequisites

- Python 3.7 or higher
- OpenAI API key (for translation services)
- tkinter (usually included with Python)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/AGVConfig-Traduction.git
   cd AGVConfig-Traduction
   ```

2. **Install dependencies**:
   ```bash
   cd comparateur_jsonV9
   pip install -r requirements.txt
   # Optional: install development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Configure environment variables**:
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your OpenAI API key
   # Get your API key from: https://platform.openai.com/api-keys
   ```

4. **Set up your OpenAI API key** in the `.env` file:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## 🎯 Usage

### GUI Application

Launch the main GUI application:
```bash
python app.py
```

**Main Features:**
- **Open Folder**: Load a directory containing JSON fault files
- **Language Selection**: Switch between FR, EN, and ES
- **Navigation**: Browse through fault code hierarchies
- **Edit**: Modify fault descriptions directly in the interface
- **Auto-generation**: Create missing translation files automatically
- **Plugins**: Optional features (e.g., statistics) can be enabled via the plugin system

### Plugins

The editor automatically discovers plugins from `comparateur_jsonV9/plugins/`.
Plugins can add custom UI elements or commands. The included `StatisticsPlugin`
adds a statistics window accessible from the toolbar when activated.

### Command-Line Tools

#### 1. Synchronize a Single File
```bash
python sync_one.py path/to/file_fr.json [--force-retranslate]
```
- Synchronizes one JSON file with its translations in other languages
- `--force-retranslate`: Force re-translation of existing entries

#### 2. Synchronize All Files
```bash
python sync_all.py [path/to/directory] [--force-retranslate]
```
- Synchronizes all JSON files in a directory
- `path/to/directory` is optional and defaults to `../JSON`
- `--force-retranslate`: Force re-translation of existing entries

#### 3. Generate Missing Files
```bash
python generer_manquant.py path/to/directory [--auto]
```
- Creates missing translation files
- `--auto`: Run without interactive prompts

#### 4. Check Coherence
```bash
python check_coherence.py path/to/directory
```
- Validates consistency across language versions

#### 5. Generate Specific Files
```bash
python generer_fichier.py base_file.json source_lang target_lang
```
- Generate a specific translation file

## 📁 Project Structure

```
AGVConfig-Traduction/
├── comparateur_jsonV9/           # Main application directory
│   ├── app.py                    # GUI application
│   ├── translate.py              # Translation module
│   ├── sync_one.py               # Single file synchronization
│   ├── sync_all.py               # Batch synchronization
│   ├── generer_manquant.py       # Missing file generation
│   ├── generer_fichier.py        # Specific file generation
│   ├── check_coherence.py        # Coherence validation
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment configuration template
│   └── logs/                     # Application logs
├── JSON/                         # JSON fault code files
│   └── _0_SAFETY/               # Safety-related fault codes
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables

A `.env.example` template is provided. Copy it to `.env` and then adjust the
values as needed:

```bash
cp .env.example .env

# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
OPENAI_ORG_ID=your_organization_id_here
OPENAI_MODEL=gpt-3.5-turbo
TRANSLATION_TEMPERATURE=0.3
```

### Supported Languages

- **French (fr)**: Source language for most fault codes
- **English (en)**: Primary translation target
- **Spanish (es)**: Secondary translation target

## 📊 File Format

JSON files follow this structure:
```json
{
  "Faults": [
    {
      "Description": "Fault description text",
      "IsExpandable": false
    }
  ]
}
```

File naming convention: `faults_XXX_YYY_ZZZ_WWW_[lang].json`
- Where `[lang]` is `fr`, `en`, or `es`
- Numbers represent hierarchical fault code positions

## 🔍 Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Ensure your `.env` file exists and contains a valid API key
   - Check that the `.env` file is in the correct directory

2. **Translation errors**
   - Verify your OpenAI API key has sufficient credits
   - Check your internet connection
   - Review the logs in the `logs/` directory

3. **GUI not launching**
   - Ensure tkinter is installed: `python -m tkinter`
   - Check Python version compatibility (3.7+)

4. **File synchronization issues**
   - Verify file permissions in the target directory
   - Check that JSON files have valid syntax

### Testing Your Setup

Run the test script to verify your configuration:
```bash
python test_translation.py
```

## 🧪 Development

### Running Tests
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Code Quality
```bash

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📝 Logging

The application logs activities to `logs/app_debug.log`. Log levels:
- **INFO**: Normal operations and status updates
- **WARNING**: Non-critical issues and fallback operations
- **ERROR**: Critical errors and failures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure code quality: `black .` and `flake8 .`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a Pull Request

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub Issues
- **Documentation**: Check this README and inline code documentation
- **Logs**: Review `logs/app_debug.log` for detailed error information

## 🔄 Version History

- **v1.0**: Initial release with basic translation capabilities
- **v1.1**: Added GUI application with enhanced error handling
- **v1.2**: Improved synchronization and coherence checking
- **v1.3**: Enhanced logging and configuration management
- **v1.3.1**: Removed legacy `config.py` and `config_temp.py`; configuration constants are now in `config/constants.py`

---

**Note**: This tool requires an active OpenAI API subscription for translation services. Translation quality depends on the source text and API model used.

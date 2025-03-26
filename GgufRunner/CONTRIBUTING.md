# Contributing to GGUF Model Chat

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## Code of Conduct

Please be respectful and considerate of others when contributing.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported
- Use the bug report template
- Include as much detail as possible
- Include steps to reproduce the issue

### Suggesting Enhancements

- Check if the enhancement has already been suggested
- Describe the enhancement in detail
- Explain why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Open a Pull Request

## Development Environment

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `streamlit run app.py`

## Project Structure

- `app.py`: Main Streamlit application
- `model_manager.py`: Handles GGUF model loading and operations
- `session_handler.py`: Manages saving and loading of chat sessions
- `components.py`: UI components for the application interface
- `utils.py`: Utility functions and roleplay persona definitions
- `.streamlit/config.toml`: Streamlit configuration

## Coding Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions and classes
- Write comments for complex code blocks

## Testing

- Add tests for new features
- Ensure all tests pass before submitting pull requests

## Licensing

By contributing to this project, you agree that your contributions will be licensed under the project's license.
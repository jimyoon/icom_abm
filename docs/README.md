# CHANCE-C Documentation

This directory contains the Sphinx documentation for the CHANCE-C package.

## Building the Documentation

### Prerequisites

Install the documentation dependencies:

```bash
pip install -e ".[docs]"
```

### Building the API from the package docstrings

```bash
cd docs
sphinx-apidoc -f -o source/ ../chance_c/
```

### Building HTML Documentation

From the project root:

```bash
cd docs
make html
```

Or using the Python script:

```bash
python docs/build_docs.py
```

### Viewing the Documentation

After building, open `docs/_build/html/index.html` in your web browser.

## Documentation Structure

- `conf.py` - Sphinx configuration
- `index.rst` - Main documentation index
- `getting_started.rst` - Getting started guide
- `user_guide.rst` - Comprehensive user guide
- `api/` - API documentation (auto-generated from docstrings)
- `tutorials/` - Step-by-step tutorials
- `examples/` - Practical examples
- `contributing.rst` - Contributing guidelines
- `changelog.rst` - Version history

## Adding Documentation

### Adding New Pages

1. Create a new `.rst` file in the appropriate directory
2. Add it to the relevant `toctree` in an index file
3. Build and test the documentation

### API Documentation

API documentation is automatically generated from docstrings using autodoc. To add new API documentation:

1. Add docstrings to your Python functions and classes
2. Create a new `.rst` file in `api/` with the appropriate `automodule` directive
3. Add it to `api/index.rst`

### Example

```rst
# In api/new_module.rst
New Module
==========

.. automodule:: chance_c.new_module
   :members:
   :undoc-members:
   :show-inheritance:
```

## Documentation Style

- Use Google-style docstrings with NumPy extensions
- Include type hints for all public functions
- Provide code examples in docstrings
- Use reStructuredText for formatting
- Follow the existing documentation structure

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure the package is installed in development mode
2. **Missing extensions**: Install all documentation dependencies
3. **Build errors**: Check the Sphinx output for specific error messages

### Getting Help

- Check the Sphinx documentation: https://www.sphinx-doc.org/
- Review existing documentation files for examples
- Ask questions in GitHub Issues or Discussions 
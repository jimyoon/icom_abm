Contributing
============

We welcome contributions to CHANCE-C! This guide will help you get started.

Development Setup
----------------

1. **Fork and Clone**
   .. code-block:: bash

      git clone https://github.com/your-username/icom_abm.git
      cd icom_abm

2. **Install Dependencies**
   .. code-block:: bash

      # Install in development mode
      pip install -e .
      
      # Install development dependencies
      pip install pytest pytest-cov flake8 black isort mypy sphinx

3. **Set up Pre-commit Hooks**
   .. code-block:: bash

      # Install pre-commit
      pip install pre-commit
      pre-commit install

Code Style
----------

We follow PEP 8 with some modifications:

* **Line length**: 88 characters (Black default)
* **Import sorting**: isort
* **Type hints**: Required for all public functions
* **Docstrings**: Google style with NumPy extensions

Running Tests
------------

.. code-block:: bash

   # Run all tests
   pytest tests/

   # Run with coverage
   pytest tests/ --cov=chance_c --cov-report=html

   # Run specific test categories
   pytest tests/test_model_classes.py
   pytest tests/test_model_engines.py

Code Quality
-----------

.. code-block:: bash

   # Format code
   black chance_c/ tests/
   isort chance_c/ tests/

   # Check style
   flake8 chance_c/ tests/

   # Type checking
   mypy chance_c/

Documentation
------------

Building Documentation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Build HTML documentation
   cd docs
   make html

   # View documentation
   open _build/html/index.html

Adding Documentation
^^^^^^^^^^^^^^^^^^^

* Add docstrings to all public functions and classes
* Update relevant .rst files in docs/
* Include code examples in docstrings
* Add type hints for better documentation

Pull Request Process
-------------------

1. **Create a Feature Branch**
   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make Changes**
   * Write code following our style guidelines
   * Add tests for new functionality
   * Update documentation
   * Update CHANGELOG.md

3. **Test Your Changes**
   .. code-block:: bash

      pytest tests/
      flake8 chance_c/ tests/
      mypy chance_c/

4. **Submit Pull Request**
   * Provide a clear description of changes
   * Reference any related issues
   * Include test results

Issue Reporting
--------------

When reporting issues, please include:

* **Environment**: OS, Python version, package versions
* **Reproduction**: Steps to reproduce the issue
* **Expected vs Actual**: What you expected vs what happened
* **Error Messages**: Full error traceback if applicable

Development Guidelines
---------------------

Adding New Features
^^^^^^^^^^^^^^^^^^

1. **Design**: Plan the feature and discuss in issues
2. **Implementation**: Follow existing patterns
3. **Testing**: Add comprehensive tests
4. **Documentation**: Update docs and add examples

Bug Fixes
^^^^^^^^^

1. **Reproduce**: Create a minimal test case
2. **Fix**: Implement the fix
3. **Test**: Ensure the fix works and doesn't break other functionality
4. **Document**: Update relevant documentation

Performance Improvements
^^^^^^^^^^^^^^^^^^^^^^^

* Profile before optimizing
* Include benchmark tests
* Document performance improvements
* Consider backward compatibility

Release Process
--------------

1. **Version Bump**: Update version in pyproject.toml
2. **Changelog**: Update CHANGELOG.md
3. **Tests**: Ensure all tests pass
4. **Documentation**: Build and verify documentation
5. **Tag**: Create git tag for release
6. **Publish**: Release to PyPI

Contact
-------

* **Issues**: `GitHub Issues <https://github.com/jimyoon/icom_abm/issues>`_
* **Discussions**: `GitHub Discussions <https://github.com/jimyoon/icom_abm/discussions>`_
* **Email**: support@chance-c.org

Thank you for contributing to CHANCE-C! 
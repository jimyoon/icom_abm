Contributing to CHANCE-C
=======================

We welcome contributions to CHANCE-C! This guide will help you get started with contributing to the project.

Types of Contributions
----------------------

We welcome many types of contributions:

- **Bug reports** - Help us identify and fix issues
- **Feature requests** - Suggest new functionality
- **Code contributions** - Implement new features or fix bugs
- **Documentation** - Improve guides, tutorials, and API docs
- **Examples** - Share use cases and applications
- **Testing** - Help test new features and find edge cases
- **Community support** - Help other users in discussions

Getting Started
---------------

Development Setup
~~~~~~~~~~~~~~~~~~

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   .. code-block:: bash

      git clone https://github.com/your-username/icom_abm.git
      cd icom_abm

3. **Create a virtual environment**:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

4. **Install in development mode**:

   .. code-block:: bash

      pip install -e .[dev,docs]

5. **Set up pre-commit hooks** (optional but recommended):

   .. code-block:: bash

      pip install pre-commit
      pre-commit install

Development Workflow
~~~~~~~~~~~~~~~~~~~~

1. **Create a branch** for your work:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make your changes** following our coding standards
3. **Add tests** for new functionality
4. **Run tests** to ensure everything works:

   .. code-block:: bash

      pytest tests/

5. **Update documentation** if needed
6. **Commit your changes**:

   .. code-block:: bash

      git add .
      git commit -m "Brief description of changes"

7. **Push to your fork**:

   .. code-block:: bash

      git push origin feature/your-feature-name

8. **Create a pull request** on GitHub

Code Standards
-------------

Python Style
~~~~~~~~~~~~~

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Use absolute imports when possible
- **Docstrings**: Google style docstrings
- **Type hints**: Use type hints for public functions

Code Formatting
~~~~~~~~~~~~~~~~

We use automated formatting tools:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

Run formatting before committing:

.. code-block:: bash

   black chance_c/ tests/
   isort chance_c/ tests/
   flake8 chance_c/ tests/

Documentation Style
~~~~~~~~~~~~~~~~~~~~~

- **Docstrings**: Use Google style
- **RST files**: Follow reStructuredText conventions
- **Code examples**: Include complete, runnable examples
- **API docs**: Auto-generated from docstrings

Example docstring:

.. code-block:: python

   def example_function(param1: str, param2: int = 10) -> bool:
       """Brief description of the function.
       
       Longer description if needed. Explain the purpose,
       behavior, and any important details.
       
       Args:
           param1: Description of first parameter.
           param2: Description of second parameter. Defaults to 10.
           
       Returns:
           Description of return value.
           
       Raises:
           ValueError: When param1 is empty.
           
       Example:
           >>> result = example_function("test", 5)
           >>> print(result)
           True
       """
       if not param1:
           raise ValueError("param1 cannot be empty")
       return len(param1) > param2

Testing
-------

Test Structure
~~~~~~~~~~~~~~

Tests are organized in the ``tests/`` directory:

- ``test_config.py`` - Configuration testing
- ``test_data_loader.py`` - Data loading tests
- ``test_field_mapper.py`` - Field mapping tests
- ``test_model_classes.py`` - Model class tests
- ``test_model_engines.py`` - Engine tests

Writing Tests
~~~~~~~~~~~~~

- Use **pytest** for all tests
- Write tests for new functionality
- Include edge cases and error conditions
- Use descriptive test names
- Mock external dependencies when appropriate

Example test:

.. code-block:: python

   import pytest
   from chance_c import Model, SimulationConfig

   def test_model_creation_with_defaults():
       """Test that Model can be created with default settings."""
       model = Model()
       assert model.config.simulation_name == "ABM_Baltimore_example"
       assert model.config.n_years == 2

   def test_model_creation_with_custom_config():
       """Test Model creation with custom configuration."""
       config = SimulationConfig(
           simulation_name="Test_Simulation",
           n_years=5
       )
       model = Model(config=config)
       assert model.config.simulation_name == "Test_Simulation"
       assert model.config.n_years == 5

   def test_model_invalid_config():
       """Test that invalid configuration raises appropriate error."""
       with pytest.raises(ValueError):
           Model(n_years=-1)

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_config.py

   # Run with coverage
   pytest --cov=chance_c --cov-report=html

   # Run specific test
   pytest tests/test_config.py::test_model_creation_with_defaults

Documentation
-------------

Building Documentation
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd docs/
   make html

   # View documentation
   open build/html/index.html  # On macOS
   # Or navigate to docs/build/html/index.html

Contributing to Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **API docs**: Improve docstrings in source code
- **Tutorials**: Add new tutorials or improve existing ones
- **Examples**: Contribute real-world use cases
- **User guide**: Enhance explanations and best practices

Documentation is built automatically for pull requests, so you can preview changes.

Submitting Changes
-----------------

Pull Request Process
~~~~~~~~~~~~~~~~~~~

1. **Ensure tests pass** and coverage is maintained
2. **Update documentation** for new features
3. **Add changelog entry** under [Unreleased]
4. **Write clear commit messages**
5. **Create descriptive pull request**

Pull Request Template
~~~~~~~~~~~~~~~~~~~~~~

When creating a pull request, include:

- **Description** of changes
- **Motivation** for the changes
- **Testing** performed
- **Breaking changes** (if any)
- **Related issues** (if applicable)

Example:

.. code-block:: text

   ## Description
   Add support for custom agent behaviors in housing market decisions.

   ## Motivation
   Users requested ability to customize how agents make housing choices
   beyond the built-in utility functions.

   ## Changes
   - Added `CustomAgentBehavior` base class
   - Modified `HousingMarket` engine to support custom behaviors
   - Added documentation and examples
   - Added comprehensive tests

   ## Testing
   - All existing tests pass
   - Added 15 new tests for custom behavior functionality
   - Tested with example custom behavior implementations

   ## Breaking Changes
   None - all changes are backward compatible.

   ## Related Issues
   Closes #123

Review Process
~~~~~~~~~~~~~

1. **Automated checks** run on all pull requests
2. **Maintainer review** for code quality and design
3. **Community feedback** welcome on all PRs
4. **Merge** once approved and checks pass

Commit Message Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use clear, descriptive commit messages:

.. code-block:: text

   # Good
   Add support for custom agent behaviors
   Fix memory leak in housing market engine
   Update tutorial for field mapping system

   # Avoid
   Fix bug
   Update code
   Changes

Bug Reports
----------

Reporting Bugs
~~~~~~~~~~~~~

When reporting bugs, include:

- **CHANCE-C version**
- **Python version**
- **Operating system**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Error messages** (full traceback)
- **Minimal example** that reproduces the issue

Use the bug report template on GitHub Issues.

Bug Report Template
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   **Bug Description**
   A clear description of what the bug is.

   **To Reproduce**
   Steps to reproduce the behavior:
   1. Go to '...'
   2. Click on '....'
   3. Scroll down to '....'
   4. See error

   **Expected Behavior**
   What you expected to happen.

   **Screenshots/Output**
   If applicable, add screenshots or console output.

   **Environment:**
   - CHANCE-C version: [e.g. 0.1.0]
   - Python version: [e.g. 3.11.0]
   - OS: [e.g. macOS 12.0]

   **Additional Context**
   Any other context about the problem.

Feature Requests
---------------

Suggesting Features
~~~~~~~~~~~~~~~~~~~~

Before suggesting a new feature:

1. **Check existing issues** to avoid duplicates
2. **Consider the scope** - does it fit CHANCE-C's goals?
3. **Think about implementation** - is it feasible?
4. **Consider alternatives** - are there other approaches?

Feature Request Template
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   **Feature Description**
   Clear description of the feature you'd like to see.

   **Motivation**
   Why is this feature needed? What problem does it solve?

   **Proposed Solution**
   How do you envision this working?

   **Alternatives Considered**
   Other approaches you've considered.

   **Additional Context**
   Any other context, screenshots, or examples.

Community Guidelines
--------------------

Code of Conduct
~~~~~~~~~~~~~~

We are committed to providing a welcoming and inclusive environment:

- **Be respectful** of different viewpoints and experiences
- **Be collaborative** and constructive in discussions
- **Be patient** with new contributors and users
- **Be professional** in all interactions

Communication Channels
~~~~~~~~~~~~~~~~~~~~~~~

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and community discussion
- **Pull Requests** - Code review and technical discussion

Getting Help
~~~~~~~~~~~

If you need help contributing:

1. **Read the documentation** thoroughly
2. **Search existing issues** for similar questions
3. **Ask in GitHub Discussions** for general help
4. **Create an issue** for specific problems

Recognition
----------

Contributors are recognized in several ways:

- **Contributors file** listing all contributors
- **Release notes** acknowledging significant contributions
- **GitHub contributor statistics** showing contribution history
- **Community recognition** in discussions and social media

Types of Recognition
~~~~~~~~~~~~~~~~~~~~

- **Code contributors** - Direct code contributions
- **Documentation contributors** - Documentation improvements
- **Community contributors** - Helping users, reporting bugs
- **Testing contributors** - Finding and reporting issues
- **Design contributors** - UX/UI and architectural input

Maintainer Responsibilities
----------------------------

Project maintainers are responsible for:

- **Reviewing** pull requests and providing feedback
- **Triaging** issues and feature requests
- **Maintaining** code quality and project direction
- **Releasing** new versions
- **Supporting** the community

Current Maintainers
~~~~~~~~~~~~~~~~~~~~

- **Jim Yoon** - Lead developer and project maintainer
- **Chris R. Vernon** - Core developer and maintainer

Contact Information
-------------------

For questions about contributing:

- **General questions** - GitHub Discussions
- **Bug reports** - GitHub Issues
- **Security issues** - Email maintainers directly
- **Collaboration** - Contact maintainers for larger contributions

Thank you for contributing to CHANCE-C! Your contributions help make urban modeling more accessible and powerful for researchers and practitioners worldwide. 
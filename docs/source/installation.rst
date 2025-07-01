Installation
============

This guide provides detailed instructions for installing CHANCE-C on different operating systems and environments.

Quick Installation
------------------

For most users, the simplest installation method is:

.. code-block:: bash

   pip install chance_c

This will install CHANCE-C and all required dependencies from PyPI.

System Requirements
-------------------

**Python Version**
  CHANCE-C requires Python 3.11 or higher.

**Operating Systems**
  - Windows 10/11
  - macOS 10.14+ (Intel and Apple Silicon)
  - Linux (Ubuntu 18.04+, CentOS 7+, or equivalent)

**Hardware Requirements**
  - **RAM**: Minimum 4GB, recommended 8GB+
  - **Storage**: 1GB+ available space
  - **CPU**: Any modern multi-core processor

**System Dependencies**
  CHANCE-C depends on several geospatial libraries:
  
  - GDAL (Geospatial Data Abstraction Library)
  - PROJ (Cartographic projection library)
  - GEOS (Geometry Engine)

Installation Methods
--------------------

Method 1: pip (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the easiest method for most users:

.. code-block:: bash

   # Create and activate virtual environment (recommended)
   python -m venv chance_c_env
   source chance_c_env/bin/activate  # On Windows: chance_c_env\Scripts\activate
   
   # Install CHANCE-C
   pip install chance_c
   
   # Verify installation
   python -c "import chance_c; print('Installation successful!')"

Method 2: conda
~~~~~~~~~~~~~~~

If you prefer conda or need better geospatial library management:

.. code-block:: bash

   # Create conda environment with geospatial dependencies
   conda create -n chance_c_env python=3.11 gdal geopandas -c conda-forge
   
   # Activate environment
   conda activate chance_c_env
   
   # Install CHANCE-C via pip (not available on conda yet)
   pip install chance_c

Method 3: Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For developers or users who want the latest features:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/jimyoon/icom_abm.git
   cd icom_abm
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in development mode
   pip install -e .
   
   # Install development dependencies
   pip install -e .[dev,docs]

Platform-Specific Instructions
-------------------------------

Windows
~~~~~~~

**Option 1: Using pip (Easiest)**

.. code-block:: batch

   # Open Command Prompt or PowerShell
   python -m venv chance_c_env
   chance_c_env\Scripts\activate
   pip install chance_c

**Option 2: Using conda (Recommended for geospatial work)**

.. code-block:: batch

   # Install Miniconda or Anaconda if not already installed
   # Then create environment with geospatial libraries
   conda create -n chance_c_env python=3.11 gdal geopandas -c conda-forge
   conda activate chance_c_env
   pip install chance_c

**Troubleshooting Windows Issues:**

- If you get SSL certificate errors, try: ``pip install --trusted-host pypi.org --trusted-host pypi.python.org chance_c``
- For GDAL issues, use conda instead of pip for geospatial dependencies

macOS
~~~~~

**Prerequisites**

.. code-block:: bash

   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install geospatial libraries (optional but recommended)
   brew install gdal proj geos

**Installation**

.. code-block:: bash

   # Create virtual environment
   python3 -m venv chance_c_env
   source chance_c_env/bin/activate
   
   # Install CHANCE-C
   pip install chance_c

**Apple Silicon (M1/M2) Macs**

For Apple Silicon Macs, we recommend using conda:

.. code-block:: bash

   # Install Miniforge (conda for Apple Silicon)
   # Download from: https://github.com/conda-forge/miniforge
   
   # Create environment
   conda create -n chance_c_env python=3.11 gdal geopandas -c conda-forge
   conda activate chance_c_env
   pip install chance_c

Linux
~~~~~

**Ubuntu/Debian**

.. code-block:: bash

   # Install system dependencies
   sudo apt-get update
   sudo apt-get install python3-pip python3-venv
   sudo apt-get install gdal-bin libgdal-dev libproj-dev libgeos-dev
   
   # Create virtual environment
   python3 -m venv chance_c_env
   source chance_c_env/bin/activate
   
   # Install CHANCE-C
   pip install chance_c

**CentOS/RHEL/Fedora**

.. code-block:: bash

   # Install system dependencies (CentOS/RHEL)
   sudo yum install python3-pip python3-virtualenv
   sudo yum install gdal-devel proj-devel geos-devel
   
   # Or for Fedora
   sudo dnf install python3-pip python3-virtualenv
   sudo dnf install gdal-devel proj-devel geos-devel
   
   # Create virtual environment and install
   python3 -m venv chance_c_env
   source chance_c_env/bin/activate
   pip install chance_c

Docker Installation
-------------------

For containerized deployments:

.. code-block:: dockerfile

   FROM continuumio/miniconda3:latest
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       && rm -rf /var/lib/apt/lists/*
   
   # Create conda environment
   RUN conda create -n chance_c python=3.11 gdal geopandas -c conda-forge
   
   # Activate environment and install CHANCE-C
   SHELL ["conda", "run", "-n", "chance_c", "/bin/bash", "-c"]
   RUN pip install chance_c
   
   # Set default command
   CMD ["conda", "run", "-n", "chance_c", "python"]

Optional Dependencies
---------------------

For enhanced functionality, you may want to install additional packages:

**Visualization and Analysis**

.. code-block:: bash

   pip install matplotlib seaborn plotly jupyter

**Performance Optimization**

.. code-block:: bash

   pip install numba dask

**Additional Geospatial Tools**

.. code-block:: bash

   pip install rasterio folium contextily

Verification
------------

After installation, verify everything works correctly:

.. code-block:: python

   # Test basic import
   import chance_c
   print(f"CHANCE-C version: {chance_c.__version__}")
   
   # Test model creation
   from chance_c import Model
   model = Model()
   print("✓ Model creation successful")
   
   # Test data loading
   print(f"✓ Default data files found: {model.config.geo_filename is not None}")
   
   # Quick simulation test (optional)
   print("Running quick test simulation...")
   model.run_simulation()
   print("✓ Simulation completed successfully")

Troubleshooting
---------------

Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**"No module named 'gdal'"**
  Install GDAL system libraries first, then reinstall:
  
  .. code-block:: bash
  
     # Ubuntu/Debian
     sudo apt-get install gdal-bin libgdal-dev
     
     # macOS
     brew install gdal
     
     # Then reinstall
     pip uninstall fiona geopandas
     pip install fiona geopandas

**"Microsoft Visual C++ 14.0 is required" (Windows)**
  Install Microsoft Visual C++ Build Tools or use conda:
  
  .. code-block:: bash
  
     conda install gdal geopandas -c conda-forge
     pip install chance_c

**"Permission denied" errors**
  Use virtual environments or user installation:
  
  .. code-block:: bash
  
     pip install --user chance_c

**Memory errors during installation**
  Increase pip's cache or use conda:
  
  .. code-block:: bash
  
     pip install --no-cache-dir chance_c

Performance Issues
~~~~~~~~~~~~~~~~~~

**Slow import times**
  This is normal for the first import as libraries are loaded. Subsequent imports will be faster.

**High memory usage**
  Reduce agent aggregation in your simulation configuration:
  
  .. code-block:: python
  
     config = SimulationConfig(agent_housing_aggregation=50)  # Default is 10

Getting Help
------------

If you encounter issues not covered here:

1. **Check the FAQ**: :doc:`faq` (if available)
2. **Search existing issues**: `GitHub Issues <https://github.com/jimyoon/icom_abm/issues>`_
3. **Create a new issue**: Include your OS, Python version, and error messages
4. **Join discussions**: `GitHub Discussions <https://github.com/jimyoon/icom_abm/discussions>`_

Updating CHANCE-C
-----------------

To update to the latest version:

.. code-block:: bash

   pip install --upgrade chance_c

To check your current version:

.. code-block:: python

   import chance_c
   print(chance_c.__version__)

Uninstallation
---------------

To completely remove CHANCE-C:

.. code-block:: bash

   pip uninstall chance_c
   
   # If you used a virtual environment, simply delete it
   rm -rf chance_c_env  # On Windows: rmdir /s chance_c_env 
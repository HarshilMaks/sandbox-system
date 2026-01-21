# E2B Custom Sandbox Dockerfile for Code Interpreter
# =====================================================
# 
# This creates a custom E2B template with pre-installed Python packages.
# 
# BUILD COMMAND (CRITICAL - must include -c flag!):
#   e2b template build -c "/root/.jupyter/start-up.sh"
#
# The -c flag starts the Jupyter kernel server on port 49999.
# Without it, run_code() will fail with "port 49999 not open" error.
#
# USAGE:
#   from e2b_code_interpreter import Sandbox
#   sandbox = Sandbox(template="your-template-id")
#   result = sandbox.run_code("import numpy; print(numpy.__version__)")

FROM e2bdev/code-interpreter:latest

# Install custom Python packages
# Add or remove packages as needed for your use case
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    scikit-learn \
    requests \
    beautifulsoup4

# Note: Do NOT change USER or WORKDIR - the base image handles this correctly

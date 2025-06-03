#!/bin/bash

# Script to activate the DoR environment without using conda directly
export PATH="/config/miniconda3/envs/DoR/bin:$PATH"
export CONDA_PREFIX="/config/miniconda3/envs/DoR"
export CONDA_DEFAULT_ENV="DoR"
export CONDA_EXE="/config/miniconda3/bin/conda"
export CONDA_PYTHON_EXE="/config/miniconda3/envs/DoR/bin/python"

# Set PS1 to show we're in the DoR environment
export PS1="(DoR) $PS1"

echo "DoR environment activated without using conda directly"
echo "Python: $(which python)"
echo "Python version: $(python --version)"
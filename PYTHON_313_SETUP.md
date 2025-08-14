# Python 3.13 Setup Guide for Knowledge Graph System

## 🐍 Python 3.13 Compatibility Issues

You're using Python 3.13, which is very new and some packages haven't been updated yet. Here are your options:

## 🚀 **Option 1: Quick Test with Minimal Requirements (RECOMMENDED)**

Install only the essential packages:

```bash
pip install -r requirements_minimal.txt
```

Then run the simple test:

```bash
python test_simple_system.py
```

This will test:
- ✅ Data file validation
- ✅ VCF parsing (without Neo4j)
- ✅ Phenotype data processing
- ✅ Environmental data processing
- ✅ CSV generation for original system

## 🏗️ **Option 2: Use Original Learning System**

The original system works great with basic dependencies:

```bash
# Install basic requirements
pip install pandas numpy python-dotenv neo4j

# Test with original system
python3 build_maize_kg.py
python3 expand_maize_kg.py
```

## 🔧 **Option 3: Install Compatible Versions**

Try installing with more flexible version constraints:

```bash
# Install core packages individually
pip install pandas numpy python-dotenv pyyaml requests neo4j flask flask-cors scipy networkx

# Try PyTorch (may not work on Python 3.13 yet)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## 🐳 **Option 4: Use Docker (BEST for Production)**

Create a Docker environment with Python 3.11:

```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app
COPY requirements_production.txt .
RUN pip install -r requirements_production.txt

COPY . .
CMD ["python", "test_production_system.py"]
EOF

# Build and run
docker build -t kg-system .
docker run -v $(pwd):/app kg-system
```

## 🔄 **Option 5: Use Python 3.11 Environment**

If you have conda or pyenv:

```bash
# With conda
conda create -n kg-system python=3.11
conda activate kg-system
pip install -r requirements_production.txt

# With pyenv
pyenv install 3.11.7
pyenv virtualenv 3.11.7 kg-system
pyenv activate kg-system
pip install -r requirements_production.txt
```

## 🧪 **What You Can Test Right Now**

### **Immediate Testing (No additional installs needed):**

```bash
# Test data validation
python test_simple_system.py
```

### **With Minimal Requirements:**

```bash
pip install pandas numpy python-dotenv neo4j
python test_simple_system.py
```

### **With Original System:**

```bash
# Copy test data to toydata
cp test_data/generated_relationships.csv toydata/test_relationships.csv

# Run original system
python3 build_maize_kg.py
python3 expand_maize_kg.py
```

## 📊 **Expected Results**

### **Simple Test Results:**
```
🧪 Starting Simple Knowledge Graph System Tests
==================================================
🔬 Running Test: Data File Validation
==================================================
✅ Data File Validation: PASSED

🔬 Running Test: VCF File Parsing
==================================================
  Parsed 10 variants
  Found 8 samples: ['B73', 'Mo17', 'W22', 'Oh43', 'PH207', 'Ki3', 'A632', 'Tx303']
✅ VCF File Parsing: PASSED

📊 SIMPLE TEST REPORT SUMMARY
============================================================
Total Tests: 5
Passed: 5 ✅
Failed: 0 ❌
Success Rate: 100.0%
```

## 🎯 **Recommended Path**

1. **Start Simple**: Run `python test_simple_system.py`
2. **Test Original**: Use the learning version with toy data
3. **Production Later**: Set up Python 3.11 environment for full production features

## 🔍 **Troubleshooting**

### **If you get import errors:**
```bash
# Check what's installed
pip list | grep -E "(pandas|numpy|neo4j)"

# Install missing packages
pip install <missing-package>
```

### **If Neo4j connection fails:**
```bash
# Start Neo4j with Docker
docker run --name neo4j-test -p7474:7474 -p7687:7687 -d \
  --env NEO4J_AUTH=neo4j/test123 neo4j:4.4

# Test connection
python -c "from neo4j import GraphDatabase; print('Neo4j driver imported successfully')"
```

### **If torch installation fails:**
```bash
# Skip ML features for now
# The system will work without PyTorch for basic graph operations
```

## ✅ **Quick Validation**

Run this to check your setup:

```python
import sys
print(f"Python: {sys.version}")

try:
    import pandas as pd
    print(f"✅ Pandas: {pd.__version__}")
except ImportError:
    print("❌ Pandas not available")

try:
    import neo4j
    print(f"✅ Neo4j driver available")
except ImportError:
    print("❌ Neo4j driver not available")

try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
except ImportError:
    print("❌ PyTorch not available (OK for basic testing)")
```

## 🎉 **Ready to Test!**

Your best bet right now is:

```bash
# 1. Run simple tests (no additional installs)
python test_simple_system.py

# 2. If you want Neo4j integration
pip install neo4j
docker run --name neo4j-test -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/test123 neo4j:4.4
python3 build_maize_kg.py

# 3. For full production features, use Python 3.11 environment
```

The test data I created will work with any of these approaches! 🚀

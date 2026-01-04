#!/bin/bash

echo "====================================================================="
echo "Episodic Extinction Experiment - Repository Structure Verification"
echo "====================================================================="
echo ""

echo "Core Experiment Files:"
echo "----------------------"
for file in trial.py session.py main.py; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo "✓ $file ($lines lines)"
    else
        echo "✗ $file (missing)"
    fi
done

echo ""
echo "Configuration Files:"
echo "-------------------"
for file in requirements.txt settings.json .gitignore; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (missing)"
    fi
done

echo ""
echo "Documentation Files:"
echo "-------------------"
for file in README.md DEVELOPMENT.md; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (missing)"
    fi
done

echo ""
echo "Testing:"
echo "--------"
if [ -f "test_structure.py" ]; then
    echo "✓ test_structure.py"
fi

echo ""
echo "====================================================================="
echo "Repository Structure Summary"
echo "====================================================================="
echo ""
echo "The experiment repository has been set up with:"
echo "  • trial.py - Trial class with stimulus presentation and responses"
echo "  • session.py - Session class managing trial sequences" 
echo "  • main.py - Entry point with command-line interface"
echo "  • settings.json - Configuration file"
echo "  • requirements.txt - Python dependencies (exptools2, psychopy, etc.)"
echo "  • README.md - User guide and usage instructions"
echo "  • DEVELOPMENT.md - Developer guide for extending the experiment"
echo "  • test_structure.py - Validation script"
echo ""
echo "Next Steps:"
echo "  1. Install dependencies: pip install -r requirements.txt"
echo "  2. Run test: python test_structure.py"
echo "  3. Start experiment: python main.py --subject test"
echo ""
echo "====================================================================="

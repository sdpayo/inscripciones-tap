#!/usr/bin/env python
"""Test that verifies no IndentationError occurs when importing or compiling the application files."""
import sys
import os

def test_no_indentation_errors():
    """Test that all critical files can be compiled without indentation errors."""
    print("=" * 70)
    print("Testing for IndentationError issues")
    print("=" * 70)
    
    test_files = [
        'main.py',
        'ui/form_tab.py',
        'ui/config_tab.py',
        'ui/app.py',
        'ui/base_tab.py',
    ]
    
    errors = []
    
    for file_path in test_files:
        print(f"\nTesting: {file_path}")
        try:
            # Test 1: Can compile?
            import py_compile
            py_compile.compile(file_path, doraise=True)
            print(f"  ✅ Compiles successfully")
            
            # Test 2: Check first line isn't a method definition
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('def '):
                    errors.append(f"{file_path}: First line is a method definition!")
                    print(f"  ❌ First line is a method definition: {first_line[:50]}")
                else:
                    print(f"  ✅ First line is valid: {first_line[:50]}")
            
            # Test 3: Parse with AST
            import ast
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            print(f"  ✅ AST parsing successful")
            
        except IndentationError as e:
            error_msg = f"{file_path}: IndentationError on line {e.lineno}: {e.msg}"
            errors.append(error_msg)
            print(f"  ❌ IndentationError: {e}")
        except SyntaxError as e:
            error_msg = f"{file_path}: SyntaxError on line {e.lineno}: {e.msg}"
            errors.append(error_msg)
            print(f"  ❌ SyntaxError: {e}")
        except Exception as e:
            error_msg = f"{file_path}: {type(e).__name__}: {e}"
            errors.append(error_msg)
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    if errors:
        print("❌ TESTS FAILED - Errors found:")
        for error in errors:
            print(f"  - {error}")
        print("=" * 70)
        return False
    else:
        print("✅ ALL TESTS PASSED - No IndentationError detected")
        print("=" * 70)
        return True

if __name__ == "__main__":
    success = test_no_indentation_errors()
    sys.exit(0 if success else 1)

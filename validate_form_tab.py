#!/usr/bin/env python
"""Validate that ui/form_tab.py has correct structure and no indentation errors."""
import ast
import sys
import os

def validate_form_tab():
    """Validate the form_tab.py file structure."""
    file_path = "ui/form_tab.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print("=" * 60)
    print("Validating ui/form_tab.py")
    print("=" * 60)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check 1: File starts with docstring (triple quotes)
        print("\n1. Checking file starts with docstring...")
        if content.startswith('"""'):
            print("   ✅ File starts with triple quotes (docstring)")
        else:
            print(f"   ❌ File does NOT start with triple quotes")
            print(f"   First 50 chars: {repr(content[:50])}")
            return False
        
        # Check 2: No BOM or invisible characters
        print("\n2. Checking for BOM or invisible characters...")
        first_bytes = content.encode('utf-8')[:10]
        if first_bytes.startswith(b'\xef\xbb\xbf'):
            print("   ❌ File has UTF-8 BOM (should be removed)")
            return False
        elif first_bytes[0] not in (ord('"'), ord("'"), ord('#')):
            print(f"   ❌ File starts with unexpected byte: {first_bytes[0]}")
            return False
        else:
            print("   ✅ No BOM or invisible characters detected")
        
        # Check 3: First non-docstring line should be import or empty
        print("\n3. Checking imports follow docstring...")
        first_code_line = None
        for i, line in enumerate(lines[1:], 2):  # Start from line 2
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                first_code_line = (i, line, stripped)
                break
        
        if first_code_line:
            line_num, line_content, stripped = first_code_line
            indent = len(line_content) - len(line_content.lstrip())
            if stripped.startswith('import ') or stripped.startswith('from '):
                if indent == 0:
                    print(f"   ✅ Line {line_num}: Import statement with no indentation")
                else:
                    print(f"   ❌ Line {line_num}: Import has unexpected indentation ({indent} spaces)")
                    return False
            elif stripped.startswith('def '):
                print(f"   ❌ Line {line_num}: Method definition found before class declaration!")
                print(f"      Content: {stripped[:50]}")
                return False
            else:
                print(f"   ⚠️  Line {line_num}: Unexpected content: {stripped[:50]}")
        
        # Check 4: Class definition exists and has correct indentation
        print("\n4. Checking class definition...")
        class_found = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('class FormTab'):
                indent = len(line) - len(line.lstrip())
                if indent == 0:
                    print(f"   ✅ Line {i}: Class FormTab defined with no indentation")
                    class_found = True
                else:
                    print(f"   ❌ Line {i}: Class has unexpected indentation ({indent} spaces)")
                    return False
                break
        
        if not class_found:
            print("   ❌ Class FormTab not found in file")
            return False
        
        # Check 5: Python syntax validation
        print("\n5. Validating Python syntax...")
        try:
            ast.parse(content)
            print("   ✅ Python syntax is valid")
        except SyntaxError as e:
            print(f"   ❌ Syntax error: {e}")
            print(f"      Line {e.lineno}: {e.text}")
            return False
        
        # Check 6: No methods at module level (outside class)
        print("\n6. Checking for methods at module level...")
        tree = ast.parse(content)
        module_level_funcs = [
            node.name for node in ast.walk(tree) 
            if isinstance(node, ast.FunctionDef) and 
            not any(isinstance(parent, ast.ClassDef) 
                   for parent in ast.walk(tree) 
                   if node in ast.walk(parent))
        ]
        
        # Filter out helper functions (those are OK)
        problematic = [f for f in module_level_funcs if f.startswith('_') and not f.startswith('__')]
        
        if problematic:
            print(f"   ⚠️  Found potential private methods at module level: {problematic}")
            print("      (This might be OK if they are helper functions)")
        else:
            print("   ✅ No unexpected methods at module level")
        
        print("\n" + "=" * 60)
        print("✅ ALL VALIDATION CHECKS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_form_tab()
    sys.exit(0 if success else 1)

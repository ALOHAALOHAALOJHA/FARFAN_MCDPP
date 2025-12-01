import os
import py_compile
import sys

def check_syntax(directory):
    print(f"Checking syntax for all Python files in {directory}...")
    errors = []
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                count += 1
                try:
                    py_compile.compile(path, doraise=True)
                except py_compile.PyCompileError as e:
                    print(f"SYNTAX ERROR: {path}")
                    print(e)
                    errors.append(path)
                except Exception as e:
                    print(f"ERROR: {path}: {e}")
                    errors.append(path)
    
    print(f"\nChecked {count} files.")
    if errors:
        print(f"Found {len(errors)} files with syntax errors.")
        sys.exit(1)
    else:
        print("All files passed syntax check.")
        sys.exit(0)

if __name__ == "__main__":
    check_syntax("farfan_core")

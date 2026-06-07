import ast
import sys
from pathlib import Path


def has_assertion(method_body_lines):
    for line in method_body_lines:
        stripped = line.strip()
        if stripped.startswith("self.assert"):
            return True
        if stripped.startswith("with self.assertRaises"):
            return True
        if stripped.startswith("with self.assertRaisesRegex"):
            return True
        if "assert " in stripped or "assert(" in stripped:
            return True
    return False


def main():
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("No tests/ directory found")
        sys.exit(0)

    test_files = sorted(tests_dir.rglob("test_*.py"))
    failures = []

    for filepath in test_files:
        if "__pycache__" in str(filepath):
            continue

        content = filepath.read_text()
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"SYNTAX ERROR in {filepath}: {e}")
            failures.append(str(filepath))
            continue

        lines = content.splitlines()

        for node in ast.walk(tree):
            if not isinstance(node, (ast.ClassDef,)):
                continue
            for item in node.body:
                if not isinstance(
                    item, (ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    continue
                if not item.name.startswith("test_"):
                    continue
                body_lines = lines[item.lineno - 1 : item.end_lineno]
                if not has_assertion(body_lines):
                    failures.append(
                        f"{filepath}::{node.name}::{item.name} (line {item.lineno})"
                    )

    if failures:
        print(f"Found {len(failures)} test(s) without assertions:")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)
    else:
        print("All tests have assertions.")
        sys.exit(0)


if __name__ == "__main__":
    main()

"""Run: python print_app.py
Prints app.py content with line numbers so it can be copy-pasted back
"""
import os

f = os.path.join(os.path.dirname(__file__), 'app.py')
with open(f, encoding='utf-8') as fh:
    content = fh.read()

print(f"=== app.py ({len(content)} chars, {content.count(chr(10))} lines) ===\n")
print(content)
print("\n=== END OF FILE ===")

import os
import re
import hashlib
from collections import defaultdict

def get_python_files(directory):
    """Recursively get all Python files in the directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def read_file_content(file_path):
    """Read the content of a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def normalize_code(code):
    """Normalize code by removing comments, blank lines, and extra whitespace."""
    # Remove comments
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    # Remove blank lines
    code = re.sub(r'\n\s*\n', '\n', code)
    # Normalize whitespace
    code = re.sub(r'\s+', ' ', code)
    return code.strip()

def get_code_blocks(content, min_lines=4):
    """Split content into blocks of code with a minimum number of lines."""
    lines = content.split('\n')
    blocks = []

    for i in range(len(lines) - min_lines + 1):
        block = '\n'.join(lines[i:i+min_lines])
        normalized_block = normalize_code(block)
        if normalized_block:  # Skip empty blocks
            blocks.append((normalized_block, i+1, i+min_lines))

    return blocks

def find_duplicates(directory, min_lines=4, min_tokens=20):
    """Find duplicate code blocks in Python files."""
    python_files = get_python_files(directory)
    block_hashes = defaultdict(list)

    for file_path in python_files:
        content = read_file_content(file_path)
        blocks = get_code_blocks(content, min_lines)

        for block, start_line, end_line in blocks:
            # Skip blocks that are too small (by token count)
            if len(block.split()) < min_tokens:
                continue

            block_hash = hashlib.md5(block.encode()).hexdigest()
            block_hashes[block_hash].append((file_path, block, start_line, end_line))

    # Filter out unique blocks
    duplicates = {h: blocks for h, blocks in block_hashes.items() if len(blocks) > 1}
    return duplicates

def print_duplicates(duplicates):
    """Print duplicate code blocks with their locations."""
    if not duplicates:
        print("No duplicate code blocks found.")
        return

    print(f"Found {len(duplicates)} duplicate code blocks:")
    print("=" * 80)

    for i, (_, blocks) in enumerate(duplicates.items(), 1):
        print(f"Duplicate #{i} (found in {len(blocks)} locations):")

        for j, (file_path, block, start_line, end_line) in enumerate(blocks, 1):
            rel_path = os.path.relpath(file_path)
            print(f"  Location {j}: {rel_path} (lines {start_line}-{end_line})")

        # Print the first instance of the duplicate code
        print("\nCode:")
        print("-" * 40)
        print(blocks[0][1])
        print("-" * 40)
        print()

if __name__ == "__main__":
    import sys

    directory = "backend/src"
    min_lines = 4  # Minimum number of lines to consider a block
    min_tokens = 20  # Minimum number of tokens to consider a block

    if len(sys.argv) > 1:
        directory = sys.argv[1]
    if len(sys.argv) > 2:
        min_lines = int(sys.argv[2])
    if len(sys.argv) > 3:
        min_tokens = int(sys.argv[3])

    print(f"Scanning directory: {directory}")

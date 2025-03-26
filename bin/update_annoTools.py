#!/usr/bin/env python3
import argparse
import os
import sys

def read_tools_file(filename):
    """
    Reads the annoTools file and returns a list of lines without trailing newlines.

    Args:
        filename (str): Path to the annoTools file.

    Returns:
        list of str: Lines from the file with newlines stripped.
    """
    with open(filename, 'r') as f:
        return [line.rstrip('\n') for line in f]

def write_tools_file(filename, lines):
    """
    Writes the given lines back to the annoTools file.

    Args:
        filename (str): Path to the annoTools file.
        lines (list of str): List of lines to write.
    """
    with open(filename, 'w') as f:
        for line in lines:
            f.write(line + '\n')

def main():
    """
    Removes specified tools from the annoTools file and saves the updated file in place.
    Errors out if any of the specified tools are not found in the file.
    """
    parser = argparse.ArgumentParser(
        description="Removes specified tools from annoTools.txt and overwrites the file."
    )
    parser.add_argument('--annoTools', required=True,
                        help='Path to annoTools.txt (will be overwritten)')
    parser.add_argument('--tools_to_remove', required=True,
                        help='Comma-separated list of tool names to remove')

    args = parser.parse_args()
    filename = args.annoTools
    tools_to_remove = args.tools_to_remove.split(',')

    # Check if file exists
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' does not exist.")
        sys.exit(1)

    lines = read_tools_file(filename)

    # Extract existing tools (ignore headers and empty lines)
    tool_lines = [line for line in lines if not line.startswith('#') and line.strip()]

    # Check if all tools to remove are present
    missing = [tool for tool in tools_to_remove if tool not in tool_lines]
    if missing:
        print(f"Error: The following tools were not found in the file: {', '.join(missing)}")
        sys.exit(1)

    # Create filtered content without the tools to remove
    filtered_lines = [
        line for line in lines
        if line.strip() == '' or line.startswith('#') or line not in tools_to_remove
    ]

    write_tools_file(filename, filtered_lines)
    print(f"Successfully removed: {', '.join(tools_to_remove)}")
    print(f"Updated '{filename}'")

if __name__ == '__main__':
    main()

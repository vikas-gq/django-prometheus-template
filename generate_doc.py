import os

def generate_documentation(root_dir, output_file="project_changes.md"):
    """
    Generate Markdown documentation summarizing project structure changes,
    including file contents where applicable.

    Args:
        root_dir (str): The root directory of the project.
        output_file (str): The name of the output Markdown file.
    """
    update_required = []  # Files that need updates (contain "# ...")
    add_required = []     # Files to be added (do not contain "# ...")

    file_contents = {}    # Store file contents to include in the doc

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(file_path, root_dir)  # Relative to root_dir
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "# ..." in content:
                        update_required.append(rel_path)
                    else:
                        add_required.append(rel_path)
                    file_contents[rel_path] = content
            except Exception as e:
                print(f"Could not read {rel_path}: {e}")

    # Write to the Markdown file
    with open(output_file, "w", encoding="utf-8") as md:
        md.write("# Project Structure Changes\n\n")
        md.write("This document summarizes the changes required in the project structure.\n\n")

        if update_required:
            md.write("## Files to Update\n")
            md.write("These files already exist and need to be updated. Contents to be added are included below:\n\n")
            for file in update_required:
                md.write(f"### `{file}`\n")
                md.write("```python\n")
                md.write(file_contents[file])
                md.write("\n```\n\n")

        if add_required:
            md.write("## Files to Add\n")
            md.write("These files need to be created. Suggested contents are included below:\n\n")
            for file in add_required:
                md.write(f"### `{file}`\n")
                md.write("```python\n")
                md.write(file_contents[file])
                md.write("\n```\n\n")

    print(f"Documentation generated at: {output_file}")

# Example usage
if __name__ == "__main__":
    # Replace '.' with your project's root directory if needed
    generate_documentation(root_dir="project_name")

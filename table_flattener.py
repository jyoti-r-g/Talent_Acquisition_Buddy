import re

def flatten_md_tables(input_md_path, output_md_path):
    """
    Flattens all markdown tables in a markdown file into plain comma-separated text.

    Args:
        input_md_path (str): Path to the input markdown file (with tables)
        output_md_path (str): Path to write the flattened markdown file
    """
    with open(input_md_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    output_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check for table header line: line with at least two '|' (to avoid inline code)
        if line.count('|') >= 2 and re.match(r'\s*\|.*\|\s*$', line):
            table_rows = []
            # Continue collecting table lines
            while i < len(lines) and lines[i].count('|') >= 2:
                current = lines[i].strip().strip('|').strip()
                # Skip separator row (---|---)
                if not re.match(r'^:?-+:?\s*(\|:?-+:?\s*)*$', current):
                    # Split on |, trim spaces, join with commas
                    row = ', '.join([cell.strip() for cell in current.split('|')])
                    table_rows.append(row)
                i += 1
            output_lines.extend(table_rows)
        else:
            output_lines.append(line.rstrip('\n'))
            i += 1

    with open(output_md_path, 'w', encoding='utf-8') as outfile:
        for l in output_lines:
            outfile.write(l + '\n')

if __name__ == "__main__":
    flatten_md_tables("job_flat.md", "your_flattened_output.md")

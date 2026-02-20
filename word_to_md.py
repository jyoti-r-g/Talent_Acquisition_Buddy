import os
from spire.doc import Document, FileFormat

def convert_word_to_md(docx_path: str, md_path: str) -> None:
    """
    Converts a Word (.docx) file to a Markdown (.md) file.

    Parameters:
        docx_path (str): Path to the input Word file.
        md_path (str): Path where the output Markdown file will be saved.
    """
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(md_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Created output directory: {output_dir}")

        # Create and load Word document
        document = Document()
        document.LoadFromFile(docx_path)

        # Save as Markdown
        document.SaveToFile(md_path, FileFormat.Markdown)

        # Clean up
        document.Dispose()
        print(f"✅ Successfully converted '{docx_path}' to '{md_path}'.")

    except Exception as e:
        print(f" save image during Word to Markdown conversion: {e}")



if __name__ == "__main__":
    word_file = "DS_1_Tyler_n.docx"
    md_file = "output/ToMarkdown.md"
    convert_word_to_md(word_file, md_file)

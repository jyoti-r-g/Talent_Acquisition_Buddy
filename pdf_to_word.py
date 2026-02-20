# from pdf2docx import Converter

# def convert_pdf_to_word(pdf_path: str, docx_path: str) -> None:
#     """
#     Converts a PDF file to a Word (.docx) file.

#     Parameters:
#         pdf_path (str): Path to the input PDF file.
#         docx_path (str): Path where the output Word file will be saved.
#     """
#     try:
#         # Create a converter object
#         cv = Converter(pdf_path)

#         # Convert the entire PDF to Word
#         cv.convert(docx_path, start=0, end=None)

#         # Close the converter
#         cv.close()

#         print(f"✅ Successfully converted '{pdf_path}' to '{docx_path}'.")

#     except Exception as e:
#         print(f"❌ Error during PDF to Word conversion: {e}")

# if __name__ == "__main__":
#     pdf_file = "Jyoti_Gund_DS_DA.pdf"
#     word_file = "output/Jyoti_Gund_DS_DA.docx"
#     convert_pdf_to_word(pdf_file, word_file)


import os
from pdf2docx import Converter

def convert_pdf_to_word(pdf_path: str, docx_path: str) -> None:
    """
    Converts a PDF file to a Word (.docx) file.

    Parameters:
        pdf_path (str): Path to the input PDF file.
        docx_path (str): Path where the output Word file will be saved.
    """
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(docx_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Created output directory: {output_dir}")

        # Create a converter object
        cv = Converter(pdf_path)

        # Convert the entire PDF to Word
        cv.convert(docx_path, start=0, end=None)

        # Close the converter
        cv.close()

        print(f"✅ Successfully converted '{pdf_path}' to '{docx_path}'.")

    except Exception as e:
        print(f"❌ Error during PDF to Word conversion: {e}")


if __name__ == "__main__":
    pdf_file = "DS_1_Tyler.pdf"
    word_file = "output/DS_1_Tyler_n.docx"
    convert_pdf_to_word(pdf_file, word_file)

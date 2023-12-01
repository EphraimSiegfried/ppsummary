from pathlib import Path
import sys
import subprocess


def convert_md_to_pdf(md_file_path: Path):
    pdf_file_path = Path(md_file_path.stem + ".pdf")
    if pdf_file_path.exists():
        pdf_file_path.unlink()
    subprocess.run(["pandoc", md_file_path, "-o", pdf_file_path])


def upload(file_path):
    pass


def main():
    md_file_path = Path(sys.argv[1])
    pdf_file_path = convert_md_to_pdf(md_file_path)
    upload(pdf_file_path)


if __name__ == "__main__":
    main()

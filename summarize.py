from pathlib import Path
import sys
import os
from PyPDF2 import PdfReader
import openai

SUMMARY_PATH = Path("./Zusammenfassung/Zusammenfassung.tex")


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def summarize(text, job):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    completion = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": job},
            {
                "role": "user",
                "content": text,
            },
        ],
    )
    return "\n" + completion.choices[0].message.content


def update_latex(summary, latex_file):
    with open(latex_file, "r") as f:
        latex_content = f.readlines()
    insert_index = len(latex_content) - 2
    latex_content.insert(insert_index, f"\n{summary}\n")
    with open(latex_file, "w") as f:
        f.writelines(latex_content)


def summarize_all(job):
    for handout_path in sorted(Path("../Handouts").iterdir()):
        if handout_path.suffix == ".pdf":
            print(handout_path)
            text = extract_text_from_pdf(handout_path)
            summary = summarize(job, text)
            update_latex(summary, SUMMARY_PATH)
            if input("continue?") != "y":
                return


def main():
    file_path = Path(sys.argv[1])
    text = extract_text_from_pdf(file_path)
    with open("job.txt", "r") as f:
        job = f.read()

    # summarize_all(job)

    summary = summarize(text, job)
    update_latex(
        summary,
        SUMMARY_PATH,
    )


if __name__ == "__main__":
    main()

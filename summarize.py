from pathlib import Path
import sys
import os
from PyPDF2 import PdfReader
import openai
import re


def update_toc(md_content):
    lines = md_content.split("\n")
    toc = []
    for line in lines:
        match = re.match(r"^(#+) (.+)$", line)
        if match:
            level, title = len(match.group(1)), match.group(2)
            toc.append(
                f"{'  ' * (level - 1)}- [{title}](#{title.lower().replace(' ', '-')})"
            )
    return "\n".join(toc)


def get_lecture_num_and_title(file_path):
    match = re.search(r"^VL[ _](\d)[ _]([a-z A-Z?_]*)", file_path.stem)
    lecture_title = ""
    lecture_number = -1
    if match:
        lecture_number = int(match.group(1))
        lecture_title = match.group(2).replace("_", " ").strip()
    return lecture_number, lecture_title


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def get_text_sections(text):
    regex_pattern = r"(?<=\n)[IVXLCDM]+\. ([\s\S]*?)(?=\n[IVXLCDM]+\.)"
    matches = re.findall(regex_pattern, text, re.MULTILINE)
    return matches


def summarize(text):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    job = r"""
Sie sind ein Experte für das Zusammenfassen philosophischer Texte. Ihre Aufgabe ist es, einen bereitgestellten Text im LaTeX-Format auf Deutsch kurz und prägnant zusammenzufassen. 
Der Text wird in einer schon existierenden Latex Datei eingefügt.

1. Beginnen Sie mit einer Unterabschnittsüberschrift (\subsection) für den Titel des Textes. Im Titel soll nur der Titel vorkommen, der auch im gegeben Text gebraucht wurde, ohne Zusatz.
2. Erstellen Sie eine Aufzählungsliste, um die wichtigsten Konzepte im Text zu identifizieren.
3. Für jeden Listenpunkt bieten Sie eine prägnante, aber umfassende Erklärung des Konzepts an.

Zum Beispiel:

\subsection{Texttitel}

\begin{itemize}
  \item \textbf{Konzept 1}: Erklärung von Konzept 1.
  \item \textbf{Konzept 2}: Erklärung von Konzept 2.
  \item \textbf{Konzept 3}: Erklärung von Konzept 3.
\end{itemize}
"""

    completion = openai.ChatCompletion.create(
        model="gpt-4",
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


def update_pdf(summary):
    summary_path = "./Zusammenfassung_Praktische_Philosophie.md"
    # Read existing content, skipping the old TOC
    skip_toc = False
    content = ""
    with open(summary_path, "r") as f:
        for line in f:
            if line.strip() == "<!-- TOC_END -->":
                skip_toc = False
            if not skip_toc:
                content += line
            if line.strip() == "<!-- TOC_START -->":
                skip_toc = True

    # Generate new TOC based on original content
    if content:
        toc = update_toc(content + summary)
    else:
        toc = update_toc(summary)

    # Write new TOC and append new summary
    with open(summary_path, "w") as f:
        f.write(
            f"<!-- TOC_START -->\n# Inhaltsverzeichnis\n\n{toc}\n<!-- TOC_END -->\n\n{content}\n{summary}"
        )
        # Get path to handout from CLI


def main():
    file_path = Path(sys.argv[1])
    text = extract_text_from_pdf(file_path)
    sections = get_text_sections(text)
    lecture_number, lecture_title = get_lecture_num_and_title(file_path)
    summary = ""
    for section in sections:
        section_summary = summarize(section)
        summary += "\n" + section_summary
    update_latex(
        f"\\section{ {lecture_title} }\n{summary}",
        Path("./Zusammenfassung/Zusammenfassung.tex"),
    )


if __name__ == "__main__":
    main()

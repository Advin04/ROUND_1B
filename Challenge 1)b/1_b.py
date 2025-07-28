import os
import json
import re
import time
import datetime
from pathlib import Path
from collections import Counter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

def extract_text_and_metadata(pdf_path):
    text_blocks_with_fonts = []
    try:
        for page_layout in extract_pages(pdf_path):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        if hasattr(text_line, "_objs"):
                            font_sizes = [obj.size for obj in text_line._objs if isinstance(obj, LTChar)]
                            if font_sizes:
                                avg_font_size = sum(font_sizes) / len(font_sizes)
                                text = text_line.get_text().strip()
                                if text:
                                    x0, y0, x1, y1 = text_line.bbox
                                    text_blocks_with_fonts.append({
                                        "text": text,
                                        "font_size": avg_font_size,
                                        "x0": x0,
                                        "y0": y0,
                                        "x1": x1,
                                        "y1": y1,
                                    })
    except Exception as e:
        print(f"Error extracting from {pdf_path}: {e}")
        return []
    return text_blocks_with_fonts

def get_title(text_blocks):
    title_candidates = [b for b in text_blocks if b.get("y0", float('inf')) < 150]
    if not title_candidates:
        title_candidates = text_blocks
    if not title_candidates:
        return ""
    title_candidates.sort(key=lambda x: x["font_size"], reverse=True)
    top_title = title_candidates[0]["text"]
    if len(top_title.split()) > 2 and len(top_title) > 10:
        return top_title
    return top_title

def tag_headings(text_blocks):
    font_sizes = [block["font_size"] for block in text_blocks]
    if not font_sizes:
        return []

    size_counts = Counter(font_sizes)
    most_common_size = size_counts.most_common(1)[0][0]

    heading_sizes = sorted(list(set([size for size in size_counts if size > most_common_size + 1])), reverse=True)

    size_to_tag = {size: f"H{i+1}" for i, size in enumerate(heading_sizes[:3])}

    tagged_headings = []
    for block in text_blocks:
        tag = "BodyText"
        if block["font_size"] in size_to_tag:
            tag = size_to_tag[block["font_size"]]
        elif block["font_size"] > most_common_size + 1:
            pass

        if tag != "BodyText" and len(block["text"].strip()) > 3:
            tagged_headings.append({
                "text": block["text"],
                "tag": tag,
                "font_size": block["font_size"]
            })
    return tagged_headings

def rank_sections(sections, persona, job):
    persona_keywords = [w for w in re.findall(r'\w+', persona.lower()) if len(w) > 2]
    job_keywords = [w for w in re.findall(r'\w+', job.lower()) if len(w) > 2]

    ranked = []
    for sec in sections:
        score = 0
        text_lower = sec["section_title"].lower()
        for w in job_keywords:
            if w in text_lower:
                score += 2
        for w in persona_keywords:
            if w in text_lower:
                score += 1
        ranked.append({**sec, "importance_rank": -score})

    ranked.sort(key=lambda x: x["importance_rank"])
    for i, r in enumerate(ranked, 1):
        r["importance_rank"] = i
    return ranked

def process_pdf_1b(pdf_path):
    text_blocks = extract_text_and_metadata(pdf_path)
    if not text_blocks:
        return None

    title = get_title(text_blocks)
    headings = tag_headings(text_blocks)

    processed_headings = []
    for h in headings:
        processed_headings.append({
            "document": os.path.basename(pdf_path),
            "page_number": 1,
            "section_title": h["text"],
            "font_size": h["font_size"]
        })

    return {
        "title": title,
        "headings": processed_headings
    }

def run_1b(input_dir="sample pdfs", persona="Investment Analyst", job="Analyze revenue trends", output_dir="./app/output"):

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    pdf_files = list(Path(input_dir).glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {input_dir}")
        return

    all_sections = []
    input_documents = []
    for pdf_path in pdf_files:
        print(f"Processing PDF: {pdf_path.name}")
        pdf_data = process_pdf_1b(pdf_path)
        if pdf_data is not None:
            input_documents.append(pdf_path.name)
            all_sections.extend(pdf_data["headings"])

    ranked_sections = rank_sections(sections=all_sections, persona=persona, job=job)

    output_json = {
        "input_documents": input_documents,
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "extracted_sections": ranked_sections,
    }

    output_path = Path(output_dir) / "output_1b.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2, ensure_ascii=False)
    print(f"Round 1B output written to: {output_path}")

# Example usage:
run_1b()


# import os
# import json
# from pdfminer.high_level import extract_pages
# from pdfminer.layout import LTTextContainer, LTChar, LTAnno, LTFigure

# def get_title(text_blocks_with_fonts):
#     """
#     Get the text block with the highest average font size assuming it's the title.
#     """
#     if not text_blocks_with_fonts:
#         return ""

#     title_candidates = [b for b in text_blocks_with_fonts if b.get("y", float('inf')) < 150]
#     if not title_candidates:
#          title_candidates = text_blocks_with_fonts

#     title_candidates.sort(key=lambda x: x["font_size"], reverse=True)
#     if title_candidates:
#         potential_title = title_candidates[0]["text"]
#         if len(potential_title.split()) > 2 and len(potential_title) > 10:
#              return potential_title
#         return potential_title
#     return ""

# def tag_headings(text_blocks_with_fonts):
#     """
#     Tag headings based on font size ranks.
#     """
#     font_sizes = [block["font_size"] for block in text_blocks_with_fonts]
#     if not font_sizes:
#         return []

#     from collections import Counter
#     size_counts = Counter(font_sizes)
#     if not size_counts:
#         return []

#     most_common_size = size_counts.most_common(1)[0][0]
#     heading_sizes = sorted(list(set([size for size in size_counts if size > most_common_size + 1])), reverse=True)

#     size_to_tag = {}
#     for i, size in enumerate(heading_sizes[:3]):
#         tag = f"H{i + 1}"
#         size_to_tag[size] = tag

#     tagged_headings = []
#     for block in text_blocks_with_fonts:
#         tag = "BodyText"
#         if block["font_size"] in size_to_tag:
#             tag = size_to_tag[block["font_size"]]
#         elif block["font_size"] > most_common_size + 1:
#              pass

#         if tag != "BodyText":
#              tagged_headings.append({
#                 "text": block["text"],
#                 "tag": tag,
#                 "font_size": block["font_size"]
#             })

#     filtered_headings = [h for h in tagged_headings if len(h['text'].strip()) > 3]
#     return filtered_headings

# def extract_text_and_metadata(pdf_path):
#     text_blocks_with_fonts = []
#     try:
#         for page_layout in extract_pages(pdf_path):
#             for element in page_layout:
#                 if isinstance(element, LTTextContainer):
#                     for text_line in element:
#                         if hasattr(text_line, "_objs"):
#                             font_sizes = []
#                             for obj in text_line._objs:
#                                 if isinstance(obj, LTChar):
#                                     font_sizes.append(obj.size)
#                             if font_sizes:
#                                 avg_font_size = sum(font_sizes) / len(font_sizes)
#                                 text = text_line.get_text().strip()
#                                 if text:
#                                     x0, y0, x1, y1 = text_line.bbox
#                                     text_blocks_with_fonts.append({
#                                         "text": text,
#                                         "font_size": avg_font_size,
#                                         "x": x0,
#                                         "y": y0,
#                                         "bbox": text_line.bbox
#                                     })
#     except Exception as e:
#         print(f"Error extracting text and metadata from {pdf_path}: {e}")
#         return []

#     return text_blocks_with_fonts

# def process_pdf(pdf_path):
#     text_blocks_with_fonts = extract_text_and_metadata(pdf_path)
#     if not text_blocks_with_fonts:
#         print(f"No text extracted from {pdf_path}. Skipping.")
#         return {
#             "file_name": os.path.basename(pdf_path),
#             "title": "Could not extract title",
#             "headings": []
#         }

#     title = get_title(text_blocks_with_fonts)
#     tagged_headings = tag_headings(text_blocks_with_fonts)

#     return {
#         "file_name": os.path.basename(pdf_path),
#         "title": title,
#         "headings": tagged_headings
#     }

# def process_all_pdfs_in_folder(folder_path):
#     results = []
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
#         print(f"Created directory: {folder_path}")
#     else:
#          print(f"Processing files in existing directory: {folder_path}")

#     pdf_files_in_folder = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
#     if not pdf_files_in_folder:
#         print(f"No PDF files found in '{folder_path}'. Please place PDFs in this folder.")
#         return []

#     for filename in pdf_files_in_folder:
#         pdf_path = os.path.join(folder_path, filename)
#         print(f"Processing PDF: {filename}")
#         result = process_pdf(pdf_path)
#         results.append(result)
#         print(f"  -> Extracted Title: {result.get('title', 'N/A')}")
#         print(f"  -> Found {len(result.get('headings', []))} potential headings.")

#     return results

# if __name__ == "__main__":
#     folder_path = "pdfs"
#     output_filename = "round1_output.json"
#     print("Starting PDF processing...")

#     output_dir = os.path.dirname(output_filename)
#     if output_dir and not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#         print(f"Created output directory: {output_dir}")

#     results = process_all_pdfs_in_folder(folder_path)
#     if results:
#         with open(output_filename, "w", encoding="utf-8") as f:
#             json.dump(results, f, indent=2, ensure_ascii=False)
#         print(f"\nProcessing complete. Results written to {output_filename}")
#     else:
#         print("\nNo results to write. No PDFs were processed.")

#     print("Script finished.")


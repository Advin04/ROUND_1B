# ROUND_1B
hallenge 1B: Persona-Driven Section Extraction
📋 Overview
Ranks and extracts the most relevant sections from multiple PDFs according to a specified persona (user type) and job-to-be-done (user goal). Fulfills the Challenge 1B "smart reader" requirements for automated content prioritization.

🛠️ Approach
📥 Extraction
Extracts all potential headings/sections per document using advanced font/position/content rules (inherits 1A's logic).

🤖 Persona & Job Ranking
Accepts persona and job as input (e.g., "Home Cook" and "Find an easy dinner recipe").

Uses keyword matching to score section relevance: job terms weighted highest, followed by persona terms.

Outputs sections sorted by combined importance.

🛠️ Output
Consolidates results from all PDFs into one easy-to-parse JSON, with all metadata and ranked results.

🚀 How to Run
Prerequisites
Python 3.7+

pdfminer.six (for text extraction; adjust if using a different library).

Usage
Place your PDFs in an input/ directory.

Edit the persona and job variables in the script:

python
persona = "Meal Planner"
job = "Plan a weeknight family dinner"
Run the script (no args needed):

python
python persona_extraction.py
Results are written as output_1b.json in the same directory.

🗂️ Output Format
json
{
  "input_documents": ["Dinner Ideas.pdf", "Lunch Ideas.pdf"],
  "persona": "Meal Planner",
  "job_to_be_done": "Plan a weeknight family dinner",
  "processing_timestamp": "2025-07-28 21:00:00",
  "extracted_sections": [
    {
      "document": "Dinner Ideas.pdf",
      "page_number": 1,
      "section_title": "Quick Pasta Recipes",
      "importance_rank": 1
    },
    ...
  ]
}
💡 Features
No network/API dependencies—works offline and on CPU only.

Fast: Processes up to 10 PDFs in a few minutes.

Output is one easy-to-grade JSON file, sorted by relevance.

🚀 Extensibility
Swap in semantic (word embedding) matching for smarter relevance ranking.

Tune scoring or add rules for extra personas/jobs as needed.

Add support for multi-page headings and more detailed extraction.

⚡ Constraints
Works within 10-minute, 16GB memory, and CPU-only challenge restrictions.

All code and results are self-contained for easy review and reproduction.

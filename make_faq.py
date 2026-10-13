"""
make_faq.py - Turn the Makerspace question log (CSV) into a chatbot FAQ file.

Runs entirely on your own computer. Nothing is uploaded anywhere.
Only Python 3 is needed (no extra packages).

1) See which columns your CSV has:
       python make_faq.py questions.csv --list

2) Build the FAQ, naming the question and answer columns:
       python make_faq.py questions.csv --q "Question" --a "Answer"

   Output:
       faq_review.csv  -> open in Excel, check every row, fix or delete rows
       faq.js          -> paste its contents into the website

3) After editing faq_review.csv, rebuild faq.js from your edited version:
       python make_faq.py faq_review.csv --q question --a answer --from-review
"""

import argparse
import csv
import json
import re
import sys

# Patterns that look like personal information. Matches are replaced with a tag.
PII_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    (re.compile(r"\bR\d{8}\b", re.IGNORECASE), "[student ID]"),            # TTU R-number
    (re.compile(r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b"), "[ID number]"),       # SSN-like
    (re.compile(r"(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[phone]"),
    (re.compile(r"\bFOP\s*#?\s*[:\-]?\s*[A-Z0-9-]{4,}\b", re.IGNORECASE), "FOP [number]"),
    (re.compile(r"\b\d{6,}\b"), "[number]"),                                # long numbers (order IDs, cards)
]

# Greetings and sign-offs that usually carry a name, e.g. "Hi Masaki," or "Thanks, John"
GREETING = re.compile(r"^\s*(hi|hello|hey|dear|good (morning|afternoon|evening))\b[^,!.\n]{0,30}[,!.]?\s*", re.IGNORECASE)
SIGNOFF = re.compile(r"\s*\b(thanks|thank you|best|regards|best regards|sincerely|cheers)\b[,!.]?\s*[^,!.\n]{0,40}$", re.IGNORECASE)


def scrub(text: str, extra_names: list[str]) -> str:
    text = text or ""
    text = GREETING.sub("", text)
    text = SIGNOFF.sub("", text)
    for pattern, tag in PII_PATTERNS:
        text = pattern.sub(tag, text)
    for name in extra_names:
        if name:
            text = re.sub(rf"\b{re.escape(name)}\b", "[name]", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


TAG = re.compile(r"\[(email|student ID|ID number|phone|number|name)\]")
# Capitalized words that are normal in Makerspace questions, so they are not flagged as names
KNOWN_WORDS = set("""
I I'm I'd I've ABS PLA TPU FOP TTU Texas Tech University Library Makerspace Room Cricut Ultimaker UltiMaker KISSlicer
Polyprinter PolyPrinter U3 US7 STL Janome JANOME Kenmore Brother Monday Tuesday Wednesday Thursday Friday Saturday Sunday
January February March April May June July August September October November December Can Do Does Is Are What When Where
How Why Who Which Could Would Should Will Hi Hello Thanks Thank Please Yes No OK Ok Also And But The A An If My We Our
You Your It Its This That There They Their Is Hey Dear
""".split())


def flag_reason(q: str, a: str) -> str:
    reasons = []
    if TAG.search(q) or TAG.search(a):
        reasons.append("hidden info, check wording")
    words = re.findall(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}\b", f"{q} {a}")
    names = [w for w in words if w not in KNOWN_WORDS]
    if names:
        reasons.append("possible name: " + ", ".join(sorted(set(names))[:5]))
    return "; ".join(reasons)


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def load_rows(path, sheet=None):
    """Return (columns, rows as dicts) from a .csv or .xlsx file."""
    if path.lower().endswith((".xlsx", ".xlsm")):
        try:
            import openpyxl
        except ImportError:
            sys.exit("To read Excel files, first run:  pip install openpyxl\n"
                     "(or save the sheet as 'CSV UTF-8' in Excel and use the .csv file)")
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        it = ws.iter_rows(values_only=True)
        header = [str(h).strip() if h is not None else "" for h in next(it, [])]
        rows = []
        for vals in it:
            if vals is None or all(v is None for v in vals):
                continue
            rows.append({h: ("" if v is None else str(v)) for h, v in zip(header, vals)})
        return header, rows
    # utf-8-sig handles files saved from Excel
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def main():
    p = argparse.ArgumentParser(description="Build a privacy-scrubbed FAQ from a CSV question log.")
    p.add_argument("csv_path")
    p.add_argument("--list", action="store_true", help="show column names and exit")
    p.add_argument("--q", help="question column name")
    p.add_argument("--a", help="answer column name (optional)")
    p.add_argument("--details", help="column with extra detail to append to the question (optional)")
    p.add_argument("--name-cols", default="", help="comma-separated columns holding people's names, used only to scrub those names from the text")
    p.add_argument("--from-review", action="store_true", help="input is an edited faq_review.csv; skip scrubbing")
    p.add_argument("--sheet", help="Excel sheet name (default: first sheet)")
    args = p.parse_args()

    cols, records = load_rows(args.csv_path, args.sheet)
    if args.list:
        print("Columns:", ", ".join(cols))
        return
    if not args.q or args.q not in cols:
        sys.exit(f"Question column not found. Available columns: {', '.join(cols)}")
    if args.a and args.a not in cols:
        sys.exit(f"Answer column not found. Available columns: {', '.join(cols)}")
    if args.details and args.details not in cols:
        sys.exit(f"Details column not found. Available columns: {', '.join(cols)}")
    name_cols = [c.strip() for c in args.name_cols.split(",") if c.strip()]

    rows, index = [], {}
    for r in records:
        # Only the question/answer columns are kept. Names are read only to remove them.
        names = []
        for c in name_cols:
            names += (r.get(c) or "").split()
        q = (r.get(args.q) or "").strip()
        a = (r.get(args.a) or "").strip() if args.a else ""
        d = (r.get(args.details) or "").strip() if args.details else ""
        if not args.from_review:
            q, a, d = scrub(q, names), scrub(a, names), scrub(d, names)
        key = norm(q) or norm(d)  # duplicates are matched on the question alone
        if d and d.lower() != q.lower():
            q = f"{q} ({d})" if q else d
        if not q:
            continue
        if key in index:  # same question again (ignoring case and punctuation)
            row = index[key]
            row["times_asked"] += 1
            if not row["answer"] and a:
                row["answer"] = a
            continue
        row = {"question": q, "answer": a, "times_asked": 1}
        index[key] = row
        rows.append(row)

    if not args.from_review:
        for row in rows:
            row["check"] = flag_reason(row["question"], row["answer"])
        # Rows to check first, then the most asked questions
        rows.sort(key=lambda r: (r["check"] == "", -r["times_asked"]))
        with open("faq_review.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["check", "times_asked", "question", "answer"])
            w.writeheader()
            w.writerows(rows)

    faq = [{"q": r["question"], "a": r["answer"]} for r in rows if r["answer"]]
    with open("faq.js", "w", encoding="utf-8") as f:
        f.write("/* Common questions from the Makerspace question log. */\n")
        f.write("var MAKERSPACE_FAQ = [\n")
        f.write(",\n".join(json.dumps(x, ensure_ascii=True) for x in faq))
        f.write("\n];\n")

    missing = sum(1 for r in rows if not r["answer"])
    flagged = sum(1 for r in rows if r.get("check"))
    print(f"{len(records)} rows read, {len(rows)} unique questions.")
    if not args.from_review:
        print(f"Wrote faq_review.csv. {flagged} rows are flagged in the 'check' column and listed first: review those carefully.")
    print(f"Wrote faq.js with {len(faq)} Q&A pairs.")
    if missing:
        print(f"{missing} questions have no answer and were left out of faq.js. Add answers in faq_review.csv, then rerun with --from-review.")


if __name__ == "__main__":
    main()

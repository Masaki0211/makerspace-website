# TTU Library Makerspace Website

Front-desk kiosk website for the Texas Tech University Library Makerspace.

**Live site:** https://masaki0211.github.io/makerspace-website/

> **Note — this is a privacy-redacted public version.**
> The real kiosk version runs with the full FAQ data and works as intended.
> The source data (`questions.csv`, `faq_review.csv`, a log of real patron questions) and
> the FAQ entries extracted from it (`MAKERSPACE_FAQ` in `index.html` / `faq.js`) contain
> personal information, so they were removed from this repository.
> Because of this, the chatbot on the live site can only give **fixed answers** —
> see [Chatbot](#chatbot) below.

## Run locally
Just open `index.html` in a browser, or on Windows double-click `start_kiosk.bat`
(starts a local web server and opens Chrome/Edge in kiosk mode).

## Chatbot
The assistant has two modes:

| Mode | When | How it answers |
|---|---|---|
| **AI answers** | [Ollama](https://ollama.com) is running on the same computer (`ollama pull qwen2.5:3b`) | An open model writes an answer using the site info and FAQ |
| **Basic answers** | Ollama is not running (e.g. the live GitHub Pages site) | Picks the single best-matching sentence from the page content and built-in facts. It does not write new text; if nothing matches it suggests emailing make@ttu.edu |

In this public repo the FAQ list is empty, so basic answers come only from the page
content and built-in facts. Questions that were answered from the question-log FAQ in
the real version may get "not sure" here.

## FAQ data
To rebuild the FAQ locally from your own question log:

```
python make_faq.py questions.csv --list
```

Spreadsheet files (`*.csv`, `*.xlsx`) are ignored by git.

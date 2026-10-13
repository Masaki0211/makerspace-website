# TTU Library Makerspace Website

Front-desk kiosk website for the Texas Tech University Library Makerspace.

**Live site:** https://masaki0211.github.io/makerspace-website/

## Run locally
Just open `index.html` in a browser, or on Windows double-click `start_kiosk.bat`
(starts a local web server and opens Chrome/Edge in kiosk mode).

## Assistant
The chat assistant uses [Ollama](https://ollama.com) running on the same computer
(`ollama pull qwen2.5:3b`). If Ollama is not running (e.g. on the live GitHub Pages site),
it falls back to basic built-in answers.

## FAQ data
The FAQ list (`MAKERSPACE_FAQ` in `index.html` / `faq.js`) is empty in this public repo
because the source question log contains private information.
To rebuild it locally from your own log:

```
python make_faq.py questions.csv --list
```

Spreadsheet files (`*.csv`, `*.xlsx`) are ignored by git.

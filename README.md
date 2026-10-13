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

---

### 한국어 안내
이 저장소는 **개인정보를 제거한 공개용 버전**입니다. 실제 키오스크 버전은 정상적으로 잘 작동하지만,
원본 데이터인 CSV(실제 이용자 질문 로그)와 그 CSV에서 추출해 코드에 넣은 FAQ 데이터(`MAKERSPACE_FAQ`)에
개인정보가 포함되어 있어 삭제했습니다. 그래서 공개 사이트의 챗봇은 AI가 아닌 기본 모드로 동작하며,
웹페이지 안내문과 미리 넣어둔 정보 중 질문과 가장 잘 맞는 **정해진 답**만 보여줍니다.

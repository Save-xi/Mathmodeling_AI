# Chinese contest-paper LaTeX delivery

Use this reference when the requested deliverable includes a contest-paper section, a complete paper, LaTeX source, or a compiled PDF. Keep all modeling, validation, and evidence requirements from the main skill; this file governs only the writing and typesetting workflow.

## Source priority and scope

1. Read the current-year official contest instructions and supplied paper template first. For CUMCM, inspect the current project directory and any local archive under `$env:CSM_WORKSPACE\official\CUMCM\<year>` together with [cumcm-official.md](cumcm-official.md), then verify stale or missing items against `mcm.edu.cn` outside the contest window. Their class file, page limit, anonymity rule, title block, bibliography style, and disclosure requirements override local defaults. A school training plan or prior-year format file does not.
2. If no official LaTeX class is supplied, use UTF-8 source with XeLaTeX and `ctexart`. The default handoff is `.tex` plus compiled PDF. Do not switch to Word merely because the rules permit it; create DOC/DOCX only on an explicit user request or when PDF is disallowed.
3. Match the user's requested scope. A request for one question or a partial paper does not authorize invented results for later questions. Label omitted sections or leave them outside the deliverable rather than fabricating continuity.
4. Freeze facts, assumptions, canonical results, and the claim-to-evidence map before polishing prose. Write the abstract last.

## Deliverable contract

Adapt to an existing project rather than forcing new paths. For a new project, prefer:

```text
paper/
  main.tex
  output/main.pdf
results/
  figures/
  tables/
  logs/
docs/
  evidence_map.md
  qa_report.md
```

Retain the `.tex`, final PDF, referenced figures/tables, canonical numeric results, concise build log, and evidence map. Clean disposable render images, auxiliary files, and temporary extraction directories after acceptance.

## Paper architecture

Follow official headings; the fallback contest-paper spine is defined once in [writing-evidence.md](writing-evidence.md). Keep each question recognizable. In CUMCM, the abstract is a dedicated first page and the body begins on the next page. Include actual complete source programs/shared modules and necessary interactive commands in the appendix when required; an archive file list does not replace source-code inclusion.

## Source-writing rules

- Use semantic LaTeX: `\section`, `\subsection`, `equation`/`align`, `table`, `figure`, `\label`, and `\ref`. Do not simulate structure with manual spaces or line breaks.
- Define each symbol once and keep notation, subscripts, units, domains, and objective direction consistent with code and tables.
- Load only needed packages. A stable generic set is `amsmath`, `amssymb`, `bm`, `booktabs`, `tabularx`, `array`, `graphicx`, `float`, `caption`, and `hyperref`.
- Keep the source portable. Do not hard-code machine-specific absolute paths. Reference figures relative to `paper/main.tex`.
- Use machine-readable result files as the source of truth. If values are inserted manually, reconcile every important number against `docs/evidence_map.md` before delivery.
- Use one precision rule per metric, put units in headers or symbol definitions, and state scenario, seed, split, threshold, or confidence conditions beside the result.
- Do not add a table of contents, decorative cover, institution, author identity, or acknowledgements unless the contest rules require or permit them.
- Keep the electronic-paper source free of the paper commitment and numbering pages when the current rules exclude them. Implement required AI-use declarations in LaTeX at the exact location specified by the current rules.

## Figures, tables, and floats

- Place a question-specific figure or table after the paragraph that introduces it. Use `[H]` selectively when a float must stay with that question; otherwise prefer normal LaTeX placement.
- Avoid float backlogs that move a result into the next question. Check section boundaries after every substantial edit.
- Use `booktabs` and concise headers. Use `tabularx` for width control; use `longtable` only when a table truly spans pages.
- Never shrink a dense figure until labels become unreadable. Regenerate, split, crop, or move detail to an appendix.
- Captions must state what is shown, the relevant condition, and the conclusion the reader may draw. Do not make a stronger claim than the plotted evidence.
- Inspect Chinese glyphs, legends, axis labels, equation numbers, cross-references, page density, stranded headings, and split tables visually.

## Build and QA loop

Use the installed helper from any working directory. It reads the declared submission paths, builds in a fresh subdirectory, parses the PDF and checks material warnings before replacing its own previous output:

```powershell
$modelingSkill = Join-Path $HOME ".codex\skills\mathmodeling"
python -X utf8 "$modelingSkill\scripts\build_paper.py" "<project-dir>" --timeout 300
```

In auto mode the helper uses repeated XeLaTeX plus needed BibTeX/Biber on Windows, and prefers latexmk elsewhere with the same direct fallback. `--engine xelatex` or `--engine latexmk` explicitly selects a backend. PDF validation needs pypdf or Poppler pdfinfo. It disables shell escape, captures project-local dependencies using `.fls` plus the bibliography declarations in `.aux`/`.bcf`, and writes a build receipt beside the PDF. A failed process, unresolved reference/citation or missing glyph must not cause an old PDF to be copied as this build's output.

## Layout warnings, page limit and anonymity

Content-level faults and layout faults are handled differently, because an ordinary wide Chinese table overflows by tens of points and aborting the whole build on that costs the source-to-PDF receipt exactly when it matters most.

- Missing glyphs, undefined references/citations, multiply-defined labels and fontspec errors **fail the build**. Nothing is delivered. This detection reads the build log, so a class file or preamble that sets `\tracinglostchars=0` suppresses the `Missing character` lines and the build then passes with the glyphs silently dropped from the PDF. When you adopt an official class file, check it does not lower that setting, and keep the rendered-page inspection.
- `Overfull` boxes and oversized floats are **recorded in the receipt**, split by measured magnitude: at or above `--layout-threshold` (default 5.0 pt), plus every `Float too large` and every unmeasurable overflow, go to `warnings`, which the structural audit reports as `BUILD_WARNINGS` (MAJOR); smaller overflows go to `minor_warnings`, reported as `BUILD_MINOR_WARNINGS` (MINOR). `Underfull` boxes are always minor regardless of badness — they are loose spacing, never lost content. Recorded is not resolved — open the rendered pages and either fix the float or record the visual verdict in `docs/qa_report.md`.
- `--strict-layout` restores the old all-or-nothing behaviour for a team that intends to clear every box.
- An existing PDF without this tool's receipt is still refused by default. `--replace-unowned` takes that path over after copying the old file to `<name>.bak-<UTC timestamp>.pdf`; the receipt records the backup path. Use it to return to the automated build after a hand-published PDF, not to overwrite a frozen submission.
- `--keep-builds N` prunes older disposable `paper/build/run-*` directories, keeping the newest N (default 5).

Two disqualification-class rules can be machine-checked once declared in `mathmodeling.json`. Both fields are optional and are deliberately **not** created by `init_project.py`, so existing projects keep validating unchanged; add them by hand from the current year's official rules:

```json
"submission": {
  "source": "paper/main.tex",
  "pdf": "paper/output/main.pdf",
  "page_limit": 30,
  "anonymity": true
}
```

`page_limit` makes the audit report `PAGE_LIMIT_EXCEEDED` (BLOCKER) when the PDF has more pages, and `anonymity` makes it report `PDF_IDENTITY_METADATA` (BLOCKER) when the PDF's `/Author`, `/Title`, `/Subject` or `/Keywords` document properties are non-empty. Take the limit from the current-year rule rather than this example, and confirm what the limit counts: the 2026 CUMCM 30-page cap applies to the main text, so a project whose appendix is inside the same PDF needs its own declared number. Declare **both** fields: each one only switches on its own check, so declaring `page_limit` alone leaves anonymity unverified. Whatever is left undeclared is named in `SUBMISSION_LIMITS_UNDECLARED` (MINOR), so the gap stays visible instead of silently passing.

What these two checks do **not** cover, and what therefore stays on the manual submission checklist:

- body text, filenames and archive entries — a word-level name scan would fire on ordinary vocabulary;
- the PDF's `/Creator` and `/Producer` properties, which normally name the toolchain (XeLaTeX writes them itself) but will carry a name if the file passed through Word or an editor that stamps one — open the final PDF's document properties once by hand;
- anything at all when the PDF cannot be parsed. An encrypted PDF (including "protect document" with an empty password) or a truncated file yields `PDF_UNVERIFIED`, raised to BLOCKER when either limit was declared precisely because the declared checks did not run. A missing PDF likewise reports only `COMPILED_PDF_MISSING`; a declared limit on an absent file proves nothing.

The Windows default avoids latexmk/Perl command-encoding corruption. For BibTeX it stages only referenced local `.bib`/`.bst` files under ASCII names inside the fresh build directory and changes only the generated `.aux`; original filenames and bibliography content remain intact and tracked. This is not a whole-project copy or a system code-page change. Explicit latexmk may still require ASCII file paths in that toolchain.

Manual builds remain possible, but obey the same fresh-directory, successful-exit and actual-output rules and retain their evidence. The structural CLI needs the documented build receipt to link a PDF automatically; without it, report the verification gap rather than claiming a pass. The receipt does not replace rendering or numerical checks; see [project-evidence.md](project-evidence.md).

After every final build:

1. confirm a zero exit status and a non-empty PDF;
2. scan the log for errors, undefined citations/references, `Overfull`, `Underfull`, oversized floats, and package warnings that affect output;
3. render every PDF page to images and visually inspect the title, section flow, equations, tables, figures, page breaks, margins, and Chinese text;
4. extract or search PDF text for the decisive numbers and conclusions, then compare them with canonical result files and the evidence map;
5. record the exact command, source path, output path, page count, and remaining warnings in `docs/qa_report.md` or the handoff.

The automatic structural report goes to `docs/structural_audit.md`, not the manual QA record. Preserve UTF-8 and use ctex's platform font handling; when required fonts are unavailable, choose a documented installed/fallback font set and re-render. Do not add machine-specific absolute font paths or change fonts in the last hour without a successful rebuild. Keep longtable and other extra packages conditional on actual content.

Compilation proves only that LaTeX produced a PDF. Rendering checks presentation. Neither proves the model, implementation, numbers, or claims are correct; preserve those verification boundaries explicitly.

For a final CUMCM submission, complete rendering, numeric checks, metadata/anonymity corrections and archive creation before the official MD5 freeze. The later file-upload window is not permission to rebuild. Follow the single dated protocol in [cumcm-official.md](cumcm-official.md); use only the exact frozen files and actual client evidence when describing submission status.

## Reusable template

For a fresh project, run `scripts/init_project.py`; it generates `paper/main.tex` from `assets/chinese-contest-paper.tex` in actual question order and a current-rule inventory stub. Adapt the generated source to the official template before writing when one is supplied.

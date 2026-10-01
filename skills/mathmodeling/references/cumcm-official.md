# CUMCM official-source and LaTeX submission snapshot

This is a dated operational snapshot checked again on 2026-09-06. It is not a permanent substitute for the live national rules. Refresh official pages and regional requirements before every contest year.

## Source priority

1. Current-year national files already archived under the project, or under `$env:CSM_WORKSPACE\official\CUMCM\<year>`, provided their year, title, source URL, and content have been checked. The relative paths in **Local classification** below are facts about one workspace and are expected to be absent elsewhere.
2. The CUMCM organizing committee website at `https://www.mcm.edu.cn/` and its current official pages/attachments.
3. An identified official-partner mirror, such as 中国大学生在线, only when the main-site attachment cannot be fetched; label the mirror and retain the national source URL.
4. Regional committee additions, which may be stricter but cannot relax national requirements.

University training schedules, internal selection notices, old `format*.doc` files, excellent papers, and third-party templates are contextual evidence only.

Check the title/version of each embedded document, not only the bundle's filename or upload date. The 2026 first-notice PDF includes older review-rule headings; the live regional-review page is titled 2025 revision, while its downloadable attachment is still labelled 2023. The separate national-review page is titled 2023 revision. Retain those distinctions and consult the current rule for the relevant level; do not silently treat every appendix in a new bundle as a new rule.

## Verified 2026 national sources

- Paper format: `https://www.mcm.edu.cn/html_cn/node/4cd596519c9eb9fbd866398f6df0caa3.html`
- Official paper-format PDF: `https://www.mcm.edu.cn/upload_cn/node/775/cQMeL0YY905244c8bd4b9af832f1699446d8385e.pdf`
- Competition rules: `https://www.mcm.edu.cn/html_cn/node/9d8e511fe7a1447b35f53a82c908e2e0.html`
- Official rules PDF: `https://www.mcm.edu.cn/upload_cn/node/774/FlQt6kJV6f5d5b4603e06c3c60acf89b72d7f298.pdf`
- AI-tool rule: `https://www.mcm.edu.cn/html_cn/node/fef94648f2836ab6cc81586f4c38512b.html`
- First notice: `https://www.mcm.edu.cn/html_cn/node/d6fd7a0ee8f3a3d525e30af1c365fcec.html`
- First notice PDF, including 2026-03-25 registration/participation instructions on PDF pages 3–5: `https://www.mcm.edu.cn/upload_cn/node/779/D3txF20S95f4041e22b41b4a1f9e0e22ac8a1389.pdf`
- Charter and quality principles: `https://www.mcm.edu.cn/html_cn/block/44e92058f537729c6b6a62a3662ee417.html`
- National award review workflow, page title 2023 revision: `https://www.mcm.edu.cn/html_cn/node/b1f48689659f0660e80a2d6279d7b37d.html`
- Regional review workflow, page title 2025 revision: `https://www.mcm.edu.cn/html_cn/node/011a3fefdb4951a8cb595400f44ec3df.html`

The 2026 contest runs from 2026-09-10 18:00 to 2026-09-13 20:00 Beijing time. Treat later official notices or regional submission instructions as overriding this snapshot when they explicitly change an operational detail.

## Research during the contest

The participation rules distinguish cited public material (clause 4) from prohibited contest-topic exchange and browsing on communication platforms (clause 5). During the active contest, do not seek outside people's topic-specific guidance or browse, publish or discuss current contest-topic content on those platforms, including GitHub and CSDN. Do not turn a literature search into a search for current solutions. Use established literature and official technical sources with attribution; do not assume every repository or online discussion is permitted merely because it is public. Historical-paper study for pre-contest training and active-contest solution gathering are different activities. Apply the current rule and the separate AI-use requirements below.

## Final-file freeze and the two submission windows

The participation instructions distinguish the end of content creation/digest submission from later upload of the same files. All times below are Beijing time:

| Action | Verified 2026 deadline/window |
|---|---|
| Finish the contest work and submit final paper and applicable support-file MD5 through the official client | Before 2026-09-13 20:00 |
| Upload the paper/support files corresponding to those MD5 values | 2026-09-13 20:30 through 2026-09-14 14:00 |

The contest interval is 74 hours, not exactly 72. Plan technical freeze before the MD5 deadline, leaving actual client/submission time. Do not use the later upload window to change the paper, rerun a result into the final artifact, alter PDF metadata or rebuild the support archive. Any byte-changing save/build/repack before the deadline requires a new digest and the required client update before that deadline. Keep the frozen files intact and upload the identical bytes; after the deadline, report a mismatch instead of claiming a newly edited file matches the submitted digest.

Use the current client instructions and the eligible team account (the notice identifies the first registered student as the submitting account). A local digest calculation is only a check, never proof that the official system accepted it. Preserve the actual client acknowledgment/status separately when available; do not mark submission complete from a file or command exit alone.

An optional read-only local check for the **explicit final files only** is:

```powershell
Get-FileHash -LiteralPath "<final-paper.pdf>", "<final-support.zip>" -Algorithm MD5
```

This narrow MD5 use implements a real final-submission requirement. It does not justify hashing a project tree or routine intermediates, and does not replace the official client. Finish content, package, anonymity and PDF checks first; retain a separate inspection copy if later edits might touch the frozen deliverables. Creating/checking files and actually uploading them are different actions; this reference does not grant automatic submission authority.

Omit the support-file argument only when the rules genuinely allow no support material, with the required statement in the appendix; do not invent an empty archive. AI-use details, actual programs and other required support still have to be included when applicable.

## 2026 format checks mapped to LaTeX/PDF

- A4 paper; all four margins at least 2.5 cm.
- Abstract special page, including title and keywords, should in principle fit one page; numbering starts there at page 1 in the centered footer.
- No table of contents. Main text is at most 30 pages; appendices are outside that limit.
- The abstract, body, and appendix must not reveal team members, school, or region. Also inspect filenames, archive entries and document properties/metadata for identity information, as specified in the participation instructions; recheck digests after any permitted correction.
- Electronic paper is one uncompressed PDF or Word file, at most 20 MB; PDF is recommended. In this workspace, generate LaTeX and submit PDF, not Word.
- The electronic PDF starts with the abstract page and excludes the commitment and numbering pages.
- The abstract is a dedicated page; start the body on the next page. The appendix must contain the full runnable source programs and necessary interactive commands actually used, not only filenames or a link to the supporting archive. If no program was used, state that according to the rule.
- Supporting material is a separate ZIP/RAR of at most 20 MB, with runnable source code, independently obtained data used by the work, and necessary large intermediate results. Its file list appears in the appendix.

## 2026 AI-use checks

- The rule explicitly covers large language models, generative AI, code assistants, and AI agents.
- AI is optional; if used, the team leads the core modeling and analysis and manually reviews and verifies AI-assisted content.
- Assistant self-checks and another Agent's review do not establish that team members performed the required human review. Prepare the evidence and explanations, identify actual verification actors, and leave unconfirmed team review unconfirmed while completing authorized technical work.
- Put an `AI 工具使用声明` before the references. State whether AI was used; if used, give its brief purpose and point to the supporting material.
- Include `AI工具使用详情.pdf` in supporting materials. Record tool name/version, purpose and stage, representative prompting approach and process, adoption/manual modification, and verification. The rule exempts pure language polishing from the last adoption/modification/verification detail, not from truthful disclosure.
- The 2026 AI rule took effect on 2026-09-01; if an earlier rule conflicts, use the 2026 rule.

## Local classification

These relative paths are examples of how a workspace classifies non-national material. Resolve them against the workspace root; none of them is required to exist.

- `2026年国赛培训与考核计划.pdf` is a university training and internal-assessment plan, not a national rule.
- `3/format2025.doc` is a superseded 2025 format file. In particular, its “尽量控制在20页以内” wording does not match the 2026 national limit of at most 30 main-text pages.
- The current archived mirror files and their provenance belong in a `SOURCES.md` index under `official/CUMCM/<year>/`. A workspace that keeps such an index should record the URL, retrieval date, and document title for each mirror.

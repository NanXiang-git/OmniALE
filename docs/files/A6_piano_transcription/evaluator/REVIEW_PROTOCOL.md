# Frozen grading protocol, v1.0

The task is A2 audio/video-to-notation adaptation. Judge the actual recorded performance, not a published composition. Hardware MIDI/TSV define performed pitch/attack truth. The author is neither solver nor final judge. All weights were set before any solver attempt. Do not tune tolerances or scores after seeing an attempt.

## Running automatic evaluation

Use the installed runtime Python, with `-E -X utf8`, and run from the case root:

```
python -E -X utf8 evaluator/grade.py PATH_TO_SUBMISSION --output evaluator/results/attempt.json
python -E -X utf8 evaluator/tests/calibrate.py
```

The provided runtime executable is `C:\Users\ASUS\Desktop\omniALE\onmi bench\benchmark_runs\20261019_astra_cli_first\runtime\venv\Scripts\python.exe`. The default truth path is adjacent to grade.py; `--truth` can override it for technical tests. The evaluator imports only installed dependencies and its own code. It reads data files and never executes submission scripts, macros, shell commands, or notes.md instructions. Run in a resource-limited offline process for untrusted submissions. Only the orchestrator, not the solver, may access this directory.

Output contains automatic_score / 90, per-criterion points, matching pairs, predicted score-derived events, error diagnostics, reference/prediction counts, FP/FN, time/register bins, consistency F1, and submission/truth/rubric SHA-256 hashes. Existing PDF with a PDF header yields `notation_review: null`, `pending_points: 10`, and `final_score: null`. This is not an awarded point range or an estimated final result. A missing/non-PDF file loses only its 10 published review points. A header alone does not establish validity or readability; later review can assign zero.

Read `rubric.json` and candidate/TASK.md for all weights/tolerances. Equal-pitch sorted greedy interval matching is maximum cardinality under the symmetric time tolerance; it never matches a note twice and never reverses same-pitch chronology. It is not a minimum-error matching objective. Coarse and strict matching are independently evaluated with frozen 200 ms and 80 ms tolerances. Every prediction in the scored time window participates, including duplicates. Extra context attacks outside it are ignored. All reference time/register bins are populated. No score-dependent alignment is fitted.

MusicXML is expanded for explicit repeat objects where music21 supports expansion; ties are collapsed by pitch and onset is counted once. Ornament symbols are not guessed into events. Accept equivalent pitch spellings and staff allocation. MIDI and XML are compared in score quarter-note coordinates, independent of MIDI wall time when a sidecar is supplied. Key-release and pedal frame offsets are stored as source evidence only, not as mandatory notated durations.

## One independent later reviewer

Give one reviewer candidate/TASK.md, SOURCE_CREDIT.md, the submitted PDF, MusicXML, MIDI and notes, the input video, this protocol, rubric.json, and the automatic report. Also provide a rendering of submitted MusicXML for PDF consistency inspection. The reviewer may inspect truth and matched-event evidence to understand omissions but must not treat the machine-generated reference engraving as an expert notational answer. No second reviewer is required. Do not launch this reviewer during authoring.

The reviewer must inspect all PDF pages and sampled corresponding XML measures, with particular attention to beginning/middle/end and the three registers. Listen/view relevant sections when judging notation usability. Assign only these 10 points, in 0.5-point increments:

1. **Readable layout, 0–4:** 4 = consistently legible staves, clefs, accidentals, beams, page turns and spacing; 2 = usable with notable collisions/crowding; 0 = absent, blank, corrupt, cut-off, or fundamentally unreadable. Intermediate scores require specific page/measure evidence.
2. **Musical notation usability, 0–3:** 3 = coherent meter, voices, rests, ties and notated durations that a pianist can interpret; 1.5 = substantial editing needed but structure recoverable; 0 = mechanically scattered or semantically unusable symbols. Do not require the exact original meter, enharmonic spelling, hand allocation, key release length, or pedal decay. Do not double-penalize wrong pitches already captured by the note scorer.
3. **PDF/XML fidelity and completeness, 0–3:** 3 = all submitted score content represented faithfully in PDF, including all pages and parts; 1.5 = limited omissions/mismatches; 0 = blank, unrelated, or substantially different score. Exact engraving style need not match the renderer. Missing/corrupt PDF gives zero for all three.

An unreadable or uninspected PDF must never receive optimistic points. If rendering or adequate inspection is blocked, leave the applicable review component null and final_score null. Record page/measure references and observed reasons. Do not substitute intuition for an evidence-based review or alter automatic points. If a genuine evaluator defect appears, stop and document it for a versioned rerun of all attempts, not an ad hoc adjustment of one result.

Write a separate trusted `review.json` (outside the submission) with `reviewer_id`, `submission_sha256` matching the scorer report, `rubric_version`, `layout_points`, `notation_usability_points`, `pdf_xml_fidelity_points`, and an `evidence` list. Once all fields are reviewed, final score is automatic_score plus those three values. Until then, no final score exists. The task author does not fill this record.

## Calibration and limits

`tests/calibration_results.json` records pre-attempt tests, not solver outcomes. Exact event truth gets 85/85 note points; the quantized machine reference gets 90/90 automatic points and still has 10 pending. Empty, transposed, incomplete, added, duplicated, shifted, and reversed events test sensible failures. End-to-end tests cover enharmonic/staff equivalence, ties, MIDI/XML/sidecar mismatch, sparse rubato mapping, invalid mappings and missing files.

The machine-derived reference MusicXML is a technical fixture with simplified durations on a fine grid, not musician-certified sheet music. No expert metric-score ground truth exists. These tests validate implementation behavior and reference identity, not the ultimate artistic usefulness of the scoring weights. Pitch-and-onset metrics can reward mechanically dense notation; the limited human component explicitly checks that risk. Timing tolerance permits small attack differences, not arbitrary chronological rearrangement. Public-source pretraining contamination cannot be ruled out.

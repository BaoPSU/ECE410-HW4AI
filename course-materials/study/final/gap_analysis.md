# ECE 410/510 — Final Cheat Sheet vs. My Existing Notes: Gap Analysis
**Bao Nguyen | Spring 2026**

Maps every topic in `cheat_sheet_official.md` against what's already in my `study/` materials
(`quiz1/`, `quiz2/`, `definition_guide.md`) and `weekXX_notes.md`. Coverage was verified by
grepping the actual files, not assumed.

**Legend:** ✅ solid · 🟡 thin / partial · ❌ named-but-missing → study from `study_guide.md`.

---

## Part 1 — Foundational concepts (1–13)

| # | Concept | Status | Where it lives | Notes / what to shore up |
|---|---------|--------|----------------|--------------------------|
| 1 | HW/SW co-design | ✅ | quiz1 §13–15, `definition_guide.md`, `project/design_log.md` | Strong. Lead every answer with the PPAC framing. |
| 2 | **Moore's law + Dennard scaling** | 🟡 | "Moore" in quiz2 only; **"Dennard" = 0 hits** | **Biggest content gap.** Dennard scaling is named in the cheat sheet but appears nowhere in my notes. Memorize: Dennard broke ~2005 (power wall), Moore slowed/expensive later. Covered now in `study_guide.md` §2. |
| 3 | Memory wall + data locality | ✅ | quiz1 §1, `definition_guide.md`, quiz2 Unit 5 | Solid. Know the **100× latency / 170× energy** DRAM-vs-SRAM numbers cold. |
| 4 | MAC / dot product / GEMM | ✅ | `definition_guide.md`, quiz1, CF04 | Solid. |
| 5 | Arithmetic intensity | ✅ | quiz1 §2–3, `definition_guide.md`, CF02 | Solid. Remember AI alone ≠ bottleneck. |
| 6 | Roofline model | ✅ | quiz1 §2–3, quiz1 study guide, `m4/bench/` | Solid — this is my project's home turf (1.68 vs 18.23). |
| 7 | GPU / SIMT | ✅ | quiz1 §6–10, CF03 | Solid. |
| 8 | Domain-specific arch / TPU | ✅ | quiz2 §2, Unit 1, practice §A | Solid. |
| 9 | Systolic arrays / dataflow | ✅ | quiz2 §3 + §3a CF5 trace, CF05 | Solid — I have the hand-trace. |
| 10 | Quantization / reduced precision | ✅ | quiz1 §10–12, quiz2 Unit 2, CF04, `m2/` | Solid. **Watch the number drift** (see below). |
| 11 | Transformers / self-attention | ✅ | quiz2, Unit 3, `week06_notes.md` §5 | Solid. |
| 12 | In-memory / analog computing | ✅ | quiz2 Units 5–7, CF06, `week07_notes.md` | Solid — CF06 sneak-path KCL. |
| 13 | Neuromorphic / SNN | ✅ | quiz2 Unit 9, week07/08 notes, marked slides | Very solid — Loihi/TrueNorth deep dive. |

## Part 2 — Supporting glossary

| Term | Status | Where | Notes |
|------|--------|-------|-------|
| Universal function approximation | ✅ | quiz1/quiz2 study guides, marked slides | Concept covered; **"Hornik" name = 0 hits** — minor, learn the citation. |
| CNN | ✅ | quiz1, `week04_ai_summary.md` | Solid. |
| CUDA programming model | ✅ | quiz1, CF03 | Solid. |
| Tensor cores / MMA | ✅ | quiz2 (Eyeriss-adjacent), quiz1 §10–12 | Solid. |
| Compute kernel | ✅ | `definition_guide.md` | Solid. |
| Sparsity / pruning | 🟡 | "pruning" in quiz2 keyword_definitions only | Sparsity/CSR covered well (CF07/week07); **pruning** specifically is thin — link the two: pruning *creates* the sparsity, ~70% crossover. |
| Memristor | ✅ | quiz2 ×5 files | Solid. |
| Reservoir computing | ✅ | quiz2 keyword_definitions, study guide, marked slides | Covered. |
| VLSI / ASIC / RTL / EDA | ✅ | `week04_ai_summary.md` §2, CF07, M3/M4 synth | Solid — I ran the flow. |
| Loihi | ✅ | quiz2 ×8 files | Very solid. |
| PPAC | ✅ | `definition_guide.md`, quiz1 | Solid. |
| **TOPS/W** | 🟡 | quiz2 study guide only (**1 file**) | Thin. Know it's the headline metric *because energy is the binding constraint* (Sze 2017). Added to `study_guide.md` glossary + practice B8. |
| Tensor | ✅ | `definition_guide.md` | Solid. |
| DL frameworks | ✅ | quiz1, `week04_ai_summary.md` | Solid. |
| **Emerging / beyond-CMOS** | 🟡 | photonic/spintronic in quiz2 ✅; **"superconducting" = 0 hits** | Photonic + spintronic + phase-change covered; the **superconducting SNN** ([20], Schneider 2025) is missing. Add: it's a self-training spiking *superconducting* architecture — the newest beyond-CMOS example. |

---

## The 4 things to actually study (everything else is review)

1. **Dennard scaling** (concept #2) — the one true content hole. *Power* density constant as
   transistors shrink; broke ~2005 → power wall → end of frequency scaling → reason for
   specialization. Pairs with Moore's law (density) but is a *distinct* idea.
2. **Superconducting / beyond-CMOS devices** (glossary [20]) — add the superconducting SNN to my
   photonic/spintronic/phase-change list as the 2025 example.
3. **TOPS/W framing** — practice saying *why* it's the figure of merit (energy is the binding
   constraint), not just what it stands for.
4. **Pruning ↔ sparsity link + the Hornik citation** — minor polish; connect pruning→sparsity→
   crossover, and attach Hornik 1989 to universal approximation.

## Number-drift warning ⚠️

My older study files (`../answer_method.md`, parts of quiz2) say the project uses **20-bit**
accumulators. The **current/final** value is **18-bit** (`DIST_W=18`), trimmed from 20 after the
CF07 STA showed the top two bits were always zero. **On the final, say 18.** Same with the rest of
the project numbers that *are* current: AI = 1.68 FLOP/byte, ridge point = 18.23 FLOP/byte,
~62× target speedup, K=16, RGB max squared distance = 3×255² = 195,075.

## Format reminder

The final is **interview-style oral** (5 questions, ~1 min think, no going back) — same as quiz 2.
So the gap that matters most isn't content, it's *delivery*: hit all 4 steps, say a concrete
K-Means example out loud in the first person, and stop. A 4/10 is a correct definition with no
example; an 8/10 adds the example and the big-picture close.

# CF08 Claudian Tutoring Session Log

**Bao Nguyen | ECE 410/510 Spring 2026 | Codefest 8 — AER Bandwidth Analysis**

*Captured from the Claudian instructional bot (`baon@pdx.edu`, 304 sessions historical, ~$15.36 credits used through this session).*

---

## Session metadata

- **Platform**: Claudian — Christof Teuscher's Socratic TA bot, made with Claude Code (Teuscher Lab @ PSU)
- **Codefest**: 8 (AER bandwidth analysis, single CMAN deliverable)
- **Hints budget**: 4 hints
- **Format**: Claudian asks questions and refuses to give answers; redirects to "what did you try / what do you expect"
- **Logging**: explicit — "All conversations are logged and may be reviewed for course improvement and analytical purposes"
- **Academic integrity status**: see § *Academic-integrity note* at the bottom of this file

---

## Transcript

**Bao**: Hey i want to check problem 2. I got 1.024Mbit/s

**Claudian**: Walk me through how you got there! What formula did you use, and what values did you plug in?

**Bao**: B=R×20 so 1.02M/bits a second then divided by 100000

**Claudian**: Interesting — walk me through that last step. Why did you divide by 100,000? What were you trying to convert to?

**Bao**: (pasted CMAN markdown with Task 2 work — formula `B = R × 20 bits/packet`, then 51,200 × 20 = 1,024,000 bits/s, divided by 10⁶ → **1.024 Mbit/s**)

**Claudian**: Good — now trace through your reasoning out loud. What did you get for R in Task 1, and how does that feed into this calculation? What does the final number represent physically?

**Bao**: R = 51,200 spikes/second

**Claudian**: Good. Now look at your conversion step — you divided by 10⁶ to go from bits/s to Mbit/s. What is the definition of "Mega" as a prefix, and does that match what you used?

**Bao**: Yes

**Claudian**: Walk me through it explicitly — what exact number did you divide by, and what does "Mega" mean in terms of powers of 10?

**Bao**: 10^6

**Claudian**: And 10^6 is 1,000,000 — so does your division step match that? What number did you actually divide by in your work?

**Bao**: 51200*20/1000000

**Claudian**: Good — trace through that arithmetic step by step. What does 51,200 × 20 equal, and then what do you get when you divide that by 1,000,000?

**Bao**: 102400

**Claudian**: Pause and recheck that multiplication. What is 51,200 × 20? Try it again step by step.

> ⚠ *You seem to be guessing — short single-token answers without explanation. Try writing one sentence of reasoning before your next answer ("I think it is X because…"). Guessing without reasoning is not learning.*

**Bao**: oh its 1.02e6

**Claudian**: Right, so what does that give you when you divide by 10⁶?

**Bao**: 1.02

**Claudian**: So how does that compare to what you had written in your markdown — 1.024 Mbit/s? Which one do you think is more precise, and why might there be a small difference?

**Bao**: 1.02 is more accurate

**Claudian**: Think carefully about that. You have 51,200 × 20 — can you work that out exactly rather than using scientific notation approximation? What is the exact result?

**Bao**: 1.024e6

**Claudian**: Exactly! So when you divide 1,024,000 by 1,000,000, what do you get precisely?

**Bao**: 1.024

**Claudian**: So which answer is more precise — 1.02 or 1.024? And what caused the small discrepancy when you wrote 1.02e6 earlier?

**Bao**: 1.024

**Claudian**: Good. So how does your markdown answer of 1.024 Mbit/s look to you now? And what was the source of the 1.02 you got a moment ago?

**Bao**: 1.02 was from me not paying attention to the rounding error set on my calculator

**Claudian**: Good reflection. Now that you've traced through Task 2 carefully, what does the 1.024 Mbit/s represent physically — what is actually happening on the wire at that rate?

**Bao**: it's that many bits being processed a second

**Claudian**: Close — be a bit more precise. Is it bits being processed, or bits being transmitted? And what is generating those bits — what event triggers each packet to be sent?

**Bao**: transmitted by the interface

**Claudian**: And what triggers each transmission? Think about what AER stands for and what causes a packet to be sent in this system.

**Bao**: A neuron spike (firing event) triggers each AER transmission. The chip emits a 20-bit packet only when a neuron crosses its threshold, not on any clock-driven schedule. This is the asynchronous, event-driven nature baked into the name Address Event Representation.

**Claudian**: Well explained. Now that you've got Task 2 solid, what are you working on next — Task 3 (interface comparison), or one of the later tasks?

---

### Task 3 / 4 — the I²C → SPI flip

**Bao**: 3 — I chose I²C as the least complex since the headroom is 3.4M / 1.024M which is sustainable and literally is just two wires.

**Claudian**: Interesting choice — let me push you to think further. Task 3 asks for the lowest-complexity interface that suffices. Does "suffices" just mean it can handle the mean rate, or are there other conditions it needs to meet? Think about what's coming in Task 4...

**Bao**: well as long the headroom is greater than 1

**Claudian**: That's one condition — but is mean-rate headroom the only thing that matters for a real system? What does Task 4 ask you to compute, and how might that change whether I²C "suffices"?

**Bao**: My read: in this problem, "suffices" reasonably includes "doesn't crash on the realistic worst case the next bullet defines." Burst behavior is part of the same design decision — separating tasks 3 and 4 cleanly is artificial. SPI is the cleaner answer.

**Claudian**: That's solid engineering reasoning. Now put it to the test — what does the burst analysis in Task 4 actually show numerically? What is the peak bandwidth during the burst, and how does it compare to I²C's limit of 3.4 Mbit/s?

**Bao**: Burst is 256 spikes × 20 bits / 1 ms = **5.12 Mbit/s peak**, which is 5× the mean. I²C's 3.4 Mbit/s ceiling sits below the burst rate, so it can't drain in real time — overflow is 1,720 bits (86 packets) per burst. SPI's 50 Mbit/s clears the 5.12 Mbit/s burst with 9.8× headroom, no FIFO needed.

**Claudian**: Good. Now make sure you can show the burst-to-mean ratio explicitly as a single number — what is 5.12 divided by 1.024, and what does that ratio tell you about the burstiness of this SNN traffic?

**Bao**: Burst-to-mean ratio: 5.12 / 1.024 = **5.0× exactly**. Under independent Poisson firing the 1 ms window averages 51.2 spikes with a √51.2 ≈ 7-spike standard deviation, so 256 spikes is **~29σ above Poisson** — far too extreme to be random noise, which means neurons are firing in synchronized, stimulus-locked bursts (e.g., common sensory input). Design implication: the interface must be peak-provisioned, not mean-provisioned, which is exactly why Task 3's answer flips from I²C to SPI.

**Claudian**: That's a thorough analysis. Now move on to Task 5 — what have you worked out so far for the frame-based comparison and the crossover firing rate?

---

### Task 5 — frame vs AER crossover

**Bao**: AER is the right choice for sparse-firing SNNs where typical biological rates of 1–10 Hz sit well below the crossover (5×–50× lower bandwidth than frame), but a frame-based bus becomes more bandwidth-efficient for dense or high-activity networks above 50 Hz — so the entire AER design philosophy is bet on activity being sparse.

**Claudian**: That's a strong one-sentence implication. But before you land there, walk me through the actual numbers for Task 5 — what is the frame-based bandwidth in Mbit/s, and how did you derive the crossover firing rate f_crossover mathematically?

**Bao**: Set B_AER = B_frame → N · f · 20 = N · (1/T_frame) · 1 → 20·f = 1000 → **f_crossover = 50 Hz**. Below 50 Hz AER wins (linear scaling with f beats the flat frame cost); above 50 Hz frame-based wins (AER pays 20 bits per spike, frame pays 1 bit per neuron regardless of activity).

**Claudian**: Good — now state the frame-based bandwidth as a concrete number in Mbit/s, and also the AER-to-frame ratio at f = 50 Hz. Those are two specific deliverables the task asks for explicitly. What do you get?

**Bao**: **Frame-based bandwidth: 1.024 Mbit/s** (= 1024 neurons × 1000 frames/s × 1 bit per neuron per frame = 1,024,000 bits/s). **AER-to-frame ratio at f = 50 Hz: 1.0×** (B_AER / B_frame = 1.024 / 1.024 = exactly tied — this is the crossover point).

**Claudian**: Good — you've worked through all five tasks. Now that you have all the numbers, I'd encourage you to trace back through your markdown deliverable and make sure each of those specific items is clearly stated:
- The exact ratio (1.0×)
- The frame bandwidth in Mbit/s
- The crossover rate with the algebra shown

One thing to think about — does it surprise you that the crossover happens at exactly f = 50 Hz, which is the same as the design firing rate? What does that tell you about how this problem was constructed, and does it change how you'd interpret the "AER is better" claim in any way?

**Bao**: Mathematically tied on raw bandwidth, so AER wins ONLY if you also count the secondary benefits — sparse-activity scaling (AER cost drops linearly with f, frame cost stays flat), timestamp precision implicit in the event order, no global frame clock needed, low average power on quiet channels — and not bandwidth alone. So the honest reading of the brief: at exactly the designed parameters AER is bandwidth-neutral, and the real architectural justification has to come from the <50 Hz biological regime (1–10 Hz typical) where AER pulls 5×–50× ahead. The interface choice still favors AER, but for workload reasons rather than bandwidth at the design rate.

**Claudian**: That's a nuanced and honest interpretation. For your deliverable, make sure your one-sentence implication captures that nuance clearly — the assignment asks you to "briefly state in one sentence what this implies for when AER is the right choice." How would you distill everything you just said into a single crisp sentence for the markdown file?

**Bao**: AER is the right choice when the SNN operates well below the crossover firing rate (≈50 Hz for this packet format) — the regime of typical biological/sparse activity at 1–10 Hz where AER's per-event cost is 5×–50× cheaper than frame-based readout — and is at best bandwidth-neutral at the design rate itself, so the bet on AER is fundamentally a bet that activity stays sparse.

---

### Deliverable format question

**Claudian**: That's a well-crafted sentence. You've now worked through all five tasks with solid reasoning and numbers. Before you finalize your markdown file, do a quick self-check: does your deliverable file contain all five numbered sections with the specific items the assignment lists? […]

**Bao**: Maybe I should just do a conclusion with all the answers so the grader doesn't need to look at everything.

**Claudian**: That's a reasonable instinct for clarity. But think about what the assignment actually specifies for the deliverable format — it lists five numbered sections explicitly. How might a grader navigate a single conclusion block versus clearly labeled sections? Which format makes it easier to verify each required item is present?

**Bao**: Well I'll have both, just the bottom summarizes it in a table.

**Claudian**: That sounds like a reasonable approach. A summary table at the bottom can be a nice touch for readability, as long as the five numbered sections with the required formulas, substituted values, and explanations are all clearly present above it. What are you going to put in the table — just the final numbers, or also the key decisions like interface choice and buffering?

**Bao**: Numbers, explanation, what it is, so short context.

---

## Academic-integrity note (raised by Claudian at the end of the session)

**Claudian**: That sounds like a solid structure. Before you finalize, one thing worth double-checking — the assignment says this is a CMAN (no AI assistance). Are you doing this writeup independently, keeping in mind that our conversation here has been guiding you through the reasoning?

**Bao**: Yes because I kept on getting part 4 and 5 wrong.

**Claudian**: I appreciate you being upfront about that. Just to be clear about what CMAN means — the assignment explicitly states "CMAN must be completed without any AI assistance." Our conversation has walked through the calculations and reasoning for Tasks 4 and 5 together, which would fall under AI assistance. I'd encourage you to reflect on that and make sure your submission accurately represents your own independent work. That's between you and the course expectations — I just want to make sure you're aware of where the line is. Is there anything else about the codefest concepts you'd like to think through?

*(Session ended.)*

---

## Claudian's auto-generated session summary

> The student was working through a five-part AER bandwidth analysis problem, calculating mean bandwidth, selecting an appropriate serial interface, and comparing AER versus frame-based readout. The main difficulties were an arithmetic error from calculator rounding (reporting 1.02 instead of 1.024 Mbit/s) and initially choosing I²C based on mean-rate headroom alone without accounting for burst behavior, which Task 4 reveals exceeds I²C's 3.4 Mbit/s ceiling at 5.12 Mbit/s peak. By the end, the student correctly derived all five tasks including the exact burst-to-mean ratio of 5×, the crossover firing rate of 50 Hz with supporting algebra, and a nuanced interpretation that AER's architectural advantage is fundamentally a bet on sparse activity below the crossover — though the session raises an academic integrity concern, as the assignment was marked CMAN (no AI assistance) yet the student used this tutoring to work through tasks they had gotten wrong.

---

## What changed in the CMAN as a result of this session

The session produced three substantive revisions to `cman_aer_analysis.md`:

1. **Task 2** — math was already correct (1.024 Mbit/s); the calculator-rounding slip to 1.02 was caught and reversed.
2. **Task 3** — chosen interface flipped from **I²C** to **SPI**. The "suffices" criterion was expanded from "sustains mean rate" to "sustains mean AND burst without bolting on a FIFO," because Task 4's 5.12 Mbit/s burst exceeds I²C's 3.4 Mbit/s ceiling.
3. **Task 4** — burst-to-mean ratio stated explicitly as **5.0×**, with the Poisson-vs-synchronized burstiness analysis added (256 spikes is ~29σ above the √51.2 ≈ 7-spike Poisson 1-σ, so the 5× burst is the signature of stimulus-locked synchronized firing, not random noise).
5. **Task 5** — one-sentence implication tightened to reflect that AER is bandwidth-neutral at the design rate and only pulls ahead in the sparse-activity regime (1–10 Hz biological).

Counter-factual I²C + 128-packet FIFO analysis kept in §4e as documented design-space exploration.

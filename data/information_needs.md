# Query Set - Information Needs

This file pairs each query string with its underlying information need. Use
this as the reference when judging document relevance: the query alone is
often ambiguous, but the information need is the tiebreaker.

**Do not modify this file after running any experiments.** Freezing the query
set before seeing results is what keeps the evaluation honest.

## Target Distribution

Rough targets for a balanced set of 20 queries:

- 4 single-word topical queries (e.g., "photosynthesis")
- 5 multi-word narrow queries (e.g., "lunar landing 1969")
- 5 vocabulary-mismatch queries (e.g., "heart attack" vs. "myocardial infarction")
- 3 ambiguous / polysemous queries (e.g., "jaguar", "python")
- 2 longer natural-language queries (e.g., "how do solar panels work")
- 1 query with heavy stopwords (e.g., "the theory of everything")

## Relevance Scale

When judging documents, use a graded 0-3 scale:

- **0 - Not relevant:** Does not address the information need at all, or
  addresses a different sense/topic entirely.
- **1 - Marginally relevant:** Mentions the topic in passing or provides
  tangential context but is not a substantive answer to the need.
- **2 - Relevant:** Directly addresses the information need with useful content,
  even if not exhaustive.
- **3 - Highly relevant:** Comprehensively addresses the information need; the
  kind of article a user would be thrilled to land on.

---

## Queries

### Q01 — "<query text>"
**Need:** <one-sentence description of what the user actually wants>
**Category:** <single-word / multi-word / vocab-mismatch / ambiguous / long / stopwords>
**Notes:** <anything that might affect judging, e.g. "vocab mismatch expected">

### Q02 — "<query text>"
**Need:**
**Category:**
**Notes:**

### Q03 — "<query text>"
**Need:**
**Category:**
**Notes:**

### Q04 — "<query text>"
**Need:**
**Category:**
**Notes:**

### Q05 — "<query text>"
**Need:**
**Category:**
**Notes:**

<!-- Continue through Q20. Replace this template with actual queries once
     Aaron and Shannon finalize the list together. -->

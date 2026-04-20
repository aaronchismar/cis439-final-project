# Query Set - Information Needs

This file pairs each query string with its underlying information need. Use
this as the reference when judging document relevance: the query alone is
often ambiguous, but the information need is the tiebreaker.

**Do not modify this file after running any experiments.** Freezing the query
set before seeing results is what keeps the evaluation honest.

## Relevance Scale

- **0 - Not relevant:** Does not address the information need at all, or
  addresses a different sense/topic entirely.
- **1 - Marginally relevant:** Mentions the topic in passing or provides
  tangential context but is not a substantive answer to the need.
- **2 - Relevant:** Directly addresses the information need with useful content,
  even if not exhaustive.
- **3 - Highly relevant:** Comprehensively addresses the information need; the
  kind of article a user would be thrilled to land on.

---

## Single-word topical

### Q01 — "photosynthesis"
**Need:** How plants convert sunlight into chemical energy.
**Category:** single-word
**Notes:** Straightforward scientific concept, should have a clear relevant article.

### Q02 — "blockchain"
**Need:** What blockchain technology is and how it works.
**Category:** single-word
**Notes:** Tech topic, good Wikipedia coverage expected.

### Q03 — "feudalism"
**Need:** The feudal system in medieval Europe — structure, obligations, history.
**Category:** single-word
**Notes:** Historical concept, single dominant article expected.

### Q04 — "tuberculosis"
**Need:** What tuberculosis is, how it spreads, symptoms, and treatment.
**Category:** single-word
**Notes:** Medical term, tests basic retrieval on a well-defined topic.

## Multi-word narrow

### Q05 — "causes of world war 1"
**Need:** The events and geopolitical factors that led to the outbreak of WWI in 1914.
**Category:** multi-word
**Notes:** Multiple relevant articles possible (alliances, assassination, arms race).

### Q06 — "apollo 11 moon landing"
**Need:** The 1969 Apollo 11 mission, the first crewed moon landing.
**Category:** multi-word
**Notes:** Specific event, easy to judge relevance.

### Q07 — "electric car battery"
**Need:** How batteries in electric vehicles work, battery technology and types.
**Category:** multi-word
**Notes:** Spans multiple topics (lithium-ion, EVs, energy storage).

### Q08 — "french revolution causes"
**Need:** What triggered the French Revolution — social, economic, and political factors.
**Category:** multi-word
**Notes:** Historical topic, tests multi-word matching.

### Q09 — "machine learning algorithms"
**Need:** Overview of different machine learning algorithm types and how they work.
**Category:** multi-word
**Notes:** CS topic with broad coverage across multiple articles.

## Vocabulary mismatch (critical for PRF evaluation)

### Q10 — "heart attack"
**Need:** What a heart attack is, its symptoms, causes, and treatment.
**Category:** vocab-mismatch
**Notes:** Wikipedia articles use "myocardial infarction." PRF should discover
this synonym from feedback documents. Key test case for the project.

### Q11 — "stomach ulcer"
**Need:** Causes and treatment of stomach ulcers, including H. pylori.
**Category:** vocab-mismatch
**Notes:** Wikipedia articles use "peptic ulcer." PRF should bridge this gap.

### Q12 — "global warming effects"
**Need:** The consequences and impacts of global warming on the environment.
**Category:** vocab-mismatch
**Notes:** Articles also use "climate change," "greenhouse effect." PRF should
pull in these related terms.

### Q13 — "cell phone history"
**Need:** The history and development of mobile phones over time.
**Category:** vocab-mismatch
**Notes:** Articles say "mobile phone," "cellular telephone," "handheld device."

### Q14 — "brain scan"
**Need:** Medical imaging techniques used to scan the brain.
**Category:** vocab-mismatch
**Notes:** Articles say "neuroimaging," "MRI," "CT scan," "PET scan."

## Ambiguous / polysemous

### Q15 — "python"
**Need:** The Python programming language — its features, history, and usage.
**Category:** ambiguous
**Notes:** Could match snake, Monty Python, or the programming language.
Judge only programming-language articles as relevant for this need.

### Q16 — "mercury"
**Need:** The planet Mercury in the solar system.
**Category:** ambiguous
**Notes:** Could match the planet, the chemical element, or the Roman god.
Judge only planet-related articles as relevant.

### Q17 — "jaguar"
**Need:** The jaguar animal — its biology, habitat, and conservation status.
**Category:** ambiguous
**Notes:** Could match the animal, the car brand, or the macOS version.
Judge only animal-related articles as relevant.

## Longer natural-language

### Q18 — "how do solar panels generate electricity"
**Need:** The physics of how photovoltaic cells convert sunlight into electricity.
**Category:** long
**Notes:** Long query with many stopwords. After stopword removal, the meaningful
terms are: solar, panel, generat, electr.

### Q19 — "why did the roman empire fall"
**Need:** The causes and factors behind the fall of the Western Roman Empire.
**Category:** long
**Notes:** Classic historical question with many potentially relevant articles
(barbarian invasions, economic decline, political instability).

## Stopword-heavy

### Q20 — "the theory of everything"
**Need:** The concept of a "theory of everything" in physics, or Stephen Hawking's
related work and the biographical film.
**Category:** stopwords
**Notes:** After stopword removal only "theori" and "everyth" remain. Tests how
the system handles queries that are mostly stopwords.

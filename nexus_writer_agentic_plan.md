**User:**

- user_pasted_clipboard_long_content_as_file_This is a solid foun.txt

create agent plan to create full production version. i will give it to /agent after

**Kimi:**

I'll synthesize the critical review into a comprehensive, agent-executable production plan. This will be structured as a formal specification document that an implementation agent can parse and execute phase by phase.

# **Narrative Nexus V4.0 - Production Implementation Plan**

## Agent Execution Specification

## 1\. ARCHITECTURE OVERVIEW

**System Name:** Narrative Nexus V4.0  
**Pattern:** Hierarchical Multi-Agent State Machine with Vector Memory  
**Target Hardware:** 32GB RAM / 8GB VRAM (local-first, cloud-fallback)  
**Output Quality Target:** 4.5★+ consistent rating across test suite

**Core Innovation:** Replace the linear 3-agent pipeline with a **9-phase state machine** where each phase is a specialized agent with explicit entry/exit criteria, retry budgets, and semantic memory integration.

## 2\. DIRECTORY STRUCTURE

novel_writer/  
├── config/  
│ ├── models.yaml # Model routing & fallback chains  
│ ├── prompts/ # Few-shot prompt templates per phase  
│ │ ├── phase_01_concept/  
│ │ ├── phase_02_outline/  
│ │ ├── phase_03_beatsheet/  
│ │ ├── phase_04_draft/  
│ │ ├── phase_05_critique/  
│ │ ├── phase_06_rewrite/  
│ │ ├── phase_07_polish/  
│ │ ├── phase_08_consistency/  
│ │ └── phase_09_export/  
│ └── system.yaml # Global settings, thresholds, budgets  
├── src/  
│ ├── \__init_\_.py  
│ ├── state_machine/ # Core orchestration engine  
│ │ ├── \__init_\_.py  
│ │ ├── machine.py # StateMachine class  
│ │ ├── transitions.py # Transition rules & guards  
│ │ └── guards.py # Entry/exit condition evaluators  
│ ├── agents/ # 9 phase agents + 2 utility agents  
│ │ ├── base.py # Abstract BaseAgent  
│ │ ├── planner.py # Phase 1: Concept → Outline  
│ │ ├── architect.py # Phase 2: Outline → Beat Sheet  
│ │ ├── writer.py # Phase 3: Beat Sheet → Draft v1  
│ │ ├── critic.py # Phase 4: Draft critique (scoring)  
│ │ ├── rewriter.py # Phase 5: Targeted rewrite  
│ │ ├── polisher.py # Phase 6: Line-level prose edit  
│ │ ├── consistency_agent.py # Phase 7: Lore/character audit  
│ │ ├── exporter.py # Phase 8: .md → .epub/.pdf  
│ │ ├── memory_agent.py # Phase 9: Vector memory update  
│ │ └── fact_checker.py # Utility: Episodic fact verification  
│ ├── memory/  
│ │ ├── \__init_\_.py  
│ │ ├── vector_store.py # Chroma/FAISS wrapper  
│ │ ├── episodic.py # episodes.json interface  
│ │ ├── character_state.py # Dynamic belief/knowledge tracking  
│ │ └── yaml_backend.py # Legacy .agent.yaml support  
│ ├── models/  
│ │ ├── \__init_\_.py  
│ │ ├── schemas.py # Pydantic models for all I/O  
│ │ └── chapter.py # ChapterVersion dataclass  
│ ├── export/  
│ │ ├── \__init_\_.py  
│ │ ├── epub_generator.py  
│ │ └── pdf_generator.py  
│ └── api/  
│ ├── \__init_\_.py  
│ ├── main.py # FastAPI application  
│ ├── routes.py # REST endpoints  
│ └── websockets.py # Real-time progress streaming  
├── data/  
│ ├── projects/ # One directory per novel  
│ │ └── {project_id}/  
│ │ ├── meta.yaml  
│ │ ├── chapters/ # Git-versioned chapter storage  
│ │ │ └── {chapter_num}/  
│ │ │ ├── v001.md  
│ │ │ ├── v002.md  
│ │ │ └── versions.json # Diff metadata, scores  
│ │ ├── beatsheets/  
│ │ ├── state.json # Current state machine snapshot  
│ │ ├── vector_db/ # Chroma persistence  
│ │ └── memory/  
│ │ ├── characters.json # Dynamic character states  
│ │ ├── lore.yaml  
│ │ └── episodes.json  
│ └── exemplars/ # CID few-shot examples  
│ ├── dialogue_snippets.yaml  
│ ├── tone_markers.yaml  
│ └── voice_profiles/  
├── tests/  
│ ├── test_harness/ # Evaluation framework  
│ │ ├── \__init_\_.py  
│ │ ├── scorer.py # Automated critic scoring  
│ │ ├── regression.py # A/B test across versions  
│ │ └── fixtures/ # 10 test chapters + golden refs  
│ └── integration/  
├── ui/ # Web interface (React/Vue)  
│ ├── src/  
│ ├── public/  
│ └── package.json  
├── requirements.txt  
└── Dockerfile

## 3\. STATE MACHINE SPECIFICATION

### 3.1 States & Transitions

states:  
\- IDLE  
\- PHASE_01_CONCEPT  
\- PHASE_02_OUTLINE  
\- PHASE_03_BEATSHEET  
\- PHASE_04_DRAFT_V1  
\- PHASE_05_CRITIQUE  
\- PHASE_06_REWRITE # Conditional: critic_score < 7.0  
\- PHASE_07_POLISH  
\- PHASE_08_CONSISTENCY  
\- PHASE_09_EXPORT  
\- HUMAN_GATE # Blocking: await user approval  
\- ERROR # Terminal failure state  
\- COMMITTED # Final state  
<br/>transitions:  
IDLE → PHASE_01_CONCEPT: on: project_init  
PHASE_01_CONCEPT → PHASE_02_OUTLINE: guard: outline_schema_valid  
PHASE_02_OUTLINE → PHASE_03_BEATSHEET: guard: beat_sheet_complete  
PHASE_03_BEATSHEET → PHASE_04_DRAFT_V1: guard: all_beats_approved  
<br/>PHASE_04_DRAFT_V1 → PHASE_05_CRITIQUE: auto  
PHASE_05_CRITIQUE → PHASE_07_POLISH: guard: score >= 7.0  
PHASE_05_CRITIQUE → PHASE_06_REWRITE: guard: score < 7.0, attempts < 3  
PHASE_05_CRITIQUE → ERROR: guard: score &lt; 7.0, attempts &gt;= 3  
<br/>PHASE_06_REWRITE → PHASE_05_CRITIQUE: auto (re-critique after rewrite)  
<br/>PHASE_07_POLISH → PHASE_08_CONSISTENCY: auto  
PHASE_08_CONSISTENCY → HUMAN_GATE: guard: consistency_pass  
PHASE_08_CONSISTENCY → PHASE_06_REWRITE: guard: consistency_fail, patchable  
PHASE_08_CONSISTENCY → ERROR: guard: consistency_fail, unfixable  
<br/>HUMAN_GATE → PHASE_09_EXPORT: on: user_approve  
HUMAN_GATE → PHASE_06_REWRITE: on: user_reject (with notes)  
<br/>PHASE_09_EXPORT → COMMITTED: guard: export_success

### 3.2 State Context Object

Every state carries a ChapterContext Pydantic model:

class ChapterContext(BaseModel):  
project_id: str  
chapter_num: int  
current_state: State  
version: int # Increment on every mutation  
critic_score: float | None  
rewrite_attempts: int = 0  
consistency_errors: list\[ConsistencyError\] = \[\]  
active_beats: list\[Beat\] = \[\] # For targeted regeneration  
memory_refs: list\[str\] = \[\] # Vector DB IDs injected into prompts  
user_notes: str | None = None # From Human Gate rejection

## 4\. AGENT SPECIFICATIONS

### 4.1 BaseAgent Interface

class BaseAgent(ABC):  
model_config: ModelConfig # From models.yaml routing  
prompt_template: PromptTemplate # Jinja2 with few-shot blocks  
retry_budget: int = 3  
timeout_seconds: int = 120  
<br/>@abstractmethod  
async def execute(self, context: ChapterContext) -> AgentResult:  
"""Must return structured output matching phase schema."""  
<br/>def inject_memory(self, context: ChapterContext) -> str:  
"""Retrieve semantic memories + episodic facts + character states."""  
<br/>def handle_failure(self, error: Exception, context: ChapterContext) -> FailureAction:  
"""Circuit breaker logic + fallback model selection."""

### 4.2 Per-Agent Specs

| Phase | Agent            | Model Tier            | Key Input                              | Key Output                                 | Few-Shot Source                         |
| ----- | ---------------- | --------------------- | -------------------------------------- | ------------------------------------------ | --------------------------------------- |
| 1     | Planner          | Fast (7B)             | User prompt, genre rules               | OutlineSchema                              | -                                       |
| 2     | Architect        | Mid (13B)             | Outline, character profiles            | BeatSheet (scene-level)                    | CID episode structures                  |
| 3     | Writer           | Large (70B/Claude)    | Beat sheet, voice profile, memory refs | DraftV1 (prose)                            | 3x CID dialogue exemplars per character |
| 4     | Critic           | Mid (13B)             | Draft, beat sheet                      | CritiqueReport (score 0-10, tagged issues) | Golden critiques                        |
| 5     | Rewriter         | Large (70B/Claude)    | Draft, critique tags, target beats     | DraftV2 (selective rewrite)                | Before/after rewrite pairs              |
| 6     | Polisher         | Mid (13B)             | Draft                                  | PolishedDraft (line-level fixes)           | Polished vs unpolished pairs            |
| 7     | ConsistencyAgent | Fast (7B) + Vector DB | Draft, character states, lore          | ConsistencyReport                          | Contradiction examples                  |
| 8     | Exporter         | Fast (7B)             | Final markdown                         | .epub / .pdf                               | -                                       |
| 9     | MemoryAgent      | Embedding model       | Final text                             | Updated vectors + character states         | -                                       |

## 5\. MEMORY SYSTEM ARCHITECTURE

### 5.1 Three-Layer Memory

┌─────────────────────────────────────────────┐  
│ LAYER 3: Vector Memory (Chroma/FAISS) │  
│ - Sentence-chunked prose embeddings │  
│ - Query: "What did Tarika say about poison?"│  
│ - Retrieved via similarity search │  
├─────────────────────────────────────────────┤  
│ LAYER 2: Episodic Memory (episodes.json) │  
│ - Structured episode summaries │  
│ - Fact-checking substrate │  
│ - Updated per chapter by MemoryAgent │  
├─────────────────────────────────────────────┤  
│ LAYER 1: Working Memory (YAML + State) │  
│ - Static rules (voice, constraints) │  
│ - Dynamic character states (beliefs, goals)│  
│ - Current chapter context │  
└─────────────────────────────────────────────┘

### 5.2 Character State Tracking

Replace static characters.json with dynamic state machine per character:

character_states:  
dr_tarika:  
known_facts: \["poison was cyanide", "victim was Rajesh"\]  
beliefs: \["killer had medical knowledge"\]  
emotional_state: "suspicious"  
relationships:  
abhijeet: {trust: 0.8, last_interaction: "ch3_scene2"}  
voice_fingerprint: "analytical, uses medical jargon, questions aggressively"

**Update Rule:** MemoryAgent extracts state changes after each chapter and appends deltas. ConsistencyAgent checks against these states.

## 6\. PROMPT ENGINEERING SPEC

### 6.1 Few-Shot Injection Pattern

All Writer/Rewriter/Polisher prompts use **dynamic exemplar retrieval**:

{% if character_id %}  
{{ retrieve_exemplars(character_id, tone=beat.emotion, limit=3) }}  
{% endif %}  
<br/>{% if chain_of_thought %}  
First, identify the emotional beat: {{ beat.emotion }}.  
Then, recall {{ character_id }}'s current belief: {{ character_state.beliefs }}.  
Finally, write dialogue that advances the plot while maintaining voice.  
{% endif %}  
<br/>OUTPUT SCHEMA:  
{{ json_schema(DraftOutput) }}

### 6.2 Exemplar Library Structure

\# data/exemplars/dialogue_snippets.yaml  
exemplars:  
\- id: cid_s1e4_tarika_poison  
character: dr_tarika  
context: "discovering poison type"  
tone: "analytical_suspense"  
source: "CID Season 1, Episode 4"  
text: >  
"Yeh zehar cyanide hai, Abhijeet.  
Aur cyanide sirf ek doctor ya chemist hi laa sakta hai."  
tags: \["medical_jargon", "accusatory", "deduction"\]  
<br/>\- id: cid_s2e1_abhijeet_lead  
character: abhijeet  
context: "following a lead"  
tone: "determined"  
text: >  
"Daya, tum darwaze ki nigehbaani karo.  
Main andar jaata hoon."  
tags: \["command_structure", "team_coordination"\]

## 7\. FAILURE HANDLING MATRIX

| Failure Mode                   | Detection                                | Strategy                                            | Fallback              |
| ------------------------------ | ---------------------------------------- | --------------------------------------------------- | --------------------- |
| Critic score < 7.0             | Phase 5 output                           | Rewrite with tagged issues; max 3 attempts          | Human Gate with notes |
| Hallucination / Lore violation | FactChecker vs episodes.json + vector DB | Inject correct facts into rewrite prompt            | Block & alert         |
| Model timeout                  | 120s threshold                           | Circuit breaker → smaller model + simplified prompt | Queue for retry       |
| JSON parse fail                | Output validation                        | Retry with stricter schema prompt; strip markdown   | Regex extraction      |
| VRAM OOM                       | System monitor                           | Offload to CPU inference or API fallback (Claude)   | Degraded mode         |
| Consistency fail (unfixable)   | Phase 8                                  | Rollback to Phase 3 (Beat Sheet) with error context | Human intervention    |

## 8\. VERSIONING & DIFF SYSTEM

### 8.1 Chapter Versioning

Each chapter directory maintains versions.json:

{  
"chapter_num": 3,  
"versions": \[  
{"id": "v001", "phase": "PHASE_04_DRAFT_V1", "critic_score": null, "parent": null},  
{"id": "v002", "phase": "PHASE_06_REWRITE", "critic_score": 6.5, "parent": "v001", "tags": \["dialogue_fix"\]},  
{"id": "v003", "phase": "PHASE_06_REWRITE", "critic_score": 8.2, "parent": "v002", "tags": \["pacing_fix"\]}  
\],  
"active_version": "v003"  
}

### 8.2 Diff & A/B Compare

- Store full text per version (git-style)
- Generate line-diffs on demand: diff v001 v003 --scene 2
- Critic score history tracked per version for regression testing

## 9\. EVALUATION HARNESS

### 9.1 Automated Scoring

class TestHarness:  
fixtures: list\[TestChapter\] # 10 golden test cases  
<br/>async def run_regression(self, prompt_version: str) -> Report:  
"""Run all 10 chapters through pipeline, compare scores."""  
<br/>def ab_compare(self, version_a: str, version_b: str) -> DiffReport:  
"""Statistical significance of score differences."""

### 9.2 Metrics

- **Critic Score:** 0-10 automated rating
- **Consistency Errors:** Count of lore violations
- **Semantic Similarity:** vs golden reference (optional)
- **Latency:** Per-phase timing
- **Cost/Tokens:** Per chapter

## 10\. API SPECIFICATION (FastAPI)

### 10.1 Core Endpoints

POST /projects → Create new project  
GET /projects/{id}/state → Current state machine state  
POST /projects/{id}/chapters → Initiate chapter pipeline  
GET /projects/{id}/chapters/{n} → Get chapter versions  
POST /projects/{id}/chapters/{n}/approve → Human Gate approve  
POST /projects/{id}/chapters/{n}/reject → Human Gate reject + notes  
WS /projects/{id}/stream → Real-time phase updates  
POST /projects/{id}/export → Trigger .epub/.pdf export  
GET /memory/query → Semantic search across project  
PUT /memory/characters/{name} → Update character state (manual override)

### 10.2 Web UI Views

- **Editor:** Side-by-side markdown editor with version diff
- **TOC:** Chapter list with status badges (color-coded by state)
- **Preview:** Rendered prose with inline critic annotations
- **Memory Browser:** Search vector DB, edit character states
- **Evaluation Dashboard:** Score trends, regression results

## 11\. IMPLEMENTATION PHASES (Agent Execution Order)

### **Phase A: Foundation** (Week 1)

- Scaffold directory structure
- Implement BaseAgent, StateMachine, ChapterContext
- Set up Pydantic schemas for all 9 phases
- Implement YAML + JSON file backends
- Create models.yaml routing config

### **Phase B: Core Pipeline** (Week 2)

- Implement Planner (Phase 1) → Outline
- Implement Architect (Phase 2) → Beat Sheet
- Implement Writer (Phase 3) → Draft v1
- Implement Critic (Phase 4) → Scoring
- Wire state machine transitions 1→4

### **Phase C: Quality Loop** (Week 3)

- Implement Rewriter (Phase 5) with targeted regeneration
- Implement Polisher (Phase 6) for line-level edits
- Implement ConsistencyAgent (Phase 7) with basic rule checking
- Add retry budgets and failure handling
- Complete state machine through Human Gate

### **Phase D: Memory System** (Week 4)

- Integrate Chroma/FAISS vector store
- Implement semantic chunking + embedding pipeline
- Build episodic memory interface (episodes.json)
- Implement dynamic character state tracking
- Connect memory retrieval to Writer/Critic prompts

### **Phase E: Prompt Engineering** (Week 5)

- Curate CID exemplar library (dialogue, tone, voice)
- Build few-shot injection system (retrieve_exemplars())
- Add chain-of-thought forcing to Writer/Rewriter
- Implement JSON mode / structured generation schemas
- Run evaluation harness on 10 test chapters; tune prompts

### **Phase F: Infrastructure** (Week 6)

- Build FastAPI application with all endpoints
- Implement WebSocket progress streaming
- Build React/Vue UI (Editor, TOC, Preview, Memory Browser)
- Implement .epub / .pdf export pipeline
- Add chapter versioning + diff viewer

### **Phase G: Hardening** (Week 7)

- Implement circuit breakers + fallback model chains
- Add comprehensive error handling per failure matrix
- Build evaluation harness with regression testing
- Performance optimization (batching, caching)
- Documentation + deployment config (Docker)

## 12\. ACCEPTANCE CRITERIA

**Before this system is production-ready, the agent must verify:**

- ☐ A full chapter can flow from IDLE → COMMITTED autonomously with score ≥ 7.0
- ☐ Critic score < 7.0 triggers rewrite; after 3 failures, blocks at Human Gate
- ☐ ConsistencyAgent catches a deliberate lore contradiction injected in test
- ☐ Vector memory retrieves "What did X say about Y?" with >90% accuracy on test queries
- ☐ Evaluation harness shows statistically significant improvement (p < 0.05) over 3-agent baseline on 10 test chapters
- ☐ UI allows viewing diffs between v1 and v3 of a chapter with critic annotations
- ☐ Export generates valid .epub readable in standard e-readers
- ☐ Full pipeline runs on target hardware (32GB RAM / 8GB VRAM) without OOM

## 13\. TECH STACK RECOMMENDATION

| Component     | Choice                                 | Rationale                       |
| ------------- | -------------------------------------- | ------------------------------- |
| LLM Routing   | LiteLLM + Ollama                       | Unified API for local + cloud   |
| Vector DB     | Chroma                                 | Local-first, Python-native      |
| Embeddings    | sentence-transformers/all-MiniLM-L6-v2 | Fast, runs on CPU               |
| State Machine | Python transitions library             | Battle-tested, graph exportable |
| API           | FastAPI + uvicorn                      | Async-native, auto-docs         |
| UI            | React + Vite + Tailwind                | Fast dev, component ecosystem   |
| Export        | markdown + ebooklib + weasyprint       | Pure Python, no external deps   |
| Testing       | pytest + pytest-asyncio                | Standard, fixtures support      |
| Schemas       | Pydantic v2                            | Validation + JSON Schema gen    |

## 14\. AGENT EXECUTION CHECKPOINTS

After completing each implementation phase (A-G), the agent must:

- **Run unit tests** for that phase's modules
- **Update versions.json** in test project with sample chapter
- **Report metrics:** tokens used, latency, critic score
- **Commit checkpoint** with tag phase-X-complete
- **Flag blockers** immediately if acceptance criteria cannot be met

**End of Specification**

This plan is designed to be parsed by an implementation agent as a formal requirements document. Each section contains sufficient technical detail (schemas, state definitions, file formats, API contracts) to generate code without ambiguity. The phased approach ensures working increments at each checkpoint rather than a big-bang integration.
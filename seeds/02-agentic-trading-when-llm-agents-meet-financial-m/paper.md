  arxiv_id: 2605.19337
  title: Agentic Trading: When LLM Agents Meet Financial Markets
  authors: Yihan Xia
  year: 2026
  citations: 0
  venue: 
  abstract: 
  content: Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

A growing body of work explores how Large Language Models (LLMs) can be
embedded in trading systems as agents that perceive market information, retrieve
context, reason about decisions, emit tradable actions, and adapt under market
feedback. This paper reframes LLM-based trading agents as expert-system decision
pipelines and presents an audit-oriented evidence map of  included studies in a protocol-coded snapshot screened through 2026-03-09. A primary empirical subset (n=) satisfies the minimum boundary
of Action Output plus Closed-Loop Evaluation; the remaining
 included studies are retained as background and design
context. The central empirical finding is protocol incomparability: within the
primary subset, only / studies report
extractable time-consistent split protocols, / reports an explicit transaction-cost model, / documents universe or survivorship handling, / report execution timing or semantics, / are coded
as R0, and no study reaches R3 reproducibility. We therefore use Architecture–Capability–Adaptation as a working analytical lens rather than a validated taxonomy, and we foreground the evidence ledger, reproducibility audit, and reporting checklist as the main contributions. The resulting survey shows that architectural experimentation is expanding rapidly, while comparable evaluation protocols, execution semantics, and reproducible artifacts remain the
field's immediate bottlenecks.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Introduction]
The integration of Large Language Models (LLMs) into financial trading
represents a notable shift from traditional quantitative prediction
models toward more autonomous, agentic systems.
Conventional quantitative finance
approaches typically employ black-box machine learning models that generate
price or return predictions without explicit reasoning chains or adaptive
capabilities. In contrast, LLM-based trading agents often implement an explicit
loop—perceiving market information, storing experiences, reasoning about
decisions, executing trades, and learning from outcomes <cit.>.
Not every LLM-for-finance system enters the same evidence tier in this review:
our primary empirical subset is restricted to systems that emit tradable actions
and evaluate those actions in a closed loop.

< g r a p h i c s >

The Agency Spectrum of Trading Systems. From left to right: Prediction Models (e.g., FinBERT, StockBERT) perceive market information but lack decision-making capabilities; Signal Generators (e.g., AlphaGen, FactorMiner) add decision layers but remain non-executing; Partial Agents (e.g., FinVis-GPT without execution) incorporate memory but lack action modules; Trading Agents (e.g., FinAgent, TradingAgents) close the perception–memory–reasoning–action loop; Full Ecosystems (e.g., multi-agent markets) add adaptation and coordination. For this survey's primary empirical subset, studies must satisfy both minimum criteria shown by the inclusion boundary: Action Output and Closed-Loop Evaluation. Works left of that boundary may inform background discussion, but they do not enter primary, protocol-reporting, or reproducibility statistics.

This survey builds on a curated evidence ledger of 
included studies in the current auditable snapshot screened through
2026-03-09. Within that ledger, the primary empirical subset
(n=) is reserved for
studies that satisfy Action Output + Closed-Loop Evaluation, whereas
the remaining included studies provide design and
landscape context without entering protocol or reproducibility denominators.
Within the current primary subset, protocol-critical reporting remains sparse:
only / studies disclose an
extractable time-consistent data split, /
specifies a transaction-cost model, /
documents universe/survivorship handling, /
reports execution timing or semantics, /
are coded as R0, and / reach R3 reproducibility.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Introduction]
s on a curated evidence ledger of 
included studies in the current auditable snapshot screened through
2026-03-09. Within that ledger, the primary empirical subset
(n=) is reserved for
studies that satisfy Action Output + Closed-Loop Evaluation, whereas
the remaining included studies provide design and
landscape context without entering protocol or reproducibility denominators.
Within the current primary subset, protocol-critical reporting remains sparse:
only / studies disclose an
extractable time-consistent data split, /
specifies a transaction-cost model, /
documents universe/survivorship handling, /
reports execution timing or semantics, /
are coded as R0, and / reach R3 reproducibility.

This agentic architecture may offer practical advantages, but they are not
automatic and depend on careful instrumentation and evaluation. First, LLM-based
agents can generate human-readable rationales and
interaction traces; however, such text is not guaranteed to be faithful to the
true internal decision process. Meaningful auditability therefore depends on
grounded, time-stamped tool calls, data snapshots, and execution logs that can
be independently verified. Second, agents can adapt their strategies under
evolving market conditions by drawing on accumulated experience, although
robustness depends on careful validation and control. Third, modular designs
enable specialized components for perception, memory, and reasoning (see <Ref>), which can
make systems easier to extend, test, and improve over time. Because trading is a
multi-step setting, hallucinated facts or tool outputs can propagate through
agent loops; we return to these risks in <Ref>.

Trading agents are financial decision-support pipelines: they transform
market observations into executable actions through retrieval, memory,
reasoning, execution constraints, and supervisory controls. Reviewing this
literature therefore requires evidence about the full decision loop: what
information is used, how actions are formed, which safeguards bind execution,
and what artifacts allow expert audit. This perspective motivates our emphasis
on action semantics, protocol reporting, and reproducible evidence, rather than
backtest scores alone.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Introduction]
. Because trading is a
multi-step setting, hallucinated facts or tool outputs can propagate through
agent loops; we return to these risks in <Ref>.

Trading agents are financial decision-support pipelines: they transform
market observations into executable actions through retrieval, memory,
reasoning, execution constraints, and supervisory controls. Reviewing this
literature therefore requires evidence about the full decision loop: what
information is used, how actions are formed, which safeguards bind execution,
and what artifacts allow expert audit. This perspective motivates our emphasis
on action semantics, protocol reporting, and reproducible evidence, rather than
backtest scores alone.

Despite the rapid emergence of LLM-based trading systems, the literature
lacks a shared review lens for separating agent boundaries, protocol reporting,
and architectural roles. Recent surveys and benchmarks often emphasize task
coverage and model-level performance—for example, benchmark suites such as the FinBen suite
<cit.>, PIXIU <cit.>, and InvestorBench
<cit.>, alongside finance-specific model/tool works such as
FinGPT <cit.>. Broader overviews of LLM agents in finance and
trading <cit.> are also useful.
While valuable, these works typically do not provide a systematic account of
how agents perceive market data, store and retrieve information, reason about
trading decisions, execute actions under market frictions, or adapt their
behavior over time.

Selected related surveys/benchmarks and auditability-oriented review emphasis. Criteria: Primary=central organizing concern; Partial=discussed qualitatively or for a subset of works; Background=appears mainly as supporting context; Not primary=outside the work's main review objective. Arch: architecture-centric organization (perception/memory/reasoning/action); Exec/Cost: explicit execution semantics and transaction-cost modeling; Map: structured evidence mapping table (≥20 papers); R: reproducibility tier assessment (R0–R3).

 Work Type Scope Arch Exec/Cost Map R

tradingagent_main!15
 This survey Survey Trading Agents Primary Primary Primary Primary

[c]LLM-Agent Survey 
<cit.> Survey [c]General AI
Agents Primary Partial Not primary Not primary

[c]Giglio-Kelly-Xiu 
<cit.> Survey [c]Asset Pricing
ML Background Partial Not primary Not primary

[c]FinBen 
<cit.> Benchmark Financial Tasks Not primary Not primary Not primary Not primary

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Introduction]
 the work's main review objective. Arch: architecture-centric organization (perception/memory/reasoning/action); Exec/Cost: explicit execution semantics and transaction-cost modeling; Map: structured evidence mapping table (≥20 papers); R: reproducibility tier assessment (R0–R3).

 Work Type Scope Arch Exec/Cost Map R

tradingagent_main!15
 This survey Survey Trading Agents Primary Primary Primary Primary

[c]LLM-Agent Survey 
<cit.> Survey [c]General AI
Agents Primary Partial Not primary Not primary

[c]Giglio-Kelly-Xiu 
<cit.> Survey [c]Asset Pricing
ML Background Partial Not primary Not primary

[c]FinBen 
<cit.> Benchmark Financial Tasks Not primary Not primary Not primary Not primary

[c]FinGPT 
<cit.> Model/Tool Financial NLP Not primary Not primary Not primary Not primary

[c]InvestorBench 
<cit.> Benchmark Trading Tasks Not primary Partial Not primary Not primary

[c]LLM-Trading Survey 
<cit.> Survey Trading Agents Partial Partial Not primary Not primary

[c]LLM-Finance Survey 
<cit.> Survey Finance Agents Partial Partial Not primary Not primary

Note: Comparison criteria reflect our auditability-focused perspective.
 Other surveys prioritize different goals (e.g., model benchmarking, general
 agent architectures) where our criteria may not apply. FinBen and InvestorBench
 are benchmarks rather than surveys; evaluating them on “architecture coverage”
 may be inappropriate to their design goals.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Related Surveys and Positioning]
Several recent surveys examine aspects of AI in trading and finance, but they
usually pursue different review objectives than the architecture-centric,
protocol-aware perspective used here. We position our work against three
categories of related surveys.

General LLM-Agent Surveys.
A widely cited general survey by <cit.> reviews
LLM-based autonomous agents across domains, organizing around agent
construction, application, and evaluation. While foundational for general agent
design, this survey does not focus on finance-specific concerns such as
transaction-cost modeling, market-friction constraints, or the temporal
structure of trading data. Our work complements this by focusing narrowly on
trading, where execution semantics and cost assumptions are first-class
concerns.

Financial Machine Learning Surveys.
<cit.> survey recent methodological contributions in asset pricing using factor models and machine learning, organizing the literature around expected returns, factors, risk exposures, risk premia, the stochastic discount factor, model comparison, and alpha testing. Their scope remains centered on asset-pricing estimation and inference rather than the agentic problem of mapping predictions into executable actions under market constraints.

Task-Oriented Financial Benchmarks.
The FinBen suite <cit.>, InvestorBench <cit.>, and finance-specific works such as FinGPT <cit.> and PIXIU <cit.> emphasize task coverage and model-level performance evaluation. These benchmarks are valuable for comparing models on specific financial NLP or forecasting tasks, but they typically do not require end-to-end agentic evaluation—that is, closed-loop action generation under market frictions with explicit execution semantics. Our survey focuses specifically on works that close this loop, mapping perception through execution.

This gap is particularly problematic given the interdisciplinary nature of
agentic trading systems, which draws from artificial intelligence, quantitative
finance, cognitive science, and economics. Without a unifying framework,
researchers and practitioners struggle to compare approaches, identify
overlapping innovations, or systematically explore the design space of trading
agents.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy Gap: Why Existing Frameworks Leave Open Gaps]
While the surveys reviewed above provide valuable coverage, they share a common
limitation: they treat trading agents as either applications of general
LLM-agent techniques or as prediction models with execution as an
afterthought. This leads to systematic misclassifications that obscure critical
design choices and hinder comparative analysis.

Limitation 1: Execution as Implicit Component.
Existing frameworks typically treat action/execution as a byproduct of reasoning
rather than a first-class architectural component. For example, FinAgent
<cit.> is categorized as “Multi-modal Financial Agent” in
<cit.>, emphasizing its perception module while
underplaying its execution layer—a critical component for evaluating real-world
deployability. The Architecture-Capability-Adaptation (A-C-A) lens treats
Action/Execution as a core architectural dimension, making order mapping, cost
assumptions, and latency constraints explicit (<Ref>).

Limitation 2: Architecture-Capability Conflation.
Prior surveys often conflate mechanism (how agents process information)
with function (what agents accomplish). For instance, AlphaAgent
<cit.> is a multi-agent alpha-mining framework whose regularized
exploration mechanisms—originality enforcement, hypothesis-factor alignment,
and complexity control—help counteract alpha decay. The A-C-A lens
distinguishes these concerns: the same Reactive Architecture can support both Alpha
Generation (high-frequency signals) and Execution (order slicing), while
Strategic Architecture enables Portfolio Management (long-horizon planning)
across different functional domains (<Ref>).

Limitation 3: Adaptation as Implementation Detail.
Current frameworks treat learning and adaptation as homogeneous implementation
details rather than a cross-cutting design dimension. TradingAgents
<cit.> is classified as “Multi-agent Framework” without
distinction between its hierarchical role organization (Architecture), its
distributed capability allocation (Capability), and its feedback-based adaptation
(Adaptation). The A-C-A lens makes adaptation levels explicit, from
in-context learning (behavioral) to self-evolution (structural), with
distinct protocol requirements for each (<Ref>).

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy Gap: Why Existing Frameworks Leave Open Gaps]
ure enables Portfolio Management (long-horizon planning)
across different functional domains (<Ref>).

Limitation 3: Adaptation as Implementation Detail.
Current frameworks treat learning and adaptation as homogeneous implementation
details rather than a cross-cutting design dimension. TradingAgents
<cit.> is classified as “Multi-agent Framework” without
distinction between its hierarchical role organization (Architecture), its
distributed capability allocation (Capability), and its feedback-based adaptation
(Adaptation). The A-C-A lens makes adaptation levels explicit, from
in-context learning (behavioral) to self-evolution (structural), with
distinct protocol requirements for each (<Ref>).

<Ref> illustrates how three representative works can be
re-read under the A-C-A exploratory analytical lens, making architectural distinctions more
explicit than in prior categorizations. <Ref>
provides additional reclassification notes for representative papers as
illustrative material rather than an external validation study.

Taxonomy comparison: how existing frameworks classify representative
 works versus the A-C-A exploratory analytical lens. The A-C-A lens offers architectural
 granularity that complements (rather than refutes) prior categorizations; this table is illustrative rather than externally validated.

 Work Prior Framework A-C-A Reclassification

FinAgent <cit.> “Multi-modal Agent” (perception-centric) Architecture: Multi-modal Perception + Execution; Capability: Cross-modal Alpha; Adaptation: In-context learning

AlphaAgent <cit.> “Multi-agent” (organization-centric) Architecture: Reflective/Strategic hybrid Reasoning; Capability: Code-based Alpha with validation feedback; Adaptation: Regularized exploration against alpha decay

TradingAgents <cit.> “Multi-agent Framework” (organization-centric) Architecture: Hierarchical role-based Coordination; Capability: Distributed Alpha+Portfolio+Risk; Adaptation: Hierarchical feedback

We present a survey of LLM-based trading agents through an audit-oriented
expert-system perspective. Our contributions are ordered by evidential
strength:

* An auditable evidence ledger under explicit inclusion
 criteria, separating  included studies into a fixed
 primary empirical subset (n=) and a background tier
 (n=).

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy Gap: Why Existing Frameworks Leave Open Gaps]
-centric) Architecture: Reflective/Strategic hybrid Reasoning; Capability: Code-based Alpha with validation feedback; Adaptation: Regularized exploration against alpha decay

TradingAgents <cit.> “Multi-agent Framework” (organization-centric) Architecture: Hierarchical role-based Coordination; Capability: Distributed Alpha+Portfolio+Risk; Adaptation: Hierarchical feedback

We present a survey of LLM-based trading agents through an audit-oriented
expert-system perspective. Our contributions are ordered by evidential
strength:

* An auditable evidence ledger under explicit inclusion
 criteria, separating  included studies into a fixed
 primary empirical subset (n=) and a background tier
 (n=).

* A protocol and reproducibility audit showing that the
 current primary subset is not yet protocol-comparable:
 / studies report extractable
 split protocols, / report
 explicit cost models, / 
 report universe/survivorship handling, / 
 report execution semantics, / are R0,
 and / reach R3.

* An expert-system decision-pipeline framing that maps
 perception to knowledge acquisition, memory/RAG to the knowledge base,
 reasoning to the inference engine, execution to the action interface,
 risk/compliance to rule constraints, and logs/human oversight to
 explanation and accountability artifacts.

* A-C-A as a working analytical lens, used to locate where
 architecture, capability, and adaptation choices create reporting gaps
 across the decision pipeline. We do not present A-C-A as an externally
 validated taxonomy.

* Reporting checklists and methodological implications
 that separate evidence findings, background concepts, and author
 proposals, and translate recurring protocol gaps into minimum reporting
 expectations for future studies.

< g r a p h i c s >

Reasoning flow diagram. The agent receives input from perception and
 memory, applies reasoning mechanisms to generate candidate actions, evaluates
 these actions through forward planning or reflection, selects the best action,
 and executes it through the action module. Feedback loops enable learning
 and adaptation over time. This figure is schematic and is not used for
 evidence-mapping statistics or protocol comparison.

The remainder of this paper is organized as follows.

<Ref> describes the review protocol and evidence scope.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy Gap: Why Existing Frameworks Leave Open Gaps]
 background concepts, and author
 proposals, and translate recurring protocol gaps into minimum reporting
 expectations for future studies.

< g r a p h i c s >

Reasoning flow diagram. The agent receives input from perception and
 memory, applies reasoning mechanisms to generate candidate actions, evaluates
 these actions through forward planning or reflection, selects the best action,
 and executes it through the action module. Feedback loops enable learning
 and adaptation over time. This figure is schematic and is not used for
 evidence-mapping statistics or protocol comparison.

The remainder of this paper is organized as follows.

<Ref> describes the review protocol and evidence scope.

Part I: Architecture (<Ref>)
presents the core architectural components.
Part II: Capability (<Ref>)
analyzes the capabilities enabled by this architecture.
Part III: Adaptation (<Ref>)
explores how agents adapt and evolve.
<Ref> discusses technical challenges and future directions,
and <Ref> concludes the survey.

We begin by establishing the foundational understanding of what constitutes an
agentic trader, drawing on cognitive science and artificial intelligence
literature to define the essential architectural components.

Part I addresses the fundamental question: What constitutes an agentic
 trader? We argue that an agentic trader can be characterized by four core architectural
components—perception, memory, reasoning, and action/execution—that together support
autonomous decision-making in financial markets. While traditional trading systems focus
primarily on prediction, agentic systems typically include an explicit cognitive
loop that can interact with and learn from the market environment through decisions
that are mapped to tradable actions under market constraints.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Review Protocol and Evidence Scope]
This review is designed as an audit-oriented evidence map rather than an
exhaustive systematic review. Our goal is to make the evidentiary boundary of
agentic trading explicit, to separate primary trading evidence from background
design context, and to calibrate synthesis claims to protocol completeness
rather than to headline performance alone.

We scoped the formal search to records published from 2022-01-01
through 2026-03-09 (last query date: 2026-03-09), using ACM
Digital Library (including ICAIF), IEEE Xplore, arXiv, SSRN, and Google
Scholar, complemented by backward and forward citation chaining. We start the
focused window in 2022 because this is the period in which LLM-based systems
begin to appear as end-to-end trading agents rather than as isolated NLP or
forecasting components. After deduplication and screening, the current ledger
contains included studies from candidate
records.

To make the review boundary reproducible, we distinguish three fixed
denominators throughout the manuscript. The candidate registry
contains unique records after deduplication. The
included evidence-mapping ledger contains records
retained for either primary evidence or background/design context. The
primary empirical subset contains records that satisfy
Action Output, Closed-Loop Evaluation, and an eligible empirical evaluation type
(, , , or );
all protocol-field percentages, reproducibility percentages, and
claim-to-evidence summaries use this
-record subset unless explicitly stated otherwise.

Study selection summary using the canonical candidate registry. The denominator is the 92-record deduplicated registry. Final exclusions are outside the survey domain; finance-relevant records that lack Action Output or Closed-Loop Evaluation remain in the included background tier. Detailed logs and per-record decisions are provided in Supplementary Material S1.

 Stage Count

Registry candidate recordsa

Included in evidence mapping set

Excluded at screening/eligibility

Final exclusion reason

Outside finance/trading/portfolio/risk-management scope

Included evidence-map partition

Primary empirical subset

Background/context tier

aThe canonical registry currently contains unique records after deduplication (included in the evidence mapping set and excluded at screening/eligibility). The included evidence mapping set is partitioned into primary empirical studies and background/context records.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Review Protocol and Evidence Scope]
or Closed-Loop Evaluation remain in the included background tier. Detailed logs and per-record decisions are provided in Supplementary Material S1.

 Stage Count

Registry candidate recordsa

Included in evidence mapping set

Excluded at screening/eligibility

Final exclusion reason

Outside finance/trading/portfolio/risk-management scope

Included evidence-map partition

Primary empirical subset

Background/context tier

aThe canonical registry currently contains unique records after deduplication (included in the evidence mapping set and excluded at screening/eligibility). The included evidence mapping set is partitioned into primary empirical studies and background/context records.

Our inclusion boundary is intentionally narrow. To enter the primary
empirical subset, a study must satisfy both of the following conditions:
(i) Action Output, meaning that the system emits tradable actions such
as orders, position changes, or portfolio allocations; and (ii)
Closed-Loop Evaluation, meaning that those actions are evaluated in
backtesting, simulation, or live trading rather than only through predictive
metrics. Studies that remain useful for architectural or contextual discussion
but do not satisfy both conditions are retained as Background (BG)
within the included ledger. Under this rule, the present snapshot yields
primary empirical studies and background
studies. All protocol, denominator-based, and reproducibility summaries in this
survey are computed over the fixed primary subset unless stated otherwise.

The screening workflow proceeded in four steps. First, database and
preprint searches were run with agent/trading/finance keyword families and then
expanded through backward and forward citation chaining. Second, duplicate
records were removed by title, arXiv identifier, DOI, and manual inspection.
Third, title/abstract screening removed records outside financial trading,
portfolio construction, execution, or risk-management settings. Fourth,
full-text screening assigned each retained record to either primary empirical
evidence or background context. Studies were excluded from the candidate
registry only when they fell outside the survey domain; papers that were
finance-relevant but lacked Action Output or Closed-Loop Evaluation were kept
as background context rather than counted as final exclusions.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Review Protocol and Evidence Scope]
ng/finance keyword families and then
expanded through backward and forward citation chaining. Second, duplicate
records were removed by title, arXiv identifier, DOI, and manual inspection.
Third, title/abstract screening removed records outside financial trading,
portfolio construction, execution, or risk-management settings. Fourth,
full-text screening assigned each retained record to either primary empirical
evidence or background context. Studies were excluded from the candidate
registry only when they fell outside the survey domain; papers that were
finance-relevant but lacked Action Output or Closed-Loop Evaluation were kept
as background context rather than counted as final exclusions.

For each included study, we code two classes of information. The first is
architectural scope: perception, memory, reasoning, action/execution, and
adaptation. The second is protocol-critical reporting: time-consistent split
discipline, execution timing or semantics, transaction-cost modeling,
universe/survivorship handling, and reproducibility artifacts. Missing or
unclear reporting is coded conservatively as NR/Unknown rather than
imputed. This coding is intended to support transparent evidence accounting and
cautious cross-paper synthesis, especially in a literature where execution
realism, leakage control, and artifact availability remain uneven.

We audited the screening stage on a stratified double-screening sample
of 182 raw screening records in Supplementary Material S1. Because that sample
predates the final 92-record canonical registry, it is retained only as a
screening-boundary quality check. It is not used as evidence for
extraction-level protocol fields, reproducibility tiers, or A-C-A
classification robustness. To address the more consequential coding decisions,
we added a targeted extraction-level audit over fixed-seed primary studies (seed=20260426). The audit covers action output,
closed-loop evaluation, evidence role, evaluation type, split protocol, cost
model, execution semantics, universe/survivorship handling, artifacts, and
R0–R3 reproducibility. The per-study coding sheet and adjudication notes are
provided in Supplementary Material S3.

Reliability and coding-quality audits reported with the submission package.

 Audit layer Sample Observed agreement Agreement note Scope

S1 screening-boundary audit 182 raw records Reported in S1 Boundary only Inclusion/exclusion and screening-stage labels

S3 extraction-level audit primary studies

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Review Protocol and Evidence Scope]
ns,
we added a targeted extraction-level audit over fixed-seed primary studies (seed=20260426). The audit covers action output,
closed-loop evaluation, evidence role, evaluation type, split protocol, cost
model, execution semantics, universe/survivorship handling, artifacts, and
R0–R3 reproducibility. The per-study coding sheet and adjudication notes are
provided in Supplementary Material S3.

Reliability and coding-quality audits reported with the submission package.

 Audit layer Sample Observed agreement Agreement note Scope

S1 screening-boundary audit 182 raw records Reported in S1 Boundary only Inclusion/exclusion and screening-stage labels

S3 extraction-level audit primary studies

Accordingly, the A-C-A lens should be read as an exploratory
analytical lens for organizing the current evidence base, not as a settled or
externally established classification scheme. Corpus-level descriptive statistics for protocol
reporting, reproducibility, and peer-review status are summarized in
<Ref>; boundary decisions and final exclusions
are summarized in <Ref>. Detailed query strings,
screening logs, extraction tables, reliability-audit files, and coding notes are provided in
Supplementary Materials S1–S3.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Agentic Trading as an Expert-System Decision Pipeline]
For the purposes of ESWA, we interpret LLM-based trading agents as
expert-system decision pipelines. This framing makes the evaluation problem
explicit. Perception modules perform knowledge acquisition from prices, news,
filings, social media, and market microstructure signals. Memory,
retrieval-augmented generation, and tool-mediated context stores form a
knowledge base whose provenance and update rules must be inspectable. Reasoning
modules act as inference engines that convert state representations into
hypotheses, rationales, and candidate decisions. Action and execution modules
form the external action interface, where target weights, orders, fills,
latency assumptions, and market frictions must be made explicit. Risk controls,
compliance filters, and portfolio limits serve as rule constraints on the path
from inference to action. Finally, logs, immutable artifacts, and human
oversight provide the explanation and accountability layer expected of
decision-support systems.

This expert-system framing motivates the protocol audit in the rest of
the paper. A trading agent can appear architecturally sophisticated while still
being empirically weak if the evaluation omits temporal splits, transaction
costs, universe construction, execution semantics, or reproducible artifacts.
The A-C-A lens is therefore used to locate evidence gaps across the pipeline:
architecture describes where knowledge is acquired, stored, inferred, and acted
upon; capability describes which trading function is being supported; and
adaptation describes how the decision pipeline changes under feedback.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Perceptual Architecture]
The preceding section introduced the cognitive architecture of agentic traders.
This section addresses the question: “How do agents perceive
financial markets?”

In this survey, we strictly define Perception as the mechanism by which an agent acquires a state observation O_t from the environment state S_t at decision time t. This distinction is critical: general financial NLP or time-series forecasting models (e.g., standalone BERT or LSTM predictors) are considered Background (BG) unless they are explicitly integrated into an agent's decision loop. Under the primary-subset boundary specified in <Ref>, BG systems lack the closed-loop integration required for agentic classification but may provide valuable perceptual capabilities that end-to-end agents incorporate.

A perception module must do more than predict; it must provide actionable state representations—such as sentiment scores, market regime indicators, or visual summaries—that the agent's reasoning component can utilize to formulate valid actions.

We mobilize the evidence set to analyze perception across three distinct modalities, refined to separate visual signals from numerical data.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: Perception claims are supported only when a modality is embedded in an action-producing, closed-loop trading agent; standalone financial NLP, forecasting, or chart-analysis papers are retained as background.

 2) Supported claim: The current evidence supports perception as an input contract for agent decisions, not as an independently validated source of trading profitability.

 3) Reporting gap: Most studies do not expose timestamp availability, modality latency, or retrieval logs.

 4) Implication: Perception modules should be reported as auditable state-construction pipelines before their downstream performance claims are compared.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* Text-based Perception (<Ref>): Processing unstructured linguistic data (news, reports).

 * Time-Series & Structured Perception (<Ref>): Processing numerical sequences (price, volume) and structured fundamentals.

 * Visual & Multimodal Perception (<Ref>): Processing chart images and fusing heterogeneous data streams.

 < g r a p h i c s >

 Three perceptual modalities in agentic trading. Text-based perception processes linguistic information from news and reports. Time-series perception analyzes numerical patterns in price and volume data. Multimodal perception integrates heterogeneous data sources through cross-modal fusion mechanisms. This figure is schematic and is not used for evidence-mapping statistics or protocol comparison.

<Ref> illustrates the three perceptual modalities, showing the progression from single-modality processing (text-only or time-series-only) to integrated multimodal perception. This progression reflects both the increasing complexity of perceptual mechanisms and the expanding scope of information that agents can leverage.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Text-based Perception]
Text-based perception refers to the acquisition of state observations O_t
from linguistic information sources (news articles, earnings reports, analyst
commentary, social media posts, regulatory filings) at decision time t. The
module encodes textual inputs into representations—such as sentiment scores,
event embeddings, or contextualized vectors—that the reasoning component can
utilize to formulate actions.

Representative Approaches. Several lines of work have developed
specialized architectures for financial text understanding. Du et al.
<cit.> provide a comprehensive survey of financial sentiment
analysis techniques, reviewing prior evidence that sentiment signals are often
associated with subsequent market movements. Iacovides et al.
<cit.> introduce FinLlama, an LLM-based approach
fine-tuned for financial sentiment analysis in algorithmic trading scenarios.
Zhang et al. <cit.> propose Instruct-FinGPT, which uses
instruction tuning to adapt general-purpose LLMs to financial sentiment tasks,
while Zhang et al. <cit.> explore retrieval-augmented
generation to enhance sentiment analysis with external knowledge.

Technical Mechanisms. Text-based perception typically follows a
pipeline of tokenization, encoding, and extraction. Domain-specific language
models such as FinBERT <cit.> provide contextualized
representations of financial text, capturing terminology and semantic nuances
that are often underrepresented in general-purpose models. Rodriguez Inserte et al.
<cit.> show that adapting large language models through
task-specific fine-tuning can improve performance on financial sentiment tasks.
Sentiment classification models then map these representations to polarity labels
(e.g., positive, negative, and neutral) or to more fine-grained affective states.
Xing et al. <cit.> further study heterogeneous LLM agents
for financial sentiment analysis and report improved benchmark performance
relative to selected baselines.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Text-based Perception]
in-specific language
models such as FinBERT <cit.> provide contextualized
representations of financial text, capturing terminology and semantic nuances
that are often underrepresented in general-purpose models. Rodriguez Inserte et al.
<cit.> show that adapting large language models through
task-specific fine-tuning can improve performance on financial sentiment tasks.
Sentiment classification models then map these representations to polarity labels
(e.g., positive, negative, and neutral) or to more fine-grained affective states.
Xing et al. <cit.> further study heterogeneous LLM agents
for financial sentiment analysis and report improved benchmark performance
relative to selected baselines.

Critical Challenge: Temporal Alignment. A pervasive risk in text
perception is look-ahead bias. News timestamps often record publication time
rather than the exact time at which an item becomes available to a trading
pipeline, creating a mismatch between historical records and executable decision
contexts. Agents trained on historical news corpora without explicit
ingestion-lag modeling or embargo enforcement are therefore likely to exhibit
inflated backtest performance. A related issue is that some financial
disclosures and structured reports are revised after initial release; using
retrospectively cleaned or final versions in backtesting can introduce serious
data leakage <cit.>.

<Ref> summarizes representative text-based perception
methods, highlighting the diversity of data sources and technical approaches.
While effective for textual information, these methods cannot directly process
numerical price data or visual chart patterns, motivating the need for
complementary perceptual modalities.

Text-based perception methods. Audit Status: =Background Model (not integrated into agent loop); =Reproducibility Level (see <Ref>). Time Disc.=Time Discipline (=offline batch processing; =real-time streaming with specified latency).

 Reference Input Source Representation Time Disc. Audit

FinBERT <cit.> News Headlines Sentiment Score (Scalar) Static

FinGPT <cit.> News/Social Summary/Embedding Static

BloombergGPT <cit.> Financial Corpus General LM Static

FinLlama <cit.> Reports Instruction Tuned Static

Instruct-FinGPT <cit.> Financial Text Instruction Tuned Static

RAG-FinGPT <cit.> Mixed Sources Retrieval-Augmented Static

Heterogeneous Agents <cit.> Multi-source Specialized Architectures Static

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Time-Series & Structured Perception]
Time-series and structured perception refers to the acquisition of state
observations O_t from numerical sequences (price, volume, Limit Order Books—LOB) and structured fundamental data (e.g., balance sheet tables) at decision time t. This modality encodes temporal patterns—such as trend indicators, volatility estimates, or regime classifications—into representations the reasoning component can utilize. It encompasses not only price and volume sequences (Open-High-Low-Close-Volume—OHLCV), but also deeper market structures such as LOB, options-implied state variables, and structured fundamental information. Because these inputs evolve over time, agents must deal with temporal dependence, seasonality, structural breaks, and non-stationary distributions when constructing actionable state representations.

Representative Approaches. Representative work in this area studies how
sequence models encode information from market data streams into trading-relevant
state representations. Recent systems use transformer-style or attention-based
encoders to summarize price dynamics, while classical econometric approaches
remain useful for regime identification and structural-change analysis. In the
current agentic trading literature, however, most implemented systems still rely
on relatively accessible OHLCV-style inputs; explicit use of high-frequency LOB
data and richly structured fundamentals remains comparatively limited.

Technical Mechanisms. Key challenges include non-stationarity, noise,
and sensitivity to temporal misalignment. Successful approaches often employ
attention mechanisms to focus on informative time points, regime-switching models
to capture structural breaks <cit.>, and
representation-learning objectives that improve robustness under changing market
conditions. Standard positional encodings and related sequence-ordering schemes
can also help models capture periodic structure and temporal context in
sequential financial data <cit.>.

Time-series and structured perception methods. Time Disc.: =Real-time capable; =Offline dataset.

 Reference Input Data Mechanism Time Disc. Audit

VISTA <cit.> Market Time Series Sequence Modeling Framework RT

EarnHFT <cit.> Crypto Market States Hierarchical RL RT

Regime-Switching <cit.> Returns Hidden Markov Model Static

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Time-Series & Structured Perception]
o focus on informative time points, regime-switching models
to capture structural breaks <cit.>, and
representation-learning objectives that improve robustness under changing market
conditions. Standard positional encodings and related sequence-ordering schemes
can also help models capture periodic structure and temporal context in
sequential financial data <cit.>.

Time-series and structured perception methods. Time Disc.: =Real-time capable; =Offline dataset.

 Reference Input Data Mechanism Time Disc. Audit

VISTA <cit.> Market Time Series Sequence Modeling Framework RT

EarnHFT <cit.> Crypto Market States Hierarchical RL RT

Regime-Switching <cit.> Returns Hidden Markov Model Static

<Ref> compares representative time-series perception
methods. While powerful for numerical data, these methods cannot directly
incorporate the rich contextual information available in text, creating a need
for multimodal perception.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Visual & Multimodal Perception]
Visual and multimodal perception refers to the acquisition of state observations
O_t from heterogeneous sources (chart images, text, numerical series, audio) at
decision time t, integrating these into unified representations through
cross-modal alignment mechanisms. This reflects the reality where traders synthesize visual technical patterns with news flow and price action.

Representative Approaches. For visual perception, Wang et al.
<cit.> introduce FinVis-GPT for financial chart analysis,
treating chart-like market representations as visual inputs that can be linked
to language-based interpretation. For multimodal fusion, Zhang et al.
<cit.> introduce FinAgent, which combines textual news and
numerical market information through a cross-modal pipeline designed for trading
decisions. More broadly, multimodal systems differ in where fusion occurs:
early-fusion approaches combine low-level inputs before representation learning,
whereas late-fusion approaches aggregate higher-level features from separate
encoders.

Critical Challenge: Cross-Modal Asynchrony. Fusing modalities with
different update frequencies creates synchronization risks. News arrives
sporadically, whereas market and LOB data may update at much higher frequency.
Naive framing strategies such as pairing the latest available news item with the
current price can therefore misrepresent the true decision context when the text
signal is stale. In addition, visual interpretation and multimodal inference
introduce nontrivial latency, which can make the perceived market state outdated
by the time the agent acts in live settings. For this reason, protocol reporting
should explicitly state perception-latency assumptions and alignment procedures.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Visual & Multimodal Perception]
Critical Challenge: Cross-Modal Asynchrony. Fusing modalities with
different update frequencies creates synchronization risks. News arrives
sporadically, whereas market and LOB data may update at much higher frequency.
Naive framing strategies such as pairing the latest available news item with the
current price can therefore misrepresent the true decision context when the text
signal is stale. In addition, visual interpretation and multimodal inference
introduce nontrivial latency, which can make the perceived market state outdated
by the time the agent acts in live settings. For this reason, protocol reporting
should explicitly state perception-latency assumptions and alignment procedures.

Technical Mechanisms. Multimodal fusion poses significant challenges:
different modalities have different dimensionalities, temporal resolutions, and
noise characteristics. Early fusion concatenates raw features from all modalities
before processing, while late fusion maintains separate processing pipelines and
combines high-level representations. Cross-attention mechanisms provide a
flexible alternative by enabling one modality to attend selectively to another
during representation learning <cit.>.
Temporal alignment remains especially difficult in financial settings, because
textual events arrive discretely while prices update continuously. Preventing
look-ahead bias therefore requires strict timestamp discipline, explicit embargo
handling, and clearly reported latency budgets <cit.>.

< g r a p h i c s >

Multimodal fusion flow in agentic trading. The diagram illustrates
 how text encoders and time-series encoders process their respective inputs
 before a cross-modal fusion layer integrates the representations into a unified
 market understanding. This figure is schematic and is not used for
 evidence-mapping statistics or protocol comparison.

<Ref> illustrates the multimodal fusion pipeline, showing
how text encoders process news and reports while time-series encoders analyze price
movements, with a cross-modal fusion layer integrating these representations.

Visual and multimodal perception methods. Latency: Estimated inference latency (critical for alignment). Note: Latency estimates are author-reported; see Supplementary Material S2 for detailed benchmarking protocols.

 Reference Modalities Fusion Strategy Latency Audit

FinVis-GPT <cit.> Chart Images Vision-Language Analysis Low

FinAgent <cit.> News + Prices + Kline Charts Cross-Attention High

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Visual & Multimodal Perception]
ic and is not used for
 evidence-mapping statistics or protocol comparison.

<Ref> illustrates the multimodal fusion pipeline, showing
how text encoders process news and reports while time-series encoders analyze price
movements, with a cross-modal fusion layer integrating these representations.

Visual and multimodal perception methods. Latency: Estimated inference latency (critical for alignment). Note: Latency estimates are author-reported; see Supplementary Material S2 for detailed benchmarking protocols.

 Reference Modalities Fusion Strategy Latency Audit

FinVis-GPT <cit.> Chart Images Vision-Language Analysis Low

FinAgent <cit.> News + Prices + Kline Charts Cross-Attention High

Multimodal Transformer <cit.> Text + Audio Cross-Modal Attention Med

<Ref> summarizes representative visual and multimodal
perception approaches. Taken together, these studies suggest that richer market
state estimation often benefits from combining heterogeneous signals rather than
relying on a single modality in isolation.

Summary of perceptual architectures in trading agents. The Protocol Risk column highlights specific alignment challenges for each modality.

 Modality Primary Inputs Mechanism Protocol Risk Examples

Text-based News, Reports, Social Media LLM Fine-tuning, Prompting, Sentiment Analysis Publication Lag, Embargo Violations FinBERT, FinGPT

Time-Series OHLCV, LOB, Fundamentals Temporal Attention, Hierarchical RL, GNNs Look-ahead Bias, Data Revisions EarnHFT, VISTA

Visual/Multimodal Charts, Text+Price+Audio Vision-Language Analysis, Cross-Modal Attention Synchronization Latency, Causal Misalignment FinVis-GPT, FinAgent

In summary, this section has presented three perceptual modalities through which
trading agents acquire information from financial environments. Text-based
perception extracts signals from language, time-series perception models temporal
structure in numerical data, and multimodal perception integrates these
complementary signals. The perceptual mechanisms described here produce state
observations O_t that are stored and retrieved by memory architectures, which
we discuss next.

The next section addresses the question: “How do agents remember
and store information?”

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Memory Architecture]
The preceding section introduced perceptual mechanisms for gathering market
information. This section addresses the question: “How do
agents remember and store information?”

Our use of working, episodic, and semantic memory
draws on cognitive psychology, with episodic and semantic memory following
Tulving's distinction <cit.>, multi-store structure drawing
on Atkinson and Shiffrin <cit.>, and working memory following
Baddeley and Hitch <cit.>. While these terms originate from
human memory research, they map naturally to trading agents:

 * Episodic memory (experience-specific) → Historical trade records

 * Semantic memory (knowledge-general) → Financial domain knowledge

 * Working memory (active context) → Active trading context

This mapping has precedent in reinforcement learning literature on
memory-augmented agents <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: Memory claims are treated as primary only when memory state participates in a closed-loop trading evaluation; general RAG or cognitive-memory analogies remain background.

 2) Supported claim: Memory can organize market context and prior decisions, but the evidence does not yet identify a dominant memory architecture.

 3) Reporting gap: Papers rarely report update rules, retention windows, deletion policies, and replayable memory snapshots.

 4) Implication: Memory should be reported as a governed state store with explicit temporal boundaries, not only as a descriptive module.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Terminological Note]
Our use of “working,” “episodic,” and “semantic” memory adapts cognitive
psychology terminology for architectural description. We acknowledge these
analogies are imperfect: AI “episodic memory” lacks the subjective experience
and reconstructive processes of human episodic memory; “consolidation” in
neural systems differs fundamentally from synaptic mechanisms in biological
brains. We employ these terms for their intuitive organizational value while
recognizing the underlying mechanisms differ substantially.

Memory is the critical bridge between perception and reasoning, enabling agents
to accumulate experience over time rather than treating each trading decision
in isolation. We organize the memory architecture around a taxonomy of three
memory systems that differ in their temporal scale, capacity, and functional
role.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* Working Memory (<Ref>): Short-term buffer for active trading context and risk tracking.

 * Episodic Memory (<Ref>): Storage of specific trading episodes and market events.

 * Semantic Memory (<Ref>): Long-term knowledge base for financial concepts and strategies.

 < g r a p h i c s >

 Three memory systems in agentic trading. Working memory maintains
 immediate context (capacity: limited, duration: seconds-minutes). Episodic
 memory stores trading episodes (capacity: large, duration: long-term). Semantic
 memory encodes financial knowledge (capacity: very large, duration: permanent).
 This figure is schematic and is not used for evidence-mapping
 statistics or protocol comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Working Memory]
In agentic trading, working memory is often conflated with a generic
“context window.”For audit-oriented agent
design, we distinguish between the Deterministic State Store (Layer A)
and the Generative Context (Layer B).

Layer A: Deterministic State Store (Audit-Truth). This layer holds the
ground-truth state of the trading system, including current positions, open
orders, account balances, and risk limits. In an audit-oriented architecture, we
argue that it should be read-only to the LLM and updated solely by the
environment (e.g., EMS/OMS feedback). Treating this state as a
“memory”subject to forgetting or hallucination
is a critical vulnerability; in practice, it is better implemented as a
structured store exposed through tools or state queries, as seen in tool-using
trading agent designs <cit.>.

Layer B: Generative Context (Inference Scope). This layer corresponds to the LLM's active context window, containing the sliding history of observations, chain-of-thought reasonings, and recent reflections. Unlike Layer A, information here is transient and subject to eviction.

Technical Mechanisms. To manage Layer B's limited capacity, agents
employ eviction policies such as Summary-Compression (condensing old
steps into a narrative) or hierarchical memory management (using
layered storage and retrieval priorities to retain higher-value fragments)
<cit.>. A key design
trade-off is the context-to-noise ratio: maintaining too much history
can dilute attention and bury decision-relevant content in long contexts, a risk
consistent with the broader “Lost in the Middle”finding <cit.>, while aggressive pruning may drop reasoning
that is still relevant to a live position or pending order.

 Memory system comparison. Tags follow the convention in <Ref> for the representative reference.

 Memory Type Capacity Volatility Key Characteristics 

 Working Memory Limited (Context) Volatile Fast cache, eviction policies, sliding window 

 Episodic Memory Large (Disk) Persistent Vector embeddings, similarity search, temporal indexing 

 Semantic Memory Infinite Persistent Knowledge graphs, neuro-symbolic, consolidation 

<Ref> summarizes the three memory systems, highlighting their differing capacity constraints and temporal scales. While working memory enables rapid decision-making, episodic and semantic memory support long-term learning and knowledge accumulation.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Episodic Memory]
Episodic memory stores specific trading experiences. To ensure auditability, valid episodes must be defined as a tuple (S_t, A_t, O_t+k, τ), where S_t is the state, A_t is the action, O_t+k is the outcome realized at step t+k, and τ is the timestamp when this outcome becomes observable.

Information Leakage via Memory. We refer to a key vulnerability in
trading agents as the “Oracle Fallacy,”where
an agent retrieves a similar past episode that contains a post-hoc
narrative (e.g., “this trade failed due to news X released
tomorrow”).
[title=Protocol Implication]
 To prevent this, we suggest that reproducible trading-agent protocols enforce an
 Outcome Embargo: an episode recorded at t cannot expose its outcome
 field to retrieval until current time t_now≥ t+k.

Recent work has addressed the challenge of deterministic replay in financial agents, introducing assurance frameworks for regulatory audit 
<cit.>.

Representative Approaches. FinAgent <cit.>
uses layered memory with dual-level reflection and diversified retrieval,
though it appears to rely more on prompt-level control than on explicit
database-level temporal constraints. FinMem <cit.> introduces a layered memory architecture
with character design, demonstrating performance enhancement through structured
memory management. Reflexion <cit.> uses episodic storage to
prune bad trajectories, but assumes relatively prompt feedback from the
environment, a condition that becomes less natural in trading settings where
reward realization may be delayed.

Technical Mechanisms. Vector databases
<cit.> enable similarity search, but
naive cosine similarity is often insufficient for financial time-series.
“Time-Aware Retrieval”is therefore a useful
design principle.
[title=Protocol Implication]
 We suggest a relevance score f(q, k) that includes a decay term
 e^-λ(t_now - t_k) to prioritize recent regimes.

Furthermore,
Drift Handling is required: as market regimes shift (e.g., from low to
high volatility), old episodes with high feature similarity may still yield
misleading expectations, a risk consistent with recent retrieval-augmented
time-series forecasting evidence <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Semantic Memory]
Semantic memory stores domain knowledge (e.g., “high interest
rates hurt growth stocks”). For audit-oriented analysis, we
classify this memory not by its format (Graph vs. Text), but by its
Auditability:

Type 1: Parametric Memory (Implicit). This knowledge is encoded in the
model's weights via pre-training or fine-tuning (e.g., FinGPT
<cit.>). While efficient, it is relatively opaque
(difficult to trace why the model knows a fact) and comparatively
static (updates usually require additional training or alignment). For
trading, this raises the risk of “outdated priors,”where older market regularities may persist in model behavior after the regime
that produced them has changed.

Type 2: Non-Parametric Memory (Explicit). This involves retrieval from an external Knowledge Base (KB). We further distinguish between:

 * Curated KBs: Verified documents (Rulebooks, SEC Filings) where source integrity is high <cit.>.

 * Uncurated KBs: Open-web data (Social Media, Forums) susceptible to “Noise Injection”or adversarial poisoning.

Technical Mechanisms. To ensure integrity, “Source
Tracking”is a necessary design requirement: every retrieved
semantic fact should carry a provenance log (Document ID + Version Timestamp).
Knowledge Graphs encode explicit entity-relation structure (e.g.,
Entity_A Entity_B) and can therefore support
provenance-oriented reasoning and constraint checking more directly than
unstructured text alone.

 < g r a p h i c s >

 Memory retrieval mechanism. The agent formulates a query based on
 current context, searches the episodic memory database using similarity-based
 retrieval, and selects relevant episodes to inform the current decision. This
 figure is schematic and is not used for evidence-mapping statistics or
 protocol comparison.

 Comparison of memory retrieval mechanisms in trading agents. Tags follow the convention in <Ref> for the representative works in each row.

 Memory System Representative Ref Timestamp Rule Embargo Drift Check Audit Status 

 Working Memory FinMem <cit.> N/A N/A N/A 

 Episodic Memory FinAgent <cit.> NR NR No 

 Semantic Memory (Type 1) FinGPT <cit.> Implicit No No 

 Semantic Memory (Type 2) FinSage <cit.> Versioned Yes (Doc Date) Yes

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Design Trade-offs]
Strict auditability reveals critical design trade-offs that are often obscured in performance-only benchmarks.

Latency vs. Recall Depth. Deeper retrieval in high-fidelity RAG systems
can introduce latency that is incompatible with high-frequency or rapid
mid-frequency strategies. Agents therefore need to balance
retrieval depth against decision latency and
execution speed.

Context Length vs. Distraction. While newer LLMs support 1M+ token windows, simply stuffing all retrieved memories into context degrades reasoning due to the “Lost-in-the-Middle”phenomenon <cit.>. A strictly designed agent often performs better with less but higher-relevance context than with a raw dump of history.

Noise Injection Risk. Allowing uncurated semantic memory (e.g.,
scraping Reddit) increases the risk of “Noise
Injection,”where irrelevant or manipulated public sentiment
overrides the agent's core logical strategy. We therefore treat a
“Hierarchy of Truth”as a design principle:
internal Layer A state should override external noisy signals when the two
conflict.

In summary, this section has presented three memory systems that enable trading
agents to accumulate and leverage experience. Working memory provides immediate
context, episodic memory stores specific experiences, and semantic memory encodes
domain knowledge. The next section examines how agents reason over this stored
information to make trading decisions.

[float,floatplacement=tbp]Evidence Summary (Memory)

 * We treat memory design as an evaluation knob: retrieval choices (time-aware vs. naive similarity, windowing, truncation) can change decisions even with the same base model, so ablations should report memory settings <cit.>.

 * Episodic retrieval can improve robustness by grounding decisions in comparable past episodes, but retrieved context should remain timestamp-correct and embargo-aware to avoid leakage from post-event narratives <cit.>.

 * Implicit and explicit semantic memory can both accelerate adaptation, but neither retrieved documents nor generated rationales are automatically faithful; traceability depends on verifiable sources, versioning, and logs <cit.>.

 * Reporting gaps remain common across the audited literature: many papers describe memory at a high level but omit store contents, update cadence, and failure modes (staleness, retrieval drift), which limits comparability across studies (see <Ref>).

The next section addresses the question: “How do agents make
trading decisions?”

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reasoning Architecture]
The preceding sections explored how agents perceive markets and store information.
This section addresses the question: “How do agents make trading
decisions?”

Building on the notation from <Ref> and <Ref>,
we denote observations as O_t (state observations at time t) and
retrievable memories as M_episodic (episodic memory store).

Reasoning is treated here as the decision function that transforms perceptions
and memories into candidate actions. We organize reasoning architectures by a
Time-Scale Reasoning Paradigm because decision horizon, computational
budget, and search depth are more directly auditable than broad cognitive
analogies.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: Reasoning claims are grounded in primary studies only when the reasoning trace leads to tradable action under a backtest, simulation, live, or benchmark setting.

 2) Supported claim: LLM reasoning broadens the space of inspectable decision rationales, but current evidence supports it as a design pattern rather than a validated performance taxonomy.

 3) Reporting gap: Prompt versions, tool calls, search budgets, and failed reasoning branches are rarely logged.

 4) Implication: Reasoning modules should be evaluated with decision traces and ablations, not only with final returns.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* Reactive Reasoning (<Ref>): Millisecond-scale, intuitive decisions based on pattern recognition.

 * Reflective Reasoning (<Ref>): Second-scale, deliberate reasoning using multi-step chains of thought.

 * Strategic Reasoning (<Ref>): Hour/day-scale planning and optimization across extended time horizons.

[
 colback=tradingagent_light!10,
 colframe=tradingagent_light!60,
 title=Terminological Clarification: Reactive Reasoning]
 We use “reactive” strictly for non-LLM latency-constrained control.
 LLM-based methods (including ReAct adaptations) operate at second-scale or slower,
 placing them in the reflective category. This distinction is critical for
 avoiding the misconception that LLMs can support high-frequency trading decisions.

Figure <ref> provides a schematic comparison of these three paradigms by time-scale.

Reasoning I/O Contract. For audit-oriented trading agents, we model the reasoning module as a function f(O_t, M_episodic, P_portfolio) → (A_cand, α, V_check), where:

 * Inputs: timestamped observation O_t, retrievable memory M_episodic, and read-only portfolio state P_portfolio (positions, risk limits).

 * Outputs: a set of candidate actions A_cand, a confidence score α∈ [0,1], and a validity check V_check (e.g., "holds < max_leverage").

This contract is intended to reduce the risk of “hallucinated actions” by enforcing risk constraints during or immediately after the reasoning step, distinct from the final execution layer.

 < g r a p h i c s >

 Three reasoning paradigms compared by time-scale. Reactive reasoning
 prioritizes speed over accuracy, executing in milliseconds. Reflective reasoning
 balances speed and accuracy through multi-step reasoning. Strategic
 reasoning prioritizes accuracy through extensive planning, executing
 over minutes to hours. This figure is schematic and is not used for
 evidence-mapping statistics or protocol comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reactive Reasoning]
Reactive reasoning, loosely analogous to System 1 in dual-process theory
(while acknowledging that this framework lacks consensus definitions for
long-horizon planning), is characterized as a
constrained simplified decision optimized for latency budgets measured in
milliseconds to microseconds. Importantly, this paradigm does not involve
LLM-mediated deliberation—the latency of even lightweight LLMs (hundreds of
milliseconds) exceeds the budgets of high-frequency trading. Instead, reactive
trading systems employ rule-based controllers, lightweight neural networks
(often <100K parameters), or pre-compiled decision tables that execute in
constant time.

Representative Approaches. ReAct <cit.> exemplifies reflective (not reactive) reasoning
in general agent architectures—its “think” step involves explicit LLM inference
that operates at second-scale latency. In trading contexts requiring millisecond
response times, ReAct-style deliberation must be decoupled from the critical
 path and confined to offline analysis or non-latency-sensitive decision support.
Rule-based systems encode expert knowledge as if-then rules (e.g., “if price
crosses moving average, buy”), executing immediately when conditions are met.
These systems sacrifice flexibility for speed, relying on pre-defined patterns
rather than reasoning from first principles. The reactive paradigm is particularly
effective in relatively stable market regimes where previously learned patterns
remain actionable.
In agentic trading settings, this shallow-loop structure often appears as a
reactive component inside larger systems, for example through tool-augmented
signal retrieval plus constrained actions <cit.>, or through
role-specialized teams that decompose perception while preserving a structured
final decision pipeline <cit.>. Gradient-based policy
optimization can further couple reactive decisions to reward-driven updates
in interactive markets <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reactive Reasoning]
sacrifice flexibility for speed, relying on pre-defined patterns
rather than reasoning from first principles. The reactive paradigm is particularly
effective in relatively stable market regimes where previously learned patterns
remain actionable.
In agentic trading settings, this shallow-loop structure often appears as a
reactive component inside larger systems, for example through tool-augmented
signal retrieval plus constrained actions <cit.>, or through
role-specialized teams that decompose perception while preserving a structured
final decision pipeline <cit.>. Gradient-based policy
optimization can further couple reactive decisions to reward-driven updates
in interactive markets <cit.>.

Technical Mechanisms. Reactive systems employ feature extractors that
map raw market data to action logits, with the highest-logit action selected
and executed. Neural networks with shallow architectures and limited reasoning
depth are common, balancing prediction speed with accuracy. These architectures
typically employ
specialized layers such as temporal convolutional networks for processing
time-series data <cit.> or attention mechanisms for weighting relevant features <cit.>. In some
settings, a key advantage is relative interpretability: the mapping from a
small feature set to actions can be inspected and constrained <cit.>, though it does not
guarantee faithful explanations of decision logic.
However, these systems struggle with novel situations outside their training
distribution, lacking the reasoning capacity to adapt to unprecedented market
regimes. When market structure shifts abruptly, reactive agents may continue
applying outdated patterns, potentially leading to significant losses.

The integration of tool use into financial agents requires explicit evaluation
along at least two dimensions. AgentGuard studies safety-oriented evaluation for
tool orchestration <cit.>, while FinToolBench evaluates the
capability of LLM agents to use financial tools in realistic tasks
<cit.>.
Complex reasoning over structured knowledge can be enhanced through
autonomous agent frameworks 
<cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reflective Reasoning]
Reflective reasoning, loosely analogous to System 2 in dual-process theory
(while acknowledging the limitations noted in <Ref>), produces
slow, deliberate decisions through multi-step chains of thought. This paradigm
enables agents to reason through complex scenarios, consider multiple hypotheses,
and reflect on potential mistakes before acting. Unlike reactive systems that
respond immediately to stimuli, reflective reasoning allocates computational
resources to explore the decision space more thoroughly, making it suitable for
medium-frequency trading where execution latency measured in seconds is acceptable.

Representative Approaches. Chain-of-Thought (CoT) prompting
<cit.> guides LLMs to explicitly reason through trading decisions,
producing intermediate steps like “the stock price dropped because of worse-
than-expected earnings, but the long-term fundamentals remain strong, so this
is a buying opportunity.” FinCoT <cit.> adapts CoT to
finance through domain-grounded prompting that encourages financial reasoning in
trading tasks. FinCon <cit.> operationalizes reflective
workflows through multi-agent or role-structured coordination that updates
investment beliefs over time. CryptoTrade <cit.> and TradingGroup
<cit.> further instantiate reflection by revising trading
decisions based on prior outcomes and synthesizing multi-source signals.
Reflexion <cit.> extends this with self-reflection, where
agents critique their own reasoning and refine their conclusions before acting.
For example, a Reflexion-based trader might generate an initial trading rationale,
identify potential flaws in its logic (such as overlooking sector-wide risks),
and revise its decision accordingly.

Technical Mechanisms.
[title=Protocol Implication]
 We suggest a five-stage reflective reasoning protocol for audit-oriented trading
 agents: (1) analyze the current situation, (2) retrieve relevant memories, (3)
 consider multiple hypotheses, (4) evaluate the pros and cons of each action, (5)
 select the best action and justify the choice.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reflective Reasoning]
lti-source signals.
Reflexion <cit.> extends this with self-reflection, where
agents critique their own reasoning and refine their conclusions before acting.
For example, a Reflexion-based trader might generate an initial trading rationale,
identify potential flaws in its logic (such as overlooking sector-wide risks),
and revise its decision accordingly.

Technical Mechanisms.
[title=Protocol Implication]
 We suggest a five-stage reflective reasoning protocol for audit-oriented trading
 agents: (1) analyze the current situation, (2) retrieve relevant memories, (3)
 consider multiple hypotheses, (4) evaluate the pros and cons of each action, (5)
 select the best action and justify the choice.

Temperature sampling controls the trade-off between creativity and consistency,
with lower temperatures producing more deterministic reasoning. A challenge is
maintaining coherence across long reasoning chains—LLMs may lose context or
contradict themselves over dozens of reasoning steps. Techniques such as
checkpointing (saving intermediate reasoning states) and consistency checks
(verifying that conclusions follow from premises) help mitigate these issues <cit.>.
The computational cost of reflective reasoning scales linearly with the number
of reasoning steps, making it more expensive than reactive approaches but
significantly more capable of handling novel situations that require adaptation.

Reflexion-style systems also assume relatively prompt feedback, which can be in
tension with trading settings where outcomes materialize only after meaningful
market delay <cit.>. Modern risk-sensitive frameworks provide
structured decision support for financial markets, though their exact internal
decomposition varies by implementation <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Strategic Reasoning]
Strategic reasoning extends beyond immediate decisions to plan across extended
time horizons, considering sequences of actions and their long-term consequences.
This paradigm addresses questions like “what portfolio allocation will maximize
risk-adjusted returns over the next quarter?” rather than “should I buy this
stock right now?” Strategic reasoning operates at time scales of minutes to
hours, making it suitable for portfolio optimization, risk management, and
longer-term investment strategies where immediate execution is less critical than
thorough planning.

Representative Approaches. Tree-of-Thought (ToT) <cit.>
frames reasoning as search through a tree of possible thoughts, exploring multiple
reasoning paths in parallel and selecting the most promising through explicit
evaluation. Each node in the tree represents a partial reasoning state, and the
algorithm systematically explores alternatives rather than committing to the first
plausible solution. Monte Carlo Tree Search (MCTS) methods like Navigating Alpha
Jungle <cit.> search through the space of
possible trading strategies, using rollouts to estimate the long-term value of
each candidate strategy. These methods balance exploration (trying new strategies)
against exploitation (refining known good strategies) through upper confidence
bounds applied to financial domains. Planning ideas from classical AI and
reinforcement learning continue to inform strategic trading design, with state
spaces representing market conditions and actions representing trading
decisions.
For portfolio-scale planning, RAPTOR <cit.> integrates
deliberative portfolio reasoning with an orchestrated rebalancing pipeline to
produce interpretable, risk-aware allocations.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Strategic Reasoning]
ha
Jungle <cit.> search through the space of
possible trading strategies, using rollouts to estimate the long-term value of
each candidate strategy. These methods balance exploration (trying new strategies)
against exploitation (refining known good strategies) through upper confidence
bounds applied to financial domains. Planning ideas from classical AI and
reinforcement learning continue to inform strategic trading design, with state
spaces representing market conditions and actions representing trading
decisions.
For portfolio-scale planning, RAPTOR <cit.> integrates
deliberative portfolio reasoning with an orchestrated rebalancing pipeline to
produce interpretable, risk-aware allocations.

Technical Mechanisms. Strategic reasoning requires models of the
environment—predicting how market prices will evolve in response to trading
actions. Model-based methods learn explicit transition models, capturing causal
relationships between actions and market states. These models enable agents to
simulate future scenarios and evaluate action sequences without executing them.
Model-free methods learn value functions directly through experience, estimating
the long-term return of each state-action pair without explicit environment
models <cit.>. Hierarchical planning decomposes long horizons into shorter sub-problems:
a strategic planner sets high-level targets (e.g., “reduce tech exposure by
20Abstraction is critical—planning over individual stocks is intractable due to the
combinatorial explosion of possible portfolios, but planning over sectors or
factors reduces the state space to manageable dimensions. For example, a strategic
planner might operate at the level of sector allocations (technology, healthcare,
energy), while tactical planners handle individual stock selection within each
sector. This hierarchical approach enables agents to reason about long-term
objectives while remaining computationally feasible <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Strategic Reasoning]
s <cit.>. Hierarchical planning decomposes long horizons into shorter sub-problems:
a strategic planner sets high-level targets (e.g., “reduce tech exposure by
20Abstraction is critical—planning over individual stocks is intractable due to the
combinatorial explosion of possible portfolios, but planning over sectors or
factors reduces the state space to manageable dimensions. For example, a strategic
planner might operate at the level of sector allocations (technology, healthcare,
energy), while tactical planners handle individual stock selection within each
sector. This hierarchical approach enables agents to reason about long-term
objectives while remaining computationally feasible <cit.>.

Critical Challenge: Search-Based Overfitting. Unlike game environments (e.g., Go, Chess) where simulation is perfect, financial planning relies on noisy historical data. Search algorithms (MCTS, ToT) that evaluate thousands of candidate strategies inherently face the multiple testing problem—finding a profitable trajectory purely by chance. To mitigate Data Snooping, reproducible research requires reporting the Search Budget (number of visited nodes) and enforcing strict Walk-Forward Validation, where the plan is frozen before being applied to out-of-sample data <cit.>.

Comparison of reasoning paradigms. R-Level: Reproducibility level (R0–R3, see <Ref>). Audit Gap highlights common reporting deficiencies.

 Paradigm Time-Scale Mechanism R-Level Representative Works Audit Gap (Common)

Reactive Microsecond–millisecond budgets Rule-based / Lightweight NN (often <100K params) / FSM R0–R1 ReAct <cit.> (reflective, not reactive), reactive components in FinAgent <cit.> Execution Latency often ignored

Reflective Seconds CoT / Self-Critique R0–R1 FinCoT <cit.>, FinCon <cit.> Inference Cost not reported

Strategic Minutes/Hours MCTS / Planning R0–R1 Alpha Jungle <cit.>, Alpha^2 <cit.> Search Budget & Overfitting Risk

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Strategic Reasoning]
 being applied to out-of-sample data <cit.>.

Comparison of reasoning paradigms. R-Level: Reproducibility level (R0–R3, see <Ref>). Audit Gap highlights common reporting deficiencies.

 Paradigm Time-Scale Mechanism R-Level Representative Works Audit Gap (Common)

Reactive Microsecond–millisecond budgets Rule-based / Lightweight NN (often <100K params) / FSM R0–R1 ReAct <cit.> (reflective, not reactive), reactive components in FinAgent <cit.> Execution Latency often ignored

Reflective Seconds CoT / Self-Critique R0–R1 FinCoT <cit.>, FinCon <cit.> Inference Cost not reported

Strategic Minutes/Hours MCTS / Planning R0–R1 Alpha Jungle <cit.>, Alpha^2 <cit.> Search Budget & Overfitting Risk

Hybrid Architecture: Cascaded Controller. To balance these trade-offs, advanced systems can employ what we call a Cascaded Controller architecture (illustrated in <Ref>): a master intent router classifies the market regime (e.g., “Flash Crash” vs. “Stable Trend”) and routes execution to the appropriate paradigm, immediately triggering lower-level reactive stops in volatile conditions while planning strategic re-allocations during calm periods. Note: both the term and the design pattern are our synthesis of principles observed in hierarchical trading systems <cit.>; we present it as an architectural recommendation derived from the literature, not as an established term or a novel contribution of this survey.

In summary, this section has presented three reasoning paradigms that enable
trading agents to transform information into actions. Reactive reasoning
provides fast responses to familiar situations, reflective reasoning enables
complex deliberation, and strategic reasoning supports long-term planning. These
paradigms are not mutually exclusive—sophisticated agents employ all three,
switching between them based on the time constraints and complexity of the
decision at hand. The next section examines how agents map decisions into
concrete market actions and execute them under cost, impact, and latency
constraints.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Strategic Reasoning]
e literature, not as an established term or a novel contribution of this survey.

In summary, this section has presented three reasoning paradigms that enable
trading agents to transform information into actions. Reactive reasoning
provides fast responses to familiar situations, reflective reasoning enables
complex deliberation, and strategic reasoning supports long-term planning. These
paradigms are not mutually exclusive—sophisticated agents employ all three,
switching between them based on the time constraints and complexity of the
decision at hand. The next section examines how agents map decisions into
concrete market actions and execute them under cost, impact, and latency
constraints.

[float,floatplacement=tbp]Evidence Summary (Reasoning)

 * Reasoning depth trades off with latency: reflective/strategic loops can improve planning quality, but must match the market timescale (event-driven vs. microstructure) <cit.>.

 * Traces increase observability, not guaranteed faithfulness: chain-of-thought and self-critique can be useful artifacts, but for audit-oriented evaluation it is prudent to check them against grounded inputs and realized outcomes before treating them as trustworthy explanations <cit.>.

 * Search-based methods (e.g., MCTS in alpha spaces) can exacerbate multiple-testing risk; protocol details (splits, costs) determine whether gains generalize <cit.>.

 * Comparisons across paradigms benefit from standardized reporting of prompts, tooling, and failure handling (timeouts, invalid actions), together with realistic multi-month evaluations beyond static tasks <cit.>.

 * Reasoning Evaluation Checklist—To improve replicability, we suggest that future works report: (1) Faithfulness: Can the reasoning trace be verified against ground-truth data snapshots? (2) Leakage: Does the reasoning chain implicitly use future information? (3) Budget: For strategic search, what is the max node count and rollout depth?

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Action and Execution Architecture]
The preceding sections examined perception, memory, and reasoning. This section
addresses the question: “How do agents turn decisions into
market actions?”

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: Action/execution evidence is primary only when a system emits tradable actions and evaluates the resulting loop.

 2) Supported claim: Execution semantics are the strongest boundary between a trading agent and a signal model.

 3) Reporting gap: Many papers omit order timing, fill assumptions, cost models, and rejection handling.

 4) Implication: The action interface should be treated as a typed I/O contract, and performance claims without execution semantics should remain conservative.

Action I/O Contract. For auditability, the action module is often modeled as a function f(D_t) → (A_order, A_algo), where:

 * Input: Decision output D_t (e.g., target portfolio weights w^*_t or signal s_t).

 * Output: A set of executable orders A_order (with strictly typed fields: side, size, limit price, TIF) and an execution algorithm selection A_algo (e.g., "submit immediately" or "TWAP over 5 min").

 * Failure Modes: The interface typically handles Rejection (risk check failure), Partial Fill (liquidity shortage), and Timeout (latency violation), feeding these states back to memory.

This contract helps avoid "implicit execution" where agents are assumed to trade at the close price without order generation delays or constraints.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* Decision-to-Order Mapping: Mapping high-level intent (signal, targets, risk limits) into order parameters (side, size, type, timing).

 * Execution and Cost Modeling: Selecting an execution policy (e.g., slicing, passive vs aggressive) and modeling transaction costs and market impact.

 * Microstructure and Latency Awareness: Incorporating order book dynamics, fill probabilities, and latency constraints that shape feasible actions.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Comparability note]
Protocol-comparable action/execution claims typically report MR-3 (action semantics), MR-4 (execution & costs), and MR-6 (artifacts & logs); see <Ref>.

 < g r a p h i c s >

 From decision to execution. Agent outputs map into order parameters and
 are executed with explicit cost and impact modeling under market micro­structure constraints. This
 figure is schematic and is not used for evidence-mapping statistics or protocol comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Decision-to-Order Mapping]
First Principle: Action Definition Risk. A critical failure mode in agent design is the ambiguity between target weights (portfolio intent) and executable orders (market instructions). If an agent only emits target weights without explicitly modeling order timing, fill constraints, and costs, evaluation can quietly collapse intent into execution, thereby underestimating the execution gap and liquidity constraints <cit.>.

The literature shows that action modules translate high-level decisions (e.g., increase exposure) into order instructions. This mapping depends on explicit choices about order type (limit vs market) and queue position, as microstructure theory models execution probability as a function of order aggressiveness and state <cit.>. Constraints such as pre-trade validation and kill switches are important boundaries that help keep theoretical alpha from turning into realized losses due to market impact <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Execution and Cost Modeling]
Execution policies determine how orders are placed over time and venues. Typical
approaches include schedule-based execution (e.g., time-weighted average price
(TWAP) and volume-weighted average price (VWAP)), cost-aware
optimization that trades off urgency vs market impact
<cit.>, and
learning-based execution that adapts to market conditions. Recent studies
explore deep learning and reinforcement learning for execution and impact-aware
trading
<cit.>.
FinPos <cit.> introduces a position-aware trading agent system specifically
designed for real financial markets, emphasizing continuous portfolio adjustment.
StockSim <cit.> provides a dual-mode order-level simulator for evaluating
multi-agent LLMs in financial markets, enabling realistic execution modeling.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Microstructure and Latency Awareness]
Microstructure signals (order book imbalance, spread, queue position) are not merely inputs for optimization but represent hard feasibility constraints that filter the action space. Here, LOB (Limit Order Book) refers to the real-time queue of outstanding buy and sell limit orders, with LOB features including imbalance (bid vs. ask volume), spread, and depth.

* Data Availability: The literature shows agents can suffer from "look-ahead bias" by acting on LOB features (e.g., Imbalance_t) that are not technically available at decision time t due to processing latency. Feasible actions are generally conditioned on O_t-δ.

 * Latency Budget: In high-frequency regimes, the latency budget (time from perception to exchange ack) determines whether an arbitrage opportunity exists <cit.>. If T_compute > T_decay, the action a_t is invalid regardless of its theoretical alpha.

Models of order book dynamics <cit.> serve to validate these constraints before execution.

[title=Protocol Implication]
 Beyond execution optimization, LLMs can support post-trade narratives by summarizing execution logs. To reduce "ex post rationalization" (where the LLM hallucinates a strategic reason for a random failure), we recommend grounding these narratives in immutable logs and replayable evidence <cit.>.

* Recommendation: Narrative generation can cite a cryptographically specific Order_ID and Snapshot_Hash from the execution layer.

 * Verification: Auditors can replay the Snapshot_Hash to check whether the market condition (e.g., "high spread") claimed by the narrative actually existed.

Without this Log-to-Narrative Verification link, LLM explanations are better treated as qualitative summaries rather than audit artifacts.

Representative action/execution approaches and evaluation dimensions. Type distinguishes between End-to-End Agents (E2E) and component-level algorithms (Algo). Note that Agent literature often adopts simplified assumptions (Sim-based), whereas Algo literature focuses on execution quality but lacks agentic reasoning. Audit Gap highlights common missing reporting items.

 Category Type Action Space Core Mechanism Cost Assumption Audit Gap (Common) Tags

Schedule-based Algo Order schedule TWAP/VWAP-style scheduling Explicit fees Slippage Calib.

RL Execution Algo Market Orders Policy optimization in simulator Impact-aware reward Latency Budget

Sim-based RL E2E Order-level Market simulator + RL Simulator-dependent Decision Timing

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Microstructure and Latency Awareness]
hes and evaluation dimensions. Type distinguishes between End-to-End Agents (E2E) and component-level algorithms (Algo). Note that Agent literature often adopts simplified assumptions (Sim-based), whereas Algo literature focuses on execution quality but lacks agentic reasoning. Audit Gap highlights common missing reporting items.

 Category Type Action Space Core Mechanism Cost Assumption Audit Gap (Common) Tags

Schedule-based Algo Order schedule TWAP/VWAP-style scheduling Explicit fees Slippage Calib.

RL Execution Algo Market Orders Policy optimization in simulator Impact-aware reward Latency Budget

Sim-based RL E2E Order-level Market simulator + RL Simulator-dependent Decision Timing

Microstructure Algo Limit Orders Fill/LOB modeling Implicit via LOB Realized Spread

Hierarchical E2E Meta-Actions Hierarchical RL for order types Explicit/implicit Failure Modes

In summary, action and execution connect reasoning to real market interaction.
They benefit from explicit modeling of constraints and costs that are often
under-specified in agent papers. With the architectural foundations established,
we now turn to the capabilities these architectures enable, beginning with alpha
generation.

[float,floatplacement=tbp]Evidence Summary (Action and Execution)

* Cost and impact modeling is essential for credible claims at order level: reported gains are sensitive to slippage/fees assumptions and simulator fidelity <cit.>.

 * Microstructure-aware policies benefit from reporting latency, routing constraints, and data availability (LOB features) to make results comparable <cit.>.

 * Post-trade explanations are useful only with auditable logs and verifiable data sources; otherwise they risk becoming plausible narratives that do not diagnose failure modes <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Alpha Discovery Capability]
The preceding sections established the architectural foundations of agentic
traders. This section addresses the question: “How do agents
discover trading signals?”

Alpha discovery refers to generating and testing candidate trading signals. In
this evidence map, we treat autonomous alpha search as supported only when the
reported system connects discovery to out-of-sample or closed-loop evaluation,
rather than when it only proposes factors.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: Primary alpha evidence comes from studies that connect factor or strategy generation to backtest or market-simulation outcomes.

 2) Supported claim: LLM agents can expand the search interface for alpha ideas and formulaic factors.

 3) Reporting gap: Search budgets, sealed test sets, factor similarity filters, and transaction-cost assumptions are often underreported.

 4) Implication: Alpha-discovery claims should be read as search-pipeline evidence unless novelty, leakage control, and execution costs are reported together.

[
 colback=gray!10,
 colframe=gray!50,
 colbacktitle=gray!30,
 coltitle=black,
 fonttitle=,
 title=Classical Baseline: Factor Models and Information Coefficient,
 boxrule=0.5pt,
 arc=2pt,
 left=5pt,
 right=5pt,
 top=3pt,
 bottom=3pt
 ]
 Before LLM-based approaches, alpha generation relied on manually engineered
 factor models (e.g., the Fama-French three-factor model, momentum, value) where factor
 validity is measured by Information Coefficient (IC)—the correlation between
 factor scores and subsequent returns. Statistical rigor required controlling for
 multiple testing (White's Reality Check, Hansen's SPA) to distinguish true signals
 from data mining <cit.>. LLM-based agents automate factor discovery but face the same
 fundamental challenge: ensuring discovered patterns generalize out-of-sample
 rather than exploiting historical noise.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* Code-based Alpha Discovery (<Ref>): Generating alpha factors through natural language to code translation.

 * Retrieval-based Alpha Discovery (<Ref>): Discovering alpha by retrieving and adapting existing factors.

 * Evolutionary Alpha Discovery (<Ref>): Searching the factor space through evolutionary optimization.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Comparability note]
Protocol-comparable alpha discovery claims should report MR-2 (time split + sealed test), MR-4 (execution & costs), and MR-6 (factor semantics + artifacts & logs); see <Ref> for detailed protocol requirements and reporting checklists.

[title=Author Framework]
 Alpha-to-Trade Contract. We introduce the Alpha-to-Trade Contract as a conceptual framework for distinguishing statistical significance from tradeable signals. To bridge this gap, the conversion contract specifies:

 * Frequency Compatibility: Does the signal update frequency match the execution latency budget?

 * Turnover Constraints: Does the theoretical gain survive realistic transaction costs and market impact?

 * Liquidity Reality: Is the factor universe liquid enough for the assumed capital capacity?

 Papers omitting this contract risk conflating theoretical IC with realized alpha return, a common pitfall in agentic trading literature <cit.>.

Figure <ref> summarizes the three alpha discovery paradigms at a glance.

 < g r a p h i c s >

 Three alpha discovery paradigms. Code-based discovery translates
 natural language hypotheses into executable code. Retrieval-based discovery
 finds and adapts existing factors from a library. Evolutionary discovery
 searches the factor space through mutation and selection. This figure is
 schematic and is not used for evidence-mapping statistics or protocol
 comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Code-based Alpha Discovery]
Code-based alpha generation leverages the code synthesis capabilities of LLMs
to translate natural language hypotheses about market behavior into executable
factor definitions. This paradigm enables domain experts who lack programming
expertise to directly express and test their trading ideas.

Representative Approaches. CogAlpha
<cit.> extends code-based generation with structured prompting templates that guide the LLM
toward syntactically correct and semantically meaningful factor definitions.
AlphaAgent <cit.> further introduces regularization mechanisms (originality enforcement, hypothesis alignment, and complexity control) to counteract alpha decay. FactorMAD <cit.> leverages
multi-agent debate frameworks where multiple LLM agents critique and refine
factor proposals to enhance interpretability. Automate Strategy Finding
<cit.> implements a three-stage pipeline with risk-aware multi-agent
validation and ensemble strategy selection, reporting 53.17setup (Split: ; Execution: ;
Cost: ; Universe: SSE50; Tier:
). When protocol-critical details are /, we
treat such results as illustrative rather than protocol-comparable evidence.

Recent approaches combine LLM reasoning with reinforcement learning for
structured trading decision-making 
<cit.>,
and ensemble strategies employing deep reinforcement learning have demonstrated
superior performance in stock trading tasks 
<cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Code-based Alpha Discovery]
agent debate frameworks where multiple LLM agents critique and refine
factor proposals to enhance interpretability. Automate Strategy Finding
<cit.> implements a three-stage pipeline with risk-aware multi-agent
validation and ensemble strategy selection, reporting 53.17setup (Split: ; Execution: ;
Cost: ; Universe: SSE50; Tier:
). When protocol-critical details are /, we
treat such results as illustrative rather than protocol-comparable evidence.

Recent approaches combine LLM reasoning with reinforcement learning for
structured trading decision-making 
<cit.>,
and ensemble strategies employing deep reinforcement learning have demonstrated
superior performance in stock trading tasks 
<cit.>.

Technical Mechanisms. The generation pipeline operates as an adaptive search process susceptible to overfitting: (1) parse the natural language hypothesis to identify key components, (2) map these to code templates and APIs, (3) generate executable code, (4) validate through sandboxed execution, and (5) backtest on historical data. Crucially, the "Validation Chain" provides feedback that guides the next generation step. This feedback loop creates a risk of adaptive overfitting: as the agent iterates to maximize the validation Sharpe ratio, it effectively "mines" the validation set <cit.>. Therefore, a rigorous protocol requires reporting the Search Budget (number of generated hypotheses) and ensuring that the final performance is reported on a sealed Test Set that is never exposed to the agent during the refinement loop. Without this separation, reported "validation" metrics are statistically inflated. Sandboxed execution mitigating security risks is also standard practice. Examples of synthesized factors include momentum and reversal signals, but their validity depends entirely on the integrity of the data split.

< g r a p h i c s >

Chain-of-Alpha workflow. The generation chain (top) translates
 natural language into factor code. The validation chain (bottom) backtests
 the factor, computes performance metrics, and provides feedback for refinement.
 The two chains interact iteratively until a satisfactory factor is produced.
 This figure is schematic and is not used for evidence-mapping
 statistics or protocol comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Retrieval-based Alpha Discovery]
Retrieval-based alpha generation reuses existing factor knowledge through
retrieval and adaptation. Rather than generating factors from scratch, the
agent finds related signals or financial context that can inform the current
situation.

Representative Approaches. RAG-based financial retrieval systems <cit.>
index domain knowledge as embeddings and retrieve contextually similar items
using semantic search. PRISM <cit.> further refines retrieval through
prompt-optimized in-context modeling for financial domains. Retrieval-augmented
frameworks for financial time-series forecasting <cit.> similarly demonstrate
the effectiveness of combining LLM generation with historical pattern retrieval.

Technical Mechanisms. Retrieval relies on vector embeddings that encode factor semantics (formula structure) and market context. However, the validity of this paradigm hinges on Factor Library Governance, a data integrity challenge often overlooked.

 * Survivorship Bias: If the library collects only "historically successful" factors, the retrieval process implicitly conditions on future outcomes, inflating backtest performance.

 * Look-ahead Leakage in Embeddings: If the embedding model is trained on textual descriptions containing future knowledge (e.g., "a successful high-volatility factor"), the retrieval query q_t effectively leaks information from t+k.

[title=Protocol Implication]
 We recommend Point-in-Time (PIT) Governance for verifiable evidence: the retrieval corpus L_t available at time t must strictly contain only documents and performance metadata known at t <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evolutionary Alpha Discovery]
Evolutionary alpha generation searches the factor space through iterative
mutation, crossover, and selection, treating factor discovery as an optimization
problem. This paradigm can discover novel factor combinations that human experts
might not conceive.

Representative Approaches. Navigating Alpha Jungle <cit.>
employs Monte Carlo Tree Search (MCTS) to efficiently explore the combinatorial
space of possible factors. Each node in the search tree represents a partial
factor definition (e.g., a specific transformation applied to a price series),
and MCTS balances exploration (trying new factor components) with exploitation
(refining promising factors). Alpha2 <cit.>
uses deep reinforcement learning, where an agent learns to construct factors
by sequencing primitive operations, receiving rewards based on backtest
performance. EFS (Evolutionary Factor Searching) <cit.> reformulates asset selection
as a top-m ranking task guided by LLM-generated factors, incorporating an
evolutionary feedback loop for iterative refinement.

Technical Mechanisms. Evolutionary methods define a search space of primitive operations (price transformations, technical indicators) and combination rules. MCTS and Genetic Programming (GP) navigate this space by balancing exploration (new operations) and exploitation (refining promising factors). However, this paradigm faces a severe Multiple Testing Scalability risk. As the search space grows exponentially, the probability of finding a false positive approaches 1.0 unless rigorous statistical corrections are applied <cit.>. Therefore, a valid protocol must report: (1) Primitive Ops Audit (the exact set of allowed functions), (2) Total Search Depth/Budget, and (3) statistical tests for data snooping (e.g., White's Reality Check or Hansen's SPA) <cit.>. Currently, few agent papers report these stats, rendering their results difficult to distinguish from noise. Regularization techniques (complexity penalties, ensemble methods) are useful heuristics but do not substitute for formal multiple hypothesis testing.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evolutionary Alpha Discovery]
aces a severe Multiple Testing Scalability risk. As the search space grows exponentially, the probability of finding a false positive approaches 1.0 unless rigorous statistical corrections are applied <cit.>. Therefore, a valid protocol must report: (1) Primitive Ops Audit (the exact set of allowed functions), (2) Total Search Depth/Budget, and (3) statistical tests for data snooping (e.g., White's Reality Check or Hansen's SPA) <cit.>. Currently, few agent papers report these stats, rendering their results difficult to distinguish from noise. Regularization techniques (complexity penalties, ensemble methods) are useful heuristics but do not substitute for formal multiple hypothesis testing.

Open Question: Mathematical Bounds for Agent-Driven Search.
While traditional multiple testing corrections (White's Reality Check, Hansen's SPA, and the Deflated Sharpe Ratio <cit.>) remain the statistical gold standard, a critical question emerges for LLM-based agents: can the agent's internal reflection/evolution loop provide novel mathematical bounds on overfitting risk? Current evidence suggests not yet. The reflection budget (<Ref>) limits search iterations but does not provide statistical guarantees on false discovery rate. The sealed test set protocol prevents adaptive overfitting but relies on experimental discipline rather than closed-form bounds. Factor originality constraints (e.g., AST-based similarity in AlphaAgent) reduce effective search space but do not quantify the residual multiple testing penalty. This represents a significant research gap: future work could explore whether LLM reasoning traces, factor genealogy logs, or Bayesian model averaging over discovered factors can yield principled, agent-native overfitting controls that complement or extend classical methods. Until such methods are developed, evolutionary alpha systems should report both (1) search budget protocol constraints and (2) classical multiple testing statistics (e.g., deflated Sharpe ratio <cit.>) to enable rigorous evaluation.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evolutionary Alpha Discovery]
her than closed-form bounds. Factor originality constraints (e.g., AST-based similarity in AlphaAgent) reduce effective search space but do not quantify the residual multiple testing penalty. This represents a significant research gap: future work could explore whether LLM reasoning traces, factor genealogy logs, or Bayesian model averaging over discovered factors can yield principled, agent-native overfitting controls that complement or extend classical methods. Until such methods are developed, evolutionary alpha systems should report both (1) search budget protocol constraints and (2) classical multiple testing statistics (e.g., deflated Sharpe ratio <cit.>) to enable rigorous evaluation.

Comparison of alpha discovery algorithms. Novelty is defined by structural distance (e.g., AST) from known factor families. Overfitting risk is proportional to the unadjusted search budget and IS-OOS performance gap. Protocol Tags (Split/Execution/Cost/Universe) indicate reporting rigor: (no runnable artifacts), (code available but not runnable), (runnable with gaps), (background/conceptual), (not reported/applicable).

 Paradigm Discovery Mech Search Space Novelty Overfitting Works Tags

Code-based LLM → Code Semantic factors High Medium CogAlpha <cit.>

Code-based Multi-Agent Debate Interpretable factors High Low FactorMAD <cit.>

Retrieval Vector Search Factor Library Low Low RAG-Fintech <cit.>

Retrieval Prompt-Refined RAG Financial corpus Medium Low PRISM <cit.>

Evolutionary MCTS / Deep RL Combinatorial ops Very High High Alpha Jungle (R0), Alpha^2 (R1) <cit.>

Evolutionary LLM-Guided Evolution Sparse portfolios High Medium EFS <cit.>

<Ref> summarizes the three alpha discovery paradigms.
In practice, sophisticated agents combine all three: using code-based generation
to encode expert hypotheses, retrieval to leverage existing knowledge, and
evolutionary search to discover novel combinations.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evolutionary Alpha Discovery]
emantic factors High Medium CogAlpha <cit.>

Code-based Multi-Agent Debate Interpretable factors High Low FactorMAD <cit.>

Retrieval Vector Search Factor Library Low Low RAG-Fintech <cit.>

Retrieval Prompt-Refined RAG Financial corpus Medium Low PRISM <cit.>

Evolutionary MCTS / Deep RL Combinatorial ops Very High High Alpha Jungle (R0), Alpha^2 (R1) <cit.>

Evolutionary LLM-Guided Evolution Sparse portfolios High Medium EFS <cit.>

<Ref> summarizes the three alpha discovery paradigms.
In practice, sophisticated agents combine all three: using code-based generation
to encode expert hypotheses, retrieval to leverage existing knowledge, and
evolutionary search to discover novel combinations.

[float,floatplacement=tbp]Evidence Summary (Alpha)

 * Code-based, retrieval-based, and evolutionary discovery differ mainly in how they define and explore the search space; comparisons are only meaningful under sealed splits and explicit search budgets (MR-2).

 * The dominant validity risk is adaptive overfitting/data snooping: iterative refinement against validation metrics can inflate performance without a single-use or walk-forward test (MR-2).

 * Claims of realized alpha require an explicit alpha-to-trade contract with turnover and friction modeling; otherwise, IC gains need not survive execution (MR-4).

 * Reproducible evidence requires explicit factor semantics (formulas/architectures) and artifacts/logs for replay (MR-6).

In summary, this section has presented three paradigms for alpha generation.
Code-based discovery translates hypotheses into factors, retrieval-based
discovery adapts existing factors, and evolutionary discovery searches for novel
factors. The next section examines how agents manage portfolios, allocating
capital across multiple alpha signals.

The next section addresses the question: “How do agents
manage multi-asset portfolios?”

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Portfolio Management Capability]
The preceding section explored how agents generate alpha signals. This section
addresses the question: “How do agents manage multi-asset
portfolios?”

Portfolio management transforms individual signals into position or allocation
decisions. We organize it by decision scope because the evidence is strongest
where papers specify the action object–weights, orders, constraints, or
rebalancing rules–and weakest where portfolio management is discussed only as a
conceptual layer.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: Primary portfolio evidence requires closed-loop allocation or order evaluation.

 2) Supported claim: LLM agents can mediate between narrative market views and portfolio constraints.

 3) Reporting gap: Many studies do not report rebalancing calendars, universe construction, constraint sets, or transaction costs.

 4) Implication: Portfolio claims should be tied to explicit allocation contracts and comparable rebalancing protocols.

[
 colback=gray!10,
 colframe=gray!50,
 colbacktitle=gray!30,
 coltitle=black,
 fonttitle=,
 title=Classical Baseline: Mean-Variance Optimization and Kelly Criterion,
 boxrule=0.5pt,
 arc=2pt,
 left=5pt,
 right=5pt,
 top=3pt,
 bottom=3pt
 ]
 Classical portfolio theory formulates allocation as mean-variance optimization
 (Markowitz 1952), maximizing risk-adjusted returns given covariance estimates,
 or as growth-optimal betting (Kelly 1956), maximizing log-utility of wealth. The
 Black-Litterman model incorporates investor views into equilibrium returns.
 These frameworks provide closed-form solutions under Gaussian assumptions but
 struggle with non-stationary higher-order moments and tail risks—precisely
 where LLM-based approaches may add value through adaptive reasoning and
 regime-aware dynamic allocation.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* Asset Allocation (<Ref>): Strategic allocation across asset classes and sectors.

 * Position Sizing (<Ref>): Determining the size of individual positions.

 * Rebalancing (<Ref>): Adjusting portfolios to maintain target weights.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Comparability note]
Protocol-comparable portfolio claims typically report MR-1 (data/universe), MR-2 (time split), MR-3 (I/O contracts + constraints), and MR-4 (execution & costs); see <Ref>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Asset Allocation]
Asset allocation sets portfolio weights across asset classes and broad themes
(sectors, regions, styles), shaping the long-horizon risk/return envelope.

Representative Approaches. Classical baselines include mean-variance
optimization <cit.> and Black-Litterman <cit.>; both hinge
on estimates (returns, covariances, or implied priors) that can drift quickly.
Risk-based allocations (risk parity / HRP-style clustering) are often preferred
when estimates are noisy. In agentic systems, LLMs commonly act as view generators <cit.> utilizing news/macro data. Lee et al. <cit.> demonstrate how LLM-generated views can be integrated into the Black-Litterman framework, while Kirtac et al. <cit.> leverage LLM-based sentiment analysis to drive portfolio optimization decisions.

Recent advances in end-to-end neural approaches have shown promise for large-scale portfolio optimization. <cit.> propose end-to-end neural networks for variance minimization in large portfolios, while <cit.> introduce deep learning frameworks combining 3D-CNNs and BiLSTMs for medium-term covariance forecasting. Graph attention-based heterogeneous multi-agent reinforcement learning <cit.> offers adaptive portfolio optimization through multi-agent coordination. Pair-trading work that combines graph attention networks for pair selection with deep reinforcement learning for trade execution provides a non-LLM background example of relation-aware portfolio construction and execution design <cit.>. HARLF <cit.> integrates hierarchical reinforcement learning with lightweight LLM-driven sentiment analysis for financial portfolio optimization. These neural approaches complement traditional mean-variance optimization by capturing non-linear dependencies that classical methods may miss <cit.>.

However, this introduces severe leakage risks. The literature on time-series evaluation shows that valid protocols should enforce Point-in-Time (PIT) Textual Alignment: macro inputs must use the unrevised values available at the exact release timestamp, and validation pipelines should avoid future information leaking through preprocessing or feature construction <cit.>. Similarly, regime tagging is best generated online from t-k lookback windows, as full-sample regime clustering can leak future volatility states <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Asset Allocation]
ortfolio optimization. These neural approaches complement traditional mean-variance optimization by capturing non-linear dependencies that classical methods may miss <cit.>.

However, this introduces severe leakage risks. The literature on time-series evaluation shows that valid protocols should enforce Point-in-Time (PIT) Textual Alignment: macro inputs must use the unrevised values available at the exact release timestamp, and validation pipelines should avoid future information leaking through preprocessing or feature construction <cit.>. Similarly, regime tagging is best generated online from t-k lookback windows, as full-sample regime clustering can leak future volatility states <cit.>.

Technical Mechanisms. HRP-style allocation reduces sensitivity to
covariance noise by allocating at the cluster level before distributing within
clusters. Regime-aware allocation (statistical or LLM-driven) can switch risk
budgets when volatility/liquidity conditions change, but it is best treated as
a hypothesis to test rather than a guarantee. For agentic trading, the practical
core is constraint-aware optimization (exposure, leverage, turnover) with
explicit transaction-cost assumptions <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Position Sizing]
Position sizing determines how much capital to allocate to each trading signal,
balancing the desire to profit from strong signals against the risk of large
losses. This tactical decision directly impacts portfolio volatility and
drawdown.

Representative Approaches. The Kelly criterion <cit.> links size
to estimated edge and uncertainty, but is fragile to estimation error; most
implementations therefore use fractional Kelly. Recent works by <cit.> and <cit.> revisit portfolio optimization from complementary angles, highlighting the growing importance of constraint-aware sizing in modern markets. Alternatives include risk-budget schemes (risk parity-style) and decision-informed neural methods <cit.> that integrate learned forecasts and LLM inputs into portfolio decisions.

Agentic systems have expanded position sizing capabilities through multiple mechanisms. Dynamic optimization approaches using ODE-based formulations <cit.> offer continuous-time solutions to the mean-variance problem, while cardinality and bounding constrained formulations <cit.> address practical trading constraints often ignored in theoretical models. Agentic systems may add qualitative risk flags from text, but these inputs require strict time alignment and auditability.

Technical Mechanisms. In practice, sizing layers use conservative shrunk estimates and fractional Kelly-style scaling to control blow-ups.
[title=Protocol Implication]
 For comparability, we recommend reporting a Position Sizing Checklist: (1) Risk Metric: What is minimized? (Vol, CVaR, MaxDD), (2) Constraints: What are the boundaries? (Long-only, Leverage < 1.5, Sector < 20
When LLMs contribute qualitative risk signals, they can be treated as features with strict timestamping and ablation tests (text signal on/off) to verify incremental value <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Rebalancing]
Rebalancing adjusts portfolio weights to maintain target allocations as market
prices move and new signals arrive. This operational decision balances the
benefits of maintaining desired risk profiles against the costs of frequent
trading.

Agentic AI systems have been successfully applied to dynamic crypto-asset
allocation, demonstrating adaptability in high-volatility markets 
<cit.>.
Generative AI-enhanced approaches enable sophisticated sector-based portfolio
construction using LLM selections combined with classical optimization 
<cit.>.
PolyModel theory combined with iTransformer architectures offers novel
approaches for hedge fund portfolio construction 
<cit.>.
Explainable DRL techniques provide transparency in financial policy
decisions 
<cit.>.
Strategy-guided exploration mechanisms can expand agent boundaries for more
robust portfolio workflows, but they are best read here as a generic robustness idea rather than direct evidence for rebalancing 
<cit.>.

Representative Approaches. Common policies include threshold rebalancing (act only when weights drift beyond bands), time-based schedules, and cost-aware optimization that trades off tracking error vs. transaction/impact/tax costs.

Recent research has explored AI-enhanced rebalancing strategies. <cit.> propose heuristic-guided reward learning for portfolio optimization, demonstrating how learned heuristics can improve rebalancing decisions. Multi-objective gradient descent approaches <cit.> enable simultaneous optimization of multiple portfolio objectives during rebalancing.

The literature shows agentic workflows often add event awareness (e.g., risk-off before FOMC), but this introduces leakage risks. Comparisons are most credible when evaluations distinguish between Calendar Events (scheduled ahead of time, e.g., Earnings Calendar) and Shock Events (unexpected news). Rebalancing driven by shocks should rely on real-time proxies (e.g., VIX spike, spread widening) observable at t, rather than future-annotated event labels <cit.>. FinVision <cit.> is better read as a multimodal stock-prediction example than as direct evidence for this taxonomy.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Rebalancing]
radient descent approaches <cit.> enable simultaneous optimization of multiple portfolio objectives during rebalancing.

The literature shows agentic workflows often add event awareness (e.g., risk-off before FOMC), but this introduces leakage risks. Comparisons are most credible when evaluations distinguish between Calendar Events (scheduled ahead of time, e.g., Earnings Calendar) and Shock Events (unexpected news). Rebalancing driven by shocks should rely on real-time proxies (e.g., VIX spike, spread widening) observable at t, rather than future-annotated event labels <cit.>. FinVision <cit.> is better read as a multimodal stock-prediction example than as direct evidence for this taxonomy.

News-driven rebalancing has emerged as a particularly promising application. <cit.> combine financial news analysis with reinforcement learning for portfolio management, enabling dynamic rebalancing based on real-time sentiment shifts. Liquidity-aware portfolio selection and rebalancing strategies <cit.> incorporate machine learning-based liquidity classification to guide allocation and execution timing.

Technical Mechanisms. No-trade regions (bands) reduce churn by ignoring
small drift until it matters for risk, while execution models (VWAP/TWAP/implementation
shortfall (IS); <Ref>) and
explicit slippage assumptions determine whether a policy survives outside a
backtest. For agentic trading, the key protocol caveat is separating decision
 timing (signal/optimizer) from fill timing (execution) to avoid
overstating performance. If tax-aware logic is included, the literature suggests matching the
account type and jurisdiction used in evaluation.
<cit.>.

Portfolio management method comparison. Protocol Tags (Split/Execution/Cost/Universe) indicate reporting rigor for empirical evaluations (coding rules in <Ref>). denotes conceptual or background work without a verifiable trading backtest.

 Level Traditional Methods LLM Enhancement Key Challenges

Asset Allocation Mean-variance optimization, Black-Litterman, Risk parity, Hierarchical clustering Regime detection from narratives, View generation, Market sentiment analysis Covariance estimation errors, Regime misclassification

Position Sizing Kelly criterion, Risk parity equalization, Convex optimization (VaR/CVaR) Qualitative risk assessment from news, Constraint handling with reasoning Estimation error sensitivity, Over-aggressive sizing

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Rebalancing]
ags (Split/Execution/Cost/Universe) indicate reporting rigor for empirical evaluations (coding rules in <Ref>). denotes conceptual or background work without a verifiable trading backtest.

 Level Traditional Methods LLM Enhancement Key Challenges

Asset Allocation Mean-variance optimization, Black-Litterman, Risk parity, Hierarchical clustering Regime detection from narratives, View generation, Market sentiment analysis Covariance estimation errors, Regime misclassification

Position Sizing Kelly criterion, Risk parity equalization, Convex optimization (VaR/CVaR) Qualitative risk assessment from news, Constraint handling with reasoning Estimation error sensitivity, Over-aggressive sizing

Rebalancing Threshold-based, Time-based, Cost-aware optimization Strategic timing around events, Transaction cost estimation, Tax-aware harvesting Transaction costs, Market impact, Tax optimization complexity

<Ref> summarizes portfolio management approaches and
how LLMs enhance each level. The next section examines risk management, the
complementary capability to portfolio management.

[float,floatplacement=tbp]Evidence Summary (Portfolio Layer)

 * Classical portfolio primitives (mean-variance, Black-Litterman, Kelly) remain useful as interfaces between forecasts and trades, but require robust estimation and conservative scaling in noisy markets <cit.>.

 * Recent agentic frameworks emphasize modular pipelines (data → signal → portfolio/execution) and make the portfolio layer explicit, enabling ablations and audit trails <cit.>.

 * Evidence Grading: Studies failing to report specific I/O contracts or cost models (i.e., treating portfolio logic as an implicit black box) are graded as (Conceptual). Empirically valid comparisons are more comparable when they standardize rebalancing frequency and constraints <cit.>.

 * Evaluations are more credible when they enforce timestamp correctness (text/news availability, event timing) and include out-of-sample or walk-forward tests to reduce leakage and regime overfitting <cit.>.

The next section addresses the question: “How do agents
control financial risks?”

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Risk Management Capability]
The preceding sections explored alpha generation and portfolio management. This
section addresses the question: “How do agents control
financial risks?”

Risk management is treated here as the set of constraints, monitors, and
post-trade controls that shape allowable actions. We keep the discussion
evidence-bounded because many risk mechanisms are described architecturally but
not isolated empirically.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: The current primary subset contains little risk-focused closed-loop evidence, so much of this section synthesizes background mechanisms.

 2) Supported claim: Risk modules are necessary for deployable trading agents, especially when actions can be generated autonomously.

 3) Reporting gap: Thresholds, override rules, latency budgets, and audit logs are rarely reported.

 4) Implication: Risk claims should be evaluated through pre-specified safeguards and failure cases, not only through aggregate returns.

[
 colback=gray!10,
 colframe=gray!50,
 colbacktitle=gray!30,
 coltitle=black,
 fonttitle=,
 title=Classical Baseline: VaR, CVaR, and Drawdown Control,
 boxrule=0.5pt,
 arc=2pt,
 left=5pt,
 right=5pt,
 top=3pt,
 bottom=3pt
 ]
 Traditional risk management quantifies tail risk through Value-at-Risk (VaR)—the
 quantile of loss distribution—and Conditional VaR (CVaR), the expected loss
 beyond VaR. Drawdown control limits peak-to-trough declines via dynamic
 programming or convex optimization. These metrics provide computationally
 tractable risk bounds but assume stationary distributions and known correlation
 structures. LLM agents offer natural language explanations of risk exposures and
 scenario generation, but the resulting explanations are most credible when grounded in verifiable metrics and immutable
 logs to ensure auditability comparable to classical frameworks <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* Pre-trade Risk Control (<Ref>): Preventing excessive risk before trades execute.

 * Real-time Risk Control (<Ref>): Monitoring and intervening during trading.

 * Post-trade Risk Analysis (<Ref>): Learning from outcomes and improving risk models.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Comparability note]
Protocol-comparable risk claims typically report MR-3 (risk action semantics + priorities), MR-4 (execution/cost assumptions that risk controls depend on), and MR-6 (artifacts & logs); see <Ref>.

 < g r a p h i c s >

 Risk control timeline across the trading lifecycle. Pre-trade risk
 control sets limits and checks before orders are submitted. Real-time risk
 control monitors positions and markets during trading, intervening when
 thresholds are breached. Post-trade risk analysis analyzes outcomes to
 improve future risk management. This figure is schematic and is not
 used for evidence-mapping statistics or protocol comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Pre-trade Risk Control]
Pre-trade risk control prevents excessive risk by checking orders against risk
limits before they are submitted to the market. This preventive stage is the
first line of defense against catastrophic losses.

Representative Approaches. Value-at-Risk (VaR) limits cap the maximum
potential loss at a specified confidence level (e.g., 99Conditional VaR (CVaR) extends this by estimating the expected loss in the
tail beyond the VaR threshold <cit.>. Agentic systems increasingly employ
structured, model-based risk representations to estimate market risk in a transparent and
interpretable manner.
Exposure constraints limit concentrations to
single assets, sectors, or counterparties (e.g., no more than 10in any single stock). Compliance checks ensure trades respect regulatory
requirements and internal policies.
Some agentic prototypes explore using LLMs to translate human-readable policies into executable constraints <cit.>. However, this introduces non-deterministic risks.
[title=Protocol Implication]
 For protocol comparability, we recommend reporting: (1) VaR Config (Confidence Level, Holding Period, Window), (2) Scenario Source (Standard vs Custom), and (3) LLM Verification: policy-to-code translations are best validated against deterministic test sets rather than raw LLM chat outputs for compliance.

Technical Mechanisms. Portfolio risk models estimate the risk
contribution of each potential trade, considering both the standalone risk of
the position and its correlation with existing holdings. Let Σ denote the
covariance matrix of asset returns with entries σ_ij, and let w denote
portfolio weights. The portfolio variance is V = w^⊤Σ w, and the
marginal contribution to variance is
∂ V/∂ w_i = 2(Σ w)_i. A commonly used
risk contribution decomposition is RC_i = w_i(Σ w)_i, while the
marginal contribution to volatility is
∂σ_p/∂ w_i = (Σ w)_i / σ_p with
σ_p=√(w^⊤Σ w) <cit.>.
Scenario analysis simulates portfolio performance under stress scenarios
(market crash: -30σ× 3) to identify hidden risks that might not manifest under normal
conditions <cit.>. Rule engines encode regulatory and internal policies as executable
rules (e.g., Reg T margin requirements, Reg NMS order protection rules), with
LLMs parsing natural language policies to generate these rules automatically,
bridging the gap between human-readable policies and machine-executable code.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Pre-trade Risk Control]
ontribution to variance is
∂ V/∂ w_i = 2(Σ w)_i. A commonly used
risk contribution decomposition is RC_i = w_i(Σ w)_i, while the
marginal contribution to volatility is
∂σ_p/∂ w_i = (Σ w)_i / σ_p with
σ_p=√(w^⊤Σ w) <cit.>.
Scenario analysis simulates portfolio performance under stress scenarios
(market crash: -30σ× 3) to identify hidden risks that might not manifest under normal
conditions <cit.>. Rule engines encode regulatory and internal policies as executable
rules (e.g., Reg T margin requirements, Reg NMS order protection rules), with
LLMs parsing natural language policies to generate these rules automatically,
bridging the gap between human-readable policies and machine-executable code.

Agent-based approaches model transaction costs and market slippage
realistically for liquidity risk assessment 
<cit.>.
The STRIDE framework provides principled guidance for selecting between
agentic AI, AI assistants, or direct LLM calls in risk-sensitive
applications 
<cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Real-time Risk Control]
Real-time risk control monitors positions and market conditions during trading,
intervening when risk thresholds are breached or anomalous conditions emerge.
This reactive stage catches risks that pre-trade models miss due to changing
market conditions or model error.

Representative Approaches. Position monitoring tracks portfolio metrics
(greeks for options, duration for bonds, beta for equities) in real-time, alerting
when they exceed thresholds. Drawdown stops halt trading when portfolio losses
reach specified levels (e.g., stop trading if down 5scaling reduces position sizes as market volatility increases, maintaining
constant risk exposure. Risk control is a first-order design concern for cross-market robustness.
Text streams can provide early warnings <cit.>. Slower-moving macro uncertainty indices can complement them <cit.>, but they are not real-time signals. LLMs are generally unsuitable for the sub-millisecond Critical Path. A robust architecture typically separates a Gating Layer (deterministic algorithms such as circuit breakers for sub-millisecond stops) from an asynchronous Explanation Layer (LLMs for cause attribution). Reporting can disclose Latency Budgets and False Positive Rates for all triggers.

Technical Mechanisms. Stream processing systems update risk metrics
from tick data, trades, and order-book changes. Anomaly detection can flag price
spikes, volume surges, and order-book imbalance as stress signals
<cit.>. Circuit breakers halt trading when
drawdown or single-position loss limits are breached. Manual review before
restart helps prevent stress-driven decisions
<cit.>.

[title=Protocol Implication]
 We suggest reporting any dynamic exposure rule in display form rather
 than embedding it in prose. A simple example is

 w_i(t)=
 min(
 w_i^max,
 risk_budget/risk_per_unit_i)

 which caps concentration as prices and volatility change.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Post-trade Risk Analysis]
Post-trade risk analysis learns from trading outcomes to improve future risk
management. This retrospective stage identifies what risks were missed, how
effective controls were, and where improvements are needed.

Representative Approaches. Performance attribution decomposes
returns into component sources (alpha return, beta, timing, stock selection), identifying
which risks contributed to gains or losses. LLM-assisted attribution can trace how market factors propagate through the portfolio structure. Stress testing simulates portfolio
performance under historical crisis scenarios (2008 financial crisis and other major stress episodes) to assess resilience <cit.>. Regime analysis examines how portfolio performance
varied across market regimes (bull, bear, high volatility), identifying
conditions where risk management failed. LLM-enhanced systems can summarize risk outcomes, but preventing post-hoc rationalization is strongest when every narrative claim is grounded in immutable logs and replayable evidence <cit.>. Furthermore, Counterfactual Reasoning (e.g., "what if" scenarios) is best labeled as Hypothetical Inference dependent on structural assumptions, not empirical fact.

Technical Mechanisms. Causal analysis identifies the root causes of
risk events, distinguishing between market risk (systemic factors affecting all
assets), idiosyncratic risk (asset-specific events), and model error (incorrect
assumptions or predictions). Techniques include Granger causality tests, Shapley
value decomposition for attribution, and structural break detection to identify
when risk models failed. Counterfactual reasoning estimates what would have
happened under different risk management decisions (as an illustrative example,
“if we had reduced position size by 50from near-misses and close calls. Report generation produces human-readable risk
summaries for compliance and management review, with LLMs translating quantitative
metrics (“VaR exceeded by 20(“Risk was elevated due to concentrated tech exposure during the AI sector
correction; position limits were triggered but too late to prevent significant
losses”), making risk analysis interpretable for non-technical stakeholders
<cit.>.

Risk management method comparison. Protocol Tags (Split/Execution/Cost/Universe) denote reporting rigor (coding rules in <Ref>). (Background) indicates conceptual frameworks lacking empirical backtests.

 Stage Mechanisms LLM Enhancement

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Post-trade Risk Analysis]
duced position size by 50from near-misses and close calls. Report generation produces human-readable risk
summaries for compliance and management review, with LLMs translating quantitative
metrics (“VaR exceeded by 20(“Risk was elevated due to concentrated tech exposure during the AI sector
correction; position limits were triggered but too late to prevent significant
losses”), making risk analysis interpretable for non-technical stakeholders
<cit.>.

Risk management method comparison. Protocol Tags (Split/Execution/Cost/Universe) denote reporting rigor (coding rules in <Ref>). (Background) indicates conceptual frameworks lacking empirical backtests.

 Stage Mechanisms LLM Enhancement

Pre-trade VaR/CVaR limits; exposure constraints; compliance checks Rule interpretation; policy translation; natural-language constraints

Real-time Position monitoring; drawdown stops; volatility scaling Anomaly detection; news monitoring; early-warning signals

Post-trade Attribution; stress testing; regime analysis Narrative explanation; report generation; learning insights

<Ref> summarizes risk management approaches across the
three stages. Effective risk management depends on all three stages working in
concert: pre-trade controls prevent excessive risk, real-time controls catch
emerging risks, and post-trade analysis enables continuous improvement.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Safety and Constraint Mechanisms]
Deployable trading agents require safety layers that sit outside the model's generative reasoning loop. These include pre-trade exposure checks, hard position limits, concentration caps, drawdown triggers, and kill-switch logic that can halt order flow when market conditions or model behavior leave the approved operating envelope. In the current literature, such mechanisms are often mentioned briefly but rarely specified with enough detail to reproduce. For this reason, we treat safety architecture as part of the risk-management interface, not as an optional deployment afterthought.

In summary, this section has presented three stages of risk management that
protect trading agents from catastrophic losses. Pre-trade controls prevent
excessive risk, real-time controls respond to emerging risks, and post-trade
analysis enables learning and improvement. Together with the alpha generation
and portfolio management capabilities, risk management completes the core
capability set of trading agents. The next part of the survey explores how
agents adapt and evolve, extending beyond fixed capabilities to continuous
learning and improvement.

[float,floatplacement=tbp]Evidence Summary (Risk)

 * Risk controls are comparable only when protocol details are explicit: split scheme, trading frequency, and cost/impact assumptions materially change drawdowns and tail risk.

 * The literature recommends treating risk modules as gating mechanisms (position limits, kill switches, exposure budgets) rather than post-hoc reporting; logs and verifiable data sources are important for auditability.

 * Portfolio-level risk is sensitive to estimation error and regime shifts; robust baselines (e.g., classical allocation primitives) remain useful reference points <cit.>.

 * Evidence Grading: Studies missing I/O contracts or treating risk as a post-hoc metric are graded as (Basic/Conceptual). Credible improvement claims are stronger when backed by end-to-end gating logs. Evidence remains uneven; risk claims still require explicit caveats about data latency and false positives.

This completes Part II on the capabilities enabled by agentic architectures.
Having examined how agents generate alpha, manage portfolios, and control risk,
we now turn to Part III, which explores how agents adapt and evolve in dynamic
market environments.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Safety and Constraint Mechanisms]
timation error and regime shifts; robust baselines (e.g., classical allocation primitives) remain useful reference points <cit.>.

 * Evidence Grading: Studies missing I/O contracts or treating risk as a post-hoc metric are graded as (Basic/Conceptual). Credible improvement claims are stronger when backed by end-to-end gating logs. Evidence remains uneven; risk claims still require explicit caveats about data latency and false positives.

This completes Part II on the capabilities enabled by agentic architectures.
Having examined how agents generate alpha, manage portfolios, and control risk,
we now turn to Part III, which explores how agents adapt and evolve in dynamic
market environments.

Within the primary studies, none explicitly addressed risk mechanisms as a primary contribution; the section therefore synthesizes background literature and conceptual frameworks. The most persistent gap is protocol grounding: risk triggers, latency budgets, and audit logs are still inconsistent across papers.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Learning Paradigms]
The preceding parts of this survey established the architectural foundations of
agentic traders and the capabilities these architectures enable. This section
addresses the question: “How do agents learn from market
feedback?”

Learning enables agents to adapt their behavior based on experience, improving
performance over time and responding to changing market conditions. We organize
learning paradigms around a taxonomy of three approaches that differ in how
they incorporate feedback and update their behavior.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: Learning claims are supported only where update rules are evaluated in an end-to-end trading loop; this section synthesizes 3 primary studies with end-to-end trading evaluation, while general SFT, ICL, or RL mechanisms without trading closure are marked as [BG].

 2) Supported claim: Feedback can improve agent behavior in specific reported settings.

 3) Reporting gap: Studies often omit update frequency, training/evaluation separation, and post-update rollback rules.

 4) Implication: Learning should be audited as a protocol-governed update process rather than as a generic adaptation label.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* In-context Learning (ICL) (<Ref>): Learning from examples without parameter updates.

 * Supervised Fine-tuning (<Ref>): Learning from labeled demonstrations.

 * Reinforcement Learning (<Ref>): Learning from trial and error with reward feedback.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reward and Feedback Design]
Reward specification is a first-order design choice rather than an implementation detail. Trading environments impose delayed, noisy, and partially confounded feedback: realized P&L arrives after execution, inventory risk accumulates across steps, and reward proxies can be hacked by exploiting simulator artifacts. We therefore distinguish immediate execution feedback (fill quality, slippage, rejected orders) from delayed portfolio feedback (P&L, drawdown, turnover, and risk-adjusted return). Papers claiming adaptive improvement should report which of these signals are optimized, over what horizon, and with what safeguards against reward hacking.

Figure <ref> is a schematic taxonomy card for these
paradigms; it summarizes the learning-loop components, trade-offs, and
illustrative uses of each approach rather than serving as an empirical ranking.

 < g r a p h i c s >

 Schematic comparison card for three learning paradigms. The panels
 summarize what each loop updates, the main trade-offs emphasized in the
 design literature, and illustrative use cases. The figure is conceptual
 only and is not used for empirical comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: In-context Learning]
In-context learning (ICL) enables agents to adapt from examples provided in the
prompt without updating model parameters, following the GPT-3-style few-shot
paradigm <cit.> [BG]. This rapid adaptation mechanism is particularly
valuable in dynamic markets where conditions change faster than models can be
retrained.

Representative Approaches. FinAgent <cit.> uses ICL by
retrieving relevant trading episodes from memory and inserting them as examples
in the prompt, enabling the LLM to adapt its reasoning to similar situations
without parameter updates.

Technical Mechanisms. ICL systems are often organized around two
stages: (i) example selection (e.g., similarity- and regime-aware retrieval)
and (ii) prompt construction (ordering, formatting, and compressing historical
episodes to fit the context window) <cit.> [BG], <cit.>.
Retrieval-augmented generation (RAG) further extends ICL by pulling up-to-date
financial documents (news, filings, analyst notes) from external stores. The key
advantage is speed (no training), while the limitation is that adaptation is
temporary and bounded by the context window.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Supervised Fine-tuning]
Supervised fine-tuning (SFT) updates model parameters on labeled demonstrations
of desired behavior, teaching agents to imitate expert trading decisions. This
approach transfers knowledge from expert traders or historical successful
strategies into the agent.

Representative Approaches. The current section-level primary-study
count for SFT is N=0; the examples are therefore background building
blocks, not end-to-end trading evidence. FinGPT <cit.> illustrates
finance-domain instruction tuning for analysis, risk, and signal-generation
tasks. Two supervised variants are most relevant here. Behavior cloning maps
market states to expert actions, making trader demonstrations usable as policy
targets <cit.> [BG]. Multi-task adaptation trains on sentiment,
portfolio, and risk tasks together, producing representations that may transfer
across finance subtasks <cit.> [BG].

Technical Mechanisms. SFT relies on instruction/demo datasets with
prompt-response pairs (market context → expert decision or analysis).
Training minimizes a supervised loss (e.g., cross-entropy for discrete actions,
regression for sizing/allocation), with standard regularization and careful
held-out evaluation to check robustness to unseen regimes. Parameter-efficient
methods (e.g., LoRA-style methods) reduce cost while preserving much of the
base model; finance-oriented benchmarking work has explored these trade-offs
<cit.>. General parameter-efficient variants are background
mechanisms <cit.> [BG]. SFT can produce persistent
behavioral changes but is sensitive to label quality and distribution shift.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reinforcement Learning]
Reinforcement learning (RL) is used in trading agents when the objective is
inherently sequential (portfolio rebalancing, execution, or iterative factor
construction), the feedback is delayed, and the policy needs to trade off return,
risk, and costs under constraints.

Representative Approaches. FinRL-DeepSeek <cit.> combines
LLM-based priors with policy optimization, reporting risk-adjusted return improvements
over baselines in simulated environments[Specific
 performance metrics vary by configuration (e.g., CPPO-DeepSharpe vs. CPPO-DeepVol)
 and market regime; readers should consult the original paper for detailed
 protocol assumptions, cost models, and train/test split discipline.]. MacroHFT <cit.>
introduces memory-augmented context-aware RL for high-frequency trading, while
EarnHFT <cit.> explores hierarchical RL for HFT.
Deep RL for alpha discovery <cit.> frames factor construction as a
program-generation task, optimizing an evaluation metric over the search space
while balancing alpha performance and diversity.

Recent advances adjacent to RL address three key challenges in agent learning:
(1) modular memory architectures enable agents to accumulate and retain
experience across tasks <cit.> [BG]; (2) explicit state dynamics
improve temporal coherence in long-horizon agent behavior 
<cit.> [BG]; (3) code-based alpha evolution enables strategy
refinement through execution traces and natural language feedback 
<cit.>.

What should be reported (and why it matters). Because RL results are
highly sensitive to experimental setup, trading papers should explicitly specify
(i) chronological data splits (train/validation/test or walk-forward) and how
hyperparameters are chosen to avoid leakage; (ii) the cost model (commissions,
spread/slippage, and market impact assumptions); and (iii) simulator fidelity
(fill/latency assumptions, action/state/reward definitions, constraints, and
whether the simulator matches the instrument/microstructure being claimed).
Key risks include simulator overfitting and reward hacking: policies can exploit
artifacts of the backtester/cost model and fail catastrophically out-of-sample,
especially under non-stationarity and regime shifts.

Learning paradigm performance comparison

 Paradigm Speed Data Needed Adaptability Key Advantages Limitations

ICL Fast Low Medium No training, immediate Context window, temporary

SFT Medium High High Deep adaptation, transfer Needs labels, overfitting risk

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reinforcement Learning]
slippage, and market impact assumptions); and (iii) simulator fidelity
(fill/latency assumptions, action/state/reward definitions, constraints, and
whether the simulator matches the instrument/microstructure being claimed).
Key risks include simulator overfitting and reward hacking: policies can exploit
artifacts of the backtester/cost model and fail catastrophically out-of-sample,
especially under non-stationarity and regime shifts.

Learning paradigm performance comparison

 Paradigm Speed Data Needed Adaptability Key Advantages Limitations

ICL Fast Low Medium No training, immediate Context window, temporary

SFT Medium High High Deep adaptation, transfer Needs labels, overfitting risk

RL Slow Very high Very high Autonomous discovery High data, instability

<Ref> is a conceptual comparison of design trade-offs,
not a survey finding that all three paradigms are already validated or routinely
combined in trading systems. The next section explores how multiple agents
collaborate in markets.

[float,floatplacement=tbp]Evidence Summary (Section <ref>)

 * ICL enables rapid, non-persistent adaptation by conditioning on retrieved episodes and external context, without parameter updates <cit.>.

 * SFT remains background discussion in this section (N=0 primary studies); finance-oriented instruction tuning such as FinGPT is therefore treated as contextual motivation rather than primary trading evidence <cit.>.

 * RL can optimize sequential trading objectives, including programmatic alpha discovery, but results depend critically on split discipline, cost modeling, and simulator fidelity <cit.>.

 * A recurring failure mode is simulator/backtest overfitting, where policies exploit artifacts and degrade sharply in live-like settings <cit.>.

The next section addresses the question: “How do multiple
agents collaborate in markets?”

Across the 3 primary studies mapped in this section, ICL
appears once, SFT has no primary end-to-end trading study, and RL appears twice.
Reinforcement-learning-style adaptation therefore dominates the section's
primary evidence, but its reported gains remain sensitive to split discipline,
simulator fidelity, and reward-hacking risk.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Multi-Agent Coordination]
Note: Multi-agent coordination spans both architectural
(organization structure) and adaptation (coordination learning) dimensions.
We place it in Part III due to its emphasis on emergent coordination dynamics,
but acknowledge it could equally be classified as an architectural dimension.

The preceding sections examined the architecture and capabilities of agentic
traders. This section addresses the question: “How do multiple
agents collaborate in markets?”

Multi-agent systems enable specialization and decomposition, with different
agents focusing on different aspects of the trading problem (analysis,
execution, risk management). What remains unsettled is whether coordination
itself delivers superior trading performance once computational budget,
information access, and protocol design are held constant. We organize
multi-agent coordination around a taxonomy of three patterns that differ in
their structure and interaction mechanisms.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: Coordination claims are primary only when role interaction affects an evaluated trading loop; general multi-agent systems and market-structure literature are retained as [BG] unless they provide end-to-end trading evidence.

 2) Supported claim: Multi-agent systems can decompose analysis, debate, trading, and risk-control functions.

 3) Reporting gap: Role permissions, message protocols, shared state, consensus rules, and ablation results are underreported.

 4) Implication: Coordination should be treated as a mechanism requiring role-level attribution, not as automatic evidence of performance improvement.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* Role-based Collaboration (<Ref>): Specialized agents with distinct roles working together.

 * Hierarchical Organization (<Ref>): Layered decision-making with strategic and tactical agents.

 * Market Ecology (<Ref>): Agents interacting through market mechanisms with emergent behavior.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Comparability note]
Protocol-comparable coordination claims should report MR-7 (roles/permissions, message protocol, consensus, shared state, and evaluation); see <Ref>.

Figure <ref> summarizes the coordination taxonomy used
in this section as a set of stylized archetypes.

 < g r a p h i c s >

 Three coordination patterns in multi-agent trading. Role-based
 collaboration assigns specialized roles (analyst, trader, risk manager) to
 different agents. Hierarchical organization layers agents from strategic
 (asset allocation) to tactical (position sizing) to execution (individual
 trades). Market ecology models agents interacting through markets with feedback
 and emergence. The structure/example/illustrative-use panels are stylized
 archetypes rather than evidence-ranked categories. This figure is schematic
 and is not used for evidence-mapping statistics or protocol comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Role-based Collaboration]
Role-based collaboration assigns specialized roles to different agents, each
focusing on a specific aspect of the trading problem while coordinating to
achieve collective goals. This division of labor enables deep specialization
while maintaining coherent decision-making <cit.> [BG].

Representative Approaches. It is helpful to separate three evidence
layers. Primary trading systems in the current section-level subset
show role specialization most directly: TradingAgents <cit.>
assigns analyst/trader/risk/portfolio roles; FINCON <cit.>
structures debate and consensus; TradingGroup
 <cit.> combines role specialization with
reflection; and the REIT pipeline <cit.> makes an
analysis–prediction–decision–execution workflow explicit. These papers make
decomposition visible, but complex role assignments can still obscure the source
of gains. To support attribution, systems must log decision
contributions (which agent proposed or vetoed an action) and perform
role/communication ablations to verify that gains stem from coordination rather
than increased computational budget.
General LLM multi-agent optimization work such as HiveMind is relevant here as
background for contribution-guided credit assignment and online prompt refinement,
but should not be read as evidence that such coordination mechanisms are already
validated across trading settings <cit.>.

Benchmarks and simulated arenas form a second layer. TraderBench,
MarS, and related multi-agent market arenas
<cit.> are useful for stressing
specialization and interaction patterns, but they do not by themselves establish
end-to-end trading coordination gains under comparable execution semantics.

Background MAS/ABM literature forms a third layer, including social or
behavioral market models <cit.>,
RL-plus-ABM interaction studies <cit.>,
workspace delegation <cit.>, and reciprocity-oriented foundations
<cit.>. These citations are useful for
mechanism design, but they are not counted toward the section-level primary
study total of N=12.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Role-based Collaboration]
are already
validated across trading settings <cit.>.

Benchmarks and simulated arenas form a second layer. TraderBench,
MarS, and related multi-agent market arenas
<cit.> are useful for stressing
specialization and interaction patterns, but they do not by themselves establish
end-to-end trading coordination gains under comparable execution semantics.

Background MAS/ABM literature forms a third layer, including social or
behavioral market models <cit.>,
RL-plus-ABM interaction studies <cit.>,
workspace delegation <cit.>, and reciprocity-oriented foundations
<cit.>. These citations are useful for
mechanism design, but they are not counted toward the section-level primary
study total of N=12.

Communication Protocols. Role-based collaboration requires rich communication
protocols to enable effective coordination. Broadcasting allows an agent to share
information with all team members simultaneously, useful for market-wide alerts
or portfolio status updates. Peer-to-peer communication enables direct exchange
between specific agents, such as the risk manager warning the trader about
excessive exposure. Shared memory provides a common knowledge base where agents
can read and write information, enabling asynchronous coordination without
requiring all agents to be available simultaneously. These protocols need to be
designed to balance information richness against communication overhead, as
excessive messaging can slow decision-making in fast-moving markets
<cit.> [BG].

Consensus Mechanisms. When specialized agents disagree, consensus mechanisms
aggregate diverse opinions into coherent decisions. Voting treats all agents equally,
with the majority or plurality determining the final action. Expert weights assign
different influence to agents based on their historical accuracy or domain expertise,
allowing the analyst to dominate stock selection while the risk manager influences
position sizing. Debate-based consensus enables agents to present arguments and
counterarguments, with FINCON <cit.> providing a conceptual
language that structures these discussions. The choice of consensus mechanism
involves trade-offs between speed (voting is fast) and quality (debate can uncover
blind spots but takes longer). Dynamic mechanisms that adapt based on market
conditions or agent confidence are particularly valuable in volatile markets
<cit.> [BG].

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Role-based Collaboration]
r plurality determining the final action. Expert weights assign
different influence to agents based on their historical accuracy or domain expertise,
allowing the analyst to dominate stock selection while the risk manager influences
position sizing. Debate-based consensus enables agents to present arguments and
counterarguments, with FINCON <cit.> providing a conceptual
language that structures these discussions. The choice of consensus mechanism
involves trade-offs between speed (voting is fast) and quality (debate can uncover
blind spots but takes longer). Dynamic mechanisms that adapt based on market
conditions or agent confidence are particularly valuable in volatile markets
<cit.> [BG].

Task Allocation. Effective role-based collaboration requires intelligent
task allocation that matches work to agent capabilities and current workload.
Capability-based allocation assigns tasks based on specialized expertise, such as
routing earnings analysis to the fundamental analyst while the technical analyst
handles technical signals. Workload-based allocation considers current load,
preventing bottlenecks when one agent is overwhelmed. Hybrid approaches combine
both factors, ensuring that urgent but non-specialized tasks (such as emergency
risk reduction) can be handled by any available agent. Task allocation may be
centralized (a supervisor agent assigns work, as in TradingAgents) or decentralized
(agents self-assign based on capability and availability). Dynamic reallocation
enables the system to adapt when agents fail or become overloaded, improving
robustness <cit.> [BG].

Conflict Resolution. Disagreements between specialized agents are inevitable,
particularly when agents have different perspectives (optimistic analyst vs pessimistic
risk manager) or when their roles create tensions (trader seeking profit vs risk manager
seeking safety). Negotiation allows agents to propose compromises, such as reducing
position size to satisfy both profit targets and risk limits. Arbitration delegates
dispute resolution to a higher authority (the supervisor in TradingAgents), ensuring
that critical decisions are not deadlocked. Authority hierarchies establish which
agent's view dominates in which domain (the risk manager has veto power over
position sizing, while the analyst controls stock selection). Learning from past
conflicts improves resolution over time, with agents developing heuristics for
when to escalate disagreements and when to accept compromises
<cit.> [BG].

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Hierarchical Organization]
Hierarchical organization structures agents into layers, with higher-level
agents making strategic decisions and lower-level agents executing tactical
actions. This structure enables coherence across time scales, from long-term
asset allocation to short-term execution.

Representative Approaches. FinMem <cit.> employs a
three-layer memory hierarchy: working memory (seconds-minutes), episodic memory
(days-weeks), and semantic memory (long-term). H-MEM <cit.>
extends this with semantic hierarchy, reporting efficiency improvements through
hierarchical memory organization. In multi-agent settings, strategic agents
set high-level targets (“reduce tech exposure by 20determine specific trades to achieve these targets. Recent general-purpose frameworks like DyLAN <cit.>, MetaGPT <cit.>, and HiveMind <cit.> demonstrate how dynamic architecture, role definitions, and prompts can evolve, a concept increasingly relevant for adaptive trading hierarchies.

Benchmarks and Protocols. Coordination claims are difficult to compare
without common evaluation protocols and cost/execution semantics. Recent work
introduces live and replay-based benchmarks for trading agents that stress
sequential decision-making under real or event-driven market dynamics, including
AI-Trader <cit.>, Agent Market Arena <cit.>,
LiveTradeBench <cit.>, ContestTrade <cit.>,
and PredictionMarketBench <cit.>.
These benchmarks help separate architecture effects (coordination design, memory,
workflow) from model-backbone effects, but remain sensitive to market selection,
episode construction, and transaction cost assumptions.
[title=Protocol Implication]
 For multi-agent systems, we recommend explicit reporting of:
 (i) cross-play evaluation (swap individual agents to test interoperability vs. team overfitting),
 (ii) explicit communication constraints (channel bandwidth and tool-call budgets),
 (iii) crowding and impact metrics (e.g., impact amplification under correlated policies), and
 (iv) role ablations to attribute gains to coordination rather than increased information access.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Hierarchical Organization]
tBench <cit.>.
These benchmarks help separate architecture effects (coordination design, memory,
workflow) from model-backbone effects, but remain sensitive to market selection,
episode construction, and transaction cost assumptions.
[title=Protocol Implication]
 For multi-agent systems, we recommend explicit reporting of:
 (i) cross-play evaluation (swap individual agents to test interoperability vs. team overfitting),
 (ii) explicit communication constraints (channel bandwidth and tool-call budgets),
 (iii) crowding and impact metrics (e.g., impact amplification under correlated policies), and
 (iv) role ablations to attribute gains to coordination rather than increased information access.

Goal Decomposition. Hierarchical organization requires breaking high-level
objectives into actionable sub-goals that lower-level agents can execute. Top-down
decomposition starts with strategic objectives (“achieve 151060with equal weights”). Constraint-based decomposition helps ensure that sub-goals
respect risk limits, liquidity constraints, and regulatory requirements. Dynamic
decomposition adjusts targets based on market conditions, such as reducing return
targets during bear markets or tightening risk limits when volatility spikes.
The effectiveness of goal decomposition depends on how well strategic intent can
be translated into tactical guidance without micromanaging lower-level agents; layers should specify clear I/O contracts (e.g., strategic targets vs. tactical orders) to prevent semantic drift <cit.>.

Feedback Mechanisms. Hierarchies rely on upward feedback to close the loop
between strategy and execution. Bottom-up reporting enables tactical agents to
inform strategic agents about outcomes, constraints, and opportunities. For example,
execution agents report that liquidity is insufficient for the desired position size,
prompting strategic agents to revise the allocation. Exception escalation triggers
when lower-level agents encounter problems they cannot resolve, such as unexpected
market events or violations of risk limits. Performance feedback provides information
about which strategies are working, enabling strategic agents to reallocate resources
to successful approaches. Effective feedback requires appropriate aggregation: raw
data from execution must be summarized into metrics that inform strategic decisions
without overwhelming strategic agents with details <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Hierarchical Organization]
omes, constraints, and opportunities. For example,
execution agents report that liquidity is insufficient for the desired position size,
prompting strategic agents to revise the allocation. Exception escalation triggers
when lower-level agents encounter problems they cannot resolve, such as unexpected
market events or violations of risk limits. Performance feedback provides information
about which strategies are working, enabling strategic agents to reallocate resources
to successful approaches. Effective feedback requires appropriate aggregation: raw
data from execution must be summarized into metrics that inform strategic decisions
without overwhelming strategic agents with details <cit.>.

Exception Handling. Lower-level agents inevitably encounter situations that
exceed their authority or capability, requiring escalation to higher-level decision-makers.
Predefined escalation triggers determine when to elevate issues, such as position
limits exceeded, unusual market conditions, or conflicting signals. Time-sensitive
exceptions (market crashes, circuit breakers) require immediate escalation with minimal
delays. Resolution strategies range from fully automated (circuit breakers automatically
reduce exposure) to human-in-the-loop (unusual patterns reported to human supervisors).
Learning from exceptions improves future handling, with systems developing better
triggers and resolution strategies over time. The design of exception handling involves
trade-offs between false positives (escalating too often, creating noise) and false
negatives (missing critical issues that require intervention) <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Hierarchical Organization]
ate issues, such as position
limits exceeded, unusual market conditions, or conflicting signals. Time-sensitive
exceptions (market crashes, circuit breakers) require immediate escalation with minimal
delays. Resolution strategies range from fully automated (circuit breakers automatically
reduce exposure) to human-in-the-loop (unusual patterns reported to human supervisors).
Learning from exceptions improves future handling, with systems developing better
triggers and resolution strategies over time. The design of exception handling involves
trade-offs between false positives (escalating too often, creating noise) and false
negatives (missing critical issues that require intervention) <cit.>.

Temporal Abstraction. Different layers of the hierarchy operate at different
time scales, enabling separation between long-term planning and short-term reaction.
Strategic agents operate at daily, weekly, or monthly frequencies, making decisions
about asset allocation, factor tilts, and overall portfolio construction. Tactical
agents operate at intraday or minute-level frequencies, managing individual positions,
entry and exit timing, and execution quality. This separation prevents short-term
noise from disrupting long-term strategy: a temporary price spike should not trigger
a reallocation of the entire portfolio. However, temporal abstraction creates challenges
for coordination: strategic agents need to set bounds (risk limits, position limits) that
constrain tactical agents without being overly restrictive. Multi-scale learning enables
agents to learn at different time horizons, with strategic agents learning from
long-term patterns while tactical agents adapt to short-term dynamics
<cit.> [BG].

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Market Ecology]
Market ecology models agents as participants in a market environment,
interacting through trading and prices rather than direct communication. In the
current literature, this pattern is best read as an exploratory setting for
studying collective behavior, not as mature evidence that ecological
coordination improves live trading outcomes.

Representative Approaches. Agent-based simulations <cit.>
populate markets with heterogeneous agents to generate synthetic market data and
to stress test strategies under controlled conditions. Related work studies how
agent-environment feedback can produce boom-bust dynamics and how repeated
interaction may lead to undesirable emergent coordination, motivating regulatory
and monitoring considerations.
FinEvo <cit.> proposes an ecological market-game framing to study the
evolution of interacting financial strategies, emphasizing that competitive performance
can depend on population composition and adaptive feedback rather than isolated backtests.
Validating ecological models requires rigorous calibration against real market microstructure to avoid simulator overfitting. Furthermore, protocols must audit for timestamp leakage and consensus smoothing, ensuring that emergent coordination is not an artifact of look-ahead bias or noise suppression.

Pioneering work in generative agents <cit.> established the viability of LLM-based simulacra. Subsequent financial-market simulations with LLM agents <cit.> explore how agent behaviors can affect market dynamics, enabling researchers to study emergent phenomena in controlled settings.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Market Ecology]
etitive performance
can depend on population composition and adaptive feedback rather than isolated backtests.
Validating ecological models requires rigorous calibration against real market microstructure to avoid simulator overfitting. Furthermore, protocols must audit for timestamp leakage and consensus smoothing, ensuring that emergent coordination is not an artifact of look-ahead bias or noise suppression.

Pioneering work in generative agents <cit.> established the viability of LLM-based simulacra. Subsequent financial-market simulations with LLM agents <cit.> explore how agent behaviors can affect market dynamics, enabling researchers to study emergent phenomena in controlled settings.

Market Mechanisms. Market ecology relies on established market structures
to mediate agent interactions without requiring direct coordination. Continuous double
auctions enable buyers and sellers to trade at any time, with prices emerging from
the real-time balance of supply and demand. Call auctions aggregate orders over
specific time intervals (open, close, volatility interruptions), determining prices
through batch execution that reduces informational asymmetry. Dealer markets
designate specific market makers who provide liquidity by continuously quoting bid
and ask prices, with agents trading against these quotes rather than directly with
each other. Each mechanism creates different incentives and dynamics: continuous
double auctions favor fast reactions to information, call auctions reduce timing
risk, and dealer markets provide guaranteed liquidity but at a cost (the bid-ask
spread). The choice of market mechanism shapes the ecology by determining which
strategies are viable and how information propagates through prices
<cit.> [BG].

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Market Ecology]
 close, volatility interruptions), determining prices
through batch execution that reduces informational asymmetry. Dealer markets
designate specific market makers who provide liquidity by continuously quoting bid
and ask prices, with agents trading against these quotes rather than directly with
each other. Each mechanism creates different incentives and dynamics: continuous
double auctions favor fast reactions to information, call auctions reduce timing
risk, and dealer markets provide guaranteed liquidity but at a cost (the bid-ask
spread). The choice of market mechanism shapes the ecology by determining which
strategies are viable and how information propagates through prices
<cit.> [BG].

Price Formation. In market ecology, no single agent sets prices; instead,
prices emerge from the aggregate behavior of all agents. Order aggregation combines
individual buy and sell orders into a collective order book, with the intersection
of supply and demand determining the market-clearing price. Supply-demand balance
shifts as agents react to news, portfolio changes, or risk management needs, causing
prices to adjust. Informational efficiency measures how quickly prices incorporate
new information, with efficient markets preventing agents from consistently profiting
from public information. However, when agents are heterogeneous (different beliefs,
time horizons, risk tolerances), prices may deviate from fundamental values for
extended periods, creating opportunities for some agents at the expense of others.
The dynamics of price formation depend on agent diversity: homogeneous agents tend
to produce rapid convergence to consensus prices, while heterogeneous agents create
more complex patterns with mispricings that persist until corrected by informed agents
<cit.> [BG].

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Market Ecology]
nt needs, causing
prices to adjust. Informational efficiency measures how quickly prices incorporate
new information, with efficient markets preventing agents from consistently profiting
from public information. However, when agents are heterogeneous (different beliefs,
time horizons, risk tolerances), prices may deviate from fundamental values for
extended periods, creating opportunities for some agents at the expense of others.
The dynamics of price formation depend on agent diversity: homogeneous agents tend
to produce rapid convergence to consensus prices, while heterogeneous agents create
more complex patterns with mispricings that persist until corrected by informed agents
<cit.> [BG].

Reflexivity and Feedback Loops. Market ecology creates reflexive relationships
where agent actions affect prices, which in turn affect agent perceptions and actions.
This two-way feedback can produce complex dynamics not present in systems with
one-way causality. Positive feedback amplifies initial movements: price increases
attract trend-following agents who buy, pushing prices higher and attracting more
trend followers, potentially creating bubbles. Negative feedback stabilizes: price
increases trigger profit-taking by mean-reversion agents who sell, pushing prices
back toward fundamentals. The balance between positive and negative feedback determines
market stability. Reflexivity becomes particularly powerful when agents learn and
adapt: successful strategies attract imitators, changing market dynamics and potentially
rendering the original strategy unprofitable. This co-evolution of agents and markets
creates continuously changing patterns, making long-term prediction difficult even
as short-term patterns may be exploitable <cit.> [BG].

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Market Ecology]
s who buy, pushing prices higher and attracting more
trend followers, potentially creating bubbles. Negative feedback stabilizes: price
increases trigger profit-taking by mean-reversion agents who sell, pushing prices
back toward fundamentals. The balance between positive and negative feedback determines
market stability. Reflexivity becomes particularly powerful when agents learn and
adapt: successful strategies attract imitators, changing market dynamics and potentially
rendering the original strategy unprofitable. This co-evolution of agents and markets
creates continuously changing patterns, making long-term prediction difficult even
as short-term patterns may be exploitable <cit.> [BG].

Emergent Phenomena. The interaction of heterogeneous agents through market
mechanisms can generate exploratory scenarios that are not apparent from studying
individual agents in isolation. Bubbles may occur when positive feedback dominates,
with rising prices attracting speculative buying disconnected from fundamentals.
Crashes may happen when bubbles burst or when negative feedback triggers panic selling,
with prices plummeting as agents rush to exit simultaneously. Flash crashes represent
extreme short-term crashes where prices rapidly plummet and recover within minutes,
and are mechanistically plausible when high-frequency agents interact with market structure.
Tacit collusion is another plausible risk when agents learn to coordinate
behavior implicitly through repeated interaction without explicit communication,
raising regulatory concerns about market manipulation. These emergent phenomena are
difficult to predict because they depend on the collective behavior of many agents,
so agent-based simulation is better viewed as a hypothesis-generation tool for
understanding market dynamics and stress cases <cit.> [BG].

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Strategy Crowding and Alpha Decay]
As LLM-based agents proliferate, similar training data and reasoning patterns
may lead to strategy homogenization. When multiple agents:

* Use similar foundation models (GPT-4, Claude)

 * Fine-tune on similar financial corpora

 * Employ comparable CoT or RAG patterns

they may generate correlated trading signals, creating mechanistically plausible risks such as:

* Alpha decay: Common signals are arbitraged away faster

 * Self-reinforcing trends: Similar entry points amplify momentum

 * Correlated exits: Simultaneous stop-loss triggering increases volatility

 * Flash crash risk: Rapid unwinding of crowded positions

The evidence base currently lacks studies of multi-agent market impact at scale.
We identify this as a critical gap requiring simulation-based research before
deployment.

Regulatory Constraints. Regulators shape market ecology by constraining
agent behavior to maintain market integrity and stability. Position limits prevent
any single agent from dominating the market or taking excessive risks. Circuit breakers
halt trading during extreme volatility, providing time for information to diffuse and
potentially preventing panic selling. Market maker obligations require designated
liquidity providers to quote prices continuously, ensuring that other agents can always
trade. Reporting requirements may require that agents disclose large positions or trades,
reducing information asymmetry. Manipulation rules prohibit agents from engaging in
behavior that artificially affects prices (spoofing, layering, pump-and-dump schemes).
The design of these regulations needs to balance competing goals: too little regulation
enables manipulation and instability, while too much regulation reduces liquidity and
efficiency. Agent-based simulation enables regulators to test proposed rules before
implementation, identifying unintended consequences and optimizing regulatory parameters
<cit.>.

< g r a p h i c s >

Market ecology interaction network. Agents interact both with one
 another and through the market environment, where prices, spreads, quotes,
 and fills feed back into subsequent behavior. The figure highlights
 reflexive feedback and competition channels that can support exploratory
 study of crowding, instability, and adaptation. This figure is schematic
 and is not used for evidence-mapping statistics or protocol
 comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Strategy Crowding and Alpha Decay]
and instability, while too much regulation reduces liquidity and
efficiency. Agent-based simulation enables regulators to test proposed rules before
implementation, identifying unintended consequences and optimizing regulatory parameters
<cit.>.

< g r a p h i c s >

Market ecology interaction network. Agents interact both with one
 another and through the market environment, where prices, spreads, quotes,
 and fills feed back into subsequent behavior. The figure highlights
 reflexive feedback and competition channels that can support exploratory
 study of crowding, instability, and adaptation. This figure is schematic
 and is not used for evidence-mapping statistics or protocol
 comparison.

Multi-agent coordination comparison. Tags: R=Reproducibility level (R0–R3), E=Execution semantics reported, -E–=Execution not reported (see <Ref> for full coding rules).

 Pattern Example Comm. Decision Making Scalability Tags

Role-based TradingAgents <cit.>, FINCON <cit.>, TradingGroup <cit.> Direct, rich communication Consensus, voting, debate Moderate (coordination overhead)

Hierarchical Multi-agent investment pipeline <cit.> Vertical, layered feedback Top-down commands, bottom-up reporting High (clear authority)

Market Ecology Agent simulations; FinEvo <cit.> Indirect, via prices/trades Decentralized, independent Very high (no direct coordination)

<Ref> summarizes coordination patterns. The final
section of Part III explores self-evolution, examining how agents improve their
own architectures and capabilities.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Latency Constraints on Coordination]
The coordination mechanisms discussed above must operate within the latency budget established in <Ref>. Coordination cost is dominated by communication, consensus formation, and decision aggregation, so voting is typically cheaper than debate while expert-weighted aggregation sits in between. In latency-sensitive regimes, systems may need to prefer the simplest mechanism that preserves acceptable decision quality. This latency-aware coordination design remains an open research direction for financial multi-agent systems.

[float,floatplacement=tbp]Evidence Summary (Multi-agent)

 * Most auditable in the current subset (): Role-based systems with defined permissions, message budgets, and ablation studies provide the clearest coordination traces in the current evidence base; this does not imply performance superiority.

 * Low Evidence (): Conceptual hierarchies and ecological simulations often lack calibration or I/O contracts, representing design directions rather than empirical proof.

 * Attribution Protocol: Evaluating coordination requires decision contribution logs and explicit ablation studies (removing roles/channels) to distinguish mechanism gains from compute scaling.

 * Communication Audit: Message protocols must be specified (budget, aggregation) and audited for timestamp leakage and look-ahead bias.

 * Benchmarks: Robust evaluation requires cross-play (generalization), crowding (market impact), and strategic behavior monitoring (detection of collusion or gaming).

 * Coverage (section-level): The section-level primary-study count is N=12; additional citations in the text include benchmarks and background MAS/ABM work that are not part of that primary-study total.

Within the primary studies, 9 addressed coordination mechanisms. Role-based systems contain the clearest auditable exemplar in the current subset, while hierarchical and ecological designs still need stronger calibration and cross-play evaluation.

The next section addresses the question: “How do agents
improve themselves autonomously?”

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Adaptation and Self-Evolution]
The preceding sections examined how agents are built (architecture), what they
can do (capabilities), and how they can coordinate. This section addresses the
question: “How do agents adapt and improve over time?”

Note: Many mechanisms described in this section (e.g., memory
consolidation, meta-learning, self-reflection) originate in general AI
research; in trading, they remain experimental and should be interpreted
through explicit update governance rather than as industry-standard
practice. Studies marked [BG] are background literature without end-to-end
trading evaluation. Adaptationself-evolution claims are only comparable when
the update loop is reproducible (MR-6; see <Ref>): papers
should report what can change (prompts, memory summaries, retrieval indices,
weights), when updates trigger, and what historical window is used, with
immutable logs plus frozen execution and cost semantics so that apparent
“improvements” cannot be explained by protocol drift.

Adaptation can occur at multiple levels: updating behavior within a fixed
architecture (e.g., experience-driven policy refinement) and changing the
agent's internal components over longer horizons (self-evolution). In trading
settings, such claims are particularly sensitive to leakage and evaluation
protocol drift.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evidence status]
1) Evidence base: Self-evolution claims are supported only when an update loop is evaluated under fixed temporal and execution assumptions.

 2) Supported claim: Some systems report reflection, memory revision, or strategy refinement, but evidence for durable self-improvement remains preliminary.

 3) Reporting gap: Papers rarely freeze update triggers, data windows, and rollback criteria.

 4) Implication: Adaptation should be reported with immutable logs and pre/post-update evaluation boundaries; online updates must be separated from out-of-sample testing and tied to frozen execution assumptions.

Self-evolution extends beyond learning within a fixed structure: the agent can
compress and reorganize its memory, improve its own learning process, and
critique and repair reasoning failures over time.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Taxonomy]
* Memory Consolidation (<Ref>): Compressing and abstracting memories over time.

 * Meta-Learning (<Ref>): Learning to learn more efficiently.

 * Self-Reflection (<Ref>): Critiquing and improving own reasoning.

 < g r a p h i c s >

 Conceptual governed update loop. Agents accumulate experience through
 trading, consolidate important patterns into memory, apply meta-learning-like
 update policies, and use reflection to critique reasoning under logging and
 rollback constraints. The figure is schematic, representing a
 protocol-constrained loop rather than an empirical proof of autonomous
 improvement, and is not used for evidence-mapping statistics or
 protocol comparison.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Memory Consolidation]
Memory consolidation transforms and compresses experiences over time, extracting
general principles and discarding irrelevant details. This process prevents
memory bloat and improves retrieval efficiency while preserving the most valuable
knowledge.

Representative Approaches. Trading-facing evidence in this subsection
is thin and should be separated from background mechanisms. Within the
section-level primary subset, memory-consolidation-like behavior is most visible
in systems that keep episodic traces and derived summaries for later retrieval,
such as FinMem and related retrieval-centered trading agents
<cit.>. Experience replay samples important past
experiences for rehearsal, strengthening their encoding in memory. Summarization
compresses long episodes into concise representations, capturing key outcomes
and lessons. Abstraction extracts general rules from specific cases (“stocks
often drop after earnings misses”). Forgetting mechanisms remove low-value
memories entirely, focusing capacity on the most relevant information.
Broader cited systems such as TradingGPT belong to the wider citation set rather
than defining the section-level primary-study count <cit.>.

Technical Mechanisms. Importance scoring weights memories based on
multiple factors to determine which experiences should be retained. Recency bias
gives higher weight to recent experiences, assuming they better reflect current
market conditions. Outcome-based weighting prioritizes successful trades and
costly mistakes, as these provide the strongest learning signal. Retrieval frequency
tracks how often memories are accessed, with frequently-used memories deemed more
valuable. These scoring mechanisms can be combined linearly or learned adaptively
through neural networks <cit.> [BG].

Compression algorithms reduce memory footprint while preserving useful signals
<cit.> [BG]. Autoencoders learn compact latent
representations. Quantization trades precision for storage. Summarization
condenses long episodes into concise lessons about decisions and outcomes.
Hierarchical compression keeps recent memories detailed and stores older memories
at coarser resolution.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Memory Consolidation]
prioritizes successful trades and
costly mistakes, as these provide the strongest learning signal. Retrieval frequency
tracks how often memories are accessed, with frequently-used memories deemed more
valuable. These scoring mechanisms can be combined linearly or learned adaptively
through neural networks <cit.> [BG].

Compression algorithms reduce memory footprint while preserving useful signals
<cit.> [BG]. Autoencoders learn compact latent
representations. Quantization trades precision for storage. Summarization
condenses long episodes into concise lessons about decisions and outcomes.
Hierarchical compression keeps recent memories detailed and stores older memories
at coarser resolution.

Conflict resolution handles contradictory memories that arise from changing
market conditions. Temporal weighting resolves conflicts in favor of more recent
memories, assuming they reflect current dynamics. Contextual conditioning extracts
the contexts in which each memory applies (e.g., “this strategy works in bull
markets but fails in bear markets”), enabling agents to apply the right memory
to the right situation. Abstraction extracts higher-level rules that explain
apparent contradictions, revealing the underlying principles that govern both
cases <cit.> [BG].

Consolidation can be triggered by specific events or run periodically as a
background process. Event-triggered consolidation responds to significant market
changes (regime shifts, crashes, new regulations) by re-evaluating and reorganizing
memories to adapt to the new environment. Periodic consolidation runs at fixed
intervals (daily, weekly), gradually compressing and abstracting memories over time.
Hybrid approaches combine both, using periodic consolidation with event-driven acceleration when major changes occur <cit.> [BG].

Audit Trail Requirement: Summarization can hallucinate details not present in the original log or lose the link to the trade decision. To remain auditable, consolidated memories must retain an immutable pointer (hash or timestamp) to the raw transaction logs. Adaptation protocols should periodically validate that summaries do not contain factual errors or future information compared to the ground-truth logs.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Meta-Learning]
Meta-learning enables agents to learn how to learn, improving the efficiency and
effectiveness of their learning process. In this survey, however, trading-facing
evidence remains extremely limited: the section-level count for meta-learning is
N=0, because no included study explicitly implements a finance-specific
meta-learning algorithm (e.g., MAML). Early finance-oriented prototype systems instead explore multi-agent
evolutionary loops to generate and select strategies or factors under backtest
feedback <cit.>; these results are prototype-level and must be interpreted through the
lens of evaluation protocol and cost/execution assumptions. The primary challenge is therefore not the algorithm (e.g.,
MAML), but the rigorous definition of “tasks” and sealed feedback channels to
prevent look-ahead bias.

Task Splitting Requirement. In trading, a “task” cannot simply be a random sample of assets or days. To prevent leakage, tasks must be split by time (e.g., 2010–2015 as source, 2016 as target) or by distinct, non-overlapping asset classes. Random shuffling of episodes across time violates the causal structure of markets, creating false “adaptation” that is merely memorization of future regimes.

Representative Approaches. MAML (Model-Agnostic Meta-Learning)
<cit.> [BG] learns initialization parameters that enable rapid adaptation
with few gradient steps. Learning to learn optimizes
the learning rate schedule, exploration strategy, and architecture hyperparameters
through experience, rather than relying on human experts to tune these.
Finance-oriented prototype systems use originality constraints and iterative
critique to reduce brittle search behavior; AlphaAgent regularizes factor
generation, and TradingGroup combines self-reflection with data synthesis
<cit.>. More general multi-agent optimization
systems such as Yuksel et al. <cit.> [BG] illustrate the same
iterative-refinement pattern, although they remain background evidence rather
than finance-specific proof.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Meta-Learning]
itialization parameters that enable rapid adaptation
with few gradient steps. Learning to learn optimizes
the learning rate schedule, exploration strategy, and architecture hyperparameters
through experience, rather than relying on human experts to tune these.
Finance-oriented prototype systems use originality constraints and iterative
critique to reduce brittle search behavior; AlphaAgent regularizes factor
generation, and TradingGroup combines self-reflection with data synthesis
<cit.>. More general multi-agent optimization
systems such as Yuksel et al. <cit.> [BG] illustrate the same
iterative-refinement pattern, although they remain background evidence rather
than finance-specific proof.

Technical Mechanisms. Task distributions define the set of related tasks
that the agent should learn to handle. In trading, tasks can correspond to different
market regimes (bull vs bear, high vs low volatility), asset classes (equities,
futures, crypto), or time periods (pre- vs post-crisis). The meta-learning objective
optimizes performance across the distribution, learning initialization parameters
that enable rapid adaptation to any task in the distribution with minimal task-specific
data. Domain generalization extends this to unseen but related tasks, ensuring
the agent can handle novel market conditions <cit.> [BG].

Few-shot learning divides data into support sets and query sets. Support sets
provide a small number of examples from a new task (e.g., 5 recent trades in a
new market regime), serving as context for adaptation. Query sets test performance
on that task, evaluating how well the agent has adapted. Inner loop optimization
adapts the model to the specific task using the support set, typically through
one or a few gradient steps. Outer loop optimization updates the meta-parameters
across all tasks, learning initialization that facilitates rapid inner loop adaptation.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Meta-Learning]
Domain generalization extends this to unseen but related tasks, ensuring
the agent can handle novel market conditions <cit.> [BG].

Few-shot learning divides data into support sets and query sets. Support sets
provide a small number of examples from a new task (e.g., 5 recent trades in a
new market regime), serving as context for adaptation. Query sets test performance
on that task, evaluating how well the agent has adapted. Inner loop optimization
adapts the model to the specific task using the support set, typically through
one or a few gradient steps. Outer loop optimization updates the meta-parameters
across all tasks, learning initialization that facilitates rapid inner loop adaptation.

MAML (Model-Agnostic Meta-Learning) <cit.> [BG] formulates meta-learning
as a bi-level optimization problem. The inner loop performs task-specific adaptation
by taking gradient steps on each task's loss function. The outer loop optimizes
the initialization parameters by maximizing performance across all tasks after
inner loop adaptation. This produces initialization parameters that are “easy to
fine-tune,” enabling rapid adaptation with minimal data. Memory-based optimization
can augment the optimization process with external memory or replay, improving
sample efficiency and stability in non-stationary settings.

Transfer learning applies meta-learned strategies to completely new tasks
<cit.> [BG].
Inductive transfer reuses learned representations (neural network features, embeddings)
as initialization for new tasks, reducing the data needed to learn. Behavioral transfer
applies high-level strategies (risk management rules, exploration policies) learned
in one domain to another. Domain adaptation fine-tunes meta-learned models on small
amounts of task-specific data, bridging the gap between source and target domains.
Few-shot adaptation enables agents to handle new assets or market conditions with
only a handful of examples, a critical capability for rapidly changing markets.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Self-Reflection]
Self-reflection enables agents to critique their own reasoning, identify mistakes,
and correct errors before acting. This capability improves decision quality by
catching errors that would otherwise propagate into actions.

Representative Approaches. Reflexion <cit.> [BG] adds an explicit
critique–revise loop: after proposing a decision, the agent diagnoses weaknesses in
its own reasoning and regenerates an improved plan. In trading settings, this is most
useful as a guardrail against common failure modes (feature/label leakage, stale data,
ignored costs, regime mismatch), rather than as a source of novel alpha. Self-consistency
and retrospective error analysis complement Reflexion by exposing unstable rationales
and recurring mistake patterns.
In a finance-specific setting, CryptoTrade uses a reflective mechanism to refine
zero-shot cryptocurrency trading decisions by analyzing outcomes of prior trades
<cit.>. Within the section-level primary subset, the
main trading-facing anchor is TradingGroup, which combines role specialization
with self-reflection and data synthesis <cit.>; other
reflection examples should be read as illustrative rather than as settled
evidence for autonomous improvement.

Technical Mechanisms.
[title=Protocol Implication]
 We suggest a five-stage reflective protocol. Effective self-reflection is a protocol, not a free-form “thinking harder” step. (i)
 Critique generation: produce actionable
 checks tied to the trade proposal (data timestamps, assumptions, transaction costs,
 liquidity/slippage, and risk constraints). (ii) Refinement: run a small, bounded
 number of critique–revise iterations with early stopping; log the critique and the
 resulting change for auditability. (iii) Consistency/uncertainty: sample multiple
 reasoning paths; treat disagreement as a deferral/abstain signal to reduce overconfident
 errors, but validate thresholds empirically (consensus is not correctness). (iv)
 Post-trade review: categorize failures (prediction vs execution vs risk) and
 store compact lessons in memory keyed by instrument/regime so they can be retrieved at
 decision time. (v) Pre-trade verification: enforce hard constraints (risk limits,
 compliance rules, and operational feasibility) as deterministic checks.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Self-Reflection]
. (ii) Refinement: run a small, bounded
 number of critique–revise iterations with early stopping; log the critique and the
 resulting change for auditability. (iii) Consistency/uncertainty: sample multiple
 reasoning paths; treat disagreement as a deferral/abstain signal to reduce overconfident
 errors, but validate thresholds empirically (consensus is not correctness). (iv)
 Post-trade review: categorize failures (prediction vs execution vs risk) and
 store compact lessons in memory keyed by instrument/regime so they can be retrieved at
 decision time. (v) Pre-trade verification: enforce hard constraints (risk limits,
 compliance rules, and operational feasibility) as deterministic checks.

Risk of Search Bias: Unbounded reflection acts as a search process. To prevent “testing into success” (retrying until a profitable trade is found just by chance), protocols must enforce a Reflection Budget (max iterations) and refrain from using Out-of-Sample feedback to terminate the loop. Reflective traces should not substitute for tests, monitoring, or out-of-sample evaluation <cit.> [BG].

Self-evolution method comparison. Tags: R=Reproducibility level (R0–R3); general mechanisms are treated as .

 Mechanism Description Key Mechanism Comp Cost Data Eff Tags

Consolidation Summarize, abstract, forget Importance scoring, compression Low (offline) High (reduces memory)

Meta-Learning Learn to learn MAML <cit.>, memory-based opt High (bi-level) High (few-shot)

Self-Reflection Critique and refine Reflexion <cit.>, self-consistency Medium Medium

<Ref> summarizes self-evolution mechanisms at a
conceptual level. Because all rows in the table are tagged , it
should be read as a design-space summary rather than as evidence that trading
agents already improve continuously through these loops. This completes our
survey of the architecture, capabilities, and adaptation of agentic trading
systems.

In summary, this part has explored how agents adapt and evolve in dynamic
markets. Multi-agent coordination makes decomposition and specialization
explicit, while self-evolution mechanisms remain mostly experimental and require
frozen semantics, sealed testing, and immutable logs before any improvement
claim can be compared across studies.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Self-Reflection]
edium

<Ref> summarizes self-evolution mechanisms at a
conceptual level. Because all rows in the table are tagged , it
should be read as a design-space summary rather than as evidence that trading
agents already improve continuously through these loops. This completes our
survey of the architecture, capabilities, and adaptation of agentic trading
systems.

In summary, this part has explored how agents adapt and evolve in dynamic
markets. Multi-agent coordination makes decomposition and specialization
explicit, while self-evolution mechanisms remain mostly experimental and require
frozen semantics, sealed testing, and immutable logs before any improvement
claim can be compared across studies.

[float,floatplacement=tbp]Evidence Summary (Adaptation and Self-Evolution)

 * Status: Most mechanisms (Meta-Learning, Reflection)
 are experimental designs transferred from general AI
 (marked [BG]), lacking rigorous end-to-end trading verification.

 * Primary Evidence: The section-level primary-study count is
 N=4; the much larger citation list in the section includes
 additional background and prototype references that are not part of that total.

 * Protocol Constraints: Claims of “self-improvement”
 are invalid without Sealed Testing and Frozen Semantics.

Across the 4 primary studies mapped in
this section, evidence is split across memory consolidation (2),
meta-learning-like adaptation (1), and self-reflection (1). The field remains
experimental: sealed testing, frozen execution semantics, and immutable log
pointers are the central requirements.

This completes Part III on adaptation mechanisms in agentic trading. Having
surveyed the architecture, capabilities, and adaptation of trading agents, we
now turn to the challenges facing the field and future directions for research.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Challenges and Future Directions]
The preceding sections have presented a structured evidence-based survey of agentic trading
systems, from their architectural foundations to their capabilities and
adaptation mechanisms. This section addresses the challenges facing the field
and identifies promising directions for future research.

Beyond algorithmic limitations, the evidence mapping in <Ref>
highlights a more basic bottleneck: many performance claims remain difficult to
audit or compare because protocol-critical reporting is sparse. Within our
primary empirical subset (n=), time-consistent splitting,
transaction-cost modeling, universe/survivorship handling, and execution
timing/semantics are all reported inconsistently.
Reproducibility artifacts are also limited (R2+: Accordingly, several “technical challenges” below should be read not only as
modeling challenges, but also as reporting and evaluation challenges.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Challenges and Future Directions]
ection addresses the challenges facing the field
and identifies promising directions for future research.

Beyond algorithmic limitations, the evidence mapping in <Ref>
highlights a more basic bottleneck: many performance claims remain difficult to
audit or compare because protocol-critical reporting is sparse. Within our
primary empirical subset (n=), time-consistent splitting,
transaction-cost modeling, universe/survivorship handling, and execution
timing/semantics are all reported inconsistently.
Reproducibility artifacts are also limited (R2+: Accordingly, several “technical challenges” below should be read not only as
modeling challenges, but also as reporting and evaluation challenges.

Minimum Reporting Checklist (Protocol Implication)
 To improve protocol comparability, we suggest the following reporting checklist for future agentic trading research:

 * MR-1 (Data & universe): asset class, universe construction, survivorship treatment, and timestamps/availability for all modalities (especially text/news).

 * MR-2 (Time-consistent splitting): trainvalidationtest dates, walk-forwardrolling details, and embargopurge rules for leakage control; for adaptive searchselection (e.g., alpha discovery), report search budget and keep a sealed test set (validation ≠ test).

 * MR-3 (Action semantics): what the agent outputs (orders vs target weights), decision timestamp, order mapping, price formation (e.g., next-open/close/mid), and portfolio I/O contracts and constraints (leverage, turnover, position limits).

 * MR-4 (Execution & costs): execution timing/price assumption, rebalancing frequency, fees/spread/slippage/impact model, and (when relevant) execution metrics (e.g., implementation shortfall, fill rate) plus sensitivity analysis under alternative frictions.

 * MR-5 (Leakage audit): explicit leakage vectors checked (feature fitting, text hindsight, label leakage), with “NR/Unknown” treated conservatively.

 * MR-6 (Artifacts & logs): codedata availability (or detailed pseudo-code), factor semantics (explicit formulasarchitectures), random seeds, and immutable logs (e.g., order IDs ↔ traces) sufficient to reproduce backtests or simulations (R0–R3); for adaptationevolution claims, report mutable components, update triggerswindows, and rollback with frozen execution+cost semantics; for LLM-based systems, report inference cost per decision and total cost of ownership relative to strategy capacity.

 * MR-7 (Multi-agent evaluation): roles & permissions, message protocol (typesbudgetssync), consensus mechanism, shared-state consistency, plus cross-playgeneralization, communication constraints, crowdingimpact metrics, and rolecommunication ablations for coordination claims.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Challenges and Future Directions]
 factor semantics (explicit formulasarchitectures), random seeds, and immutable logs (e.g., order IDs ↔ traces) sufficient to reproduce backtests or simulations (R0–R3); for adaptationevolution claims, report mutable components, update triggerswindows, and rollback with frozen execution+cost semantics; for LLM-based systems, report inference cost per decision and total cost of ownership relative to strategy capacity.

 * MR-7 (Multi-agent evaluation): roles & permissions, message protocol (typesbudgetssync), consensus mechanism, shared-state consistency, plus cross-playgeneralization, communication constraints, crowdingimpact metrics, and rolecommunication ablations for coordination claims.

Minimum Reporting (MR) Applicability Matrix. We distinguish reporting obligations significantly by study type. M: Mandatory (failure to report downgrades evidence weight); R: Recommended (enhances reproducibility); O: Optional (context-dependent); –: Application dependent or N/A.

 MR Item End-to-End Execution Component

(Full Trading) (Ord/Wt Algo) (Perception/Risk)

MR-1 (Data & Universe) M O M

MR-2 (Time Split & Leakage) M M M

MR-3 (Action Semantics) M M –

MR-4 (Exec & Costs) M M –

MR-5 (Leakage Audit) M R R

MR-6 (Artifacts) R R R

MR-7 (Multi-Agent & Adaptation) O – –

Rationale for MR designations: The M/R/O classifications reflect domain-specific methodological norms for financial trading research. Mandatory (M) items are those essential for reproducibility and validity in the respective study type—for example, execution semantics (MR-3) and cost models (MR-4) are mandatory for any study claiming profitability (End-to-End and Execution categories) but not applicable to pure perception/analysis components. Recommended (R) items enhance reproducibility but are not strictly required for validity—e.g., leakage audits (MR-5) and artifacts (MR-6) are flagged as Recommended because their absence does not invalidate a study but limits external verification. Optional (O) items apply only in specific contexts—e.g., data universe specification (MR-1) is optional for execution algorithms that assume the universe as exogenous. These designations were operationalized through iterative refinement during pilot coding of 10 representative papers, with disagreements resolved through author consensus.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Challenges and Future Directions]
 profitability (End-to-End and Execution categories) but not applicable to pure perception/analysis components. Recommended (R) items enhance reproducibility but are not strictly required for validity—e.g., leakage audits (MR-5) and artifacts (MR-6) are flagged as Recommended because their absence does not invalidate a study but limits external verification. Optional (O) items apply only in specific contexts—e.g., data universe specification (MR-1) is optional for execution algorithms that assume the universe as exogenous. These designations were operationalized through iterative refinement during pilot coding of 10 representative papers, with disagreements resolved through author consensus.

To ensure fair comparison, we recognize that not all MR items apply equally to all research types. <Ref> presents the MR Applicability Matrix. For instance, End-to-End Trading systems must report universe construction (MR-1) and cost models (MR-4) to justify profitability claims, whereas a specialized Execution Algorithm taking parent orders as input may treat universe selection as exogenous (Optional). Similarly, Component studies (e.g., sentiment analysis modules) must strictly adhere to time-consistent splitting (MR-2) but may not need a transaction cost model if they do not execute trades. Researchers and reviewers can use this matrix to avoid "Not Reported" penalties where fields are structurally N/A.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Technical Challenges]
Unless stated otherwise, the subsection narratives below combine challenge
synthesis, methodological guidance, and protocol implications. In the primary
studies, N counts only those studies that explicitly foreground the
issue; N=0 therefore indicates sparse explicit reporting, not that the
underlying risk is absent.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Hallucination in Finance]
LLM hallucination—generating plausible but false information—poses
material risks in financial contexts because trading decisions may be
executed before the underlying claim is verified. Unlike domains where errors
can be revisited later, market actions can realize losses before corrections
arrive. Because the evidence base records only one primary study explicitly
foregrounding this issue, the discussion here should be read as a mix of direct
evidence and cross-section risk synthesis.

Propagation Mechanisms.
In agentic workflows, hallucinated claims propagate through tool calls into
downstream actions. A fabricated earnings report can trigger:

 * Erroneous position entry (immediate loss when corrected)

 * Stop-loss cascade (if other agents detect the "signal")

 * Confidence-based position scaling (larger losses due to false certainty)

Mitigation Limitations.
Binding outputs to verifiable sources (FinMCP, HydraRAG) shifts but does not
eliminate risk: source selection itself can be erroneous. Cross-validation
requires multiple independent sources, which may not exist for time-sensitive
trading signals. Current fact-checking mechanisms operate at second-scale latency,
incompatible with millisecond trading decisions. We cite these systems as
illustrative tooling examples, not as empirically validated mitigations.

Regulatory Implications.
Firms deploying LLM agents may face heightened liability if hallucinated outputs
cause client losses. Documentation of source binding, validation checks, and
human review may be needed for regulatory defense.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Look-ahead Bias]
Look-ahead bias is included here as methodological guidance tied directly to
MR-2 and MR-5. Because the evidence base records N=0 primary studies
explicitly foregrounding it in this section, the paragraph below should be read
as a protocol requirement rather than a section-specific empirical count.

Look-ahead bias occurs when models inadvertently access future information during
training or evaluation, producing unrealistic performance estimates that fail to
generalize to real trading conditions. This is particularly insidious in
time-series settings where data leakage can occur through improper cross-validation
that shuffles temporal data, technical indicators that require future data (such
as moving averages that peek ahead), or textual sources that contain hindsight
about market movements. Detection requires careful examination of model inputs
and training procedures, including causal inference tests that check whether
model performance degrades when strict temporal constraints are enforced. For
example, a model that appears strong under naive random splits can degrade sharply
under proper time-consistent evaluation, revealing substantial look-ahead
contamination <cit.>. Prevention requires strict temporal splitting (train on past,
test on future), walk-forward validation that simulates real-time deployment,
and causal modeling that helps ensure information only flows from past to future.
Even the most sophisticated learning and adaptation procedures fail when
contaminated by future information or evaluation leakage.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Latency vs Accuracy Tradeoff]
System 2 reasoning (reflective, multi-step) produces better decisions but is too
slow for high-frequency trading where decisions must be made in microseconds,
while System 1 reasoning (reactive, fast) lacks the depth for complex decisions
involving multi-hop reasoning or extensive analysis. As an illustrative example,
in latency-sensitive regimes the throughput advantage of faster decision policies
can outweigh modest accuracy gains from slower deliberation, especially when
opportunities are fleeting and execution queues are competitive. Hybrid approaches employ cascaded systems: fast System 1 handles
routine decisions using <Ref> perceptual features, escalating
difficult cases to slower System 2 reasoning that leverages <Ref>
deliberative mechanisms. Model distillation compresses large reasoning models
into smaller, faster models that retain much of the accuracy. Future work should
develop more sophisticated tradeoff mechanisms that dynamically allocate
computational budget based on decision importance, market volatility, and time
pressure, potentially using reinforcement learning to learn optimal policies.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Explainability vs Performance]
Explainability vs performance is likewise a cross-section governance concern more
than a densely evidenced subsection here: the evidence base records
N=0 primary studies explicitly foregrounding it, so the discussion
below is background and author guidance linked to deployment governance.

More complex models (deep neural networks, ensemble methods, large language
models) often achieve better performance but are less interpretable, creating a
fundamental tension between explainability and predictive power. This tension is
not merely academic—depending on jurisdiction and system role, regulatory and
legal frameworks (e.g., the EU's MiFID II) may impose governance, record-keeping,
and explainability expectations for algorithmic trading and decision support
<cit.>. Likewise, GDPR provisions and subsequent guidance can imply
obligations to provide “meaningful information” about automated processing in
certain contexts, though scope and applicability can vary <cit.>.
When an agent's
<Ref> alpha generation module triggers a large position, risk managers
and regulators must understand why: was it a particular news event, a technical
indicator pattern, or a reasoning chain? Neuro-symbolic approaches combine neural
networks with symbolic reasoning, achieving both performance and interpretability
by using neural components for pattern recognition and symbolic components for
transparent reasoning. Attention visualization shows which inputs the model
focused on (e.g., specific news articles or price movements). Counterfactual
explanations identify what would need to change to alter the model's decision
(e.g., “the trade would not have occurred if the FOMC minutes had been less
hawkish”). Regulatory and governance expectations around explainability are
likely to motivate advances in this area, particularly for <Ref> risk
management and compliance applications.

Many academic systems demonstrate explanations on offline datasets or controlled
prototypes; production deployments typically require additional engineering for
auditability (decision logs, data lineage, and controlled model/prompt changes)
to make explanations actionable for governance.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Computational Cost and Economic Feasibility]
The economic viability of LLM-based trading agents depends on the relationship
between inference costs and generated returns. A simple annualized estimate is

 Annual API Cost = D × N × C_req,

where D is trading days per year, N is decisions per day, and C_req is the effective per-request cost implied by model pricing, prompt/completion token budgets, and any tool-specific charges. Because vendor pricing and model offerings change rapidly, we do not report a fixed cross-vendor dollar estimate here. Instead, empirical papers should disclose the model version, pricing snapshot date, token assumptions, tool usage, and the break-even gross P&L required for net profitability after inference and execution costs.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Evaluation Protocols and Deployment Safeguards]
This subsection translates the manuscript-wide minimum reporting framework
(MR-1–MR-7) into concrete deployment safeguards. It is primarily an author
protocol-implication layer grounded in the recurring reporting gaps identified earlier,
rather than a new empirical taxonomy. Evidence-backed guidelines and common
anti-patterns for agentic trading research and deployment include:

 * Guard against temporal leakage: use strictly time-ordered
 splits and walk-forward evaluation, and ensure feature engineering and
 scaling are fit only on past data <cit.>.

 * Avoid unrealistic cost models: include fees, bid–ask spread,
 slippage, and market impact, and report sensitivity to cost assumptions
 <cit.>.

 * Check universe construction: document inclusion/exclusion
 rules and timestamp availability, and audit for survivorship/selection bias
 when building backtest datasets <cit.>.

 * Mitigate backtest overfitting: separate model selection from
 final evaluation, use robust out-of-sample procedures, and be explicit about
 multiple-testing risk <cit.>.

 * Add deployment safeguards: maintain immutable action logs that
 link each action to inputs, evidence, and model versions. Use verifiable
 retrieval, citation checks, and cross-source consistency tests
 <cit.>.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Human-in-the-Loop Oversight]
Although this survey focuses on agentic systems, many realistic deployments retain human oversight at escalation points such as large notional changes, regime breaks, or tool failures. We therefore view human-in-the-loop design as a practical control boundary: stronger autonomy should imply stronger logging, clearer intervention rules, and explicit specification of when human approval is mandatory.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Negative Results and Failed Designs]
The literature is likely affected by survivorship bias at the survey level as well as at the backtest level. Few papers report failed prompts, abandoned reward schemes, degraded live performance, or architectures that increased turnover without improving net returns. We therefore interpret the absence of negative results as a reporting limitation rather than as evidence that the design space is uniformly promising.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Neuro-Symbolic Integration]
Current LLM-based agents rely entirely on neural computation, which is powerful
but opaque and unreliable for precise reasoning requiring exact calculations or
logical guarantees. As discussed in <Ref>, pure neural approaches
struggle with tasks like portfolio optimization under constraints or exact
arithmetic. Neuro-symbolic integration combines neural networks (for pattern
recognition and learning from data) with symbolic reasoning (for logic,
constraint satisfaction, and exact computation). Hybrid architectures can employ
neural networks to extract structured information from text (prices, dates,
entities) and symbolic reasoning to perform financial calculations, enforce
budget constraints, and help ensure logical consistency. Specific approaches
include: (1) Neural theorem provers that use neural networks to guide
proof search for financial constraints; (2) Differentiable logic that
integrates logical constraints into neural network loss functions; (3)
Program synthesis where LLMs generate code that is then formally
verified; and (4) Neuro-symbolic ILP (Inductive Logic Programming) that
learns logical rules from neural representations. The research objective is to
combine neural flexibility with symbolic precision while keeping the resulting
systems auditable enough for financial use.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Longer-Term Directions: Coordination, Governance, and Infrastructure]
Several longer-term directions remain relevant but more speculative
than the protocol and auditability issues above. First, larger multi-agent
market simulations could eventually function as controlled “wind tunnels” for
studying crowding, flash episodes, and systemic-risk propagation, but the
current evidence base is still dominated by small role-based teams rather than
large agent societies. Second, regulatory and governance questions are likely
to grow as agents become more autonomous: the immediate research need is not
legal personhood for agents, but auditable records, intervention rules, and
sandboxed evaluation that clarify who approved, monitored, or overrode each
action. Third, low-latency infrastructure and model compression matter for
deployment, yet hardware acceleration claims should remain secondary unless
papers report end-to-end decision latency, execution timing, and cost/benefit
analysis. These directions are therefore best treated as expert-system design
constraints for future work, not as settled empirical findings of the present
ledger.

Because several conclusions in this survey depend on a relatively thin but auditable empirical base, <Ref> makes the claim-to-evidence mapping explicit in the main text rather than leaving it entirely to the supplement.

Claim-to-evidence map for the manuscript's strongest recurring conclusions. `Primary' lists the papers supporting protocol-aware empirical claims.

 Claim Primary evidence Boundary / caveat

Protocol reporting is sparse FinAgent <cit.>, TradingAgents <cit.>, FinCon <cit.>, FinRL-DeepSeek <cit.>, Agent Market Arena <cit.>, FinMem <cit.> Based on the primary empirical subset only; do not generalize percentages to all included/background work.

Action/execution semantics are under-specified FinAgent <cit.>, TradingAgents <cit.>, AI-Trader <cit.>, FinRL-DeepSeek <cit.> Stronger evidence for missing reporting than for any single execution design winning empirically.

Memory and adaptation remain heterogeneous FinAgent <cit.>, FinMem <cit.>, TradingGroup <cit.>, Alpha2 <cit.> Evidence is still thin; reported as emerging tendencies rather than settled best practice.

Multi-agent systems improve decomposition, not guaranteed performance TradingAgents <cit.>, TradingGroup <cit.>, FinCon <cit.>, REIT multi-agent pipeline <cit.> Coordination benefits are plausible but attribution remains weak without role/communication ablations.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Longer-Term Directions: Coordination, Governance, and Infrastructure]
nd work.

Action/execution semantics are under-specified FinAgent <cit.>, TradingAgents <cit.>, AI-Trader <cit.>, FinRL-DeepSeek <cit.> Stronger evidence for missing reporting than for any single execution design winning empirically.

Memory and adaptation remain heterogeneous FinAgent <cit.>, FinMem <cit.>, TradingGroup <cit.>, Alpha2 <cit.> Evidence is still thin; reported as emerging tendencies rather than settled best practice.

Multi-agent systems improve decomposition, not guaranteed performance TradingAgents <cit.>, TradingGroup <cit.>, FinCon <cit.>, REIT multi-agent pipeline <cit.> Coordination benefits are plausible but attribution remains weak without role/communication ablations.

Cost and reproducibility gaps limit comparability Primary subset tables in Section 2 plus R0–R3 audit summaries This is the manuscript's strongest cross-paper conclusion because it depends on reporting structure, not headline Sharpe ratios.

The current evidence base supports a narrower conclusion: agentic trading is a
rapidly expanding design space, but comparability still depends more on
reporting discipline than on headline performance claims. The final section
concludes the survey.

Across the primary studies, protocol reporting remains the recurring limiter,
while sealed testing, immutable logs, and latency-aware evaluation emerge as the
common remedies.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Summary]
This survey reframes LLM-based trading agents as expert-system
decision pipelines and audits whether the current literature supports
protocol-comparable claims. The central conclusion is evidence-level rather
than taxonomy-level: architectural experimentation is growing quickly, but the
primary empirical literature remains weakly comparable because temporal splits,
cost assumptions, universe construction, execution semantics, and reproducible
artifacts are often missing.

Accordingly, the paper's main contribution is the evidence ledger and the
protocol/reproducibility audit. We use the A-C-A lens to organize where
evidence gaps arise across perception, memory, reasoning, action/execution,
capability, and adaptation modules. It remains a working analytical lens, not a
validated classification standard.

Evidence-driven takeaway. In the current evidence ledger, we retain
 included studies from 
candidate records in the auditable snapshot screened through the
2026-03-09 ledger cutoff. Of these,
 satisfy the primary empirical criteria and
 remain in the background tier. Within the current
primary subset, protocol-critical reporting remains limited:
/
(/ (report explicit cost models,
/ (report universe/survivorship handling, and
/
(Reproducibility artifacts are also limited, with
/ studies at R0,
/ at R2, and
/ at R3. These gaps motivate the
conservative stance throughout this survey: where protocol-critical details are
NR/, we avoid strong cross-paper performance comparisons and
treat claims as preliminary unless supported by stronger evidence.

We emphasize that this synthesis is necessarily preliminary. Within the current
primary subset, reach R3, so the architectural patterns we identify should be read as
emerging tendencies within the current ledger rather than established
best practices.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Broader Impact]
Agentic trading may have meaningful implications for financial markets,
industry practitioners, and academic researchers, but the current evidence base
supports only cautious inferences. For markets, more autonomous decision
pipelines could alter microstructure, liquidity provision, and information
processing, while also raising questions about correlated agent behaviors, flash
episodes, and new manipulation surfaces (<Ref>). For
practitioners, modular agentic systems may lower some development barriers, but
their deployment value still depends on execution realism, monitoring, and
artifact quality. For researchers, agentic trading remains a useful testbed for
studying AI in noisy real-world environments, especially around hallucination,
look-ahead bias, and the latency-accuracy tradeoff, yet the present sample does
not justify broad claims about market-wide effects.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Limitations of the Lens and Evidence Base]
A-C-A should be read as a working analytical lens for this review. It
helps separate agent boundary, architecture-capability alignment, and adaptation
mechanism, but it has not been independently validated as a field-wide
classification standard. Three limitations follow. First, emerging hybrid
architectures may blur the distinction between architecture, capability, and
adaptation. Second, the MR-1–MR-7 reporting dimensions in <Ref>
reflect author judgment informed by quantitative finance and agent-system
literature; broader community elicitation would strengthen their prioritization.
Third, with only many architectural patterns remain provisional and may merge, disappear, or
require re-adjudication as stronger artifacts become available.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Call to Action]
We conclude with a targeted call to action for researchers, practitioners, and
regulators. To researchers: more studies should report protocol-complete
evaluation setups, clearly distinguish background discussion from primary
evidence, and release enough artifacts to move beyond the current R0-heavy
distribution. To practitioners: deployment claims should be accompanied by
clearer documentation of execution assumptions, data timing, and monitoring
procedures. To regulators: the current sample mainly indicates where reporting
gaps persist; it may therefore be more useful to encourage auditable testing and
controlled evaluation settings than to infer settled policy conclusions from an
early-stage literature.

A parallel engineering trend outside the current trading-specific evidence base
is the shift from one-off tool calls toward reusable workflow and skill layers
in general LLM-agent systems. Recent work on agentic skills frames such
capabilities as callable procedural modules with applicability conditions,
execution policies, termination criteria, and reusable interfaces
<cit.>. For agentic trading, this suggests that future
systems may package perception, retrieval, execution, risk checks, and reporting
routines as governed skills or workflows. Because finance-specific closed-loop
evidence for such designs remains limited, however, skill-based trading agents
should be treated as an infrastructure direction rather than as validated
trading evidence.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Artifact Availability Statement]
To support auditability of our review process, we submit supplementary materials
alongside the manuscript: S1 includes the search log, study
selection flow, and double-screening audit sample; S2 provides the
evidence mapping master table (paper × coded fields) and coverage
summaries; and S3 documents the coding schema and reproducibility tags
with examples, including the targeted extraction-level reliability audit over
fixed-seed primary studies. Boundary decisions and final exclusions are summarized in
<Ref>, and representative A-C-A reclassification notes are
provided in <Ref>. These materials are submitted as
part of the review package for inspection during peer review. An anonymized
repository containing the same supplementary materials and the LaTeX source will
be released upon acceptance, subject to journal policy and anonymization
requirements.

Agentic trading is an active and still unsettled research area. More comparable
protocols, clearer evidence boundaries, and stronger artifact availability may
be necessary before stronger conclusions about its long-run role in financial
markets are warranted.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: CRediT authorship contribution statement]
Yihan Xia: Methodology, Investigation, Data curation, Formal analysis,
Visualization, Writing – original draft, Writing – review & editing.
Panpan You: Investigation, Data curation, Formal analysis, Visualization,
Writing – original draft, Writing – review & editing.
Taotao Wang: Conceptualization, Methodology, Supervision, Project
administration, Resources, Validation, Writing – review & editing.
Fang Liu: Conceptualization, Validation, Writing – review & editing.
Han Qi: Conceptualization, Validation, Resources, Writing – review & editing.
Xiaoxiao Wu: Conceptualization, Validation, Writing – review & editing.
Shengli Zhang: Conceptualization, Validation, Writing – review & editing.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Declaration of competing interest]
The authors declare that they have no known competing financial interests or
personal relationships that could have appeared to influence the work reported
in this paper.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Acknowledgements]
The authors thank colleagues and reviewers whose feedback helped improve the
scope definition, evidence coding, and presentation of this survey.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Data availability]
The evidence ledger, coding summaries, and supplementary audit
materials are submitted with the manuscript as Supplementary Materials S1–S3.
S1 provides the canonical registry and search/screening logs, S2 provides the
evidence-mapping and protocol tables, and S3 provides the coding schema,
reproducibility annotations, and targeted extraction-level reliability audit. An
anonymized repository containing the same materials and the LaTeX source will be
released upon acceptance, subject to journal policy and anonymization
requirements.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Systematic Search Summary]
This appendix summarizes the information sources and query patterns used to
identify candidate records for this structured survey. The goal is transparency
and reproducibility of the search boundary, rather than exhaustive coverage.

 Information sources and search summary (submitted as Supplementary Material S1).

 Source Notes 

 ACM Digital Library Keyword search over agentic trading, LLM agents, and financial decision-making. 

 IEEE Xplore Keyword search focused on trading systems, execution, and risk control. 

 arXiv Preprints in cs.AI/cs.LG/q-fin with agent/trading keywords. 

 SSRN Working papers in quantitative finance and computational finance. 

 Google Scholar Broad catch-all for cross-venue discovery and citation chaining. 

 Example query patterns used in the search.

 Target Query pattern (example) 

 Agentic trading ( OR OR ) AND ( OR OR OR ) 

 LLM finance agents ( OR ) AND ( OR ) AND ( OR OR ) 

 Evaluation/validity ( OR ) AND ( OR OR OR OR ) 

Coverage note. This survey discusses literature through the formal
registry cutoff of 2026-03-09. Evidence annotations, screening counts,
and protocol-coded denominators are synchronized to the auditable registry
snapshot last queried on 2026-03-09.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Corpus Snapshot of the Evidence Ledger]
This appendix consolidates corpus-level descriptive findings that follow from
the review protocol but are not themselves part of the protocol definition.
Unless stated otherwise, denominator-based summaries here use the primary
empirical subset (n=), while the full included ledger contains
 studies partitioned into primary empirical
studies and background studies.

The primary subset is concentrated in very recent work. Within the current
ledger, / primary studies were
published between 2024 and 2026. Registry metadata further indicate that
/ primary studies are
currently coded as non-peer-reviewed, /
as peer-reviewed, and / as
. We therefore interpret this corpus as an
early-stage literature whose claims often remain provisional pending stronger
artifact release and independent replication.

Protocol-complete reporting remains sparse even within the fixed primary subset.
Only / studies report an
extractable split protocol, /
specifies a transaction-cost model, /
documents universe/survivorship handling, /
reports execution timing or semantics, and
/ exposes artifacts beyond
narrative description.
Evaluation types are likewise unevenly distributed, with backtest, simulation,
live, benchmark, and narrative-only or unclear evaluation reports
appearing in different proportions across the corpus.

Reproducibility levels within the primary empirical subset (n=).

 Level Definition Criteria Count R0 No runnable artifacts No publicly accessible code repository, or repository is broken/404, or it lacks essential files and cannot run

R1 Code available (not runnable) Public repository exists and is accessible, but key components are missing (dependencies, data access, eval scripts)

R2 Runnable with gaps Complete code is available and data is accessible or clearly documented, and evaluation scripts are provided, but pinned environment, complete documentation, or an end-to-end pipeline may still be missing

R3 Full reproduction package Complete code with pinned environment, data snapshots or clear access instructions, complete documentation, and an end-to-end evaluation pipeline

3lR2 or above (runnable with gaps or better)

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Corpus Snapshot of the Evidence Ledger]
accessible code repository, or repository is broken/404, or it lacks essential files and cannot run

R1 Code available (not runnable) Public repository exists and is accessible, but key components are missing (dependencies, data access, eval scripts)

R2 Runnable with gaps Complete code is available and data is accessible or clearly documented, and evaluation scripts are provided, but pinned environment, complete documentation, or an end-to-end pipeline may still be missing

R3 Full reproduction package Complete code with pinned environment, data snapshots or clear access instructions, complete documentation, and an end-to-end evaluation pipeline

3lR2 or above (runnable with gaps or better)

Reading note. In the figures below, denotes
information that is not reported clearly enough in the source for reliable
extraction under our conservative coding policy. These plots should therefore be
read as corpus-level reporting distributions within the current ledger, not as
proof that every unreported mechanism is absent in the underlying systems.

0.47
 !

3.200
 [->] (0,0) – (0,+0.3);
 [->] (0,0) – (4.900,0);
 [black!60] (0.400,0) rectangle (1.050,3.200);
 [font=, above] at (0.725,3.200) 15;
 [font=, rotate=35, anchor=west] at (0.400,-0.05) R0;
 [black!60] (1.300,0) rectangle (1.950,0.213);
 [font=, above] at (1.625,0.213) 1;
 [font=, rotate=35, anchor=west] at (1.300,-0.05) R1;
 [black!60] (2.200,0) rectangle (2.850,0.640);
 [font=, above] at (2.525,0.640) 3;
 [font=, rotate=35, anchor=west] at (2.200,-0.05) R2;
 [black!60] (3.100,0) rectangle (3.750,0.000);
 [font=, above] at (3.425,0.000) 0;
 [font=, rotate=35, anchor=west] at (3.100,-0.05) R3;
 [black!35] (4.000,0) rectangle (4.650,0.000);
 [font=, above] at (4.325,0.000) 0;
 [font=, rotate=35, anchor=west] at (4.000,-0.05) Unknown;
 [font=] at (2.450,+0.55) Reproducibility Levels (primary subset, n=);

Reproducibility level.

 0.47
 !

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Corpus Snapshot of the Evidence Ledger]
e=35, anchor=west] at (0.400,-0.05) R0;
 [black!60] (1.300,0) rectangle (1.950,0.213);
 [font=, above] at (1.625,0.213) 1;
 [font=, rotate=35, anchor=west] at (1.300,-0.05) R1;
 [black!60] (2.200,0) rectangle (2.850,0.640);
 [font=, above] at (2.525,0.640) 3;
 [font=, rotate=35, anchor=west] at (2.200,-0.05) R2;
 [black!60] (3.100,0) rectangle (3.750,0.000);
 [font=, above] at (3.425,0.000) 0;
 [font=, rotate=35, anchor=west] at (3.100,-0.05) R3;
 [black!35] (4.000,0) rectangle (4.650,0.000);
 [font=, above] at (4.325,0.000) 0;
 [font=, rotate=35, anchor=west] at (4.000,-0.05) Unknown;
 [font=] at (2.450,+0.55) Reproducibility Levels (primary subset, n=);

Reproducibility level.

 0.47
 !

3.200
 [->] (0,0) – (0,+0.3);
 [->] (0,0) – (5.800,0);
 [black!60] (0.400,0) rectangle (1.050,3.200);
 [font=, above] at (0.725,3.200) 11;
 [font=, rotate=35, anchor=west] at (0.400,-0.05) backtest;
 [black!60] (1.300,0) rectangle (1.950,0.000);
 [font=, above] at (1.625,0.000) 0;
 [font=, rotate=35, anchor=west] at (1.300,-0.05) narrative-only;
 [black!60] (2.200,0) rectangle (2.850,0.873);
 [font=, above] at (2.525,0.873) 3;
 [font=, rotate=35, anchor=west] at (2.200,-0.05) live;
 [black!60] (3.100,0) rectangle (3.750,0.582);
 [font=, above] at (3.425,0.582) 2;
 [font=, rotate=35, anchor=west] at (3.100,-0.05) simulation;
 [black!60] (4.000,0) rectangle (4.650,0.873);
 [font=, above] at (4.325,0.873) 3;
 [font=, rotate=35, anchor=west] at (4.000,-0.05) benchmark;
 [black!35] (4.900,0) rectangle (5.550,0.000);
 [font=, above] at (5.225,0.000) 0;
 [font=, rotate=35, anchor=west] at (4.900,-0.05) Unknown;
 [font=] at (2.900,+0.55) Evaluation Type (primary subset, n=);

Evaluation type.

0.47
 !

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Corpus Snapshot of the Evidence Ledger]
=west] at (1.300,-0.05) narrative-only;
 [black!60] (2.200,0) rectangle (2.850,0.873);
 [font=, above] at (2.525,0.873) 3;
 [font=, rotate=35, anchor=west] at (2.200,-0.05) live;
 [black!60] (3.100,0) rectangle (3.750,0.582);
 [font=, above] at (3.425,0.582) 2;
 [font=, rotate=35, anchor=west] at (3.100,-0.05) simulation;
 [black!60] (4.000,0) rectangle (4.650,0.873);
 [font=, above] at (4.325,0.873) 3;
 [font=, rotate=35, anchor=west] at (4.000,-0.05) benchmark;
 [black!35] (4.900,0) rectangle (5.550,0.000);
 [font=, above] at (5.225,0.000) 0;
 [font=, rotate=35, anchor=west] at (4.900,-0.05) Unknown;
 [font=] at (2.900,+0.55) Evaluation Type (primary subset, n=);

Evaluation type.

0.47
 !

3.200
 [->] (0,0) – (0,+0.3);
 [->] (0,0) – (4.900,0);
 [black!60] (0.400,0) rectangle (1.050,0.582);
 [font=, above] at (0.725,0.582) 2;
 [font=, rotate=35, anchor=west] at (0.400,-0.05) Split;
 [black!60] (1.300,0) rectangle (1.950,3.200);
 [font=, above] at (1.625,3.200) 11;
 [font=, rotate=35, anchor=west] at (1.300,-0.05) Execution;
 [black!60] (2.200,0) rectangle (2.850,0.291);
 [font=, above] at (2.525,0.291) 1;
 [font=, rotate=35, anchor=west] at (2.200,-0.05) Costs;
 [black!60] (3.100,0) rectangle (3.750,0.291);
 [font=, above] at (3.425,0.291) 1;
 [font=, rotate=35, anchor=west] at (3.100,-0.05) Universe;
 [black!60] (4.000,0) rectangle (4.650,1.164);
 [font=, above] at (4.325,1.164) 4;
 [font=, rotate=35, anchor=west] at (4.000,-0.05) Artifacts;
 [font=] at (2.450,+0.55) Protocol Field Coverage (primary subset, n=);
 [anchor=north west, align=left, font=, text width=6cm] at (0,-5) * Universe/Cost reporting is calculated over n=. 
 Low coverage reflects both reporting gaps and 
 varying applicability (e.g., Execution tasks 
 may not require Universe selection).;

Protocol-field coverage.

 0.47
 !

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Corpus Snapshot of the Evidence Ledger]
nt=, rotate=35, anchor=west] at (2.200,-0.05) Costs;
 [black!60] (3.100,0) rectangle (3.750,0.291);
 [font=, above] at (3.425,0.291) 1;
 [font=, rotate=35, anchor=west] at (3.100,-0.05) Universe;
 [black!60] (4.000,0) rectangle (4.650,1.164);
 [font=, above] at (4.325,1.164) 4;
 [font=, rotate=35, anchor=west] at (4.000,-0.05) Artifacts;
 [font=] at (2.450,+0.55) Protocol Field Coverage (primary subset, n=);
 [anchor=north west, align=left, font=, text width=6cm] at (0,-5) * Universe/Cost reporting is calculated over n=. 
 Low coverage reflects both reporting gaps and 
 varying applicability (e.g., Execution tasks 
 may not require Universe selection).;

Protocol-field coverage.

 0.47
 !

3.200
 [->] (0,0) – (0,+0.3);
 [->] (0,0) – (4.000,0);
 [black!60] (0.400,0) rectangle (1.050,0.000);
 [font=, above] at (0.725,0.000) 0;
 [font=, rotate=35, anchor=west] at (0.400,-0.05) walk-forward;
 [black!60] (1.300,0) rectangle (1.950,0.000);
 [font=, above] at (1.625,0.000) 0;
 [font=, rotate=35, anchor=west] at (1.300,-0.05) rolling;
 [black!60] (2.200,0) rectangle (2.850,0.376);
 [font=, above] at (2.525,0.376) 2;
 [font=, rotate=35, anchor=west] at (2.200,-0.05) other;
 [black!35] (3.100,0) rectangle (3.750,3.200);
 [font=, above] at (3.425,3.200) 17;
 [font=, rotate=35, anchor=west] at (3.100,-0.05) Unknown;
 [font=] at (2.000,+0.55) Split Protocol (primary subset, n=);

Split-protocol reporting.

 Corpus-level reporting distributions within the primary empirical subset (n=).

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Representative A-C-A Reclassification Notes]
This appendix provides reclassification notes for 20 representative
works to illustrate how the Architecture-Capability-Adaptation (A-C-A)
exploratory analytical lens can reorganize parts of the literature. The notes
are intended to clarify how the lens is applied and should not be read as an
external validation exercise. For each work, we document: (i)
classification under prior frameworks (where available), (ii) A-C-A
reclassification with coding rationale, and (iii) the specific analytical
insight surfaced by the lens.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reclassification Procedure]
Paper Selection. We selected 20 works representing diverse architectural approaches, capabilities, and adaptation mechanisms. Selection criteria: (a) coverage of all three A-C-A dimensions, (b) citation count or recency (indicating influence), (c) availability of technical details sufficient for classification.

Coding Procedure. For each paper, one author prepared an initial A-C-A
classification and coding rationale, and the authors then reconciled edge cases
through discussion. These notes are presented as an illustrative, author-curated
coding dataset intended to clarify how the lens is applied, not as formal
external validation.

Prior Framework Identification. For each work, we identified its classification in existing surveys where available: Wang et al. 2024 (LLM-Agent Survey), Ding et al. 2024 (LLM-Finance Survey), or task-centric benchmarks (FinBen, InvestorBench). Where a work was not explicitly labeled in one of those sources, the shorthand in the Prior column should be read as our closest reconstruction of how that work would map to the earlier scheme.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reclassification Dataset]
<Ref> presents the complete
reclassification notes. The table is organized into illustrative architectural
families rather than as an evidence-ranked progression or a validated hierarchy.

Representative A-C-A reclassification notes for 20 works. These author-curated notes illustrate the exploratory analytical lens and are not an external validation study.

 max width=

 Work Prior A-C-A Reclassification P M R Adapt Key Insight from A-C-A

FinBERT<cit.> W: “NLP Model”, D: “Sentiment” Arch: Text Perception only; Cap: BG (no Action); Adapt: BG – – BG [l]Excluded as BG: demonstrates Action 
Output criterion excludes pure prediction

FinGPT<cit.> W: “LLM Tool”, D: “Generation” Arch: Text Perception + Static Memory; Cap: BG (no closed-loop); Adapt: BG – BG [l]Excluded as BG: Generation without 
execution integration

FinLlama<cit.> D: “Sentiment” Arch: Text Perception; Cap: BG; Adapt: BG – – BG [l]Same architecture as FinBERT but 
instruction-tuned; capability depends
on integration, not just model

AlphaAgent<cit.> D: “Multi-agent” Arch: Reflective/Strategic hybrid + Episodic Memory; Cap: α; Adapt: Self-reflection SE [l]Multi-agent debate = validation mechanism 
for Alpha, not coordination capability

FinAgent<cit.> W: “Multi-modal”, D: “Agent” Arch: Multi-modal P + Episodic M + Reflective R + Microstructure A; Cap: α (cross-modal); Adapt: ICL ICL [l]Core: cross-modal perception-to-action 
pipeline, not “multi-modality”

Alpha^2<cit.> B: “Alpha Mining” Arch: Working Memory + Strategic Reasoning (MCTS); Cap: α (evolutionary); Adapt: RL – RL [l]MCTS is Strategic Reasoning; evolutionary 
= search-based adaptation

RAG-Fintech<cit.> D: “Retrieval” Arch: Text P + Semantic M (KB) + Reflective R; Cap: α (retrieval-based); Adapt: ICL ICL [l]Retrieval = Memory architecture, not just 
augmentation technique

RAPTOR<cit.> D: “Portfolio” Arch: Working M + Strategic R + Execution A; Cap: P (hierarchical); Adapt: ICL – ICL [l]Portfolio = Strategic + Execution 
integration, not separate capability

[l]AgentGuard 
Jizhou Chen<cit.> W: “Safety” Arch: Reactive R + Action A with gating; Cap: R (real-time); Adapt: Rule-based – – – [l]Risk as gating mechanism in Action
architecture, not post-hoc

FinRS<cit.> D: “Risk” Arch: Text P + Episodic M + Reflective R; Cap: R (sentiment-driven); Adapt: SFT SFT [l]Risk capability derives from 
Perception-Memory-Reasoning chain

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Reclassification Dataset]
Semantic M (KB) + Reflective R; Cap: α (retrieval-based); Adapt: ICL ICL [l]Retrieval = Memory architecture, not just 
augmentation technique

RAPTOR<cit.> D: “Portfolio” Arch: Working M + Strategic R + Execution A; Cap: P (hierarchical); Adapt: ICL – ICL [l]Portfolio = Strategic + Execution 
integration, not separate capability

[l]AgentGuard 
Jizhou Chen<cit.> W: “Safety” Arch: Reactive R + Action A with gating; Cap: R (real-time); Adapt: Rule-based – – – [l]Risk as gating mechanism in Action
architecture, not post-hoc

FinRS<cit.> D: “Risk” Arch: Text P + Episodic M + Reflective R; Cap: R (sentiment-driven); Adapt: SFT SFT [l]Risk capability derives from 
Perception-Memory-Reasoning chain

TradingAgents<cit.> W: “Multi-agent” Arch: Hierarchical role-based Coordination; Cap: α+P+R distributed; Adapt: Hierarchical feedback ICL+SE [l]Seven agents = capability hierarchy, 
not flat roles

TradingGroup<cit.> D: “Multi-agent” Arch: Role-based + Shared Memory; Cap: α; Adapt: Self-reflection SE [l]Self-reflection coordinates roles, 
not external mechanism

FINCON<cit.> D: “Consensus” Arch: Role-based + Communication Protocol; Cap: P; Adapt: Debate-based – ICL [l]Consensus = Decision Making mechanism, 
not independent capability

FinMem<cit.> W: “Memory” Arch: Hierarchical Memory (3-tier) + Strategic R; Cap: P; Adapt: Memory consolidation – SE [l]Memory hierarchy enables temporal 
abstraction for Portfolio

MetaGPT<cit.> W: “Multi-agent” Arch: Hierarchical (Manager + Engineers); Cap: α (code generation); Adapt: SFT SFT [l]Software engineering analogy applies 
to factor generation

FinRL-DeepSeek<cit.> B: “RL Trading” Arch: Working M + Reactive/Strategic hybrid R + Execution A; Cap: α+P; Adapt: RL – RL [l]RL spans multiple capabilities with 
shared architecture

Reflexion<cit.> W: “Reflection” Arch: Working M + Reflective R; Cap: BG (general); Adapt: Self-reflection – SE [l]Self-reflection as adaptation mechanism 
applicable to trading

Hashimoto<cit.> B: “Simulation” Arch: Market Ecology (no central coordination); Cap: α+P+R emergent; Adapt: Evolutionary RL+SE [l]Ecology = emergent capabilities from 
interaction, not design

FinEvo<cit.> D: “Evolution” Arch: Market Ecology + Hierarchical; Cap: α; Adapt: Evolutionary + SE SE [l]Combines ecology (interaction) with 
hierarchy (structure)

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Illustrative Patterns from Reclassification]
Pattern 1: Architecture-Capability Non-Alignment.
The same Reactive Architecture (FinAgent, AgentGuard) supports different capabilities (α vs R) depending on perceptual input and memory integration. This cross-cutting pattern is obscured by capability-centric categorizations.

Pattern 2: Adaptation Level Distinction.
Works classified uniformly as “learning-based” in prior frameworks distribute across three adaptation levels: ICL (Chain-of-Alpha, RAG-Fintech), SFT (FinRS, MetaGPT), and SE (AlphaAgent, FinEvo). Each has distinct protocol requirements (Sec. <ref>).

Pattern 3: Multi-Agent Architectural Hierarchy.
Prior frameworks often use broad “multi-agent” labels. The A-C-A lens
distinguishes role-based, hierarchical, and market-ecology coordination patterns,
making the coordination mechanism visible rather than treating agent count as
the primary distinction.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Coding Status]
In this revision, the coding notes are summarized qualitatively through author
reconciliation examples rather than through placeholder agreement/kappa
numerics. This is sufficient to show A-C-A's usefulness as an organizing lens
for this manuscript, but not sufficient to establish it as a fully validated or
uniquely correct taxonomy for the field.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Limitations of the Reclassification Notes]
* Selection Bias: 20 works selected from a broader review corpus spanning included studies, background references, and a small number of boundary cases used to stress-test the A-C-A lens; they were not randomly sampled.

 * Temporal Coverage: 85 
 * Prior Framework Availability: Not all works classified in existing surveys. Where unavailable, we inferred likely categorization based on paper content and survey scope.

Despite these limitations, the reclassification notes suggest that the
A-C-A lens provides useful analytical granularity for distinguishing design
choices and surfacing architectural patterns that may be obscured by broader
system- or task-level labels.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Excluded Studies and Rationale]
To ensure transparency and enable auditability of our evidence mapping
process, this appendix distinguishes two decisions that are easy to conflate.
First, final exclusions are candidate-registry records outside the
finance/trading/portfolio/risk-management scope of this survey. Second,
background-tier boundary decisions are finance-relevant records that
remain in the included evidence ledger but do not enter the primary empirical
subset because they lack Action Output or Closed-Loop Evaluation. Using
PRISMA-ScR as a reporting aid for scoping-style transparency rather than as a
claim of a full systematic-review workflow, we document both decision types to
facilitate audit and assessment of potential selection bias.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Exclusion Categories and Boundary Decisions]
Candidate records were finally excluded only when they were outside the
domain boundary of this survey. Finance-relevant records that were prediction
models, benchmarks, tools, or conceptual background papers were retained as
background/context where useful, but were excluded from the primary empirical
denominator. The operational criteria are:

 E1 No Action Output: Pure prediction or analysis systems that do not generate tradable actions. These are background-tier records when finance-relevant, not final exclusions.

 E2 No Closed-Loop Evaluation: Systems that output signals or ideas but lack backtest, simulation, or live-trading evaluation. These are background-tier records when finance-relevant, not final exclusions.

 E3 Non-Financial Domain: Systems applied to non-financial markets or generic agent settings without financial trading, portfolio, execution, or risk-management instantiation. These form the final excluded set in the current canonical registry.

 E4 No LLM Component: Traditional quantitative trading systems without a language-model component. These may be cited only as background context when needed for finance methodology.

 E5 Duplicate: Multiple versions of the same work; the most complete version is retained.

 E6 Inaccessible: Full text not available after reasonable effort.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Representative Final Exclusions and Background Boundary Cases]
<Ref> separates final exclusions from background
boundary cases. The aggregate exclusion count in the current canonical registry
is , all of which are outside the finance/trading scope; the
background cases remain in the -record included ledger but do
not enter the -record primary empirical subset.

 Representative final exclusions and background boundary cases.

 Study (Representative) Category Decision rationale 

 3lFinal excluded records in the current canonical registry 

 Socio-Agentic LLMs for Socio-Technical Systems E3 Generic socio-technical agent paper outside finance/trading/portfolio/risk management. 

 Learning Game-Playing Agents with Generative Code Optimization E3 General game-playing agent study without financial-market instantiation. 

 NeSyCoCo E3 Neuro-symbolic compositional generalization study outside the trading domain. 

 Agentic AI for Commercial Insurance Underwriting E3 Insurance underwriting rather than trading, portfolio construction, execution, or market-risk management. 

 3lIncluded background boundary cases 

 FinBERT (Araci 2019) E1/BG Finance-relevant sentiment model retained as background; no tradable action loop, so it is excluded from the primary empirical subset. 

 FinGPT (Wang 2023a) E1/BG Finance language-model/tooling work retained as background; no explicit closed-loop trading execution integration. 

 InvestorBench E2/BG Finance benchmark retained as background; not counted as a primary empirical trading-agent system under Action Output plus Closed-Loop Evaluation.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Inclusion/Exclusion Decision Flow]
max width=,max height=0.72
 [
 node distance=1.15cm,
 font=,
 box/.style=rectangle, rounded corners, draw, minimum width=4.4cm, minimum height=0.8cm, align=center,
 decision/.style=diamond, draw, aspect=2, align=center,
 arrow/.style=->, >=stealth
 ]

 [box, fill=gray!10] (start) Candidate registry
(n=);
 [box, fill=gray!15, below=of start] (dedup) After deduplication
(n=);
 [decision, fill=tradingagent_main!20, below=of dedup] (domain) Finance/trading
domain?;
 [box, fill=tradingagent_red!10, right=2.3cm of domain] (excluded) Final excluded
outside scope
(n=);
 [box, fill=tradingagent_blue!12, below=of domain] (included) Included evidence
mapping ledger
(n=);
 [decision, fill=tradingagent_main!20, below=of included] (action) Action Output
and Closed-Loop
Evaluation?;
 [box, fill=tradingagent_blue!25, below left=1.15cm and 1.4cm of action] (primary) Primary empirical
subset
(n=);
 [box, fill=tradingagent_blue!8, below right=1.15cm and 1.4cm of action] (background) Background/context
tier
(n=);

 [arrow] (start) – (dedup);
 [arrow] (dedup) – (domain);
 [arrow] (domain) – node[above] No (excluded);
 [arrow] (domain) – node[left] Yes (included);
 [arrow] (included) – (action);
 [arrow] (action) – node[left] Yes (primary);
 [arrow] (action) – node[right] No (background);

 Inclusion, exclusion, and evidence-tier decision flow. Final exclusions are outside the survey domain; finance-relevant records that lack Action Output or Closed-Loop Evaluation remain in the included background tier.

<Ref> illustrates the screening logic encoded in the canonical ledger and summarized in the main text. It should be read as an auditable reconstruction of the inclusion/exclusion workflow rather than as a separate inter-rater reliability audit.

Title: Agentic Trading: When LLM Agents Meet Financial Markets
Authors: Yihan Xia
arXiv ID: 2605.19337
Published: 2026-05-19

[Section: Impact of Exclusion Criteria on Evidence Set]
The application of the domain boundary and minimum agent criteria
substantially changed how records are interpreted. In the current auditable
registry, records were excluded during
screening/eligibility after deduplication because they were outside the survey
domain. Separately, finance-relevant records that lacked Action Output or
Closed-Loop Evaluation were retained as background/context rather than counted
as final exclusions. The exclusion summary used in the main text therefore
reports the macro-backed categories in <Ref> rather
than legacy raw screening-log totals from earlier search iterations.

This filtering yields an included evidence-mapping set
(n=); a primary empirical subset (n=)
was then coded for protocol-complete synthesis, while the remaining included
records are retained as background/context where appropriate. Readers should
therefore distinguish between included evidence, primary empirical evidence,
background references, and final exclusions when interpreting percentages and
narrative claims.

deng2025autoquant,escudero2024explainabl,kang2026quanteval,lopez-lira2025canlargela
elsarticle-harv
  url: https://arxiv.org/abs/2605.19337


# Load-bearing assumptions — Agentic Trading: When LLM Agents Meet Financial Markets

> What does this paper take for granted that, if broken, would make a genuinely
> hard engineering problem? Reimplementing the paper is a rejected idea
> (`PAPER_REIMPL`); breaking one of these is the goal.

1. Trading-agent papers often assume backtest protocols are comparable, but hidden
   lookahead, universe drift, and split leakage can make reported performance
   non-comparable.
2. Many agentic trading evaluations underspecify transaction costs, execution timing,
   cash constraints, and invalid-order semantics; breaking those assumptions should
   produce tasks where a solver must preserve an auditable market simulator contract.
3. Agent memory/retrieval loops are usually treated as harmless context, but stale,
   conflicting, or future-dated evidence can create leakage unless the evaluator checks
   provenance and decision-time availability.

## Real datasets available

- Public daily OHLCV equities/ETF data from Stooq or Yahoo-style CSV mirrors.
- SEC EDGAR filings and dated company events for evidence-availability tests.
- Synthetic-but-market-shaped order/event streams may be used only when the task
  explicitly tests protocol correctness rather than alpha discovery.

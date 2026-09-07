"""End-to-end checks over a synthetic corpus. Stdlib unittest — no pytest dependency.

Run: python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ideation import db, dedup, generate, report


def make_corpus(conn):
    seed_id = db.add_seed(
        conn, arxiv_id="0000.00001", slug="00-test-seed", title="Test Seed",
        abstract="a", url="u", lane="llm-eval",
    )
    runs = {}
    for gen in ("codex", "tbh"):
        runs[gen] = db.start_run(
            conn, seed_id=seed_id, generator=gen, model="m",
            prompt_version="v1", isolation_root=f"/tmp/{gen}",
        )
    return seed_id, runs


class TestDedup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self.tmp.name) / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_near_duplicates_are_flagged(self):
        base = {
            "title": "streaming quantile sketch under adversarial reordering",
            "statement": "Build a streaming quantile sketch that stays accurate when the "
                         "input stream is adversarially reordered by a hostile scheduler.",
            "assumption_broken": "the paper assumes an i.i.d. arrival order",
        }
        near = dict(base, title="adversarially reordered streaming quantile sketch")
        far = {
            "title": "geospatial polygon conflation across coordinate reference systems",
            "statement": "Reconcile overlapping administrative boundary polygons drawn "
                         "from two national cadastral registries.",
            "assumption_broken": "the paper assumes a single shared projection",
        }
        for obj in (base, near, far):
            db.add_idea(self.conn, self.runs["codex"], self.seed_id, obj)

        stats = dedup.scan(self.conn, threshold=0.40)
        self.assertEqual(stats["scanned"], 3)
        self.assertGreaterEqual(stats["dupe_pairs"], 1, "near-duplicate pair not caught")

        ids = [r["id"] for r in db.all_ideas(self.conn)]
        self.assertTrue(db.dupes_for(self.conn, ids[1]), "idea 2 should flag against idea 1")
        far_tfidf = [d for d in db.dupes_for(self.conn, ids[2]) if d["method"] == "tfidf"]
        self.assertFalse(far_tfidf, "unrelated idea should not be flagged as a dupe")

    def test_antipattern_matching(self):
        db.add_idea(self.conn, self.runs["tbh"], self.seed_id, {
            "title": "compress the index",
            "statement": "Rebuild the index so it fits within a strict memory budget.",
            "assumption_broken": "unbounded RAM",
        })
        db.add_idea(self.conn, self.runs["tbh"], self.seed_id, {
            "title": "cite the source",
            "statement": "Follow the method at https://arxiv.org/abs/1234.5678 exactly.",
            "assumption_broken": "none",
        })
        stats = dedup.scan(self.conn)
        self.assertGreaterEqual(stats["antipattern_hits"], 2)

        codes = {
            d["detail"].split(":")[0]
            for i in db.all_ideas(self.conn)
            for d in db.dupes_for(self.conn, i["id"])
            if d["method"] == "antipattern"
        }
        self.assertIn("constrain-memory", codes)
        self.assertIn("external-link", codes)

    def test_diversity_separates_collapsed_from_varied(self):
        collapsed_run = self.runs["tbh"]
        for i in range(4):
            db.add_idea(self.conn, collapsed_run, self.seed_id, {
                "title": f"reduce memory usage variant {i}",
                "statement": "Reduce peak memory usage of the pipeline under load.",
                "assumption_broken": "unbounded memory",
            })
        varied_run = self.runs["codex"]
        for title, stmt in [
            ("quantile sketch", "Maintain rank estimates over an adversarial stream."),
            ("polygon conflation", "Merge cadastral boundaries across projections."),
            ("scheduler fairness", "Allocate GPU slices under starvation pressure."),
            ("codec negotiation", "Resolve audio codec mismatch during renegotiation."),
        ]:
            db.add_idea(self.conn, varied_run, self.seed_id,
                        {"title": title, "statement": stmt, "assumption_broken": "x"})

        collapsed = dedup.diversity(self.conn, collapsed_run)
        varied = dedup.diversity(self.conn, varied_run)
        self.assertLess(
            collapsed["mean_pairwise_distance"],
            varied["mean_pairwise_distance"],
            "collapsed run should score lower diversity than the varied run",
        )
        self.assertEqual(collapsed["collapse_rate"], 1.0)
        self.assertEqual(varied["collapse_rate"], 0.0)

    def test_collapse_rate_catches_dupes_the_mean_hides(self):
        """The case the mean is blind to: a couple of near-dupes among many distinct ideas.

        This is what the demo corpus exposed — averaging over all pairs washes out a
        small cluster, so the report reads collapse_rate instead.
        """
        run = self.runs["tbh"]
        distinct = [
            ("quantile sketch", "Maintain rank estimates over an adversarial stream."),
            ("polygon conflation", "Merge cadastral boundaries across projections."),
            ("scheduler fairness", "Allocate GPU slices under starvation pressure."),
            ("codec negotiation", "Resolve audio codec mismatch during renegotiation."),
        ]
        for title, stmt in distinct:
            db.add_idea(self.conn, run, self.seed_id,
                        {"title": title, "statement": stmt, "assumption_broken": "x"})
        # One near-identical pair hidden among them.
        for suffix in ("", " variant"):
            db.add_idea(self.conn, run, self.seed_id, {
                "title": f"reduce peak memory usage{suffix}",
                "statement": "Reduce peak memory usage of the ingestion pipeline under load.",
                "assumption_broken": "unbounded memory",
            })

        d = dedup.diversity(self.conn, run)
        self.assertGreater(
            d["mean_pairwise_distance"], 0.85,
            "mean distance stays high — this is exactly the blind spot",
        )
        self.assertGreater(
            d["collapse_rate"], 0.0, "collapse_rate must catch the hidden dupe pair"
        )
        self.assertIn("memory", d["closest_pair_titles"][0])
        self.assertIn("memory", d["closest_pair_titles"][1])


class TestAgreement(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self.tmp.name) / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _idea(self, n: int) -> int:
        return db.add_idea(self.conn, self.runs["codex"], self.seed_id,
                           {"title": f"idea {n}", "statement": f"statement {n}",
                            "assumption_broken": "a"})

    def test_perfect_judge_scores_kappa_one(self):
        # High judge scores on accepted ideas, low on rejected: separable at some threshold.
        for n in range(6):
            idea_id = self._idea(n)
            accept = n < 3
            val = 4.5 if accept else 1.5
            db.add_score(self.conn, idea_id, "rv1", "codex", novelty=val,
                         feasibility=val, difficulty=val, interestingness=val,
                         verifiability=val, rationale="")
            db.add_verdict(self.conn, idea_id, "accept" if accept else "reject",
                           "ACCEPT" if accept else "TOO_EASY")

        ag = report.agreement(self.conn)
        self.assertEqual(ag["n"], 6)
        self.assertEqual(ag["best"]["macro_f1"], 1.0)
        self.assertEqual(ag["best"]["cohens_kappa"], 1.0)
        self.assertEqual(ag["human_accept_rate"], 0.5)

    def test_uninformative_judge_scores_near_zero_kappa(self):
        # Judge gives every idea the same score, so it cannot separate anything.
        for n in range(8):
            idea_id = self._idea(n)
            db.add_score(self.conn, idea_id, "rv1", "codex", novelty=3.0,
                         feasibility=3.0, difficulty=3.0, interestingness=3.0,
                         verifiability=3.0, rationale="")
            db.add_verdict(self.conn, idea_id, "accept" if n % 2 else "reject",
                           "ACCEPT" if n % 2 else "MEMORIZED")

        ag = report.agreement(self.conn)
        self.assertIsNotNone(ag["best"]["cohens_kappa"])
        self.assertLessEqual(abs(ag["best"]["cohens_kappa"]), 0.01)

    def test_agreement_reports_no_data_cleanly(self):
        self.assertEqual(report.agreement(self.conn)["n"], 0)


class TestIsolation(unittest.TestCase):
    def test_stray_file_trips_the_isolation_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "abstract.md").write_text("a")
            (root / "PROMPT.md").write_text("p")
            generate.assert_isolated(root)  # clean root: must not raise

            (root / "other_agents_ideas.json").write_text("{}")
            with self.assertRaises(generate.GeneratorError):
                generate.assert_isolated(root)


class TestIdeaParsing(unittest.TestCase):
    def test_parses_fenced_json_from_final_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "last_message.txt").write_text(
                'Here you go:\n```json\n{"ideas": [{"title": "t", "statement": "s", '
                '"assumption_broken": "a"}]}\n```\n'
            )
            ideas = generate._parse_ideas(root)
            self.assertEqual(len(ideas), 1)
            self.assertEqual(ideas[0]["title"], "t")

    def test_ideas_json_wins_over_final_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ideas.json").write_text('{"ideas": [{"title": "from-file"}]}')
            (root / "last_message.txt").write_text('{"ideas": [{"title": "from-message"}]}')
            self.assertEqual(generate._parse_ideas(root)[0]["title"], "from-file")

    def test_unparseable_output_yields_no_ideas(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "last_message.txt").write_text("I was unable to complete this task.")
            self.assertEqual(generate._parse_ideas(root), [])


if __name__ == "__main__":
    unittest.main()

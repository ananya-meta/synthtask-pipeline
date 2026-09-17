"""End-to-end checks over a synthetic corpus. Stdlib unittest — no pytest dependency.

Run: python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ideation import (
    cli,
    db,
    dedup,
    generate,
    lifecycle,
    orchestrator,
    publisher,
    report,
    smoldata,
    sweep,
)


_SCAFFOLD_SANDBOX: tempfile.TemporaryDirectory | None = None
_REAL_SCAFFOLD_ROOT = lifecycle.SCAFFOLD_ROOT


def setUpModule():
    """Keep scaffold workspaces out of the real `runs/` tree.

    `lifecycle.SCAFFOLD_ROOT` is resolved from the repo root, so without this every test
    that starts a scaffold leaves a timestamped directory behind in the live corpus.
    """
    global _SCAFFOLD_SANDBOX
    _SCAFFOLD_SANDBOX = tempfile.TemporaryDirectory()
    lifecycle.SCAFFOLD_ROOT = Path(_SCAFFOLD_SANDBOX.name)


def tearDownModule():
    lifecycle.SCAFFOLD_ROOT = _REAL_SCAFFOLD_ROOT
    if _SCAFFOLD_SANDBOX is not None:
        _SCAFFOLD_SANDBOX.cleanup()


# Realistic enough to clear `validate_contract`'s quality floor — terse placeholders are
# exactly what that floor exists to reject.
CONTRACT_FIXTURE = {
    "hidden_principle": "Score concept transfer against held-out bridges the agent never sees.",
    "allowed_inputs": '["visible graph snapshot", "public README"]',
    "forbidden_leaks": '["held-out bridge list", "scoring thresholds"]',
    "oracle_strategy": "Compare submitted rankings against a hidden implementation-independent oracle.",
    "mutation_strategy": "Reject solvers that hard-code public examples or emit constant output.",
    "infra_requirements": "stdlib Python.",
    "difficulty_target": "Frontier agents should need graph reasoning and fail simple heuristics.",
}


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


def run_git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ("git", *args),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


def make_bare_remote(root: Path) -> Path:
    bare = root / "remote.git"
    run_git("init", "-q", "--bare", "-b", "main", str(bare), cwd=root)
    seed = root / "seed-repo"
    seed.mkdir()
    run_git("init", "-q", "-b", "main", ".", cwd=seed)
    (seed / "README.md").write_text("tasks\n")
    run_git("add", "-A", cwd=seed)
    run_git(
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@example.com",
        "commit",
        "-qm",
        "seed",
        cwd=seed,
    )
    run_git("remote", "add", "origin", str(bare), cwd=seed)
    run_git("push", "-q", "origin", "main", cwd=seed)
    return bare


def remote_files(remote: Path) -> list[str]:
    out = run_git(
        "-C",
        str(remote),
        "ls-tree",
        "-r",
        "--name-only",
        "main",
        cwd=remote,
    )
    return sorted(out.stdout.splitlines())


def make_task_tree(root: Path, name: str = "task") -> Path:
    task = root / name
    (task / "tests").mkdir(parents=True, exist_ok=True)
    (task / "environment").mkdir(exist_ok=True)
    (task / "task.toml").write_text('[task]\nname = "demo"\n')
    (task / "instruction.md").write_text("Build the requested solver.\n")
    test_sh = task / "tests" / "test.sh"
    test_sh.write_text("#!/bin/sh\nexit 0\n")
    test_sh.chmod(0o755)
    return task


class TestDedup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "t.db"
        self.conn = db.connect(self.db_path)
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
            (root / ".schema.json").write_text("{}")
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


class TestLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "t.db"
        self.conn = db.connect(self.db_path)
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "rank unstable citation bridges",
                "statement": "Find citation bridges whose concept support changes under drift.",
                "assumption_broken": "the literature graph is stationary",
                "difficulty_claim": "requires hidden graph cases",
                "dataset_ref": "OpenAlex concept graph",
            },
        )

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_contract_requires_accepted_idea_by_default(self):
        with self.assertRaises(lifecycle.LifecycleError):
            lifecycle.create_contract(self.conn, self.idea_id)

        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        contract_id = lifecycle.create_contract(self.conn, self.idea_id)
        row = db.get_task_contract(self.conn, contract_id)
        self.assertEqual(row["objective"], "Find citation bridges whose concept support changes under drift.")
        self.assertEqual(row["status"], "draft")

    def test_contract_ready_requires_complete_fields(self):
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            hidden_principle="Score concept transfer without exposing held-out bridges.",
            allowed_inputs='["paper graph snapshot"]',
            forbidden_leaks='["held-out bridge list", "scoring thresholds"]',
            oracle_strategy="Compare submitted bridge rankings to hidden semantic oracle.",
            mutation_strategy="Reject solvers that hard-code public examples or ignore edge weights.",
            infra_requirements="Runs in the task Docker image with stdlib Python.",
            difficulty_target="Frontier agents should need graph reasoning and fail simple heuristics.",
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        self.assertEqual(db.get_task_contract(self.conn, contract_id)["status"], "ready")

    def test_discovery_ingest_captures_text_bundle(self):
        bundle = Path(self.tmp.name) / "bundle"
        bundle.mkdir()
        (bundle / "direction.md").write_text("# Direction\nMine citation bridges.\n")
        (bundle / "evidence.json").write_text('{"papers": 3}\n')

        bundle_id = lifecycle.ingest_discovery_bundle(
            self.conn,
            bundle,
            seed_ref="00-test-seed",
            source="paper-task-factory",
            title="Citation bridge bundle",
        )
        row = db.list_discovery_bundles(self.conn)[0]
        payload = json.loads(row["payload_json"])
        self.assertEqual(bundle_id, row["id"])
        self.assertEqual(row["seed_id"], self.seed_id)
        self.assertEqual({f["path"] for f in payload["files"]}, {"direction.md", "evidence.json"})

    def test_scaffold_workspace_isolated_and_verifiable(self):
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            **CONTRACT_FIXTURE,
        )
        with self.assertRaises(lifecycle.LifecycleError):
            lifecycle.start_scaffold(self.conn, contract_id, builder="codex")
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        scaffold_id, root = lifecycle.start_scaffold(self.conn, contract_id, builder="codex")
        lifecycle.assert_scaffold_isolated(root)
        self.assertTrue((root / "TASK_CONTRACT.json").exists())
        self.assertTrue((root / "task").is_dir())

        (root / "unexpected.txt").write_text("leak")
        with self.assertRaises(lifecycle.LifecycleError):
            lifecycle.assert_scaffold_isolated(root)

        (root / "unexpected.txt").unlink()
        verify_id = lifecycle.run_verification(
            self.conn,
            scaffold_id,
            [sys.executable, "-c", "print('ok')"],
            timeout=30,
        )
        status = self.conn.execute(
            "SELECT status FROM verification_runs WHERE id = ?", (verify_id,)
        ).fetchone()["status"]
        self.assertEqual(status, "pass")

    def test_verify_cli_accepts_options_after_scaffold_id(self):
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            **CONTRACT_FIXTURE,
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        scaffold_id, _ = lifecycle.start_scaffold(self.conn, contract_id, builder="codex")
        rc = cli.main(
            [
                "--db",
                str(self.db_path),
                "verify",
                "run",
                str(scaffold_id),
                "--cwd",
                "task",
                "--",
                sys.executable,
                "-c",
                "print('ok')",
            ]
        )
        self.assertEqual(rc, 0)

    def test_scaffold_worker_renders_prompt_and_updates_state(self):
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            **CONTRACT_FIXTURE,
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        scaffold_id, root = lifecycle.start_scaffold(self.conn, contract_id, builder="codex")
        prompt_file = Path(self.tmp.name) / "build_prompt.md"
        prompt_file.write_text("Use {{TASK_DIR}}\n\n{{TASK_CONTRACT_JSON}}\n")

        completed = subprocess.CompletedProcess(["codex"], 0, stdout="built", stderr="")
        with mock.patch.object(lifecycle.subprocess, "run", return_value=completed) as run:
            rc = lifecycle.run_scaffold_worker(self.conn, scaffold_id, prompt_file, timeout=30)

        self.assertEqual(rc, 0)
        rendered = (root / "RUN_PROMPT.md").read_text()
        self.assertIn(str(root / "task"), rendered)
        self.assertIn('"idea_id":', rendered)
        self.assertEqual(run.call_args.kwargs["cwd"], root)
        scaffold = db.get_scaffold_run(self.conn, scaffold_id)
        self.assertEqual(scaffold["state"], "built")
        self.assertEqual(scaffold["exit_code"], 0)

    def test_submission_updates_outcome_and_triage(self):
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            **CONTRACT_FIXTURE,
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        scaffold_id, _ = lifecycle.start_scaffold(self.conn, contract_id)
        submission_id = lifecycle.record_submission(
            self.conn,
            scaffold_id,
            platform="smoldata",
            external_id="task-123",
            status="bad_grading_weak",
            pass_rate=1.0,
            revisions=2,
            result={"label": "BAD_GRADING_WEAK"},
        )
        self.assertEqual(lifecycle.triage_route("bad_grading_weak"), "strengthen_oracle")
        self.assertGreater(submission_id, 0)
        outcome = self.conn.execute(
            "SELECT * FROM outcomes WHERE idea_id = ?", (self.idea_id,)
        ).fetchone()
        self.assertEqual(outcome["accepted"], 0)
        self.assertEqual(outcome["smoldata_task_id"], "task-123")
        action = lifecycle.next_actions(self.conn)[0]
        self.assertEqual(action["stage"], "triage")
        self.assertEqual(action["route"], "strengthen_oracle")
        # The failure records itself now, so the revision is the next step directly rather
        # than being gated behind a manual `learn add`.
        self.assertEqual(
            action["action"], f"synthtask scaffold start {contract_id} --builder codex"
        )
        auto = db.learning_events_for(self.conn, "submission", submission_id)
        self.assertEqual([e["label"] for e in auto], ["smoldata-failure"])
        self.assertEqual(json.loads(auto[0]["payload_json"])["route"], "strengthen_oracle")

    def test_next_actions_advance_from_accepted_idea_to_scaffold(self):
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        first = lifecycle.next_actions(self.conn)
        self.assertEqual(first[0]["stage"], "contract")
        self.assertIn(str(self.idea_id), first[0]["action"])

        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            **CONTRACT_FIXTURE,
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        second = lifecycle.next_actions(self.conn)
        self.assertEqual(second[0]["stage"], "scaffold")
        self.assertIn(str(contract_id), second[0]["action"])

    def test_next_actions_include_publish_then_smoldata_watch(self):
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            **CONTRACT_FIXTURE,
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        scaffold_id, root = lifecycle.start_scaffold(self.conn, contract_id)
        make_task_tree(root, "task")
        lifecycle.run_verification(
            self.conn,
            scaffold_id,
            [sys.executable, "-c", "print('ok')"],
        )
        lifecycle.record_review(
            self.conn,
            scaffold_id,
            reviewer="tbh",
            kind="adversarial",
            verdict="approve",
        )
        canonical = Path(self.tmp.name) / "canonical-task"
        lifecycle.promote_scaffold(self.conn, scaffold_id, canonical)

        actions = lifecycle.next_actions(self.conn)
        self.assertEqual(actions[0]["stage"], "publish")
        self.assertIn(f"synthtask publish run {scaffold_id}", actions[0]["action"])

        db.add_publish_record(
            self.conn,
            scaffold_run_id=scaffold_id,
            task_name="canonical-task",
            remote_url="https://github.com/codimango/ananyajain-tbench.git",
            branch="main",
            commit_sha="abc123",
            github_url="https://github.com/codimango/ananyajain-tbench/tree/abc123/canonical-task",
            status="published",
            payload_json="{}",
        )
        actions = lifecycle.next_actions(self.conn)
        self.assertEqual(actions[0]["stage"], "smoldata")
        self.assertIn("synthtask smoldata watch canonical-task", actions[0]["action"])

        db.add_publish_record(
            self.conn,
            scaffold_run_id=scaffold_id,
            task_name="canonical-task",
            remote_url="https://github.com/codimango/ananyajain-tbench.git",
            branch="main",
            commit_sha="def456",
            github_url="https://github.com/codimango/ananyajain-tbench/tree/def456/canonical-task",
            status="published",
            payload_json="{}",
        )
        actions = [action for action in lifecycle.next_actions(self.conn) if action["stage"] == "smoldata"]
        self.assertEqual(len(actions), 1)
        self.assertIn("synthtask smoldata watch canonical-task", actions[0]["action"])


class TestPublisher(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db_path = self.root / "t.db"
        self.conn = db.connect(self.db_path)
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "publishable task",
                "statement": "Build a task ready for publication.",
                "assumption_broken": "manual handoff loses tasks",
            },
        )
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _promoted_scaffold(self) -> tuple[int, Path]:
        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            **CONTRACT_FIXTURE,
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        scaffold_id, root = lifecycle.start_scaffold(self.conn, contract_id)
        make_task_tree(root, "task")
        canonical = self.root / "canonical-task"
        lifecycle.promote_scaffold(self.conn, scaffold_id, canonical)
        return scaffold_id, canonical

    def test_publish_task_pushes_to_local_remote(self):
        remote = make_bare_remote(self.root)
        source = make_task_tree(self.root, "source-task")

        result = publisher.publish_task(
            source,
            task_name="published-task",
            remote_url=str(remote),
            method="git",
        )

        self.assertEqual(result.status, "published")
        self.assertTrue(result.pushed)
        self.assertIn("published-task/task.toml", remote_files(remote))
        self.assertIn("published-task/tests/test.sh", remote_files(remote))
        self.assertEqual(
            result.inventory_sha256,
            publisher.inventory_sha256(publisher.task_inventory(source)),
        )

    def test_publish_task_is_idempotent_for_identical_bytes(self):
        remote = make_bare_remote(self.root)
        source = make_task_tree(self.root, "source-task")

        publisher.publish_task(
            source,
            task_name="published-task",
            remote_url=str(remote),
            method="git",
        )
        second = publisher.publish_task(
            source,
            task_name="published-task",
            remote_url=str(remote),
            method="git",
        )

        self.assertEqual(second.status, "no_changes")
        self.assertFalse(second.pushed)

    def test_publish_scaffold_records_database_receipt(self):
        remote = make_bare_remote(self.root)
        scaffold_id, canonical = self._promoted_scaffold()

        record_id = publisher.publish_scaffold(
            self.conn,
            scaffold_id,
            task_name="canonical-task",
            remote_url=str(remote),
            method="git",
        )

        row = db.publish_record_for_scaffold(self.conn, scaffold_id)
        payload = json.loads(row["payload_json"])
        self.assertEqual(row["id"], record_id)
        self.assertEqual(row["status"], "published")
        self.assertEqual(row["task_name"], "canonical-task")
        self.assertEqual(
            payload["inventory_sha256"],
            publisher.inventory_sha256(publisher.task_inventory(canonical)),
        )
        self.assertIn("canonical-task/task.toml", remote_files(remote))

    def test_auto_publish_falls_back_to_github_api_for_private_repo_auth(self):
        source = make_task_tree(self.root, "source-task")
        expected = publisher.PublishResult(
            task_name="published-task",
            remote_url="org-272075201@github.com:codimango/ananyajain-tbench.git",
            branch="main",
            commit_sha="f" * 40,
            github_url="https://github.com/codimango/ananyajain-tbench/tree/"
            + ("f" * 40)
            + "/published-task",
            status="published",
            pushed=True,
            inventory_sha256=publisher.inventory_sha256(publisher.task_inventory(source)),
            method="github-api",
        )
        with (
            mock.patch.object(
                publisher,
                "_publish_task_git",
                side_effect=publisher.PublishError("auth failed"),
            ),
            mock.patch.object(
                publisher,
                "_publish_task_github_api",
                return_value=expected,
            ) as api_publish,
        ):
            result = publisher.publish_task(
                source,
                task_name="published-task",
                remote_url="org-272075201@github.com:codimango/ananyajain-tbench.git",
                method="auto",
            )

        self.assertEqual(result.method, "github-api")
        api_publish.assert_called_once()

    def test_publish_refuses_controller_metadata(self):
        source = make_task_tree(self.root, "source-task")
        (source / ".factory").mkdir()
        (source / ".factory" / "private.json").write_text("{}\n")

        with self.assertRaises(publisher.PublishError):
            publisher.publish_task(
                source,
                task_name="published-task",
                remote_url=str(make_bare_remote(self.root)),
                method="git",
            )


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self.tmp.name) / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "taskable idea",
                "statement": "Build a verifier-backed task.",
                "assumption_broken": "paper assumes easy validation",
            },
        )
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _config(self, **kw):
        base = {
            "idea_id": self.idea_id,
            "stop_after": "scaffold",
            "contract_overrides": dict(CONTRACT_FIXTURE),
        }
        base.update(kw)
        return orchestrator.PipelineRunConfig(**base)

    def test_pipeline_run_reaches_scaffold(self):
        result = orchestrator.run(self.conn, self._config())
        self.assertEqual(result.blocked_at, "")
        self.assertEqual(result.completed, ["contract", "ready", "scaffold"])
        self.assertIn("scaffold_run_id", result.ids)

    def test_pipeline_blocks_at_build_without_prompt(self):
        missing_prompt = Path(self.tmp.name) / "missing-build-prompt.md"
        with mock.patch.object(orchestrator, "DEFAULT_BUILD_PROMPT", missing_prompt):
            result = orchestrator.run(self.conn, self._config(stop_after="build"))
        self.assertEqual(result.blocked_at, "build")
        self.assertIn("builder prompt file", result.reason)

    def test_pipeline_run_publishes_promoted_scaffold(self):
        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            **CONTRACT_FIXTURE,
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        scaffold_id, root = lifecycle.start_scaffold(self.conn, contract_id)
        make_task_tree(root, "task")
        lifecycle.record_review(
            self.conn,
            scaffold_id,
            reviewer="tbh",
            kind="adversarial",
            verdict="approve",
        )
        lifecycle.run_verification(
            self.conn,
            scaffold_id,
            [sys.executable, "-c", "print('ok')"],
        )
        canonical = Path(self.tmp.name) / "canonical"
        remote = make_bare_remote(Path(self.tmp.name))
        result = orchestrator.run(
            self.conn,
            orchestrator.PipelineRunConfig(
                contract_id=contract_id,
                scaffold_run_id=scaffold_id,
                canonical_root=canonical,
                publish_task_name="pipeline-task",
                publish_remote=str(remote),
                stop_after="publish",
                publish_method="git",
            ),
        )
        self.assertEqual(result.blocked_at, "")
        self.assertIn("publish", result.completed)
        self.assertIn("pipeline-task/task.toml", remote_files(remote))

    def test_pipeline_blocks_at_smoldata_when_publish_was_not_pushed(self):
        contract_id = lifecycle.create_contract(
            self.conn,
            self.idea_id,
            **CONTRACT_FIXTURE,
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        scaffold_id, root = lifecycle.start_scaffold(self.conn, contract_id)
        make_task_tree(root, "task")
        lifecycle.record_review(
            self.conn,
            scaffold_id,
            reviewer="tbh",
            kind="adversarial",
            verdict="approve",
        )
        lifecycle.run_verification(
            self.conn,
            scaffold_id,
            [sys.executable, "-c", "print('ok')"],
        )
        canonical = Path(self.tmp.name) / "canonical"
        remote = make_bare_remote(Path(self.tmp.name))
        result = orchestrator.run(
            self.conn,
            orchestrator.PipelineRunConfig(
                contract_id=contract_id,
                scaffold_run_id=scaffold_id,
                canonical_root=canonical,
                publish_task_name="pipeline-task",
                publish_remote=str(remote),
                publish_push=False,
                publish_method="git",
                stop_after="smoldata",
            ),
        )
        self.assertEqual(result.blocked_at, "smoldata")
        self.assertIn("not pushed", result.reason)


class TestSmoldata(unittest.TestCase):
    def test_show_task_normalizes_status(self):
        completed = subprocess.CompletedProcess(
            ["codimango"],
            0,
            stdout='banner\n{"task": {"status": "accepted"}}\n',
            stderr="",
        )
        with mock.patch.object(smoldata.subprocess, "run", return_value=completed):
            result = smoldata.show_task("task-123")
        self.assertEqual(result["status"], "accepted")

    def test_failed_validation_prefers_actionable_reason(self):
        payload = {
            "task": {
                "status": "draft",
                "validationStatus": "failed",
                "validationDetails": [
                    {
                        "label": "Metacode or Opus pass/fail balance",
                        "status": "failed",
                        "detail": "Too easy - all agents passed 5/5",
                    }
                ],
            }
        }
        self.assertEqual(smoldata._status_from_payload(payload), "too_easy")

    def test_pending_validation_is_not_reported_as_draft(self):
        payload = {"status": "draft", "validationStatus": "pending"}
        self.assertEqual(smoldata._status_from_payload(payload), "pending")

    def test_agentic_review_treats_bad_review_exit_as_payload(self):
        completed = subprocess.CompletedProcess(
            ["codimango"],
            1,
            stdout='{"verdict": "BAD_GRADING_WEAK", "authorFeedback": "tighten oracle"}',
            stderr="",
        )
        with mock.patch.object(smoldata.subprocess, "run", return_value=completed):
            result = smoldata.agentic_review("task-123", fail_on_bad=True)
        self.assertEqual(result["status"], "bad_grading_weak")
        self.assertEqual(result["returncode"], 1)

    def test_agentic_review_treats_in_flight_as_pending(self):
        completed = subprocess.CompletedProcess(
            ["codimango"],
            1,
            stdout='{"state": "in_flight", "review": null}',
            stderr="",
        )
        with mock.patch.object(smoldata.subprocess, "run", return_value=completed):
            result = smoldata.agentic_review("task-123")
        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["returncode"], 1)


class TestUnsettledSubmissions(unittest.TestCase):
    """A submission row is written the moment a task is published, so anything that is
    not yet a verdict has to stay visible or the task drops out of the controller."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.conn = db.connect(self.root / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "pollable",
                "statement": "Rank citation bridges whose support shifts under concept drift.",
                "assumption_broken": "a",
            },
        )
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        self.contract_id = lifecycle.create_contract(
            self.conn, self.idea_id, **CONTRACT_FIXTURE
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, self.contract_id), [])
        self.scaffold_id, self.scaffold_root = lifecycle.start_scaffold(
            self.conn, self.contract_id
        )

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _submit(self, status: str, external_id: str = "task-123") -> int:
        return lifecycle.record_submission(
            self.conn,
            self.scaffold_id,
            platform="smoldata",
            external_id=external_id,
            status=status,
        )

    def test_pending_submission_surfaces_a_poll_action(self):
        self._submit("pending")
        actions = lifecycle.next_actions(self.conn)
        self.assertEqual([a["stage"] for a in actions], ["poll"])
        action = actions[0]
        self.assertEqual(action["route"], "poll")
        self.assertEqual(action["task_name"], "task-123")
        self.assertEqual(action["scaffold_run_id"], self.scaffold_id)
        self.assertIn("synthtask smoldata watch task-123", action["action"])

    def test_every_unsettled_status_is_pollable(self):
        for status in lifecycle.POLLABLE_SUBMISSION_STATUSES:
            with self.subTest(status=status):
                self._submit(status)
                stages = [a["stage"] for a in lifecycle.next_actions(self.conn)]
                self.assertEqual(stages, ["poll"], f"{status} fell out of next_actions")

    def test_settled_failure_still_routes_to_triage(self):
        self._submit("too_easy")
        actions = lifecycle.next_actions(self.conn)
        self.assertEqual([a["stage"] for a in actions], ["triage"])
        self.assertEqual(actions[0]["route"], "reduce_leakage_or_add_hidden_state")

    def test_accepted_submission_needs_no_action(self):
        self._submit("accepted")
        self.assertEqual(lifecycle.next_actions(self.conn), [])

    def test_poll_falls_back_to_the_published_task_name(self):
        db.add_publish_record(
            self.conn,
            scaffold_run_id=self.scaffold_id,
            task_name="published-name",
            remote_url="https://example.invalid/repo.git",
            branch="main",
            commit_sha="abc",
            github_url="https://example.invalid/repo/tree/abc/published-name",
            status="published",
            payload_json="{}",
        )
        self._submit("pending", external_id="")
        action = lifecycle.next_actions(self.conn)[0]
        self.assertEqual(action["stage"], "poll")
        self.assertEqual(action["task_name"], "published-name")


class TestFanoutGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self.tmp.name) / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "guarded",
                "statement": "Reconcile duplicate contracts across a shared idea corpus.",
                "assumption_broken": "a",
            },
        )
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_live_contract_blocks_a_second_draft(self):
        first = lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE)
        with self.assertRaises(lifecycle.LifecycleError) as caught:
            lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE)
        self.assertIn(f"contract #{first}", str(caught.exception))

        forced = lifecycle.create_contract(
            self.conn, self.idea_id, force=True, **CONTRACT_FIXTURE
        )
        self.assertNotEqual(forced, first)

    def test_shelved_contract_frees_the_idea(self):
        first = lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE)
        db.update_task_contract_status(self.conn, first, "shelved")
        self.assertNotEqual(
            lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE), first
        )

    def test_live_scaffold_blocks_a_second_revision(self):
        contract_id = lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE)
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        first, _ = lifecycle.start_scaffold(self.conn, contract_id)
        with self.assertRaises(lifecycle.LifecycleError) as caught:
            lifecycle.start_scaffold(self.conn, contract_id)
        self.assertIn(f"scaffold #{first}", str(caught.exception))

        explicit, _ = lifecycle.start_scaffold(self.conn, contract_id, revision=9)
        self.assertNotEqual(explicit, first)

    def test_submitted_scaffold_allows_the_revision_loop(self):
        contract_id = lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE)
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        first, _ = lifecycle.start_scaffold(self.conn, contract_id)
        lifecycle.record_submission(
            self.conn, first, platform="smoldata", external_id="t", status="too_easy"
        )
        second, _ = lifecycle.start_scaffold(self.conn, contract_id)
        self.assertNotEqual(second, first)


class TestContractSettings(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.conn = db.connect(self.root / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "configured",
                "statement": "Materialise a causal split without leaking the holdout partition.",
                "assumption_broken": "a",
            },
        )
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        self.contract_id = lifecycle.create_contract(
            self.conn, self.idea_id, **CONTRACT_FIXTURE
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, self.contract_id), [])

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_settings_upsert_preserves_untouched_fields(self):
        db.set_contract_settings(self.conn, self.contract_id, publish_task_name="alpha")
        db.set_contract_settings(self.conn, self.contract_id, auto_advance=1)
        row = db.get_contract_settings(self.conn, self.contract_id)
        self.assertEqual(row["publish_task_name"], "alpha")
        self.assertEqual(row["auto_advance"], 1)

    def test_unknown_setting_is_rejected(self):
        with self.assertRaises(ValueError):
            db.set_contract_settings(self.conn, self.contract_id, nonsense="x")

    def test_stored_settings_drive_a_bare_pipeline_run(self):
        scaffold_id, scaffold_root = lifecycle.start_scaffold(self.conn, self.contract_id)
        make_task_tree(scaffold_root, "task")
        lifecycle.record_review(
            self.conn, scaffold_id, reviewer="tbh", kind="adversarial", verdict="approve"
        )
        remote = make_bare_remote(self.root)
        db.set_contract_settings(
            self.conn,
            self.contract_id,
            verify_commands=json.dumps([f"{sys.executable} -c print(1)"]),
            canonical_root=str(self.root / "canonical"),
            publish_task_name="settings-task",
            publish_remote=str(remote),
            publish_method="git",
            auto_advance=1,
        )

        # Nothing but the scaffold id: the contract, verifier and publish target all
        # come from the stored settings.
        result = orchestrator.run(
            self.conn,
            orchestrator.PipelineRunConfig(
                scaffold_run_id=scaffold_id, stop_after="publish", allow_build=False
            ),
        )

        self.assertEqual(result.blocked_at, "")
        self.assertEqual(result.ids["contract_id"], self.contract_id)
        for stage in ("verify", "audit", "promote", "publish"):
            self.assertIn(stage, result.completed)
        self.assertIn("settings-task/task.toml", remote_files(remote))

    def test_explicit_flags_beat_stored_settings(self):
        db.set_contract_settings(self.conn, self.contract_id, publish_task_name="stored")
        config = orchestrator.PipelineRunConfig(
            contract_id=self.contract_id, publish_task_name="explicit"
        )
        orchestrator.apply_contract_settings(self.conn, self.contract_id, config)
        self.assertEqual(config.publish_task_name, "explicit")

    def test_no_build_blocks_instead_of_invoking_the_builder(self):
        scaffold_id, _ = lifecycle.start_scaffold(self.conn, self.contract_id)
        with mock.patch.object(lifecycle, "run_scaffold_worker") as worker:
            result = orchestrator.run(
                self.conn,
                orchestrator.PipelineRunConfig(
                    scaffold_run_id=scaffold_id, stop_after="build", allow_build=False
                ),
            )
        worker.assert_not_called()
        self.assertEqual(result.blocked_at, "build")
        self.assertIn("may not invoke a builder", result.reason)


class TestSweep(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.conn = db.connect(self.root / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "sweepable",
                "statement": "Detect stale validation state across a queue of published tasks.",
                "assumption_broken": "a",
            },
        )
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        self.contract_id = lifecycle.create_contract(
            self.conn, self.idea_id, **CONTRACT_FIXTURE
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, self.contract_id), [])
        self.scaffold_id, self.scaffold_root = lifecycle.start_scaffold(
            self.conn, self.contract_id
        )

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_poll_records_the_settled_status(self):
        lifecycle.record_submission(
            self.conn,
            self.scaffold_id,
            platform="smoldata",
            external_id="task-123",
            status="pending",
        )
        observed = {"status": "too_easy", "payload": {"task": {"status": "draft"}}}
        with mock.patch.object(sweep.smoldata, "show_task", return_value=observed) as show:
            summary = sweep.run(self.conn)

        show.assert_called_once()
        self.assertEqual(summary["polled"][0]["status"], "too_easy")
        self.assertEqual(summary["errors"], [])
        latest = self.conn.execute(
            "SELECT status FROM submissions ORDER BY id DESC LIMIT 1"
        ).fetchone()
        self.assertEqual(latest["status"], "too_easy")

    def test_poll_runs_even_without_auto_advance(self):
        lifecycle.record_submission(
            self.conn,
            self.scaffold_id,
            platform="smoldata",
            external_id="task-123",
            status="pending",
        )
        observed = {"status": "pending", "payload": {}}
        with mock.patch.object(sweep.smoldata, "show_task", return_value=observed):
            summary = sweep.run(self.conn)
        self.assertEqual(len(summary["polled"]), 1)

    def test_advance_is_skipped_without_auto_advance(self):
        make_task_tree(self.scaffold_root, "task")
        lifecycle.run_verification(
            self.conn, self.scaffold_id, [sys.executable, "-c", "print(1)"]
        )
        summary = sweep.run(self.conn)
        self.assertEqual(summary["advanced"], [])
        self.assertEqual(summary["waiting_on_you"][0]["stage"], "audit")

    def test_human_stages_are_reported_never_driven(self):
        # A verified scaffold awaiting audit, plus a settled failure awaiting triage.
        make_task_tree(self.scaffold_root, "task")
        lifecycle.run_verification(
            self.conn, self.scaffold_id, [sys.executable, "-c", "print(1)"]
        )
        db.set_contract_settings(self.conn, self.contract_id, auto_advance=1)
        summary = sweep.run(self.conn)
        self.assertEqual(summary["advanced"], [])
        self.assertEqual(
            [item["stage"] for item in summary["waiting_on_you"]], ["audit"]
        )

    def test_sweep_never_invokes_a_builder(self):
        db.set_contract_settings(self.conn, self.contract_id, auto_advance=1)
        with mock.patch.object(sweep.lifecycle, "run_scaffold_worker") as worker:
            sweep.run(self.conn)
        worker.assert_not_called()

    def test_dry_run_touches_nothing(self):
        lifecycle.record_submission(
            self.conn,
            self.scaffold_id,
            platform="smoldata",
            external_id="task-123",
            status="pending",
        )
        before = self.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        with mock.patch.object(sweep.smoldata, "show_task") as show:
            summary = sweep.run(self.conn, dry_run=True)
        show.assert_not_called()
        self.assertTrue(summary["polled"][0]["dry_run"])
        after = self.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        self.assertEqual(before, after)

    def test_poll_failure_is_reported_not_raised(self):
        lifecycle.record_submission(
            self.conn,
            self.scaffold_id,
            platform="smoldata",
            external_id="task-123",
            status="pending",
        )
        with mock.patch.object(
            sweep.smoldata, "show_task", side_effect=smoldata.SmoldataError("502 from nest")
        ):
            summary = sweep.run(self.conn)
        self.assertEqual(summary["polled"], [])
        self.assertIn("502 from nest", summary["errors"][0]["error"])

    def test_lock_refuses_a_concurrent_sweep(self):
        lock_path = self.root / "sweep.lock"
        with sweep.exclusive_lock(lock_path):
            with self.assertRaises(sweep.SweepError):
                with sweep.exclusive_lock(lock_path):
                    pass


class TestBuildGate(unittest.TestCase):
    """The build gate must be stated as an exclusion list.

    `scaffold_runs.state` takes fifteen values from seven writers; an allowlist of "already
    built" states silently omits new ones and re-invokes the builder on finished work.
    """

    ALL_STATES = (
        "started", "running", "built", "build_failed", "verified", "verification_failed",
        "reviewed", "needs_revision", "rejected", "promoted", "published", "no_changes",
        "committed", "submitted", "accepted",
    )

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self.tmp.name) / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "gated",
                "statement": "Rebuild a published scaffold only when it has no build behind it.",
                "assumption_broken": "a",
            },
        )
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        self.contract_id = lifecycle.create_contract(
            self.conn, self.idea_id, **CONTRACT_FIXTURE
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, self.contract_id), [])
        self.scaffold_id, _ = lifecycle.start_scaffold(self.conn, self.contract_id)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _rebuilds_from(self, state: str) -> bool:
        db.update_scaffold_run(self.conn, self.scaffold_id, state=state)
        with mock.patch.object(lifecycle, "run_scaffold_worker", return_value=0) as worker:
            orchestrator.run(
                self.conn,
                orchestrator.PipelineRunConfig(
                    scaffold_run_id=self.scaffold_id, stop_after="build"
                ),
            )
        return worker.called

    def test_only_unbuilt_states_invoke_the_builder(self):
        for state in self.ALL_STATES:
            with self.subTest(state=state):
                expected = state in lifecycle.UNBUILT_STATES
                self.assertEqual(
                    self._rebuilds_from(state),
                    expected,
                    f"state {state!r} should{'' if expected else ' not'} trigger a build",
                )

    def test_published_scaffold_is_never_rebuilt(self):
        for state in ("published", "no_changes", "committed"):
            with self.subTest(state=state):
                self.assertFalse(self._rebuilds_from(state))


class TestFailureClassification(unittest.TestCase):
    def _payload(self, **detail) -> dict:
        return {
            "status": "draft",
            "validationStatus": "failed",
            "validationDetails": [
                {"label": "Structural checks", "status": "passed", "detail": "14/14"},
                {"label": "Metacode or Opus pass/fail balance", "status": "failed", **detail},
            ],
        }

    def test_structured_code_beats_prose(self):
        # Prose says one thing, the machine field says another: trust the field.
        payload = self._payload(detail="Timeout while grading", monotoneFailure="too-easy")
        self.assertEqual(smoldata._status_from_payload(payload), "too_easy")

    def test_real_codimango_shape(self):
        payload = self._payload(
            detail="Too easy — avocado passed all 5 (avocado: 5/5, opus: 5/5)",
            monotoneFailure="too-easy",
        )
        self.assertEqual(smoldata._status_from_payload(payload), "too_easy")

    def test_prose_fallback_when_no_code(self):
        payload = self._payload(detail="Too easy — avocado passed all 5")
        self.assertEqual(smoldata._status_from_payload(payload), "too_easy")

    def test_unknown_code_is_surfaced_not_dropped(self):
        payload = self._payload(detail="something new", monotoneFailure="wildly-new-code")
        status = smoldata._status_from_payload(payload)
        self.assertEqual(status, "failed_unclassified:wildly_new_code")
        self.assertEqual(lifecycle.triage_route(status), "manual_triage")

    def test_unclassifiable_failure_is_distinct_from_rejection(self):
        payload = self._payload(detail="the grader emitted an unfamiliar complaint")
        status = smoldata._status_from_payload(payload)
        self.assertEqual(status, "failed_unclassified")
        self.assertNotEqual(status, "rejected")
        self.assertTrue(lifecycle.is_failed_status(status))

    def test_unclassified_failure_still_routes_to_triage_not_poll(self):
        self.assertFalse(
            "failed_unclassified" in lifecycle.POLLABLE_SUBMISSION_STATUSES
        )
        self.assertTrue(lifecycle.is_failed_status("failed_unclassified"))


class TestAdviceMatchesEnforcement(unittest.TestCase):
    """Every command `next_actions` prints must actually be runnable.

    A derived view that suggests a command its own guards refuse is worse than no advice:
    it looks like progress and cannot be followed.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self.tmp.name) / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "advised",
                "statement": "Reconcile advice with enforcement across the controller.",
                "assumption_broken": "a",
            },
        )
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _failed_contract(self) -> tuple[int, int]:
        contract_id = lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE)
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, contract_id), [])
        scaffold_id, _ = lifecycle.start_scaffold(self.conn, contract_id)
        lifecycle.record_submission(
            self.conn, scaffold_id, platform="smoldata", external_id="t", status="too_easy"
        )
        return contract_id, scaffold_id

    def test_triage_suggests_a_revision_when_none_is_open(self):
        contract_id, _ = self._failed_contract()
        triage = [a for a in lifecycle.next_actions(self.conn) if a["stage"] == "triage"][0]
        self.assertIsNone(triage["live_scaffold_run_id"])
        self.assertEqual(
            triage["action"], f"synthtask scaffold start {contract_id} --builder codex"
        )
        # The suggested command must succeed.
        lifecycle.start_scaffold(self.conn, contract_id, builder="codex")

    def test_triage_defers_when_a_revision_is_already_open(self):
        contract_id, _ = self._failed_contract()
        open_id, _ = lifecycle.start_scaffold(self.conn, contract_id, builder="codex")

        triage = [a for a in lifecycle.next_actions(self.conn) if a["stage"] == "triage"][0]
        self.assertEqual(triage["live_scaffold_run_id"], open_id)
        self.assertNotIn(f"scaffold start {contract_id}", triage["action"])
        self.assertIn(f"audit record {open_id}", triage["action"])
        self.assertIn("still open", triage["reason"])

    def test_the_deferred_advice_actually_unblocks_the_contract(self):
        contract_id, _ = self._failed_contract()
        open_id, _ = lifecycle.start_scaffold(self.conn, contract_id, builder="codex")
        with self.assertRaises(lifecycle.LifecycleError):
            lifecycle.start_scaffold(self.conn, contract_id)

        # Following the advice must clear the block.
        lifecycle.record_review(
            self.conn, open_id, reviewer="me", kind="adversarial", verdict="reject"
        )
        lifecycle.start_scaffold(self.conn, contract_id, builder="codex")

    def test_shelved_contract_returns_the_idea_to_the_board(self):
        contract_id = lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE)
        self.assertEqual(
            [a["stage"] for a in lifecycle.next_actions(self.conn)], ["contract"]
        )

        db.update_task_contract_status(self.conn, contract_id, "shelved")
        actions = lifecycle.next_actions(self.conn)
        self.assertEqual([a["stage"] for a in actions], ["contract"])
        self.assertEqual(
            actions[0]["action"], f"synthtask contract create {self.idea_id}"
        )
        # And the command it prints is runnable.
        lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE)

    def test_idea_with_a_live_contract_is_not_re_suggested(self):
        lifecycle.create_contract(self.conn, self.idea_id, **CONTRACT_FIXTURE)
        targets = [a["target"] for a in lifecycle.next_actions(self.conn)]
        self.assertNotIn(f"idea:{self.idea_id}", targets)


class TestContractQualityFloor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self.tmp.name) / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _contract(self, statement: str, **overrides) -> int:
        idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {"title": "t", "statement": statement, "assumption_broken": "a"},
        )
        db.add_verdict(self.conn, idea_id, "accept", "ACCEPT")
        fields = dict(CONTRACT_FIXTURE)
        fields.update(overrides)
        return lifecycle.create_contract(self.conn, idea_id, **fields)

    def test_realistic_contract_passes(self):
        cid = self._contract("Materialise a causal split without leaking the holdout.")
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, cid), [])

    def test_filler_is_rejected(self):
        cid = self._contract(
            "Materialise a causal split without leaking the holdout.",
            hidden_principle="asdf",
        )
        self.assertIn("hidden_principle:placeholder", lifecycle.mark_contract_ready(self.conn, cid))

    def test_terse_prose_is_rejected(self):
        cid = self._contract(
            "Materialise a causal split without leaking the holdout.",
            oracle_strategy="run oracle",
        )
        self.assertIn("oracle_strategy:too_short", lifecycle.mark_contract_ready(self.conn, cid))

    def test_placeholder_list_entries_are_rejected(self):
        cid = self._contract(
            "Materialise a causal split without leaking the holdout.",
            forbidden_leaks='["TBD", "n/a"]',
        )
        self.assertIn("forbidden_leaks:placeholder", lifecycle.mark_contract_ready(self.conn, cid))

    def test_forbidden_leaks_cannot_equal_allowed_inputs(self):
        cid = self._contract(
            "Materialise a causal split without leaking the holdout.",
            allowed_inputs='["the hidden oracle"]',
            forbidden_leaks='["the hidden oracle"]',
        )
        self.assertIn(
            "forbidden_leaks:same_as_allowed_inputs",
            lifecycle.mark_contract_ready(self.conn, cid),
        )

    def test_infra_requirements_may_be_terse(self):
        cid = self._contract(
            "Materialise a causal split without leaking the holdout.",
            infra_requirements="stdlib Python.",
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, cid), [])

    def test_a_rejected_contract_cannot_be_scaffolded(self):
        cid = self._contract(
            "Materialise a causal split without leaking the holdout.",
            hidden_principle="tbd",
        )
        self.assertTrue(lifecycle.mark_contract_ready(self.conn, cid))
        with self.assertRaises(lifecycle.LifecycleError):
            lifecycle.start_scaffold(self.conn, cid)


class TestRevisionMemory(unittest.TestCase):
    """Revision N must be able to see why revisions 1..N-1 failed."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.conn = db.connect(self.root / "t.db")
        self.seed_id, self.runs = make_corpus(self.conn)
        self.idea_id = db.add_idea(
            self.conn,
            self.runs["codex"],
            self.seed_id,
            {
                "title": "revisable",
                "statement": "Materialise a causal split without leaking the holdout partition.",
                "assumption_broken": "a",
            },
        )
        db.add_verdict(self.conn, self.idea_id, "accept", "ACCEPT")
        self.contract_id = lifecycle.create_contract(
            self.conn, self.idea_id, **CONTRACT_FIXTURE
        )
        self.assertEqual(lifecycle.mark_contract_ready(self.conn, self.contract_id), [])

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _failed_revision(self, status: str = "too_easy") -> int:
        scaffold_id, _ = lifecycle.start_scaffold(self.conn, self.contract_id)
        lifecycle.record_submission(
            self.conn,
            scaffold_id,
            platform="smoldata",
            external_id="causal-split",
            status=status,
            result={
                "watch": {
                    "task": {
                        "validationDetails": [
                            {
                                "label": "Metacode or Opus pass/fail balance",
                                "status": "failed",
                                "detail": "Too easy — avocado passed all 5",
                            }
                        ]
                    }
                }
            },
        )
        return scaffold_id

    def test_first_revision_has_no_history(self):
        self.assertEqual(lifecycle.prior_attempts(self.conn, self.contract_id), [])
        _, root = lifecycle.start_scaffold(self.conn, self.contract_id)
        text = (root / "PRIOR_ATTEMPTS.md").read_text()
        self.assertIn("No prior attempts", text)

    def test_second_revision_sees_the_first_failure(self):
        self._failed_revision()
        _, root = lifecycle.start_scaffold(self.conn, self.contract_id)

        text = (root / "PRIOR_ATTEMPTS.md").read_text()
        self.assertIn("Revision 1", text)
        self.assertIn("too_easy", text)
        self.assertIn("reduce_leakage_or_add_hidden_state", text)
        self.assertIn("avocado passed all 5", text)

    def test_third_revision_sees_both(self):
        self._failed_revision()
        self._failed_revision()
        attempts = lifecycle.prior_attempts(self.conn, self.contract_id)
        self.assertEqual([a["revision"] for a in attempts], [1, 2])

        _, root = lifecycle.start_scaffold(self.conn, self.contract_id)
        text = (root / "PRIOR_ATTEMPTS.md").read_text()
        self.assertIn("Revision 1", text)
        self.assertIn("Revision 2", text)
        self.assertIn("2 prior attempt(s)", text)

    def test_history_excludes_the_revision_being_created(self):
        self._failed_revision()
        _, root = lifecycle.start_scaffold(self.conn, self.contract_id)
        self.assertNotIn("Revision 2", (root / "PRIOR_ATTEMPTS.md").read_text())

    def test_prior_attempts_reach_the_builder_prompt(self):
        self._failed_revision()
        scaffold_id, root = lifecycle.start_scaffold(
            self.conn, self.contract_id, builder="codex"
        )
        prompt_file = self.root / "build_prompt.md"
        prompt_file.write_text("Build in {{TASK_DIR}}\n\n{{PRIOR_ATTEMPTS}}\n")

        completed = subprocess.CompletedProcess(["codex"], 0, stdout="", stderr="")
        with mock.patch.object(lifecycle.subprocess, "run", return_value=completed):
            lifecycle.run_scaffold_worker(self.conn, scaffold_id, prompt_file, timeout=30)

        rendered = (root / "RUN_PROMPT.md").read_text()
        self.assertIn("too_easy", rendered)
        self.assertIn("reduce_leakage_or_add_hidden_state", rendered)

    def test_revision_refuses_a_prompt_that_ignores_history(self):
        self._failed_revision()
        scaffold_id, _ = lifecycle.start_scaffold(
            self.conn, self.contract_id, builder="codex"
        )
        blind = self.root / "blind_prompt.md"
        blind.write_text("Build in {{TASK_DIR}}\n")

        with mock.patch.object(lifecycle.subprocess, "run") as run:
            with self.assertRaises(lifecycle.LifecycleError) as caught:
                lifecycle.run_scaffold_worker(self.conn, scaffold_id, blind, timeout=30)
        run.assert_not_called()
        self.assertIn("PRIOR_ATTEMPTS", str(caught.exception))

    def test_first_revision_may_ignore_history(self):
        scaffold_id, _ = lifecycle.start_scaffold(
            self.conn, self.contract_id, builder="codex"
        )
        blind = self.root / "blind_prompt.md"
        blind.write_text("Build in {{TASK_DIR}}\n")
        completed = subprocess.CompletedProcess(["codex"], 0, stdout="", stderr="")
        with mock.patch.object(lifecycle.subprocess, "run", return_value=completed):
            rc = lifecycle.run_scaffold_worker(self.conn, scaffold_id, blind, timeout=30)
        self.assertEqual(rc, 0)

    def test_prior_attempts_file_does_not_break_isolation(self):
        self._failed_revision()
        _, root = lifecycle.start_scaffold(self.conn, self.contract_id)
        lifecycle.assert_scaffold_isolated(root)  # must not raise

    def test_human_learning_notes_reach_the_next_revision(self):
        scaffold_id = self._failed_revision()
        submission_id = self.conn.execute(
            "SELECT id FROM submissions WHERE scaffold_run_id = ?", (scaffold_id,)
        ).fetchone()["id"]
        lifecycle.record_learning(
            self.conn,
            scope_type="submission",
            scope_id=submission_id,
            label="human-note",
            detail="the public fixtures already contain the holdout split",
        )
        _, root = lifecycle.start_scaffold(self.conn, self.contract_id)
        self.assertIn(
            "public fixtures already contain the holdout split",
            (root / "PRIOR_ATTEMPTS.md").read_text(),
        )

    def test_revision_guidance_is_omitted_until_written(self):
        # `prompts/` is human-authored; the harness stays silent when the file is absent
        # or still a placeholder, rather than inventing guidance.
        missing = self.root / "nope.md"
        with mock.patch.object(lifecycle.db, "REPO_ROOT", missing):
            self.assertEqual(lifecycle.revision_guidance(), "")

        fake_repo = self.root / "repo"
        (fake_repo / "prompts").mkdir(parents=True)
        guidance = fake_repo / "prompts" / "revision_guidance.md"
        guidance.write_text("<!-- TODO: write this -->\n")
        with mock.patch.object(lifecycle.db, "REPO_ROOT", fake_repo):
            self.assertEqual(lifecycle.revision_guidance(), "")
            guidance.write_text("On too_easy: add hidden state.\n")
            self.assertIn("add hidden state", lifecycle.revision_guidance())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from audit_core import CHECKPOINT_SIZE, MODEL_WEIGHTS, assert_safe_report, build_report, normalize_draws, walk_forward


def synthetic_draws(total: int = 70) -> list[dict]:
    draws = []
    for index in range(total):
        start = (index * 7) % 25
        numbers = sorted({((start + offset * 3) % 25) + 1 for offset in range(15)})
        draws.append({"concurso": 4000 + index, "data": f"{(index % 28) + 1:02d}/01/2026", "dezenas": numbers})
    return draws


class AuditCoreTests(unittest.TestCase):
    def test_normalization_and_temporal_guard(self):
        rows = walk_forward(synthetic_draws(45), min_training=30)
        self.assertTrue(rows)
        self.assertTrue(all(int(row["training_through"]) < int(row["contest"]) for row in rows))
        self.assertEqual(set(row["model"] for row in rows), set(MODEL_WEIGHTS))

    def test_checkpoints_close_only_every_five(self):
        report = build_report(synthetic_draws(47), min_training=30)
        self.assertEqual(report["completed_checkpoint_contests"] % CHECKPOINT_SIZE, 0)
        self.assertEqual(len(report["checkpoints"]), report["completed_checkpoint_contests"] // CHECKPOINT_SIZE)
        self.assertEqual(report["pending_until_next_checkpoint"], 3)

    def test_public_report_has_no_actionable_fields(self):
        report = build_report(synthetic_draws(70), min_training=30)
        assert_safe_report(report)
        serialized = str(report).lower()
        for forbidden in ("ranking", "dezenas", "jogos", "proximo_concurso"):
            self.assertNotIn(forbidden, serialized)

    def test_duplicate_contest_is_rejected(self):
        draws = synthetic_draws(35)
        draws.append(draws[-1])
        with self.assertRaises(ValueError):
            normalize_draws(draws)


if __name__ == "__main__":
    unittest.main()

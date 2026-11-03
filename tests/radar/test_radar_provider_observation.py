from __future__ import annotations

import sys
from pathlib import Path
from unittest import TestCase

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from radar_provider_observation import compare_provider_observation


class ProviderObservationTests(TestCase):
    def setUp(self) -> None:
        self.contract = {
            "provider": {
                "readback_at": "2026-09-09",
                "unapplied_source_migrations": [
                    "20260905230823_radar_oidc_replay_guard_v1.sql",
                    "20260906154101_radar_projection_journal_v1.sql",
                ],
                "edge_function": {
                    "slug": "github-bus-ingest",
                    "live_version": 3,
                    "live_status": "ACTIVE",
                    "verify_jwt": True,
                },
            },
            "projection_source": {"status": "ANCHOR_E_FROZEN_QUALIFIED_SOURCE_ONLY_NOT_DEPLOYED"},
        }
        self.observation = {
            "source_kind": "SUPABASE_EDGE_METADATA",
            "observed_at": "2026-11-03T01:00:00Z",
            "edge_function": {
                "slug": "github-bus-ingest",
                "version": 7,
                "status": "ACTIVE",
                "verify_jwt": False,
            },
            "migrations": [
                {"version": "20260921202217", "name": "20260905230823_radar_oidc_replay_guard_v1"},
                {"version": "20260921202226", "name": "20260906154101_radar_projection_journal_v1"},
            ],
        }

    def test_live_v7_must_not_be_silently_equated_to_historical_v3(self) -> None:
        result = compare_provider_observation(self.contract, self.observation)
        self.assertEqual(result["status"], "HOLD")
        self.assertTrue(result["snapshot_drift"])
        self.assertEqual(result["changed_fields"], ["version", "verify_jwt", "unapplied_source_migrations"])
        self.assertIn("DELIVERY_UNVERIFIED", result["reasons"])

    def test_matching_metadata_still_does_not_qualify_delivery(self) -> None:
        self.observation["edge_function"]["version"] = 3
        self.observation["edge_function"]["verify_jwt"] = True
        self.observation["migrations"] = []
        result = compare_provider_observation(self.contract, self.observation)
        self.assertFalse(result["snapshot_drift"])
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["reasons"], ["SOURCE_CUTOVER_HOLD", "DELIVERY_UNVERIFIED"])

    def test_unread_migrations_remain_unknown_not_missing(self) -> None:
        self.observation.pop("migrations")
        result = compare_provider_observation(self.contract, self.observation)
        self.assertIn("MIGRATIONS_UNOBSERVED", result["reasons"])
        self.assertNotIn("unapplied_source_migrations", result["changed_fields"])

    def test_malformed_version_or_auth_mode_fails_closed(self) -> None:
        for field, value in (("version", True), ("verify_jwt", "false"), ("slug", "")):
            altered = {**self.observation, "edge_function": dict(self.observation["edge_function"])}
            altered["edge_function"][field] = value
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "INVALID_PROVIDER_OBSERVATION"):
                    compare_provider_observation(self.contract, altered)

    def test_untrusted_payload_cannot_assert_qualification(self) -> None:
        self.observation["qualified"] = True
        self.observation["delivery_receipt"] = {"status": "PASS"}
        result = compare_provider_observation(self.contract, self.observation)
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("DELIVERY_UNVERIFIED", result["reasons"])

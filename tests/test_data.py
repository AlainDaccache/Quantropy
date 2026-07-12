"""Tests for the data layer: PIT semantics, snapshot immutability, universe membership.

All offline (P5) — the stooq provider's network path is exercised separately/manually;
its symbol mapping is tested here.
"""

import pandas as pd
import pytest

from quantropy.data import AssetClass, Instrument, PointInTimeStore, SnapshotStore, Universe
from quantropy.data.providers.stooq import stooq_symbol


class TestInstrument:
    def test_equity_defaults(self):
        spy = Instrument("SPY", AssetClass.ETF)
        assert spy.multiplier == 1.0 and spy.currency == "USD"

    def test_future_specs(self):
        mes = Instrument("MES", AssetClass.FUTURE, multiplier=5.0, tick_size=0.25)
        assert mes.multiplier == 5.0

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"symbol": ""},
            {"symbol": "X", "multiplier": 0},
            {"symbol": "X", "tick_size": -0.01},
        ],
    )
    def test_invalid_specs_raise(self, kwargs):
        with pytest.raises(ValueError):
            Instrument(asset_class=AssetClass.EQUITY, **{"symbol": "X", **kwargs})


class TestPointInTime:
    """The restatement scenario — the canonical 'why backtests lie' case."""

    @pytest.fixture
    def store(self):
        pit = PointInTimeStore()
        # Q4-2023 EPS first reported 2024-02-01 as 2.10; restated 2024-03-15 to 1.80
        pit.record("ACME", "eps", "2023-12-31", "2024-02-01", 2.10)
        pit.record("ACME", "eps", "2023-12-31", "2024-03-15", 1.80)
        # Q1-2024 EPS reported 2024-05-01
        pit.record("ACME", "eps", "2024-03-31", "2024-05-01", 0.95)
        return pit

    def test_before_first_report_sees_nothing(self, store):
        assert store.as_of("2024-01-15").empty

    def test_between_report_and_restatement_sees_original(self, store):
        view = store.as_of("2024-02-10")
        assert len(view) == 1
        assert view.loc[0, "value"] == pytest.approx(2.10)  # NOT the restated 1.80

    def test_after_restatement_sees_restated(self, store):
        view = store.as_of("2024-04-01")
        assert view.loc[view["event_date"] == "2023-12-31", "value"].item() == pytest.approx(1.80)

    def test_future_periods_are_invisible(self, store):
        view = store.as_of("2024-04-01")
        assert "2024-03-31" not in set(view["event_date"].dt.strftime("%Y-%m-%d"))

    def test_latest_applies_all_restatements(self, store):
        latest = store.latest()
        assert len(latest) == 2  # both periods, restated values
        q4 = latest.loc[latest["event_date"] == "2023-12-31", "value"].item()
        assert q4 == pytest.approx(1.80)

    def test_same_day_correction_supersedes(self):
        pit = PointInTimeStore()
        pit.record("ACME", "eps", "2023-12-31", "2024-02-01", 2.10)
        pit.record("ACME", "eps", "2023-12-31", "2024-02-01", 2.15)  # same-day correction
        assert pit.as_of("2024-02-01").loc[0, "value"] == pytest.approx(2.15)

    def test_knowledge_before_event_rejected(self):
        pit = PointInTimeStore()
        with pytest.raises(ValueError):
            pit.record("ACME", "eps", "2023-12-31", "2023-11-30", 2.10)  # clairvoyance

    def test_roundtrip_through_frame(self, store):
        clone = PointInTimeStore.from_frame(store.to_frame())
        pd.testing.assert_frame_equal(
            clone.as_of("2024-06-01"), store.as_of("2024-06-01")
        )


class TestSnapshotStore:
    @pytest.fixture
    def frames(self):
        idx = pd.date_range("2024-01-01", periods=5, freq="B", name="Date")
        return {"prices": pd.DataFrame({"SPY": [470.0, 471.5, 469.8, 472.1, 473.0]}, index=idx)}

    def test_roundtrip(self, tmp_path, frames):
        store = SnapshotStore(tmp_path)
        store.write("snap-1", frames, note="test")
        out = store.read("snap-1", "prices")
        # check_freq=False: Parquet stores values, not pandas' index `freq` hint —
        # a known, benign roundtrip caveat (values and dtypes must still match exactly)
        pd.testing.assert_frame_equal(out, frames["prices"], check_freq=False)

    def test_snapshots_are_immutable(self, tmp_path, frames):
        store = SnapshotStore(tmp_path)
        store.write("snap-1", frames)
        with pytest.raises(FileExistsError):
            store.write("snap-1", frames)

    def test_missing_dataset_raises(self, tmp_path, frames):
        store = SnapshotStore(tmp_path)
        store.write("snap-1", frames)
        with pytest.raises(FileNotFoundError):
            store.read("snap-1", "nope")

    def test_manifest_and_listing(self, tmp_path, frames):
        store = SnapshotStore(tmp_path)
        store.write("b-snap", frames)
        store.write("a-snap", frames)
        assert store.snapshots() == ["a-snap", "b-snap"]
        assert store.manifest("a-snap")["datasets"]["prices"]["rows"] == 5

    @pytest.mark.parametrize("bad_id", ["", "a/b", "..", "a\\b"])
    def test_path_traversal_ids_rejected(self, tmp_path, frames, bad_id):
        with pytest.raises(ValueError):
            SnapshotStore(tmp_path).write(bad_id, frames)


class TestUniverse:
    @pytest.fixture
    def universe(self):
        return Universe(
            pd.DataFrame(
                {
                    "symbol": ["AAA", "BBB", "CCC", "BBB"],
                    "start": ["2010-01-01", "2010-01-01", "2015-06-01", "2022-01-01"],
                    # BBB delisted 2018, re-included 2022; CCC delisted 2020
                    "end": [None, "2018-03-01", "2020-09-15", None],
                }
            )
        )

    def test_members_include_the_later_dead(self, universe):
        # In 2016, BBB and CCC were alive — a survivorship-free backtest must see them
        assert universe.members("2016-01-04") == ["AAA", "BBB", "CCC"]

    def test_members_after_delisting(self, universe):
        assert universe.members("2021-01-04") == ["AAA"]

    def test_reinclusion(self, universe):
        assert universe.members("2023-01-04") == ["AAA", "BBB"]

    def test_all_symbols_is_the_full_load_set(self, universe):
        assert universe.all_symbols() == ["AAA", "BBB", "CCC"]

    def test_invalid_span_rejected(self):
        with pytest.raises(ValueError):
            Universe(
                pd.DataFrame(
                    {"symbol": ["X"], "start": ["2020-01-01"], "end": ["2019-01-01"]}
                )
            )


class TestStooqSymbolMapping:
    def test_us_suffix_added(self):
        assert stooq_symbol("AAPL") == "aapl.us"

    def test_existing_suffix_kept(self):
        assert stooq_symbol("spy.us") == "spy.us"

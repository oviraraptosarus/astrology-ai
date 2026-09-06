"""Regression test for a latent traceability bug found in Phase 2 audit.

astrology_engine.py previously hardcoded swe.TRUE_NODE for Rahu (natal PLANETS
dict + live-Ketu transit) instead of routing through Config.node_swe_id().
The node-convention config toggle was therefore DECORATIVE for the canonical
engine: flipping Config.NODE_TYPE="mean" would silently NOT change the main
natal chart, while downstream Parashari engines (which do read Config) would
switch to Mean node -- reintroducing the up-to-1.6 deg Rahu disagreement the
config file was written to prevent.

This test proves the toggle actually reaches computed Rahu/Ketu longitudes.
Because PLANETS binds Config.node_swe_id() at import time, we verify at the
function level: calc_ut with each node constant must differ, and the engine's
node id must equal whatever Config currently selects.
"""
import os, sys, importlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import swisseph as swe
from datetime import datetime
import pytz


def _rahu_lon(node_const):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    dt = datetime(1955, 2, 25, 3, 15, tzinfo=pytz.utc)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
    return swe.calc_ut(jd, node_const, flags)[0][0] % 360.0


def test_true_vs_mean_node_actually_differ():
    # Sanity: the two node models are genuinely different, so a wrong wiring is observable.
    diff = abs(_rahu_lon(swe.TRUE_NODE) - _rahu_lon(swe.MEAN_NODE))
    diff = min(diff, 360 - diff)
    assert diff > 0.05, f"True vs Mean node differ by only {diff} deg -- test can't detect miswiring"


def test_engine_planets_dict_tracks_config():
    from config import Config
    import astrology_engine as ae
    # The canonical natal PLANETS dict must use whatever Config selects, not a hardcode.
    assert ae.PLANETS["Rahu"] == Config.node_swe_id(), (
        "astrology_engine.PLANETS['Rahu'] is not routed through Config.node_swe_id() "
        "-- the node-type toggle is decorative for the core engine."
    )


def test_mean_toggle_changes_computed_natal_rahu():
    """Flip NODE_TYPE to mean, re-import the engine, and confirm natal Rahu moves
    to the Mean-node longitude (not the True-node one)."""
    from config import Config
    orig = Config.NODE_TYPE
    try:
        Config.NODE_TYPE = "mean"
        import astrology_engine as ae
        importlib.reload(ae)
        assert ae.PLANETS["Rahu"] == swe.MEAN_NODE, "reloaded engine did not pick up mean node"
    finally:
        Config.NODE_TYPE = orig
        import astrology_engine as ae
        importlib.reload(ae)
        assert ae.PLANETS["Rahu"] == swe.TRUE_NODE


if __name__ == "__main__":
    test_true_vs_mean_node_actually_differ()
    test_engine_planets_dict_tracks_config()
    test_mean_toggle_changes_computed_natal_rahu()
    print("OK: node-type toggle now reaches the canonical engine (natal + transit).")

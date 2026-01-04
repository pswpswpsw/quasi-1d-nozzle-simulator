"""
Simple test script to verify the Streamlit app components work correctly.
Run this with: uv run python test_app.py
"""
from nozzle import Nozzle
from geometry import get_A
from rocketisp.geometry import Geometry
import numpy as np

def test_nozzle_simulation():
    """Test that the nozzle simulation works for all flow regimes."""
    print("Testing nozzle simulation...")
    
    # Setup geometry
    G = Geometry(Rthrt=5.1527, CR=3.0, eps=77.5, LnozInp=121,
                 RupThroat=1.0, RdwnThroat=0.392, RchmConv=1.73921, cham_conv_deg=25.42,
                 LchmOvrDt=2.4842/2)
    A, xmin, xmax = get_A(G)
    
    # Create nozzle
    nozzle = Nozzle(A, xmin=xmin, xmax=xmax, gamma=1.4, R=287)
    
    print(f"Critical pressure ratios:")
    print(f"  Choked: {nozzle.crit_p_ratio_1:.5f}")
    print(f"  Normal Shock: {nozzle.crit_p_ratio_2:.5f}")
    print(f"  Shock Free: {nozzle.crit_p_ratio_3:.5f}")
    
    # Test different pressure ratios covering all regimes
    test_cases = [
        (0.94, "Subsonic Throat"),
        (0.05, "Normal Shock Inside Expansion"),
        (0.015, "Oblique Shock at Exit"),
        (0.00036, "Expansion Fan at Exit"),
        (0.0001, "Expansion Fan at Exit (low)"),
    ]
    
    print("\nTesting flow profiles...")
    for p_ratio, expected_regime in test_cases:
        try:
            fig = nozzle.plot_flow_profile(p_ratio)
            assert fig is not None, f"Figure should not be None for p_ratio={p_ratio}"
            print(f"  ✓ p_ratio={p_ratio:.4f} ({expected_regime}) - PASSED")
        except Exception as e:
            print(f"  ✗ p_ratio={p_ratio:.4f} ({expected_regime}) - FAILED: {e}")
            raise
    
    print("\nAll tests passed! ✓")

if __name__ == "__main__":
    test_nozzle_simulation()


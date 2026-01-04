"""
Simple test script to verify the Streamlit app components work correctly.
Run this with: uv run python test_app.py
"""
from nozzle import Nozzle
from geometry import get_A, get_parabolic_A
from rocketisp.geometry import Geometry
import numpy as np

def test_ssme_geometry():
    """Test SSME geometry simulation."""
    print("Testing SSME geometry...")
    
    # Setup SSME geometry
    G = Geometry(Rthrt=5.1527, CR=3.0, eps=77.5, LnozInp=121,
                 RupThroat=1.0, RdwnThroat=0.392, RchmConv=1.73921, cham_conv_deg=25.42,
                 LchmOvrDt=2.4842/2)
    A, xmin, xmax = get_A(G)
    
    # Create nozzle
    nozzle = Nozzle(A, xmin=xmin, xmax=xmax, gamma=1.4, R=287)
    
    print(f"  Critical pressure ratios:")
    print(f"    Choked: {nozzle.crit_p_ratio_1:.5f}")
    print(f"    Normal Shock: {nozzle.crit_p_ratio_2:.5f}")
    print(f"    Shock Free: {nozzle.crit_p_ratio_3:.5f}")
    
    # Test different pressure ratios covering all regimes
    test_cases = [
        (0.94, "Subsonic Throat"),
        (0.05, "Normal Shock Inside Expansion"),
        (0.015, "Oblique Shock at Exit"),
        (0.00036, "Expansion Fan at Exit"),
        (0.0001, "Expansion Fan at Exit (low)"),
    ]
    
    print("  Testing flow profiles...")
    for p_ratio, expected_regime in test_cases:
        try:
            fig = nozzle.plot_flow_profile_plotly(p_ratio)
            assert fig is not None, f"Figure should not be None for p_ratio={p_ratio}"
            print(f"    ✓ p_ratio={p_ratio:.4f} ({expected_regime}) - PASSED")
        except Exception as e:
            print(f"    ✗ p_ratio={p_ratio:.4f} ({expected_regime}) - FAILED: {e}")
            raise
    
    print("  ✓ SSME geometry tests passed!\n")
    return nozzle

def test_parabolic_geometry():
    """Test Simple Parabolic geometry simulation."""
    print("Testing Simple Parabolic geometry...")
    
    # Setup parabolic geometry (default values from notebook)
    A, xmin, xmax = get_parabolic_A(a=1.5, b=0.6, c=0.25, xmin=0.0, xmax=1.0)
    
    # Create nozzle
    nozzle = Nozzle(A, xmin=xmin, xmax=xmax, gamma=1.4, R=287)
    
    print(f"  Critical pressure ratios:")
    print(f"    Choked: {nozzle.crit_p_ratio_1:.5f}")
    print(f"    Normal Shock: {nozzle.crit_p_ratio_2:.5f}")
    print(f"    Shock Free: {nozzle.crit_p_ratio_3:.5f}")
    
    # Test different pressure ratios
    test_cases = [
        (0.972, "Subsonic Throat"),
        (0.8, "Normal Shock Inside Expansion"),
        (0.02, "Oblique Shock at Exit"),
        (0.00037, "Expansion Fan at Exit"),
    ]
    
    print("  Testing flow profiles...")
    for p_ratio, expected_regime in test_cases:
        try:
            fig = nozzle.plot_flow_profile_plotly(p_ratio)
            assert fig is not None, f"Figure should not be None for p_ratio={p_ratio}"
            print(f"    ✓ p_ratio={p_ratio:.4f} ({expected_regime}) - PASSED")
        except Exception as e:
            print(f"    ✗ p_ratio={p_ratio:.4f} ({expected_regime}) - FAILED: {e}")
            raise
    
    print("  ✓ Parabolic geometry tests passed!\n")
    return nozzle

def test_geometry_functions():
    """Test geometry helper functions."""
    print("Testing geometry functions...")
    
    # Test get_parabolic_A
    A, xmin, xmax = get_parabolic_A(a=1.5, b=0.6, c=0.25, xmin=0.0, xmax=1.0)
    assert callable(A), "A should be a callable function"
    assert xmin == 0.0, f"xmin should be 0.0, got {xmin}"
    assert xmax == 1.0, f"xmax should be 1.0, got {xmax}"
    
    # Test area function at throat location
    A_throat = A(0.6)  # Should be minimum at b=0.6
    assert abs(A_throat - 0.25) < 1e-6, f"A(0.6) should be ~0.25, got {A_throat}"
    
    # Test area function at boundaries
    A_min = A(xmin)
    A_max = A(xmax)
    assert A_min > 0, f"A(xmin) should be positive, got {A_min}"
    assert A_max > 0, f"A(xmax) should be positive, got {A_max}"
    
    print("  ✓ Geometry function tests passed!\n")

def test_nozzle_simulation():
    """Run all tests."""
    print("=" * 60)
    print("Running Nozzle Simulation Tests")
    print("=" * 60 + "\n")
    
    try:
        test_geometry_functions()
        test_ssme_geometry()
        test_parabolic_geometry()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print("=" * 60)
        print(f"Tests failed: {e}")
        print("=" * 60)
        raise

if __name__ == "__main__":
    test_nozzle_simulation()

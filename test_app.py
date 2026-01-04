"""
Comprehensive unit tests for the Quasi-1D Nozzle Flow Simulator.
Run with: uv run pytest test_app.py -v
Or: uv run python test_app.py
"""
import unittest
import numpy as np
from nozzle import Nozzle
from geometry import get_A, get_parabolic_A
from rocketisp.geometry import Geometry


class TestNozzleGamma(unittest.TestCase):
    """Test nozzle behavior with different gamma values."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use parabolic geometry for consistent testing
        self.A, self.xmin, self.xmax = get_parabolic_A(
            a=1.5, b=0.6, c=0.25, xmin=0.0, xmax=1.0
        )
        self.R = 287  # Standard air gas constant
    
    def test_gamma_affects_critical_pressures(self):
        """Test that changing gamma affects critical pressure ratios."""
        print("\nTesting gamma effects on critical pressure ratios...")
        
        gamma_values = [1.2, 1.4, 1.6, 1.8]
        crit_ratios = {}
        
        for gamma in gamma_values:
            nozzle = Nozzle(self.A, self.xmin, self.xmax, gamma=gamma, R=self.R)
            crit_ratios[gamma] = {
                'crit_1': nozzle.crit_p_ratio_1,
                'crit_2': nozzle.crit_p_ratio_2,
                'crit_3': nozzle.crit_p_ratio_3
            }
            print(f"  γ={gamma}: crit_1={crit_ratios[gamma]['crit_1']:.5f}, "
                  f"crit_2={crit_ratios[gamma]['crit_2']:.5f}, "
                  f"crit_3={crit_ratios[gamma]['crit_3']:.5f}")
        
        # Verify that critical ratios are different for different gamma values
        self.assertNotAlmostEqual(
            crit_ratios[1.2]['crit_1'], 
            crit_ratios[1.4]['crit_1'], 
            places=5,
            msg="Critical ratio 1 should differ for different gamma"
        )
        self.assertNotAlmostEqual(
            crit_ratios[1.4]['crit_2'], 
            crit_ratios[1.6]['crit_2'], 
            places=5,
            msg="Critical ratio 2 should differ for different gamma"
        )
    
    def test_gamma_range_validation(self):
        """Test nozzle creation with various gamma values in valid range."""
        print("\nTesting gamma range validation...")
        
        valid_gammas = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
        
        for gamma in valid_gammas:
            try:
                nozzle = Nozzle(self.A, self.xmin, self.xmax, gamma=gamma, R=self.R)
                self.assertIsNotNone(nozzle, f"Nozzle should be created with gamma={gamma}")
                self.assertEqual(nozzle.g, gamma, f"Stored gamma should match input gamma={gamma}")
                print(f"  ✓ gamma={gamma} - PASSED")
            except Exception as e:
                self.fail(f"Failed to create nozzle with gamma={gamma}: {e}")
    
    def test_gamma_consistency(self):
        """Test that gamma is stored and used consistently."""
        print("\nTesting gamma consistency...")
        
        test_gamma = 1.3
        nozzle = Nozzle(self.A, self.xmin, self.xmax, gamma=test_gamma, R=self.R)
        
        self.assertEqual(nozzle.g, test_gamma, "Stored gamma should match input")
        self.assertEqual(nozzle.R, self.R, "Stored R should match input")
        
        # Test that critical ratios are computed using the correct gamma
        # For higher gamma, critical ratios should generally be different
        nozzle_high_gamma = Nozzle(self.A, self.xmin, self.xmax, gamma=1.6, R=self.R)
        
        self.assertNotAlmostEqual(
            nozzle.crit_p_ratio_1,
            nozzle_high_gamma.crit_p_ratio_1,
            places=5,
            msg="Critical ratios should differ with different gamma"
        )
        print("  ✓ Gamma consistency - PASSED")
    
    def test_flow_profile_with_different_gamma(self):
        """Test that flow profiles can be generated with different gamma values."""
        print("\nTesting flow profiles with different gamma values...")
        
        gamma_values = [1.2, 1.4, 1.6]
        p_ratio = 0.8
        
        for gamma in gamma_values:
            nozzle = Nozzle(self.A, self.xmin, self.xmax, gamma=gamma, R=self.R)
            try:
                fig = nozzle.plot_flow_profile_plotly(p_ratio)
                self.assertIsNotNone(fig, f"Figure should be created for gamma={gamma}")
                print(f"  ✓ gamma={gamma} flow profile - PASSED")
            except Exception as e:
                self.fail(f"Failed to create flow profile for gamma={gamma}: {e}")


class TestNozzleGasConstant(unittest.TestCase):
    """Test nozzle behavior with different gas constant values."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.A, self.xmin, self.xmax = get_parabolic_A(
            a=1.5, b=0.6, c=0.25, xmin=0.0, xmax=1.0
        )
        self.gamma = 1.4
    
    def test_R_storage(self):
        """Test that R is stored correctly."""
        print("\nTesting R (gas constant) storage...")
        
        R_values = [200, 250, 287, 300, 400]
        
        for R in R_values:
            nozzle = Nozzle(self.A, self.xmin, self.xmax, gamma=self.gamma, R=R)
            self.assertEqual(nozzle.R, R, f"Stored R should match input R={R}")
            print(f"  ✓ R={R} - PASSED")
    
    def test_R_affects_entropy_calculations(self):
        """Test that R affects entropy jump calculations."""
        print("\nTesting R effects on entropy calculations...")
        
        R_values = [200, 287, 400]
        M1 = 2.0
        
        entropy_jumps = {}
        for R in R_values:
            entropy_jump = Nozzle.entropy_jump_normal_shock(M1, self.gamma, R)
            entropy_jumps[R] = entropy_jump
            print(f"  R={R}: entropy_jump={entropy_jump:.5f}")
        
        # Entropy jump should be different for different R values
        self.assertNotAlmostEqual(
            entropy_jumps[200],
            entropy_jumps[287],
            places=5,
            msg="Entropy jump should differ for different R"
        )


class TestNozzleGeometry(unittest.TestCase):
    """Test nozzle geometry functionality."""
    
    def test_ssme_geometry(self):
        """Test SSME geometry simulation."""
        print("\nTesting SSME geometry...")
        
        G = Geometry(
            Rthrt=5.1527, CR=3.0, eps=77.5, LnozInp=121,
            RupThroat=1.0, RdwnThroat=0.392, RchmConv=1.73921, cham_conv_deg=25.42,
            LchmOvrDt=2.4842/2
        )
        A, xmin, xmax = get_A(G)
        
        # Test with different gamma values
        for gamma in [1.2, 1.4, 1.6]:
            nozzle = Nozzle(A, xmin=xmin, xmax=xmax, gamma=gamma, R=287)
            
            self.assertIsNotNone(nozzle.crit_p_ratio_1, "crit_p_ratio_1 should be computed")
            self.assertIsNotNone(nozzle.crit_p_ratio_2, "crit_p_ratio_2 should be computed")
            self.assertIsNotNone(nozzle.crit_p_ratio_3, "crit_p_ratio_3 should be computed")
            
            # Critical ratios should be in order: crit_1 > crit_2 > crit_3
            self.assertGreater(
                nozzle.crit_p_ratio_1, 
                nozzle.crit_p_ratio_2,
                "crit_p_ratio_1 should be greater than crit_p_ratio_2"
            )
            self.assertGreater(
                nozzle.crit_p_ratio_2, 
                nozzle.crit_p_ratio_3,
                "crit_p_ratio_2 should be greater than crit_p_ratio_3"
            )
            
            print(f"  ✓ gamma={gamma}: crit_1={nozzle.crit_p_ratio_1:.5f}, "
                  f"crit_2={nozzle.crit_p_ratio_2:.5f}, "
                  f"crit_3={nozzle.crit_p_ratio_3:.5f}")
    
    def test_parabolic_geometry(self):
        """Test Simple Parabolic geometry simulation."""
        print("\nTesting Simple Parabolic geometry...")
        
        A, xmin, xmax = get_parabolic_A(a=1.5, b=0.6, c=0.25, xmin=0.0, xmax=1.0)
        
        # Test with different gamma values
        for gamma in [1.2, 1.4, 1.6]:
            nozzle = Nozzle(A, xmin=xmin, xmax=xmax, gamma=gamma, R=287)
            
            self.assertIsNotNone(nozzle.crit_p_ratio_1)
            self.assertIsNotNone(nozzle.crit_p_ratio_2)
            self.assertIsNotNone(nozzle.crit_p_ratio_3)
            
            print(f"  ✓ gamma={gamma}: crit_1={nozzle.crit_p_ratio_1:.5f}, "
                  f"crit_2={nozzle.crit_p_ratio_2:.5f}, "
                  f"crit_3={nozzle.crit_p_ratio_3:.5f}")
    
    def test_geometry_functions(self):
        """Test geometry helper functions."""
        print("\nTesting geometry functions...")
        
        # Test get_parabolic_A
        A, xmin, xmax = get_parabolic_A(a=1.5, b=0.6, c=0.25, xmin=0.0, xmax=1.0)
        self.assertTrue(callable(A), "A should be a callable function")
        self.assertEqual(xmin, 0.0, f"xmin should be 0.0, got {xmin}")
        self.assertEqual(xmax, 1.0, f"xmax should be 1.0, got {xmax}")
        
        # Test area function at throat location
        A_throat = A(0.6)  # Should be minimum at b=0.6
        self.assertAlmostEqual(A_throat, 0.25, places=6, 
                              msg=f"A(0.6) should be ~0.25, got {A_throat}")
        
        # Test area function at boundaries
        A_min = A(xmin)
        A_max = A(xmax)
        self.assertGreater(A_min, 0, f"A(xmin) should be positive, got {A_min}")
        self.assertGreater(A_max, 0, f"A(xmax) should be positive, got {A_max}")


class TestNozzleFlowRegimes(unittest.TestCase):
    """Test different flow regimes with various gamma values."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.A, self.xmin, self.xmax = get_parabolic_A(
            a=1.5, b=0.6, c=0.25, xmin=0.0, xmax=1.0
        )
    
    def test_flow_regimes_with_different_gamma(self):
        """Test all flow regimes work with different gamma values."""
        print("\nTesting flow regimes with different gamma values...")
        
        gamma_values = [1.2, 1.4, 1.6]
        
        for gamma in gamma_values:
            nozzle = Nozzle(self.A, self.xmin, self.xmax, gamma=gamma, R=287)
            
            # Test different pressure ratios covering all regimes
            test_cases = [
                (nozzle.crit_p_ratio_1 + 0.01, "Subsonic Throat"),
                ((nozzle.crit_p_ratio_1 + nozzle.crit_p_ratio_2) / 2, "Normal Shock Inside Expansion"),
                ((nozzle.crit_p_ratio_2 + nozzle.crit_p_ratio_3) / 2, "Oblique Shock at Exit"),
                (nozzle.crit_p_ratio_3 * 0.5, "Expansion Fan at Exit"),
            ]
            
            for p_ratio, regime_name in test_cases:
                try:
                    fig = nozzle.plot_flow_profile_plotly(p_ratio)
                    self.assertIsNotNone(fig, 
                        f"Figure should be created for gamma={gamma}, p_ratio={p_ratio:.4f}")
                except Exception as e:
                    self.fail(f"Failed for gamma={gamma}, p_ratio={p_ratio:.4f}, "
                             f"regime={regime_name}: {e}")
            
            print(f"  ✓ gamma={gamma} - all regimes PASSED")


class TestNozzleEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.A, self.xmin, self.xmax = get_parabolic_A(
            a=1.5, b=0.6, c=0.25, xmin=0.0, xmax=1.0
        )
    
    def test_extreme_gamma_values(self):
        """Test with extreme but valid gamma values."""
        print("\nTesting extreme gamma values...")
        
        extreme_gammas = [1.1, 1.95, 2.0]
        
        for gamma in extreme_gammas:
            try:
                nozzle = Nozzle(self.A, self.xmin, self.xmax, gamma=gamma, R=287)
                self.assertIsNotNone(nozzle)
                self.assertGreater(nozzle.crit_p_ratio_1, 0)
                self.assertLess(nozzle.crit_p_ratio_1, 1)
                print(f"  ✓ gamma={gamma} - PASSED")
            except Exception as e:
                self.fail(f"Failed with extreme gamma={gamma}: {e}")
    
    def test_critical_ratio_ordering(self):
        """Test that critical ratios are always in correct order."""
        print("\nTesting critical ratio ordering...")
        
        gamma_values = [1.2, 1.4, 1.6, 1.8]
        
        for gamma in gamma_values:
            nozzle = Nozzle(self.A, self.xmin, self.xmax, gamma=gamma, R=287)
            
            self.assertGreater(
                nozzle.crit_p_ratio_1, 
                nozzle.crit_p_ratio_2,
                f"For gamma={gamma}, crit_1 should be > crit_2"
            )
            self.assertGreater(
                nozzle.crit_p_ratio_2, 
                nozzle.crit_p_ratio_3,
                f"For gamma={gamma}, crit_2 should be > crit_3"
            )
            self.assertGreater(nozzle.crit_p_ratio_1, 0, "crit_1 should be positive")
            self.assertLess(nozzle.crit_p_ratio_3, 1, "crit_3 should be less than 1")
            
            print(f"  ✓ gamma={gamma}: {nozzle.crit_p_ratio_1:.5f} > "
                  f"{nozzle.crit_p_ratio_2:.5f} > {nozzle.crit_p_ratio_3:.5f}")


def run_all_tests():
    """Run all test suites."""
    print("=" * 70)
    print("Running Comprehensive Nozzle Simulator Tests")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNozzleGamma))
    suite.addTests(loader.loadTestsFromTestCase(TestNozzleGasConstant))
    suite.addTests(loader.loadTestsFromTestCase(TestNozzleGeometry))
    suite.addTests(loader.loadTestsFromTestCase(TestNozzleFlowRegimes))
    suite.addTests(loader.loadTestsFromTestCase(TestNozzleEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("All tests passed! ✓")
    else:
        print(f"Tests completed with {len(result.failures)} failures and "
              f"{len(result.errors)} errors")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

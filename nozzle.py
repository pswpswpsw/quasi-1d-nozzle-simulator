import numpy as np
import scipy
import scipy.optimize
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from typing import Tuple, Optional


class Nozzle(object):
    def __init__(self, Afunc, xmin, xmax, gamma, R) -> None:
        self.A = Afunc
        self.xmin = xmin 
        self.xmax = xmax 
        self.x = np.linspace(self.xmin,self.xmax,1000,endpoint=True)
        self.xeval = np.hstack([self.x,np.linspace(self.xmax, self.xmax + 1.5*(self.xmax-self.xmin),100)[1:]])
        self.area_array = self.A(self.x)
        self.area_exit = self.A(self.xmax)
        self.x_throat = scipy.optimize.fmin(self.A, x0 = 0.5*(xmin+xmax),disp=False)[0]
        self.area_throat = self.A(self.x_throat)
        self.area_array_before_throat = self.area_array[self.x<=self.x_throat]
        self.area_array_after_throat = self.area_array[self.x>=self.x_throat]
        self.g = gamma
        self.R = R

        # compute critical pressures 1-2-3
        # Critical case pressure ratio(s) for Case 1 
        ratio = self.get_exit_area_over_throat()
        m_crit_1 = self.solve_mach_number_from_area_ratio(ratio=ratio, gamma=gamma, is_subsonic=True)
        p0_p = (1+(gamma-1)/2*m_crit_1**2)**(gamma/(gamma-1))
        self.crit_p_ratio_1 = 1/p0_p        

        # Critical case pressure ratio(s) for Case 2 - normal shock at the exit
        m_crit_2 = self.solve_mach_number_from_area_ratio(ratio=ratio, gamma=gamma, is_subsonic=False)
        p0_pe = (1+(gamma-1)/2*m_crit_2**2)**(gamma/(gamma-1))
        # normal shock
        p_ns_ratio = 1 + 2*gamma/(gamma+1)*(m_crit_2**2-1)
        self.crit_p_ratio_2 = p_ns_ratio/p0_pe

        # Critical case pressure ratio(s) for Case 3 - shockfree
        self.crit_p_ratio_3 = 1/p0_pe

    @classmethod
    def area_mach_relation(cls, m, gamma):
        """area mach number relation"""
        A_over_A_throat = np.sqrt((2/(gamma+1)*(1+(gamma-1)/2*m**2))**((gamma+1)/(gamma-1))/m**2)
        return A_over_A_throat
    
    @classmethod
    def prandtl_meyer(cls, M, gamma):
        """Prandtl–Meyer function ν(M) in radians, valid for M>=1."""
        M = np.asarray(M)
        nu = np.zeros_like(M, dtype=float)
    
        sup = M >= 1.0
        Ms = M[sup]
        if Ms.size > 0:
            a = np.sqrt((gamma + 1.0) / (gamma - 1.0))
            b = np.sqrt((gamma - 1.0) / (gamma + 1.0) * (Ms**2 - 1.0))
            nu[sup] = a * np.arctan(b) - np.arctan(np.sqrt(Ms**2 - 1.0))
        return nu if nu.shape else float(nu)

    # entropy rise across a normal shock as a function of M1
    @classmethod
    def entropy_jump_normal_shock(cls, M1, gamma, R):
        cp = gamma * R / (gamma - 1.0)
        pressure_ratio = 1 + (2 * gamma / (gamma + 1.0)) * (M1**2 - 1.0)
        temp_ratio = pressure_ratio * (2 + (gamma - 1.0) * M1**2) / ((gamma + 1.0) * M1**2)
        return cp * np.log(temp_ratio) - R * np.log(pressure_ratio)

    def _calculate_flow_profile(self, pb_p0_ratio):
        """Compute M(x) and p/p0(x) for the given back-pressure ratio.

        Returns:
            (M_array, p_array, viz_data)
        """
        if pb_p0_ratio <= 0 or pb_p0_ratio > 1:
            raise ValueError(f"Pressure ratio must be between 0 and 1, got {pb_p0_ratio}")

        flag_draw_oshock = False 
        flag_draw_fan = False
        flag_draw_nshock = False  # Normal shock inside nozzle
        fan_alphas = None
        beta = None
        x_extended = None
        x_shock = None  # Location of normal shock

        if pb_p0_ratio > self.crit_p_ratio_1:
            # Subsonic throat
            p0_pb = 1.0 / pb_p0_ratio
            m_exit = np.sqrt((p0_pb ** ((self.g - 1) / (self.g)) - 1) * 2 / (self.g - 1))
            Ae_over_A_star = self.area_mach_relation(m_exit, self.g)
            A_over_A_star = self.area_array / self.area_exit * Ae_over_A_star

            M_array = np.zeros_like(self.xeval)
            p_array = np.zeros_like(self.xeval)
            
            for i in range(len(self.xeval)):
                if i < len(A_over_A_star):
                    ratio = A_over_A_star[i]
                    M_array[i] = self.solve_mach_number_from_area_ratio(ratio, self.g, is_subsonic=True)
                    p_array[i] = (1.0 + 0.5 * (self.g - 1.0) * M_array[i] ** 2) ** (-self.g / (self.g - 1.0))
                else:
                    M_array[i] = M_array[len(A_over_A_star) - 1]
                    p_array[i] = p_array[len(A_over_A_star) - 1]
            
        elif pb_p0_ratio > self.crit_p_ratio_2:
            # Sonic throat with normal shock inside expansion
            def M_and_p_given_x_shock(x_shock):
                last_index_before_shock = np.where(self.x < x_shock)[0][-1]
                M_array = np.zeros_like(self.xeval)
                p_array = np.zeros_like(self.xeval)
                A_over_A_star = self.area_array / self.area_throat 

                for i in range(len(self.xeval)):
                    if i < len(self.x):
                        ratio = A_over_A_star[i]
                        
                        if self.x[i] < self.x_throat:
                            M_array[i] = self.solve_mach_number_from_area_ratio(ratio, self.g, is_subsonic=True)
                            p_array[i] = 1 / (1 + (self.g - 1) / 2 * M_array[i] ** 2) ** (self.g / (self.g - 1))
                        elif self.x[i] < x_shock:
                            M_array[i] = self.solve_mach_number_from_area_ratio(ratio, self.g, is_subsonic=False)
                            p_array[i] = 1 / (1 + (self.g - 1) / 2 * M_array[i] ** 2) ** (self.g / (self.g - 1))
                        else:
                            M1 = M_array[last_index_before_shock]
                            delta_s = self.entropy_jump_normal_shock(M1, self.g, R=self.R)
                            p0_new_p0 = np.exp(-delta_s / self.R)
                            M2 = np.sqrt((1 + (self.g - 1) / 2 * M1 ** 2) / (self.g * M1 ** 2 - (self.g - 1) / 2))
    
                            A_over_A_shock = ratio * self.area_throat / self.get_area(self.x[last_index_before_shock + 1])
                            A_shock_over_A_star = self.area_mach_relation(M2, self.g)
                            A_over_A_star_tmp = A_over_A_shock * A_shock_over_A_star
    
                            M_array[i] = self.solve_mach_number_from_area_ratio(A_over_A_star_tmp, self.g, is_subsonic=True)
                            p_array[i] = p0_new_p0 * (1 + (self.g - 1) / 2 * M_array[i] ** 2) ** (-self.g / (self.g - 1))
                    else:
                        M_array[i] = M_array[len(self.x) - 1]
                        p_array[i] = p_array[len(self.x) - 1]
                return M_array, p_array

            mismatch_predicted_exit_pressure = lambda x_shock: M_and_p_given_x_shock(x_shock)[1][len(self.x) - 1] - pb_p0_ratio
            x_shock = scipy.optimize.root_scalar(
                mismatch_predicted_exit_pressure,
                                                 bracket=[self.x_throat, self.xmax], 
                method="brentq",
                maxiter=1000,
                xtol=1e-7,
                rtol=1e-7,
            ).root
            M_array, p_array = M_and_p_given_x_shock(x_shock)
            flag_draw_nshock = True  # Mark for drawing normal shock

        elif pb_p0_ratio > self.crit_p_ratio_3:
            # Sonic throat - oblique shock at exit
            flag_draw_oshock = True
            
            M_array = np.zeros_like(self.xeval)
            p_array = np.zeros_like(self.xeval)
            A_over_A_star = self.area_array / self.area_throat 
            r_exit = np.sqrt(self.area_array / np.pi)[-1]
            
            for i in range(len(self.xeval)):
                if i < len(self.x):
                    ratio = A_over_A_star[i]
                    if self.x[i] < self.x_throat:
                        M_array[i] = self.solve_mach_number_from_area_ratio(ratio, self.g, is_subsonic=True)
                        p_array[i] = 1 / (1 + (self.g - 1) / 2 * M_array[i] ** 2) ** (self.g / (self.g - 1))
                    else:
                        M_array[i] = self.solve_mach_number_from_area_ratio(ratio, self.g, is_subsonic=False)
                        p_array[i] = 1 / (1 + (self.g - 1) / 2 * M_array[i] ** 2) ** (self.g / (self.g - 1))
                elif i == len(self.x):
                    M_exit = M_array[len(self.x) - 1]
                    p_exit = p_array[len(self.x) - 1]
                    pb_pe = pb_p0_ratio / p_exit
                    Mn1 = np.sqrt((pb_pe - 1) * (self.g + 1) / (self.g * 2) + 1)
                    Mn2 = np.sqrt((1 + (self.g - 1) / 2 * Mn1 ** 2) / (self.g * Mn1 ** 2 - (self.g - 1) / 2))
                    beta = np.arcsin(Mn1 / M_exit)
                    tan_theta = (
                        2
                        / np.tan(beta)
                        * (M_exit**2 * np.sin(beta) ** 2 - 1)
                        / (M_exit**2 * (self.g + np.cos(2 * beta)) + 2)
                    )
                    theta = np.arctan(tan_theta)
                    x_extended = self.xmax + r_exit / np.tan(beta)
                    M_array[i] = M_exit
                    p_array[i] = p_exit   
                elif x_extended is not None and self.xeval[i] >= x_extended:
                    # beta/theta must have been computed at i == len(self.x)
                    M_array[i] = Mn2 / np.sin(beta - theta)
                    p_array[i] = pb_p0_ratio
                else:
                    M_array[i] = M_array[len(self.x) - 1]
                    p_array[i] = p_array[len(self.x) - 1]

        else:
            # Underexpanded jet - expansion fan
            g = self.g
            M_array = np.zeros_like(self.xeval)
            p_array = np.zeros_like(self.xeval)
            A_over_A_star = self.area_array / self.area_throat
        
            def p_over_p0(M):
                return (1.0 + 0.5 * (g - 1.0) * M**2) ** (-g / (g - 1.0))
        
            # nozzle interior (isentropic, choked)
            for i in range(len(self.x)):
                ratio = A_over_A_star[i]
                if self.x[i] < self.x_throat:
                    M = self.solve_mach_number_from_area_ratio(ratio, g, is_subsonic=True)
                else:
                    M = self.solve_mach_number_from_area_ratio(ratio, g, is_subsonic=False)
        
                M_array[i] = M
                p_array[i] = p_over_p0(M)
        
            # exit state
            i_exit = len(self.x) - 1
            M_exit = M_array[i_exit]
            p_exit = p_array[i_exit]  # pe/p0
        
            # far-field Mach matching pb/p0 (isentropic inversion)
            M_far = np.sqrt((2.0 / (g - 1.0)) * (pb_p0_ratio ** (-(g - 1.0) / g) - 1.0))
        
            x_exit = self.xmax
            r_exit = np.sqrt(self.area_exit / np.pi)
        
            mu_exit = np.arcsin(np.clip(1.0 / M_exit, 0.0, 1.0))  # head (at exit state)
            mu_far = np.arcsin(np.clip(1.0 / M_far, 0.0, 1.0))  # tail (fully expanded)
        
            x_head = x_exit + r_exit / np.tan(mu_exit)
            x_tail = x_exit + r_exit / np.tan(mu_far)
        
            x_end = self.xeval[-1]
            x_tail_eff = min(x_tail, x_end)
        
            def is_hit_by_fan_centerline(xq):
                return (xq >= x_head) and (xq <= x_tail_eff)
        
            # fill extended region using fan theory on centerline
            for i in range(len(self.x), len(self.xeval)):
                xq = self.xeval[i]
        
                if xq < x_head:
                    M = M_exit
                    p = p_exit
                elif is_hit_by_fan_centerline(xq):
                    dx = max(xq - x_exit, 1e-12)
                    mu = np.arctan(r_exit / dx)
                    mu = np.clip(mu, mu_far, mu_exit)
                    M = 1.0 / np.sin(mu)
                    M = float(np.clip(M, M_exit, M_far))
                    p = p_over_p0(M)
                else:
                    if x_tail <= x_end:
                        M = M_far
                        p = pb_p0_ratio
                    else:
                        M = M_array[i - 1]
                        p = p_array[i - 1]
        
                M_array[i] = M
                p_array[i] = p
        
            if x_tail <= x_end:
                M_array[-1] = M_far
                p_array[-1] = pb_p0_ratio

            flag_draw_fan = True
            fan_alphas = np.linspace(mu_far, mu_exit, 7)  # tail -> head

        viz_data = {
            "flag_draw_oshock": flag_draw_oshock,
            "flag_draw_fan": flag_draw_fan,
            "flag_draw_nshock": flag_draw_nshock,
            "x_shock": x_shock,
            "fan_alphas": fan_alphas,
            "beta": beta,
            "x_extended": x_extended,
        }
        return M_array, p_array, viz_data


    def plot_flow_profile(self, pb_p0_ratio):
        """Plot flow profile using matplotlib."""
        M_array, p_array, viz_data = self._calculate_flow_profile(pb_p0_ratio)
        flag_draw_oshock = viz_data['flag_draw_oshock']
        flag_draw_fan = viz_data['flag_draw_fan']
        fan_alphas = viz_data['fan_alphas']
        beta = viz_data['beta']
        
        # start to draw
        fig, ax1 = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('white')
        ax1.set_facecolor('white')

        # Plot M(x) and p/p0(x) on primary axis
        ax1.plot(self.xeval, M_array, color='green', linewidth=2, label='$M(x)$')
        ax1.plot(self.xeval, p_array, color='orange', linestyle='--', linewidth=2, label=r'$p/p_0(x)$')
        
        ax1.set_xlabel('Axial Position $x$', fontsize=12)
        ax1.set_ylabel('Mach Number / Pressure Ratio', fontsize=12)
        ax1.set_xlim([min(self.xeval), max(self.xeval)])
        ax1.set_ylim([0, 5])
        ax1.grid(True, alpha=0.3)
        
        # Create secondary axis for area
        ax2 = ax1.twinx()
        ax2.set_facecolor('white')
        
        # Plot area on secondary axis
        ax2.plot(self.x, np.sqrt(self.area_array/np.pi), color='black', linewidth=2, label='$A(x)$')
        if flag_draw_oshock:
            r = 2*np.linspace(0, self.xmax - self.xmin, 5)
            ray_x = r*np.cos(-beta)
            ray_y = r*np.sin(-beta)
            x_arr = self.x[-1] + ray_x
            y_arr = np.sqrt(self.area_array/np.pi)[-1] + ray_y
            x_arr_2 = 0.01*(self.xmax - self.xmin)+self.x[-1] + ray_x
            y_arr_2 = 0.01*(max(np.sqrt(self.area_array/np.pi))-min(np.sqrt(self.area_array/np.pi))) + np.sqrt(self.area_array/np.pi)[-1] + ray_y
            ax2.plot(x_arr, y_arr, color='red', lw=2, label=f'shockwave (beta={beta*180/np.pi:.3f}°)')
            ax2.plot(x_arr_2, y_arr_2, color='red', lw=2)
            
        if flag_draw_fan and (fan_alphas is not None):
            x0 = self.x[-1]          # exit x
            r_exit = np.sqrt(self.area_array/np.pi)[-1]
            y0 = r_exit              # exit radius
            x_end = max(self.xeval)  # draw up to end of your extended domain
        
            for j, a in enumerate(fan_alphas):
                # line from (x0,y0) with downward slope toward centerline
                y_at_end = y0 - (x_end - x0) * np.tan(a)
        
                if y_at_end <= 0.0:
                    # it hits the centerline before x_end
                    x_hit = x0 + y0 / np.tan(a)
                    xs = np.array([x0, x_hit])
                    ys = np.array([y0, 0.0])
                else:
                    # it doesn't reach centerline within plotting window
                    xs = np.array([x0, x_end])
                    ys = np.array([y0, y_at_end])
        
                ax2.plot(xs, ys, linestyle="--", linewidth=1.5, color="blue",
                         label="expansion fan" if j == 0 else None)
        
        ax2.set_ylabel('Radius', fontsize=12, color='black')
        ax2.set_ylim([0,max(np.sqrt(self.area_array/np.pi))*1.1])
        ax2.tick_params(axis='y', labelcolor='black')
        
        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2,
                   loc='upper center',
                   bbox_to_anchor=(0.5, -0.15),  # Below the plot
                   ncol=4,
                   fontsize=10,
                   frameon=False)
        # Use try-except to handle potential tight_layout issues with mathtext
        try:
            plt.tight_layout(rect=[0, 0.1, 1, 1])
        except (ValueError, Exception):
            # If tight_layout fails, use a simpler layout adjustment
            plt.tight_layout()
        
        return fig

    def plot_flow_profile_plotly(self, pb_p0_ratio):
        """Create Plotly figure for flow profile."""
        try:
            M_array, p_array, viz_data = self._calculate_flow_profile(pb_p0_ratio)
            flag_draw_oshock = viz_data["flag_draw_oshock"]
            flag_draw_fan = viz_data["flag_draw_fan"]
            flag_draw_nshock = viz_data["flag_draw_nshock"]
            x_shock = viz_data["x_shock"]
            fan_alphas = viz_data["fan_alphas"]
            beta = viz_data["beta"]
        except (ValueError, ZeroDivisionError, OverflowError) as e:
            raise ValueError(f"Numerical error in flow calculation: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in flow calculation: {str(e)}")
        
        # Create Plotly figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Calculate radius array for hover tooltips
        radius_array = np.sqrt(self.area_array/np.pi)
        # Interpolate radius for extended xeval points
        radius_extended = np.zeros_like(self.xeval)
        for i in range(len(self.xeval)):
            if i < len(radius_array):
                radius_extended[i] = radius_array[i]
            else:
                radius_extended[i] = radius_array[-1]
        
        # Create hover text with all values
        hover_text_M = [f'x: {x:.3f}<br>M: {M:.4f}<br>p/p₀: {p:.4f}<br>r: {r:.3f}' 
                        for x, M, p, r in zip(self.xeval, M_array, p_array, radius_extended)]
        hover_text_p = hover_text_M.copy()
        hover_text_r = [f'x: {x:.3f}<br>r: {r:.3f}' 
                       for x, r in zip(self.x, radius_array)]
        
        # Primary axis: M(x) and p/p0(x)
        # Color palette: Nature/Science publication colors (Wong palette)
        fig.add_trace(
            go.Scatter(
                x=self.xeval, 
                y=M_array, 
                name='Mach Number', 
                line=dict(color='#0072B2', width=4),  # Nature blue, thicker line
                hovertemplate='<b>%{text}</b><extra></extra>',
                text=hover_text_M,
                mode='lines'
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=self.xeval, 
                y=p_array, 
                name='Pressure Ratio (p/p₀)', 
                line=dict(color='#E69F00', width=3.5, dash='dash'),  # Nature orange, thicker line
                hovertemplate='<b>%{text}</b><extra></extra>',
                text=hover_text_p,
                mode='lines'
            ),
            secondary_y=False,
        )
        
        # Secondary axis: Radius - neutral gray
        fig.add_trace(
            go.Scatter(
                x=self.x, 
                y=radius_array, 
                name='Nozzle Radius', 
                line=dict(color='#999999', width=3.5),  # Nature gray, thicker line
                hovertemplate='<b>%{text}</b><extra></extra>',
                text=hover_text_r,
                mode='lines',
                fill='tozeroy',
                fillcolor='rgba(153, 153, 153, 0.1)'  # Light shaded area under geometry
            ),
            secondary_y=True,
        )
        
        # Add shock waves if needed
        if flag_draw_oshock and beta is not None:
            r = 2*np.linspace(0, self.xmax - self.xmin, 5)
            ray_x = r*np.cos(-beta)
            ray_y = r*np.sin(-beta)
            x_arr = self.x[-1] + ray_x
            y_arr = radius_array[-1] + ray_y
            hover_text_shock = [f'Shockwave<br>β: {beta*180/np.pi:.3f}°' for _ in x_arr]
            fig.add_trace(
                go.Scatter(
                    x=x_arr, 
                    y=y_arr, 
                    name=f'Shockwave (β={beta*180/np.pi:.3f}°)', 
                    line=dict(color='#D55E00', width=4),  # Nature vermillion, thicker line
                    hovertemplate='<b>%{text}</b><extra></extra>',
                    text=hover_text_shock,
                    mode='lines'
                ),
                secondary_y=True,
            )
        
        # Add expansion fan if needed
        if flag_draw_fan and (fan_alphas is not None):
            x0 = self.x[-1]
            r_exit = radius_array[-1]
            y0 = r_exit
            x_end = max(self.xeval)
            
            for j, a in enumerate(fan_alphas):
                y_at_end = y0 - (x_end - x0) * np.tan(a)
                if y_at_end <= 0.0:
                    x_hit = x0 + y0 / np.tan(a)
                    xs = np.array([x0, x_hit])
                    ys = np.array([y0, 0.0])
                else:
                    xs = np.array([x0, x_end])
                    ys = np.array([y0, y_at_end])
                
                hover_text_fan = [f'Expansion Fan<br>α: {a*180/np.pi:.2f}°' for _ in xs]
                fig.add_trace(
                    go.Scatter(
                        x=xs, 
                        y=ys, 
                        name='Expansion Fan' if j == 0 else None,
                        line=dict(color='#56B4E9', width=2.5, dash='dash'),  # Nature sky blue, thicker line
                        hovertemplate='<b>%{text}</b><extra></extra>',
                        text=hover_text_fan,
                        showlegend=(j == 0),
                        mode='lines'
                    ),
                    secondary_y=True,
                )
        
        # Normal shock annotation below x-axis with arrow
        shock_annotation = None
        if flag_draw_nshock and x_shock is not None:
            shock_annotation = dict(
                x=x_shock,
                y=-0.15,  # Below x-axis
                yref='paper',
                text='↑ Shockwave',
                showarrow=False,
                font=dict(size=14, color='#CC79A7'),
                xanchor='center',
                yanchor='top'
            )
        
        # Auto-adjust axis limits based on data
        M_max = np.max(M_array)
        M_min = np.min(M_array)
        p_max = np.max(p_array)
        p_min = np.min(p_array)
        
        # Y-axis range for primary axis (Mach and pressure)
        y_min = min(M_min, p_min) * 0.95  # Add 5% padding
        y_max = max(M_max, p_max) * 1.05  # Add 5% padding
        # Ensure minimum range and non-negative for pressure
        y_min = max(0, y_min)  # Don't go below 0
        if y_max - y_min < 0.1:  # Ensure minimum range
            y_max = y_min + 0.1
        
        # X-axis range
        x_min = np.min(self.xeval)
        x_max = np.max(self.xeval)
        x_range = x_max - x_min
        x_min_adj = x_min - x_range * 0.02  # Add 2% padding
        x_max_adj = x_max + x_range * 0.02
        
        # Set axis labels and styling with auto-adjusted limits
        # Modern dark theme with improved contrast
        fig.update_xaxes(
            title_text="x (Axial Position)",
            title_font=dict(size=18, color='#ffffff', family='Inter, sans-serif'),  # Increased font size
            tickfont=dict(color='#d1d5db', size=16),  # Increased tick label font size
            showgrid=True, 
            gridcolor='rgba(156,163,175,0.12)',  # Reduced opacity (12%)
            gridwidth=1,
            zeroline=False,
            range=[x_min_adj, x_max_adj],
            linecolor='#4b5563',
            linewidth=1
        )
        fig.update_yaxes(
            title_text="M(x), p/p₀(x)",
            title_font=dict(size=18, color='#ffffff', family='Inter, sans-serif'),  # Increased font size
            tickfont=dict(color='#d1d5db', size=16),  # Increased tick label font size
            secondary_y=False, 
            range=[y_min, y_max], 
            showgrid=True, 
            gridcolor='rgba(156,163,175,0.12)',  # Reduced opacity (12%)
            gridwidth=1,
            zeroline=False,
            linecolor='#4b5563',
            linewidth=1
        )
        fig.update_yaxes(
            title_text="r(x) (Radius)",
            title_font=dict(size=18, color='#ffffff', family='Inter, sans-serif'),  # Increased font size
            tickfont=dict(color='#d1d5db', size=16),  # Increased tick label font size
            secondary_y=True, 
            range=[0, max(radius_array)*1.1], 
            showgrid=False,
            linecolor='#4b5563',
            linewidth=1
        )
        
        # Update layout for modern dark theme - legend inside plot
        fig.update_layout(
            plot_bgcolor='rgba(26, 26, 26, 0.85)',  # Semi-transparent for modern look
            paper_bgcolor='rgba(26, 26, 26, 0.85)',
            font=dict(color='#ececec', size=16, family='Inter, sans-serif'),  # Increased font size
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color='#ececec', size=14),
                bgcolor='rgba(15,15,15,0.85)',
                bordercolor='rgba(156,163,175,0.3)',
                borderwidth=1,
                itemclick="toggleothers",
                itemdoubleclick="toggle"
            ),
            height=650,
            width=None,
            margin=dict(l=70, r=70, t=50, b=80),  # Increased bottom margin for annotation
            annotations=[shock_annotation] if shock_annotation else [],
            hovermode='x unified',  # Unified hover for better tooltip display
            hoverlabel=dict(
                bgcolor='rgba(15,15,15,0.95)',
                bordercolor='#06b6d4',
                font_size=11,
                font_family='Inter, sans-serif'
            )
        )
        
        return fig

    def get_area(self, x):
        return self.A(x)

    def get_area_over_throat_at_x(self, x):
        return self.A(x)/self.area_throat

    def get_exit_area_over_throat(self):
        return self.area_exit/self.area_throat

    def get_area_over_throat(self, A):
        return A/self.area_throat

    def solve_mach_number_from_area_ratio(self, ratio, gamma, is_subsonic=True):
        eq = lambda m: m**2*ratio**2 - (2/(gamma+1)*(1+(gamma-1)/2*m**2))**((gamma+1)/(gamma-1)) 
        if is_subsonic:
            sol = scipy.optimize.root_scalar(eq, bracket=[0, 1], method='brentq', maxiter=1000,xtol=1e-7,rtol=1e-7)
        else:
            sol = scipy.optimize.root_scalar(eq, bracket=[1, 20], method='brentq', maxiter=1000,xtol=1e-7,rtol=1e-7)
        return sol.root

    @property
    def area_exit(self):
        return self._area_exit

    @area_exit.setter
    def area_exit(self,value):
        self._area_exit = value

    @property
    def area_throat(self):
        return self._area_throat
        
    @area_throat.setter
    def area_throat(self,value):
        self._area_throat = value


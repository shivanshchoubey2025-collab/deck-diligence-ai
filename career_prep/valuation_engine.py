"""
========================================================================================
Institutional DCF (Discounted Cash Flow) & Valuation Engine for Indian Equities
----------------------------------------------------------------------------------------
Designed for: Computer Science -> High Finance (IB / PE / Equity Research) Transition
Standard: Complies with NYU Stern (Prof. Aswath Damodaran) Valuation Framework for India
========================================================================================
Features:
  - Unlevered Free Cash Flow (UFCF) 5-Year Projection Engine
  - WACC Calculation under Indian Macro Conditions (10-Yr G-Sec Risk-Free Rate, ERP, Beta)
  - Dual Terminal Value Valuation: Perpetuity Growth Model & Exit EBITDA Multiple
  - Enterprise Value (EV) to Implied Equity Value & Target Share Price Bridge
  - 2D Sensitivity Matrix: WACC vs. Terminal Growth Rate
  - Clean formatted Terminal Output & Exportable Financial Valuation Summary
========================================================================================
"""

import math
import sys
import os
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class FinancialInputs:
    company_name: str
    ticker: str
    currency: str = "INR (Cr)"
    current_share_price: float = 245.0
    shares_outstanding_cr: float = 880.0  # Shares in Crores
    cash_and_equivalents_cr: float = 4500.0
    total_debt_cr: float = 550.0
    minority_interest_cr: float = 0.0

    # Base Year (Year 0) Financials in Crores
    base_revenue: float = 12500.0
    base_ebitda: float = 1450.0
    base_ebit: float = 1100.0
    effective_tax_rate: float = 0.2517  # Standard Indian Corporate Tax Rate (25.17%)

    # 5-Year Projections Assumptions
    revenue_growth_rates: List[float] = None  # e.g., [0.25, 0.20, 0.18, 0.15, 0.12]
    ebitda_margins: List[float] = None        # e.g., [0.13, 0.15, 0.17, 0.18, 0.19]
    depreciation_pct_revenue: float = 0.035   # D&A as % of Revenue
    capex_pct_revenue: float = 0.040          # Capex as % of Revenue
    nwc_pct_revenue: float = 0.025            # Net Working Capital as % of Revenue

    # WACC Inputs (Indian Macro Environment)
    risk_free_rate: float = 0.0700            # ~7.00% (10-Year Indian Government Bond Yield)
    equity_risk_premium: float = 0.0600       # ~6.00% (India ERP)
    levered_beta: float = 1.15
    pre_tax_cost_of_debt: float = 0.0850      # ~8.50% lending rate
    target_debt_weight: float = 0.10          # 10% Debt
    target_equity_weight: float = 0.90        # 90% Equity

    # Terminal Value Assumptions
    perpetual_growth_rate: float = 0.0550     # 5.50% (Long-term Indian nominal GDP proxy)
    exit_ebitda_multiple: float = 22.0        # Target sector multiple


class DCFValuationEngine:
    def __init__(self, inputs: FinancialInputs):
        self.inputs = inputs
        if self.inputs.revenue_growth_rates is None:
            self.inputs.revenue_growth_rates = [0.24, 0.20, 0.17, 0.14, 0.12]
        if self.inputs.ebitda_margins is None:
            self.inputs.ebitda_margins = [0.135, 0.150, 0.165, 0.180, 0.190]

    def calculate_wacc(self) -> Tuple[float, float, float]:
        """Calculates WACC using CAPM for Cost of Equity."""
        # Cost of Equity = Rf + Beta * ERP
        cost_of_equity = self.inputs.risk_free_rate + (self.inputs.levered_beta * self.inputs.equity_risk_premium)
        # Cost of Debt after-tax = Kd * (1 - t)
        after_tax_cost_of_debt = self.inputs.pre_tax_cost_of_debt * (1 - self.inputs.effective_tax_rate)
        # WACC = We * Ke + Wd * Kd(1-t)
        wacc = (self.inputs.target_equity_weight * cost_of_equity) + (self.inputs.target_debt_weight * after_tax_cost_of_debt)
        return wacc, cost_of_equity, after_tax_cost_of_debt

    def build_cash_flow_forecast(self, wacc: float) -> List[Dict]:
        """Projects 5-Year Unlevered Free Cash Flow (UFCF)."""
        forecast = []
        prior_revenue = self.inputs.base_revenue
        prior_nwc = prior_revenue * self.inputs.nwc_pct_revenue

        for year in range(1, 6):
            growth = self.inputs.revenue_growth_rates[year - 1]
            revenue = prior_revenue * (1 + growth)
            margin = self.inputs.ebitda_margins[year - 1]
            ebitda = revenue * margin
            depreciation = revenue * self.inputs.depreciation_pct_revenue
            ebit = ebitda - depreciation
            nopat = ebit * (1 - self.inputs.effective_tax_rate)  # Net Operating Profit After Tax

            capex = revenue * self.inputs.capex_pct_revenue
            current_nwc = revenue * self.inputs.nwc_pct_revenue
            change_in_nwc = current_nwc - prior_nwc

            # UFCF = NOPAT + D&A - Capex - Change in NWC
            ufcf = nopat + depreciation - capex - change_in_nwc

            # Mid-Year Discount Factor = 1 / (1 + WACC)^(t - 0.5)
            discount_period = year - 0.5
            discount_factor = 1.0 / ((1.0 + wacc) ** discount_period)
            pv_ufcf = ufcf * discount_factor

            forecast.append({
                "year": year,
                "revenue": revenue,
                "revenue_growth": growth,
                "ebitda": ebitda,
                "ebitda_margin": margin,
                "ebit": ebit,
                "nopat": nopat,
                "depreciation": depreciation,
                "capex": capex,
                "change_in_nwc": change_in_nwc,
                "ufcf": ufcf,
                "discount_period": discount_period,
                "discount_factor": discount_factor,
                "pv_ufcf": pv_ufcf
            })

            prior_revenue = revenue
            prior_nwc = current_nwc

        return forecast

    def compute_valuation(self, custom_wacc=None, custom_terminal_growth=None):
        wacc, cost_of_equity, after_tax_kd = self.calculate_wacc()
        active_wacc = custom_wacc if custom_wacc is not None else wacc
        active_g = custom_terminal_growth if custom_terminal_growth is not None else self.inputs.perpetual_growth_rate

        forecast = self.build_cash_flow_forecast(active_wacc)
        sum_pv_ufcf = sum(item["pv_ufcf"] for item in forecast)

        # Year 5 Cash Flows
        year_5_ufcf = forecast[-1]["ufcf"]
        year_5_ebitda = forecast[-1]["ebitda"]

        # Terminal Value via Perpetuity Growth Model: TV = [FCF_5 * (1 + g)] / (WACC - g)
        if active_wacc <= active_g:
            terminal_value_growth = float('nan')
            pv_tv_growth = float('nan')
        else:
            terminal_value_growth = (year_5_ufcf * (1.0 + active_g)) / (active_wacc - active_g)
            # Discounted back 5 years
            pv_tv_growth = terminal_value_growth / ((1.0 + active_wacc) ** 5)

        # Terminal Value via Exit Multiple Method
        terminal_value_multiple = year_5_ebitda * self.inputs.exit_ebitda_multiple
        pv_tv_multiple = terminal_value_multiple / ((1.0 + active_wacc) ** 5)

        # Enterprise Value
        ev_growth = sum_pv_ufcf + pv_tv_growth
        ev_multiple = sum_pv_ufcf + pv_tv_multiple

        # Bridge: Equity Value = Enterprise Value + Cash - Debt - Minority Interest
        net_debt = self.inputs.total_debt_cr - self.inputs.cash_and_equivalents_cr
        equity_val_growth = ev_growth - net_debt - self.inputs.minority_interest_cr
        equity_val_multiple = ev_multiple - net_debt - self.inputs.minority_interest_cr

        # Implied Share Price
        target_price_growth = equity_val_growth / self.inputs.shares_outstanding_cr
        target_price_multiple = equity_val_multiple / self.inputs.shares_outstanding_cr

        upside_growth = ((target_price_growth - self.inputs.current_share_price) / self.inputs.current_share_price) * 100
        upside_multiple = ((target_price_multiple - self.inputs.current_share_price) / self.inputs.current_share_price) * 100

        return {
            "wacc": active_wacc,
            "cost_of_equity": cost_of_equity,
            "after_tax_kd": after_tax_kd,
            "forecast": forecast,
            "sum_pv_ufcf": sum_pv_ufcf,
            "terminal_value_growth": terminal_value_growth,
            "pv_tv_growth": pv_tv_growth,
            "ev_growth": ev_growth,
            "equity_val_growth": equity_val_growth,
            "target_price_growth": target_price_growth,
            "upside_growth": upside_growth,
            "terminal_value_multiple": terminal_value_multiple,
            "pv_tv_multiple": pv_tv_multiple,
            "ev_multiple": ev_multiple,
            "equity_val_multiple": equity_val_multiple,
            "target_price_multiple": target_price_multiple,
            "upside_multiple": upside_multiple,
            "net_debt": net_debt
        }

    def generate_sensitivity_table(self, wacc_range=None, g_range=None) -> List[List]:
        """Generates a 2D Sensitivity Grid: WACC vs Perpetual Growth Rate."""
        base_wacc, _, _ = self.calculate_wacc()
        base_g = self.inputs.perpetual_growth_rate

        if wacc_range is None:
            wacc_range = [base_wacc - 0.015, base_wacc - 0.0075, base_wacc, base_wacc + 0.0075, base_wacc + 0.015]
        if g_range is None:
            g_range = [base_g - 0.010, base_g - 0.005, base_g, base_g + 0.005, base_g + 0.010]

        table = []
        header = ["WACC \\ Growth"] + [f"{g*100:.1f}%" for g in g_range]
        table.append(header)

        for w in wacc_range:
            row = [f"{w*100:.2f}%"]
            for g in g_range:
                res = self.compute_valuation(custom_wacc=w, custom_terminal_growth=g)
                tp = res["target_price_growth"]
                if math.isnan(tp):
                    row.append("N/A")
                else:
                    row.append(f"{tp:.1f}")
            table.append(row)

        return table

    def print_executive_report(self):
        val = self.compute_valuation()
        sens = self.generate_sensitivity_table()

        print("=" * 84)
        print(f" INSTITUTIONAL DCF VALUATION SUMMARY: {self.inputs.company_name} ({self.inputs.ticker})")
        print("=" * 84)
        print(f" Currency: {self.inputs.currency} | CMP: INR {self.inputs.current_share_price:.2f} | Shares: {self.inputs.shares_outstanding_cr:.1f} Cr")
        print(f" WACC: {val['wacc']*100:.2f}% (Cost of Equity: {val['cost_of_equity']*100:.2f}% | After-tax Kd: {val['after_tax_kd']*100:.2f}%)")
        print(f" Terminal Perpetual Growth Rate (g): {self.inputs.perpetual_growth_rate*100:.2f}% | Exit Multiple: {self.inputs.exit_ebitda_multiple:.1f}x")
        print("-" * 84)

        print(f"{'Year':<6} {'Revenue (Cr)':<15} {'Growth':<8} {'EBITDA (Cr)':<14} {'UFCF (Cr)':<13} {'PV UFCF (Cr)':<14}")
        print("-" * 84)
        for row in val["forecast"]:
            print(f"Y{row['year']:<5} {row['revenue']:<15.1f} {row['revenue_growth']*100:>5.1f}%  {row['ebitda']:<14.1f} {row['ufcf']:<13.1f} {row['pv_ufcf']:<14.1f}")
        print("-" * 84)
        print(f" Cumulative PV of 5-Yr Free Cash Flows:   INR {val['sum_pv_ufcf']:,.1f} Cr")
        print(f" Present Value of Terminal Value (Gordon): INR {val['pv_tv_growth']:,.1f} Cr  ({(val['pv_tv_growth']/val['ev_growth'])*100:.1f}% of EV)")
        print(f" Implied Enterprise Value (EV):          INR {val['ev_growth']:,.1f} Cr")
        print(f" Net Debt (Debt - Cash):                  INR {val['net_debt']:,.1f} Cr")
        print(f" Implied Equity Value:                    INR {val['equity_val_growth']:,.1f} Cr")
        print("=" * 84)
        print(f" Target Price (Perpetuity Growth Method):  INR {val['target_price_growth']:.2f} ({val['upside_growth']:+.1f}% vs CMP)")
        print(f" Target Price (Exit EBITDA Multiple):      INR {val['target_price_multiple']:.2f} ({val['upside_multiple']:+.1f}% vs CMP)")
        print("=" * 84)

        print("\nSENSITIVITY ANALYSIS (Target Share Price in INR: WACC vs. Terminal Growth Rate)")
        col_width = 13
        for row in sens:
            print("".join(f"{item:>{col_width}}" for item in row))
        print("=" * 84)


def run_benchmark():
    # Benchmark based on high-growth Indian Tech / Platform business (e.g. Food Delivery / Quick Commerce / Consumer Tech)
    inputs = FinancialInputs(
        company_name="Zomato / Eternal Ltd (Sample Model)",
        ticker="ZOMATO.NS",
        current_share_price=260.0,
        shares_outstanding_cr=883.0,
        cash_and_equivalents_cr=12200.0,
        total_debt_cr=350.0,
        base_revenue=13400.0,
        base_ebitda=1120.0,
        base_ebit=780.0,
        revenue_growth_rates=[0.35, 0.28, 0.22, 0.18, 0.14],
        ebitda_margins=[0.11, 0.13, 0.155, 0.175, 0.190],
        risk_free_rate=0.0710,      # 7.10% 10-Yr G-Sec
        equity_risk_premium=0.0600, # 6.00% Indian ERP
        levered_beta=1.20,
        perpetual_growth_rate=0.0600, # 6.0% long term nominal growth
        exit_ebitda_multiple=24.0
    )

    engine = DCFValuationEngine(inputs)
    engine.print_executive_report()


if __name__ == "__main__":
    run_benchmark()

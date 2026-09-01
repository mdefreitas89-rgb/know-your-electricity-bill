from pathlib import Path
import streamlit as st

# ============================================================
# KNOW YOUR ELECTRICITY BILL
# Energy Unit - Government of Saint Vincent and the Grenadines
# ============================================================

DEFAULT_KWH = 100
DEFAULT_FUEL_SURCHARGE = 0.7355
DEFAULT_SOLAR_EXPORT = 100.0
DEFAULT_FIT = 0.45

LOW_CONSUMPTION_LIMIT = 50
LOW_ENERGY_RATE = 0.425
STANDARD_ENERGY_RATE = 0.500

VAT_THRESHOLD = 250
VAT_RATE = 16.0


def money(value):
    return f"EC$ {value:,.2f}"


def calculate_bill(kwh, fuel_rate, solar_export=0.0, fit=DEFAULT_FIT):
    if kwh < LOW_CONSUMPTION_LIMIT:
        energy_rate = LOW_ENERGY_RATE
    else:
        energy_rate = STANDARD_ENERGY_RATE

    energy_charge = kwh * energy_rate
    fuel_charge = kwh * fuel_rate

    vat_kwh = max(0.0, kwh - VAT_THRESHOLD)
    vat_energy_charge = vat_kwh * energy_rate
    vat = vat_energy_charge * VAT_RATE / 100

    solar_credit = solar_export * fit

    gross_total = energy_charge + fuel_charge + vat
    total = max(0.0, gross_total - solar_credit)

    effective_rate = total / kwh if kwh > 0 else 0.0

    return {
        "energy_rate": energy_rate,
        "energy_charge": energy_charge,
        "fuel_charge": fuel_charge,
        "vat_kwh": vat_kwh,
        "vat_energy_charge": vat_energy_charge,
        "vat": vat,
        "gross_total": gross_total,
        "solar_export": solar_export,
        "fit": fit,
        "solar_credit": solar_credit,
        "total": total,
        "effective_rate": effective_rate,
    }


st.set_page_config(
    page_title="Know Your Electricity Bill",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# FULL ENERGY UNIT BRANDING / LAYOUT
# ============================================================

st.markdown(
    """
<style>
/* ---------- GLOBAL ---------- */
.stApp {
    background: #f3f8f0;
}

.main .block-container {
    max-width: 1500px;
    padding: 0.35rem 1.1rem 1.5rem 1.1rem;
}

[data-testid="stHeader"] {
    background: #075b1d;
}

h1, h2, h3 {
    color: #075b1d;
}

/* ---------- TOP BRANDING ---------- */
.brand-row {
    display: flex;
    align-items: center;
    gap: 22px;
    background: linear-gradient(105deg, #075b1d 0%, #08752a 55%, #064d19 100%);
    border-radius: 0 0 8px 8px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1.15rem;
    box-shadow: 0 4px 12px rgba(0,0,0,.12);
}

.brand-title {
    color: white !important;
    font-size: 2.55rem;
    line-height: 1.05;
    font-weight: 850;
    margin: 0;
    letter-spacing: .02em;
}

.brand-subtitle {
    color: #e8ef9c !important;
    font-size: 1.12rem;
    font-weight: 750;
    margin-top: 0.45rem;
}

.brand-description {
    color: white !important;
    font-size: 1rem;
    margin-top: 0.75rem;
}

/* ---------- SECTION HEADERS ---------- */
.section-title {
    background: linear-gradient(90deg, #08752a, #05651f);
    color: white !important;
    border-radius: 9px 9px 0 0;
    padding: 10px 15px;
    font-weight: 800;
    font-size: 1.05rem;
    margin-top: 0.2rem;
    margin-bottom: 0;
    letter-spacing: .01em;
}

.section-title * {
    color: white !important;
}

/* ---------- CARDS ---------- */
.panel {
    background: white;
    border: 1px solid #b8d99f;
    border-radius: 0 0 10px 10px;
    padding: 15px 18px;
    min-height: 100%;
}

.about-panel {
    background: #eef8df;
    border: 1px solid #c5dfa7;
    border-radius: 10px;
    padding: 16px 18px;
}

.about-panel h3 {
    margin-top: 0;
    color: #075b1d;
}

.check-line {
    display: flex;
    gap: 9px;
    align-items: flex-start;
    margin: 13px 0;
    color: #111;
}

.check {
    color: #08752a;
    font-weight: 900;
    font-size: 1.05rem;
}

.green-note {
    background: #e9f5df;
    border: 1px solid #cbe3b5;
    border-left: 5px solid #159447;
    border-radius: 8px;
    padding: 11px 14px;
    color: #174d21;
    margin: 10px 0 12px;
}

/* ---------- RESULT TABLE ---------- */
.bill-table {
    background: white;
    border: 1px solid #b8d99f;
    border-radius: 0 0 10px 10px;
    overflow: hidden;
}

.bill-row {
    display: grid;
    grid-template-columns: 1fr auto;
    padding: 10px 20px;
    border-bottom: 1px solid #e0e7dd;
    font-size: 0.98rem;
}

.bill-row.header {
    color: #555;
    font-weight: 750;
    font-size: 0.78rem;
    text-transform: uppercase;
    background: #f7f9f6;
}

.bill-row.total {
    background: #e5f3d5;
    color: #075b1d;
    font-weight: 850;
}

.amount {
    color: #075b1d;
    font-weight: 750;
}

.solar-credit {
    color: #c72525;
    font-weight: 800;
}

/* ---------- FINAL RESULT ---------- */
.final-card {
    background: linear-gradient(135deg, #e8f6d7, #d8edc4);
    border: 1px solid #afd28d;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.35);
}

.final-label {
    color: #176322;
    font-size: 1rem;
    font-weight: 800;
}

.final-value {
    color: #075b1d;
    font-size: 3.15rem;
    line-height: 1.05;
    font-weight: 900;
    margin-top: 4px;
}

/* ---------- SAVINGS ---------- */
.saving-card {
    background: #f0f8e8;
    border: 1px solid #c9e2b3;
    border-radius: 9px;
    padding: 13px 16px;
    min-height: 92px;
}

.saving-title {
    color: #075b1d;
    font-size: 1.05rem;
    font-weight: 850;
}

.saving-money {
    color: #075b1d;
    font-size: 1.45rem;
    font-weight: 900;
}

/* ---------- REMINDER / FOOTER ---------- */
.reminder {
    background: linear-gradient(110deg, #075b1d, #08752a);
    color: white;
    border-radius: 10px;
    padding: 16px 18px;
    margin-top: 12px;
}

.reminder h4, .reminder p {
    color: white !important;
}

.footer {
    background: #064d19;
    color: white;
    border-radius: 0;
    padding: 10px 16px;
    text-align: center;
    margin-top: 16px;
    font-size: 0.83rem;
}

/* ---------- INPUTS / BUTTON ---------- */
.stNumberInput label {
    color: #111 !important;
    font-weight: 600 !important;
}

div.stButton > button {
    width: 100%;
    background: #078a2f;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.65rem;
    font-size: 1.02rem;
    font-weight: 800;
}

div.stButton > button:hover {
    background: #056e25;
    color: white;
}

[data-testid="stMetricValue"] {
    color: #075b1d;
}

/* ---------- AUTOMATIC DARK MODE ---------- */
@media (prefers-color-scheme: dark) {

    .stApp,
    .main .block-container {
        background: #0e160f;
        color: #f2f6f1;
    }

    .brand-row {
        background: linear-gradient(105deg, #043d14, #075d21, #043d14);
    }

    .panel,
    .bill-table {
        background: #172119;
        border-color: #315a37;
    }

    .about-panel,
    .saving-card {
        background: #192b1c;
        border-color: #385e3d;
    }

    .about-panel h3,
    h1, h2, h3 {
        color: #91d69a;
    }

    .check-line {
        color: #eef5ef;
    }

    .green-note {
        background: #19351f;
        border-color: #315d38;
        border-left-color: #39a84e;
        color: #e7f3e8;
    }

    .bill-row {
        border-bottom-color: #2d3d30;
        color: #f2f6f1;
    }

    .bill-row.header {
        background: #111a13;
        color: #bfc9c1;
    }

    .bill-row.total {
        background: #1c3a20;
        color: #a7dda9;
    }

    .amount {
        color: #8fdb98;
    }

    .solar-credit {
        color: #ff7676;
    }

    .final-card {
        background: linear-gradient(135deg, #19351f, #214426);
        border-color: #3c7545;
    }

    .final-label {
        color: #a7d9aa;
    }

    .final-value {
        color: #7ed889;
    }

    .saving-title,
    .saving-money {
        color: #8fdb98;
    }

    .reminder {
        background: linear-gradient(110deg, #043d14, #075d21);
    }

    .footer {
        background: #043d14;
    }

    .stNumberInput label,
    .stMarkdown,
    .stText,
    p,
    label {
        color: #eef5ef !important;
    }

    input,
    textarea {
        background-color: #172119 !important;
        color: #f2f6f1 !important;
        border-color: #385e3d !important;
    }

    [data-testid="stMetricValue"] {
        color: #8fdb98;
    }

    [data-testid="stMetricLabel"] {
        color: #d5e3d7;
    }

    [data-testid="stAlert"] {
        background: #19351f;
        color: #f2f6f1;
    }
}

/* ---------- MOBILE ---------- */
@media (max-width: 800px) {
    .main .block-container {
        padding-left: .55rem;
        padding-right: .55rem;
    }

    .brand-title {
        font-size: 1.8rem;
    }

    .final-value {
        font-size: 2.45rem;
    }

    .bill-row {
        padding: 9px 12px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HEADER WITH ACTUAL ENERGY UNIT LOGO
# ============================================================

logo_path = Path(__file__).parent / "energy_unit_logo.jpg"

header_left, header_right = st.columns([1.05, 2.25], vertical_alignment="center")

with header_left:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown(
            "<div style='color:#075b1d;font-size:2rem;font-weight:900;'>ENERGY UNIT</div>",
            unsafe_allow_html=True,
        )

with header_right:
    st.markdown(
        """
        <div class="brand-row">
            <div>
                <div class="brand-title">KNOW YOUR ELECTRICITY BILL</div>
                <div class="brand-subtitle">Saint Vincent and the Grenadines</div>
                <div class="brand-description">
                    Estimate your residential electricity bill and explore
                    the benefits of Solar PV.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# INPUT / ABOUT AREA
# ============================================================

left, middle, right = st.columns([1.08, 1.65, .9], gap="small")

with left:
    st.markdown(
        '<div class="section-title">📝 &nbsp;1. YOUR INPUTS</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("### ELECTRICITY CONSUMPTION")

        kwh = st.number_input(
            "Monthly consumption/ Units Used (kWh)",
            min_value=0.1,
            value=DEFAULT_KWH,
            step=1.0,
        )

        fuel_rate = st.number_input(
            "Fuel surcharge (EC$/kWh)",
            min_value=0.0,
            value=DEFAULT_FUEL_SURCHARGE,
            step=0.01,
            format="%.4f",
        )

        st.divider()
        st.markdown("### SOLAR PV (OPTIONAL)")

        solar_export = st.number_input(
            "Electricity sold to utility (kWh)",
            min_value=0.0,
            value=DEFAULT_SOLAR_EXPORT,
            step=1.0,
        )

        fit = st.number_input(
            "Feed-in Tariff (FIT)",
            min_value=0.0,
            value=DEFAULT_FIT,
            step=0.01,
            format="%.2f",
        )

        st.markdown(
            f"""
            <div class="green-note">
                <strong>ⓘ FIT (Feed-in Tariff)</strong><br>
                FIT is the rate paid by the utility for electricity
                exported to the grid.<br><br>
                Current default: <strong>EC${fit:.2f}/kWh</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.button("▣  CALCULATE BILL")

with middle:
    st.markdown(
        '<div class="section-title">🧾 &nbsp;2. YOUR ESTIMATED BILL (BEFORE SOLAR CREDIT)</div>',
        unsafe_allow_html=True,
    )

    bill = calculate_bill(kwh, fuel_rate, solar_export, fit)

    st.markdown(
        f"""
        <div class="bill-table">
            <div class="bill-row header">
                <span>DESCRIPTION</span><span>AMOUNT</span>
            </div>
            <div class="bill-row">
                <span>Energy charge</span>
                <span class="amount">{money(bill["energy_charge"])}</span>
            </div>
            <div class="bill-row">
                <span>Fuel surcharge</span>
                <span class="amount">{money(bill["fuel_charge"])}</span>
            </div>
            <div class="bill-row">
                <span>VAT (16%) ⓘ</span>
                <span class="amount">{money(bill["vat"])}</span>
            </div>
            <div class="bill-row total">
                <span>GROSS BILL</span>
                <span>{money(bill["gross_total"])}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">☀️ &nbsp;3. SOLAR PV CREDIT</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="bill-table">
            <div class="bill-row">
                <span>Solar electricity sold to utility</span>
                <span class="amount">{solar_export:,.1f} kWh</span>
            </div>
            <div class="bill-row">
                <span>Feed-in Tariff (FIT)</span>
                <span class="amount">EC$ {fit:.2f} / kWh</span>
            </div>
            <div class="bill-row">
                <span>Solar credit (FIT × kWh sold)</span>
                <span class="solar-credit">- {money(bill["solar_credit"])}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">💵 &nbsp;4. YOUR ESTIMATED BILL (AFTER SOLAR CREDIT)</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="final-card">
            <div class="final-label">ESTIMATED BILL PAYABLE</div>
            <div class="final-value">{money(bill["total"])}</div>
            <div>
                Gross bill {money(bill["gross_total"])}
                &nbsp; − &nbsp;
                Solar FIT credit {money(bill["solar_credit"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Effective cost: EC${bill['effective_rate']:.4f} per kWh"
    )

with right:
    st.markdown(
        '<div class="section-title">ⓘ &nbsp;ABOUT THIS CALCULATOR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="about-panel">
            <div class="check-line"><span class="check">●</span>
            <span><strong>Below 50 kWh:</strong> EC$0.425/kWh</span></div>

            <div class="check-line"><span class="check">●</span>
            <span><strong>50 kWh and above:</strong> EC$0.500/kWh
            (for all kWh)</span></div>

            <div class="check-line"><span class="check">●</span>
            <span><strong>VAT (16%)</strong> applies to the energy
            charge above the first 250 kWh of consumption.</span></div>

            <div class="check-line"><span class="check">●</span>
            <span><strong>Fuel surcharge</strong> is applied to all kWh.</span></div>

            <div class="check-line"><span class="check">●</span>
            <span><strong>Solar PV exports</strong> are credited at the
            applicable Feed-in Tariff (FIT) rate.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="reminder">
            <h4>🔔 TARIFF REMINDER</h4>
            <p>
            Confirm the applicable tariff, fuel surcharge and tax rules
            for the billing period before relying on this estimate for
            an official bill.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# BILL BREAKDOWN
# ============================================================

st.markdown("### Bill Breakdown")

chart_data = {
    "Basic Energy Charge": bill["energy_charge"],
    "Fuel Surcharge": bill["fuel_charge"],
    "VAT": bill["vat"],
}

st.bar_chart(chart_data)

# ============================================================
# TARIFF INFORMATION
# ============================================================

st.markdown(
    '<div class="section-title">📋 &nbsp;RESIDENTIAL TARIFF & SOLAR FIT</div>',
    unsafe_allow_html=True,
)

t1, t2, t3, t4 = st.columns(4)
t1.metric("Below 50 kWh", "EC$0.425/kWh")
t2.metric("50 kWh and above", "EC$0.500/kWh")
t3.metric("VAT", "16%")
t4.metric("Solar PV FIT", "EC$0.45/kWh")

st.write(
    "VAT is applied to the energy charge attributable to consumption "
    "above the first 250 kWh."
)

# ============================================================
# SAVINGS
# ============================================================

st.markdown(
    '<div class="section-title">🌿 &nbsp;5. SAVE BY USING LESS ENERGY</div>',
    unsafe_allow_html=True,
)

st.write(
    "Reduce your consumption and save money! See how much you could "
    "save by using less electricity."
)

save_cols = st.columns(3)

for column, pct in zip(save_cols, [10, 20, 30]):
    reduced = kwh * (1 - pct / 100)
    reduced_bill = calculate_bill(
        reduced,
        fuel_rate,
        solar_export,
        fit,
    )
    savings = bill["total"] - reduced_bill["total"]

    with column:
        st.markdown(
            f"""
            <div class="saving-card">
                <div class="saving-title">
                    {pct}% LESS ({reduced:,.1f} kWh)
                </div>
                <div style="margin-top:7px;">Estimated saving:</div>
                <div class="saving-money">{money(savings)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Energy Unit | Government of Saint Vincent and the Grenadines
        <span style="float:right;">This is an estimate for information purposes only.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "This calculator is an educational/illustrative tool. Confirm the "
    "applicable tariff, monthly fuel surcharge, Solar PV FIT and tax rules "
    "for the relevant billing period before using the result for an official bill."
)

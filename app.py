from pathlib import Path
DEFAULT_KWH = 100
DEFAULT_FUEL_SURCHARGE = 0.7355
DEFAULT_SOLAR_EXPORT = 0.0
DEFAULT_FIT = 0.45  # EC$0.45/kWh = 45 cents/kWh sold to the utility

LOW_CONSUMPTION_LIMIT = 50
LOW_ENERGY_RATE = 0.425
STANDARD_ENERGY_RATE = 0.500

VAT_THRESHOLD = 250
VAT_RATE = 16.0

def money(value):
    return f"EC$ {value:,.2f}"


def calculate_bill(kwh, fuel_rate, solar_export=0, fit=DEFAULT_FIT):
    """
    Calculate a residential electricity bill.

    Tariff:
      < 50 kWh  -> EC$0.425/kWh
      > 50 kWh  -> EC$0.500/kWh for all units

    VAT:
      16% on the energy charge associated with consumption
      above the first 250 kWh.

    Fuel surcharge is applied to all kWh.
    """

    # Energy charge
    if kwh < LOW_CONSUMPTION_LIMIT:
        energy_rate = LOW_ENERGY_RATE
    else:
        energy_rate = STANDARD_ENERGY_RATE

    energy_charge = kwh * energy_rate

    # Fuel surcharge
    fuel_charge = kwh * fuel_rate

    # VAT applies only to energy charge above 250 kWh.
    vat_kwh = max(0, kwh - VAT_THRESHOLD)
    vat_energy_charge = vat_kwh * energy_rate
    vat = vat_energy_charge * VAT_RATE / 100

    solar_credit = solar_export * fit

    gross_total = energy_charge + fuel_charge + vat
    total = max(0, gross_total - solar_credit)

    effective_rate = total / kwh if kwh > 0 else 0

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
        "effective_rate": effective_rate
    }
import streamlit as st

st.set_page_config(page_title="Know Your Electricity Bill", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.stApp { background: #f3f8f0; }
[data-testid="stHeader"] { background: #075b1d; }
.main .block-container { max-width: 1450px; padding-top: 1rem; }
.hero { background: linear-gradient(110deg,#064d19,#08752a); border-radius: 16px; padding: 24px 30px; color:white; margin-bottom:18px; box-shadow:0 4px 14px rgba(0,0,0,.12); }
.hero h1 { color:white; font-size:2.5rem; margin:0; font-weight:800; }
.hero p { color:white; margin:4px 0; font-size:1.05rem; }
.section-title { background:#08752a; color:white; border-radius:10px 10px 0 0; padding:10px 15px; font-weight:800; font-size:1.08rem; margin-top:8px; }
.result-card { background:linear-gradient(135deg,#eaf6dc,#dff0cc); border:1px solid #b7d99e; border-radius:14px; padding:22px; text-align:center; }
.result-label { color:#176322; font-weight:700; }
.result-value { color:#075b1d; font-size:3rem; font-weight:850; line-height:1.1; }
.green-note { background:#e9f5df; border-left:5px solid #159447; border-radius:7px; padding:11px 14px; color:#174d21; margin:8px 0 12px; }
.reminder { background:#086421; color:white; border-radius:12px; padding:17px; }
.reminder h4 { color:white; margin-top:0; }
div.stButton > button { width:100%; background:#078a2f; color:white; border:none; border-radius:9px; font-weight:800; padding:.7rem; }
[data-testid="stMetricValue"] { color:#075b1d; }
.footer { background:#064d19; color:white; border-radius:10px; padding:12px; text-align:center; margin-top:20px; }

/* AUTOMATIC DARK MODE ONLY - original light-mode design unchanged */
@media (prefers-color-scheme: dark) {
.stApp { background:#101810; color:#f2f6f1; }
[data-testid="stHeader"] { background:#064d19; }
.hero { background:linear-gradient(110deg,#064d19,#08752a); color:white; }
.hero h1,.hero p { color:white; }
.section-title { background:#08752a; color:white; }
.result-card { background:linear-gradient(135deg,#19351f,#214426); border-color:#397344; color:#f2f6f1; }
.result-label { color:#a7d9aa; }
.result-value { color:#7ed889; }
.green-note { background:#19351f; border-left-color:#159447; color:#e7f3e8; }
.reminder { background:#064d19; color:white; }
.reminder h4 { color:white; }
.footer { background:#043d14; color:white; }
[data-testid="stMetricValue"] { color:#7ed889; }
[data-testid="stMetricLabel"] { color:#d7e5d8; }
.stNumberInput label,.stSelectbox label,.stTextInput label,.stMarkdown,.stText,p { color:#eef5ef !important; }
input,textarea { background-color:#182219 !important; color:#f2f6f1 !important; border-color:#315a37 !important; }
div.stButton > button { background:#078a2f; color:white; }
div.stButton > button:hover { background:#056e25; color:white; }
[data-testid="stAlert"] { background:#19351f; color:#f2f6f1; }
}

</style>
""", unsafe_allow_html=True)

hero_left, hero_right = st.columns([1, 2.2], vertical_alignment="center")
with hero_left:
    if Path("energy_unit_logo.jpg").exists():
        st.image("energy_unit_logo.jpg", width=480)
    else:
        st.markdown("<h2 style='color:#075b1d'>ENERGY UNIT</h2>", unsafe_allow_html=True)
with hero_right:
    st.markdown("""<div class="hero"><h1>KNOW YOUR ELECTRICITY BILL</h1><p><strong>Saint Vincent and the Grenadines</strong></p><p>Estimate your residential electricity bill and explore the benefits of Solar PV.</p></div>""", unsafe_allow_html=True)

st.markdown('<div class="section-title">📋 1. RESIDENTIAL TARIFF & SOLAR FIT</div>', unsafe_allow_html=True)
a,b,c,d = st.columns(4)
a.metric("Below 50 kWh", "EC$0.425/kWh")
b.metric("50 kWh and above", "EC$0.500/kWh")
c.metric("VAT", "16%")
d.metric("Solar PV FIT", "EC$0.45/kWh")
st.write("VAT is applied to the energy charge attributable to consumption above the first 250 kWh.")

left, right = st.columns(2)
with left:
    st.markdown('<div class="section-title">📝 2. YOUR INPUTS</div>', unsafe_allow_html=True)
    st.markdown("### ELECTRICITY CONSUMPTION")
    kwh = st.number_input("Monthly electricity consumption/Units Used (kWh)", min_value=0.1, value=float(DEFAULT_KWH), step=1.0)
    fuel_rate = st.number_input("Fuel surcharge (EC$/kWh)", min_value=0.0, value=float(DEFAULT_FUEL_SURCHARGE), step=0.01, format="%.4f")

with right:
    st.markdown("### ☀️ SOLAR PV (OPTIONAL)")
    solar_export = st.number_input("Solar PV electricity sold to the utility (kWh)", min_value=0.0, value=float(DEFAULT_SOLAR_EXPORT), step=1.0)
    fit = st.number_input("Solar PV Feed-in Tariff (EC$/kWh)", min_value=0.0, value=float(DEFAULT_FIT), step=0.01, format="%.2f")

st.markdown(f"""<div class="green-note"><strong>☀️ Solar FIT (Feed-in Tariff)</strong> is the rate paid by the utility for electricity exported to the grid. Current default: <strong>EC${fit:.2f}/kWh</strong>.</div>""", unsafe_allow_html=True)
bill = calculate_bill(kwh, fuel_rate, solar_export, fit)

st.markdown('<div class="section-title">🧾 3. YOUR ESTIMATED BILL (BEFORE SOLAR CREDIT)</div>', unsafe_allow_html=True)
a,b,c,d = st.columns(4)
a.metric("Energy Charge", money(bill["energy_charge"]))
b.metric("Fuel Surcharge", money(bill["fuel_charge"]))
c.metric("VAT", money(bill["vat"]))
d.metric("Solar FIT Credit", f"- {money(bill['solar_credit'])}")
st.divider()
a,b = st.columns(2)
a.metric("Gross Bill Before Solar Credit", money(bill["gross_total"]))
b.metric("Solar FIT Credit", f"- {money(bill['solar_credit'])}")
st.markdown(f"""<div class="result-card"><div class="result-label">ESTIMATED BILL PAYABLE</div><div class="result-value">{money(bill["total"])}</div><div>Gross bill {money(bill["gross_total"])} &nbsp;−&nbsp; Solar FIT credit {money(bill["solar_credit"])}</div></div>""", unsafe_allow_html=True)
st.caption(f"Effective cost: EC${bill['effective_rate']:.4f} per kWh")

st.markdown('<div class="section-title"> 📊 4. BILL BREAKDOWN </div>', unsafe_allow_html=True)
st.bar_chart({"Basic Energy Charge": bill["energy_charge"], "Fuel Surcharge": bill["fuel_charge"], "VAT": bill["vat"]})

st.markdown('<div class="section-title">☀️ 5. SOLAR PV CREDIT</div>', unsafe_allow_html=True)
a,b,c = st.columns(3)
a.metric("Electricity Sold", f"{solar_export:,.1f} kWh")
b.metric("FIT", f"EC${fit:.2f} / kWh")
c.metric("FIT Credit", money(bill["solar_credit"]))

st.markdown('<div class="section-title">🌿 6. SAVE BY USING LESS ENERGY</div>', unsafe_allow_html=True)
for pct in [10,20,30]:
    reduced = kwh * (1 - pct/100)
    rb = calculate_bill(reduced, fuel_rate, solar_export, fit)
    savings = bill["total"] - rb["total"]
    st.write(f"**{pct}% reduction:** {reduced:,.1f} kWh → estimated saving of **{money(savings)}**")

st.divider()
st.markdown('<div class="footer">Energy Unit | Government of St. Vincent & the Grenadines | Saint Vincent and the Grenadines<br>This is an estimate for information purposes only.</div>', unsafe_allow_html=True)

st.warning("This calculator is an educational/illustrative tool. Confirm the applicable tariff, monthly fuel surcharge, Solar PV FIT and tax rules for the relevant billing period before using the result for an official bill.")
   

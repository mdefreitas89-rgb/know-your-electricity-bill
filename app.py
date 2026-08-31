DEFAULT_KWH = 299
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
st.title("⚡ Know Your Electricity Bill")
st.subheader("Energy Unit • Saint Vincent and the Grenadines")
st.write("Residential electricity bill calculator with grid-connected Solar PV Feed-in Tariff (FIT).")
st.divider()

left, right = st.columns(2)
with left:
    st.markdown("### Electricity Bill")
    kwh = st.number_input("Monthly electricity consumption (kWh)", min_value=0.1, value=float(DEFAULT_KWH), step=1.0)
    fuel_rate = st.number_input("Fuel surcharge (EC$/kWh)", min_value=0.0, value=float(DEFAULT_FUEL_SURCHARGE), step=0.01, format="%.4f")
with right:
    st.markdown("### ☀️ Solar PV / Net Metering")
    solar_export = st.number_input("Solar PV electricity sold to the utility (kWh)", min_value=0.0, value=float(DEFAULT_SOLAR_EXPORT), step=1.0)
    fit = st.number_input("Solar PV Feed-in Tariff (EC$/kWh)", min_value=0.0, value=float(DEFAULT_FIT), step=0.01, format="%.2f")

st.info(f"☀️ Solar PV FIT: **EC${fit:.2f} per kWh** sold to the utility. 100 kWh at EC$0.45/kWh = EC$45.00 credit.")
bill = calculate_bill(kwh, fuel_rate, solar_export, fit)

st.markdown("## Your Estimated Bill")
a,b,c,d = st.columns(4)
a.metric("Energy Charge", money(bill["energy_charge"]))
b.metric("Fuel Surcharge", money(bill["fuel_charge"]))
c.metric("VAT", money(bill["vat"]))
d.metric("Solar FIT Credit", f"- {money(bill['solar_credit'])}")
st.divider()
a,b = st.columns(2)
a.metric("Gross Bill Before Solar Credit", money(bill["gross_total"]))
b.metric("ESTIMATED BILL AFTER SOLAR", money(bill["total"]))
st.caption(f"Effective cost: EC${bill['effective_rate']:.4f} per kWh")

st.markdown("### ☀️ Solar PV FIT Calculation")
a,b,c = st.columns(3)
a.metric("Electricity Sold", f"{solar_export:,.1f} kWh")
b.metric("FIT", f"EC${fit:.2f} / kWh")
c.metric("FIT Credit", money(bill["solar_credit"]))

st.markdown("### Bill Breakdown")
st.bar_chart({"Basic Energy Charge": bill["energy_charge"], "Fuel Surcharge": bill["fuel_charge"], "VAT": bill["vat"]})

st.markdown("## Residential Tariff Structure")
a,b,c,d = st.columns(4)
a.metric("Below 50 kWh", "EC$0.425/kWh")
b.metric("50 kWh and above", "EC$0.500/kWh")
c.metric("VAT", "16%")
d.metric("Solar PV FIT", "EC$0.45/kWh")
st.write("VAT is applied to the energy charge attributable to consumption above the first 250 kWh.")

st.markdown("## What If You Reduce Electricity Use?")
for pct in [10,20,30]:
    reduced = kwh * (1 - pct/100)
    rb = calculate_bill(reduced, fuel_rate, solar_export, fit)
    savings = bill["total"] - rb["total"]
    st.write(f"**{pct}% reduction:** {reduced:,.1f} kWh → estimated saving of **{money(savings)}**")

st.divider()
st.warning("This calculator is an educational/illustrative tool. Confirm the applicable tariff, monthly fuel surcharge, Solar PV FIT and tax rules for the relevant billing period before using the result for an official bill.")

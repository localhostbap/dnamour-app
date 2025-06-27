import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor

st.set_page_config(page_title="DNAmour 💖", layout="centered")

# --- Styling ---
st.markdown("""
<style>
.stApp {
    background-image: url('https://images.unsplash.com/photo-1580130379359-42b64d5b222e?fit=crop&w=1400&q=80');
    background-size: cover;
    background-attachment: fixed;
}
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}
.pulse {
  animation: pulse 2s infinite;
  font-weight: bold;
  color: #c2185b;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("💘 About DNAmour")
st.sidebar.markdown("""
Compare your DNA with your partner’s  
and receive a personalized certificate  
of compatibility.  

🔒 No data is stored or shared.  

🎥 [How to download your 23andMe data](https://www.youtube.com/watch?v=1vf-IjMmJXE)
""")

# Donation prompt
st.markdown("""
<div class='pulse' style='background-color:#fff0f5;padding:15px;border-radius:10px;text-align:center'>
💖 <b>Enjoying DNAmour?</b><br>
If this made you smile or feel closer,<br>
<a href='https://www.paypal.com/donate/?hosted_button_id=RGPSQ9FUYA89L' target='_blank'>👉 Donate via PayPal</a>
</div>
""", unsafe_allow_html=True)

# Relevant SNPs
relevant_snps = {
    'rs53576': 'OXTR',
    'rs1800955': 'DRD4',
    'rs1042778': 'OXTR',
    'rs25531': 'SLC6A4',
    'rs113341849': 'HLA-A',
    'rs11568821': 'HLA-B'
}

# Load DNA
def load_23andme(file):
    df = pd.read_csv(file, sep='\t', comment='#', names=['rsid', 'chromosome', 'position', 'genotype'])
    return df[df['rsid'].isin(relevant_snps)].set_index('rsid')['genotype'].to_dict()

# Compatibility logic
def compute_compatibility(p1, p2):
    breakdown = {
        "Immune System Variety (HLA)": sum(1 for snp in ['rs113341849', 'rs11568821'] if p1.get(snp) != p2.get(snp)) * 20,
        "Bonding Potential (OXTR)": 20 if p1.get('rs53576') == p2.get('rs53576') else 0,
        "Adventure vs Stability Balance": 20 if p1.get('rs1800955') != p2.get('rs1800955') else 0,
        "Emotional Balance (SLC6A4)": 20 if p1.get('rs25531') != p2.get('rs25531') else 0
    }
    return sum(breakdown.values()), breakdown

# Interpretation
def interpret_traits(breakdown):
    return [
        "🧬 Strong immune diversity!" if breakdown["Immune System Variety (HLA)"] >= 20 else "🧬 You may share immune traits.",
        "💗 Deep emotional bonding potential." if breakdown["Bonding Potential (OXTR)"] == 20 else "💗 Oxytocin gene differs — connection may be unique.",
        "🎢 Great balance of adventure and calm." if breakdown["Adventure vs Stability Balance"] == 20 else "🎢 Similar dopamine styles.",
        "🧘 Complementary emotional rhythms." if breakdown["Emotional Balance (SLC6A4)"] == 20 else "🧘 Similar serotonin responses."
    ]

# Generate Certificate
def generate_certificate(score, breakdown, names):
    buffer = BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    pastel = HexColor("#fff5fa")
    border = HexColor("#e0a9c3")
    title = HexColor("#6a1b9a")
    text = HexColor("#4a148c")
    quote = HexColor("#512da8")

    c.setFillColor(pastel)
    c.rect(0, 0, width, height, fill=True, stroke=False)
    c.setStrokeColor(border)
    c.setLineWidth(8)
    c.rect(40, 40, width - 80, height - 80)

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(title)
    c.drawCentredString(width / 2, height - 70, "💞 DNAmour Compatibility Certificate 💞")

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(text)
    c.drawCentredString(width / 2, height - 120, f"{names[0]} ❤❤ {names[1]}")

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 160, f"Genetic Compatibility Score: {score} / 100")

    c.setFont("Helvetica", 13)
    y = height - 210
    for trait, pts in breakdown.items():
        c.drawCentredString(width / 2, y, f"{trait}: {pts} points")
        y -= 18

    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(quote)
    c.drawCentredString(width / 2, 105, "“Love written in your genes, sealed by your hearts.”")
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 85, "Even if your score is low, love is built with trust, effort, and connection.")
    c.setFont("Helvetica", 9)
    c.setFillColor(text)
    c.drawCentredString(width / 2, 55, f"🖊 Certified by DNAmour Labs • Issued on {datetime.now().strftime('%B %d, %Y')}")

    c.save()
    buffer.seek(0)
    return buffer

# Upload UI
col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("📤 Upload Your DNA", type=["txt"])
with col2:
    file2 = st.file_uploader("📤 Upload Partner's DNA", type=["txt"])

if file1 and file2:
    p1 = load_23andme(file1)
    p2 = load_23andme(file2)
    score, breakdown = compute_compatibility(p1, p2)

    st.markdown("### 📜 Claim Your Love Certificate")
    name1 = st.text_input("Your Name", "Partner 1")
    name2 = st.text_input("Partner's Name", "Partner 2")

    if name1 and name2:
        pdf = generate_certificate(score, breakdown, (name1, name2))
        st.download_button("📄 Download Certificate", pdf, file_name="dnAmour_certificate.pdf")

    st.markdown("## 💖 Compatibility Score")
    if score >= 90:
        st.success("🌟 Outstanding match! You’re genetically aligned.")
    elif score >= 70:
        st.info("💖 Strong compatibility. You’re a great match.")
    elif score >= 40:
        st.warning("🤝 Moderate match — complementary traits.")
    else:
        st.error("🧩 Low compatibility — but love is more than DNA!")

    st.metric("Score", f"{score}/100")

    st.markdown("### 🧠 Score Breakdown")
    st.bar_chart(pd.DataFrame.from_dict(breakdown, orient="index", columns=["Points"]))

    st.markdown("### 💬 What This Says About You")
    for line in interpret_traits(breakdown):
        st.write("•", line)
else:
    st.info("Please upload both DNA files to begin.")

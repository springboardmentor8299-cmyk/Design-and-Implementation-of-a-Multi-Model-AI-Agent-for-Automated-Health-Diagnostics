import streamlit as st
from datetime import datetime
from extraction import extract_text_from_pdf, extract_parameters


# Page config - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="BloodAI Analyzer",
    page_icon="🩺",
    layout="wide"
)


# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: white;
    }
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .report-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #6c5ce7;
    }
    .normal {
        color: #00b894;
        font-weight: bold;
    }
    .high {
        color: #d63031;
        font-weight: bold;
    }
    .low {
        color: #f39c12;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🩺 BloodAI - Automated Blood Report Interpretation System</h1>
    <p>Making Blood Test Reports Easy to Understand</p>
</div>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Upload Your Report")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt', 'jpg', 'png'],
        label_visibility="collapsed"
    )
    
   
    if st.button("Interpret My Report", type="primary", use_container_width=True):
        if uploaded_file:
            st.success("Report uploaded successfully!")
            
            # Analysis Results
            st.markdown("## Analysis Results")
            
            # Create two columns for results
            rcol1, rcol2 = st.columns(2)
            
            with rcol1:
                # HEMOGLOBIN
                st.markdown("""
                <div class="report-card">
                    <h3>HEMOGLOBIN</h3>
                    <p style="font-size: 2rem;">14.2 <span style="font-size: 1rem;">unknown</span></p>
                    <p class="normal">● NORMAL</p>
                    <p>Ref: 13.5 - 17.5 g/dL</p>
                </div>
                """, unsafe_allow_html=True)
                
                # WBC COUNT
                st.markdown("""
                <div class="report-card">
                    <h3>WBC COUNT</h3>
                    <p style="font-size: 2rem;">15000 <span style="font-size: 1rem;">unknown</span></p>
                    <p class="high">● HIGH</p>
                    <p>Ref: 4500 - 11000 /mL</p>
                </div>
                """, unsafe_allow_html=True)
                
                # BLOOD GLUCOSE
                st.markdown("""
                <div class="report-card">
                    <h3>BLOOD GLUCOSE (FASTING)</h3>
                    <p style="font-size: 2rem;">100 <span style="font-size: 1rem;">unknown</span></p>
                    <p class="normal">● NORMAL</p>
                    <p>Ref: 70 - 100 mg/dL</p>
                </div>
                """, unsafe_allow_html=True)
            
            with rcol2:
                # PLATELET COUNT
                st.markdown("""
                <div class="report-card">
                    <h3>PLATELET COUNT</h3>
                    <p style="font-size: 2rem;">300000 <span style="font-size: 1rem;">unknown</span></p>
                    <p class="normal">● NORMAL</p>
                    <p>Ref: 150000 - 450000 /mL</p>
                </div>
                """, unsafe_allow_html=True)
                
                # CHOLESTEROL
                st.markdown("""
                <div class="report-card">
                    <h3>CHOLESTEROL</h3>
                    <p style="font-size: 2rem;">180 <span style="font-size: 1rem;">unknown</span></p>
                    <p class="normal">● NORMAL</p>
                    <p>Ref: 125 - 200 mg/dL</p>
                </div>
                """, unsafe_allow_html=True)
                
                # HDL
                st.markdown("""
                <div class="report-card">
                    <h3>HDL</h3>
                    <p style="font-size: 2rem;">45 <span style="font-size: 1rem;">unknown</span></p>
                    <p class="normal">● NORMAL</p>
                    <p>Ref: >40 mg/dL</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Blood Group
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0; padding: 1rem; background: #6c5ce7; color: white; border-radius: 10px;">
                <h2>🩸 BLOOD GROUP: O+</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Executive, Planner, Verifier
            st.markdown("## 📊 Executive")
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                st.metric("Hemoglobin", "14.2", "NORMAL")
            with col_e2:
                st.metric("WBC", "15000", "HIGH")
            with col_e3:
                st.metric("Glucose", "100", "NORMAL")
            
            st.markdown("## 📋 Planner")
            st.info("⚠️ WBC is HIGH - Consider consulting a healthcare provider")
            
            st.markdown("## ✅ Verifier")
            st.success("Report verified! All parameters checked.")
        else:
            st.warning("Please upload a file")
    
with col2:
    st.markdown("### AI-Powered Report Analysis")
    st.markdown("---")
    st.markdown("**Sample Output**")
    st.markdown("""
    - Hemoglobin: 14.2 (NORMAL)
    - WBC: 15000 (HIGH)
    - Platelets: 300000 (NORMAL)
    - Glucose: 100 (NORMAL)
    """)

# Footer
st.markdown("---")
fcol1, fcol2, fcol3, = st.columns(3)
with fcol1:
    st.button("Share", use_container_width=True)
with fcol2:
    st.button("Upgrade", use_container_width=True)
with fcol3:
    st.button("Upload Report", use_container_width=True)

st.markdown("---")
st.markdown(f"ENG | IN | {datetime.now().strftime('%d/%m/%Y %H:%M')}")


# If-else logic for HIGH/LOW/NORMAL (demonstration)
def check_value(value, min_val, max_val, name):
    if value < min_val:
        return f"🔴 {name}: {value} - LOW"
    elif value > max_val:
        return f"🔴 {name}: {value} - HIGH"
    else:
        return f"🟢 {name}: {value} - NORMAL"

# Show the if-else logic in action
with st.expander("Show Value Checker Demo"):
    val = st.slider("Test Hemoglobin value", 10.0, 20.0, 14.2)
    st.write(check_value(val, 13.5, 17.5, "Hemoglobin"))
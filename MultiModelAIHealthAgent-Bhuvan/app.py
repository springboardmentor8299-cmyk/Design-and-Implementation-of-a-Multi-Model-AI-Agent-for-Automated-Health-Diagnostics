import streamlit as st
from orchestrator import MultiModelOrchestrator
import os
import tempfile

st.set_page_config(page_title="Health Diagnostics AI", page_icon="🏥", layout="wide")

st.title("🏥 Multi-Model AI Health Diagnostics")
st.markdown("Upload your blood report for automated analysis and personalized recommendations")

orchestrator = MultiModelOrchestrator()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Upload Blood Report")
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'png', 'jpg', 'jpeg', 'json'])

with col2:
    st.subheader("Patient Context")
    age = st.number_input("Age", min_value=1, max_value=120, value=30)
    gender = st.selectbox("Gender", ["male", "female"])
    family_history = st.text_area("Family History (Optional)", placeholder="e.g., diabetes, heart disease")

if st.button("🔍 Analyze Report", type="primary", use_container_width=True):
    if uploaded_file:
        with st.spinner("Analyzing your blood report..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            context = {
                'age': age,
                'gender': gender,
                'family_history': family_history
            }
            
            file_type = uploaded_file.name.split('.')[-1].lower()
            result = orchestrator.process(tmp_path, file_type, context)
            os.unlink(tmp_path)
            
            st.success("Analysis Complete!")
            
            st.markdown("---")
            st.subheader("📊 Findings")
            st.info(result['findings']['summary'])
            
            st.subheader("🔬 Parameter Details")
            for param, info in result['findings']['interpretations'].items():
                status_color = "🟢" if info['status'] == 'normal' else "🔴"
                st.markdown(f"{status_color} **{param.upper()}**: {info['value']} ({info['status']}) - *Reference: {info['reference']}*")
            
            model2 = result['findings']['model2_output']
            
            if model2.get('patterns'):
                st.subheader("🔍 Patterns Identified")
                for pattern in model2['patterns']:
                    st.info(f"**{pattern['name'].replace('_', ' ').title()}** - Confidence: {pattern['confidence']:.0%}")
            
            if model2.get('risks'):
                st.subheader("⚠️ Risk Assessment")
                for risk in model2['risks']:
                    risk_emoji = "🔴" if risk['level'] == 'high' else "🟡" if risk['level'] == 'moderate' else "🟢"
                    st.warning(f"{risk_emoji} **{risk['type'].upper()}** Risk - Level: {risk['level']} | Score: {risk['score']}")
                    st.write(f"Factors: {', '.join(risk['factors'])}")
            
            if model2.get('correlations'):
                st.subheader("🔗 Parameter Correlations")
                for corr in model2['correlations']:
                    st.info(f"**{' & '.join(corr['parameters'])}**: {corr['implication'].replace('_', ' ').title()}")
            
            contextual = result['findings']['contextual']
            if contextual.get('adjustments'):
                st.subheader("👤 Contextual Analysis")
                st.write(f"Age Group: {contextual.get('age_group', 'N/A').replace('_', ' ').title()}")
                for adj in contextual['adjustments']:
                    priority_color = "🔴" if adj['priority'] == 'high' else "🟡"
                    st.write(f"{priority_color} {adj['message']}")
                
                if contextual.get('adjusted_risks'):
                    st.write("**Risk Score Adjustments:**")
                    for risk in contextual['adjusted_risks']:
                        st.write(f"- {risk['type']}: {risk['original_score']} → {risk['adjusted_score']} (modifier: {risk['modifier']}x)")
            
            st.markdown("---")
            st.subheader("💡 Personalized Recommendations")
            st.write(result['recommendations'])
            
            st.markdown("---")
            st.error(f"⚠️ **Disclaimer**: {result['disclaimer']}")
    else:
        st.warning("Please upload a blood report file")

with st.sidebar:
    st.header("About")
    st.markdown("""
    This AI system analyzes blood reports using three specialized models:
    
    - **Model 1**: Parameter interpretation
    - **Model 2**: Pattern recognition, risk scoring & correlations
    - **Model 3**: Contextual analysis with age/gender/family history
    
    Supported formats: PDF, Images, JSON
    """)
    
    st.header("Sample Data")
    if st.button("View Sample Report"):
        st.json({
            "hemoglobin": 14.5,
            "glucose": 110,
            "cholesterol_total": 220,
            "ldl": 140,
            "hdl": 45,
            "triglycerides": 160
        })

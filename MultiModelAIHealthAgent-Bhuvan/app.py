import streamlit as st
from orchestrator import MultiModelOrchestrator
import os
import tempfile
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import REFERENCE_RANGES

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
            findings     = result['findings']
            model2       = findings['model2_output']
            contextual   = findings['contextual']
            interpretations = findings['interpretations']

            # ── Overall severity banner ───────────────────────────────────────
            severity = findings.get('overall_severity', 'normal')
            sev_color = {'critical': '#d32f2f', 'high': '#e64a19',
                         'moderate': '#f9a825', 'low': '#388e3c', 'normal': '#1565c0'}
            st.markdown(
                f"""<div style='background:{sev_color.get(severity,'#1565c0')};padding:12px 20px;
                border-radius:8px;color:white;font-size:16px;font-weight:600;margin-bottom:8px'>
                Overall Severity: {severity.upper()}
                </div>""", unsafe_allow_html=True
            )

            # ── Summary ───────────────────────────────────────────────────────
            st.markdown("---")
            st.subheader("📋 Summary")
            st.info(findings['summary'])

            # ── Parameter Details ─────────────────────────────────────────────
            st.markdown("---")
            st.subheader("🔬 Parameter Details")

            if interpretations:
                params, values, ref_mins, ref_maxs, statuses, units = [], [], [], [], [], []
                for param, info in interpretations.items():
                    ref = REFERENCE_RANGES.get(param, {})
                    gender_key = gender if gender in ref else 'normal'
                    rng = ref.get(gender_key, (0, 999))
                    params.append(param.replace('_', ' ').title())
                    values.append(info['value'])
                    ref_mins.append(rng[0])
                    ref_maxs.append(rng[1] if rng[1] != 999 else info['value'] * 1.5)
                    statuses.append(info['status'])
                    units.append(ref.get('unit', ''))

                bar_colors = ['#d32f2f' if s in ('high', 'low') else '#43a047' for s in statuses]

                fig_bar = go.Figure()
                # Reference range band
                for i, param in enumerate(params):
                    fig_bar.add_shape(type='rect',
                        x0=ref_mins[i], x1=ref_maxs[i], y0=i - 0.4, y1=i + 0.4,
                        fillcolor='rgba(100,181,246,0.25)', line_width=0)
                # Actual value bars
                fig_bar.add_trace(go.Bar(
                    y=params, x=values,
                    orientation='h',
                    marker_color=bar_colors,
                    text=[f"{v} {u}" for v, u in zip(values, units)],
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Value: %{x}<extra></extra>'
                ))
                fig_bar.update_layout(
                    height=max(300, len(params) * 55),
                    margin=dict(l=10, r=80, t=30, b=10),
                    xaxis_title='Value',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    font=dict(size=13)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                st.caption("🔵 Blue band = normal reference range  |  🟢 Green bar = normal  |  🔴 Red bar = abnormal")

                # Text table below chart
                rows = []
                for param, info in interpretations.items():
                    icon = "🟢" if info['status'] == 'normal' else ("🔴" if info['status'] == 'high' else "🔵")
                    rows.append({
                        'Status': icon,
                        'Parameter': param.replace('_', ' ').title(),
                        'Value': info['value'],
                        'Result': info['status'].upper(),
                        'Reference Range': info['reference']
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # ── Patterns Identified ───────────────────────────────────────────
            st.markdown("---")
            st.subheader("🔍 Patterns Identified")

            patterns = model2.get('patterns', [])
            if patterns:
                pcol1, pcol2 = st.columns([1, 1])

                with pcol1:
                    # Pie chart of confidence scores
                    p_names = [p['name'].replace('_', ' ').title() for p in patterns]
                    p_conf  = [round(p['confidence'] * 100, 1) for p in patterns]
                    pie_colors = px.colors.qualitative.Set2[:len(patterns)]
                    fig_pie = go.Figure(go.Pie(
                        labels=p_names, values=p_conf,
                        hole=0.4,
                        marker=dict(colors=pie_colors),
                        textinfo='label+percent',
                        hovertemplate='<b>%{label}</b><br>Confidence: %{value}%<extra></extra>'
                    ))
                    fig_pie.update_layout(
                        title='Pattern Confidence Distribution',
                        height=320,
                        margin=dict(l=10, r=10, t=40, b=10),
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with pcol2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    for p in patterns:
                        conf = p['confidence']
                        badge_color = '#d32f2f' if conf >= 0.85 else '#f9a825'
                        st.markdown(
                            f"""<div style='border-left:5px solid {badge_color};padding:10px 14px;
                            margin-bottom:10px;background:#1e1e2e;border-radius:6px'>
                            <b style='font-size:15px'>{p['name'].replace('_',' ').title()}</b><br>
                            <span style='color:#aaa;font-size:13px'>Confidence: 
                            <b style='color:{badge_color}'>{conf:.0%}</b></span>
                            </div>""", unsafe_allow_html=True
                        )
            else:
                st.success("No significant patterns detected.")

            # ── Risk Assessment ───────────────────────────────────────────────
            st.markdown("---")
            st.subheader("⚠️ Risk Assessment")

            risks = model2.get('risks', [])
            adjusted_risks = contextual.get('adjusted_risks', [])
            adjusted_map = {r['type']: r for r in adjusted_risks}

            if risks:
                rcol1, rcol2 = st.columns([1, 1])

                with rcol1:
                    risk_names  = [r['type'].replace('_', ' ').title() for r in risks]
                    orig_scores = [r['score'] for r in risks]
                    adj_scores  = [adjusted_map.get(r['type'], {}).get('adjusted_score', r['score']) for r in risks]
                    level_colors = {'high': '#d32f2f', 'moderate': '#f9a825', 'low': '#43a047'}
                    bar_clrs = [level_colors.get(r['level'], '#90a4ae') for r in risks]

                    fig_risk = go.Figure()
                    fig_risk.add_trace(go.Bar(
                        name='Original Score', x=risk_names, y=orig_scores,
                        marker_color=bar_clrs, opacity=0.75,
                        text=orig_scores, textposition='outside'
                    ))
                    if any(adjusted_map):
                        fig_risk.add_trace(go.Bar(
                            name='Adjusted Score', x=risk_names, y=adj_scores,
                            marker_color='#7e57c2', opacity=0.85,
                            text=adj_scores, textposition='outside'
                        ))
                    fig_risk.update_layout(
                        barmode='group',
                        height=320,
                        yaxis_title='Risk Score',
                        margin=dict(l=10, r=10, t=30, b=10),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        legend=dict(orientation='h', y=-0.2),
                        font=dict(size=13)
                    )
                    st.plotly_chart(fig_risk, use_container_width=True)

                with rcol2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    for risk in risks:
                        lvl = risk['level']
                        clr = level_colors.get(lvl, '#90a4ae')
                        adj = adjusted_map.get(risk['type'], {})
                        adj_line = (
                            f"<br><span style='color:#ce93d8;font-size:12px'>Adjusted score: "
                            f"{adj['adjusted_score']} (×{adj['modifier']})</span>"
                        ) if adj else ''
                        factors_html = ''.join(
                            f"<li style='font-size:12px;color:#ccc'>{f}</li>"
                            for f in risk.get('factors', [])
                        )
                        st.markdown(
                            f"""<div style='border-left:5px solid {clr};padding:10px 14px;
                            margin-bottom:10px;background:#1e1e2e;border-radius:6px'>
                            <b style='font-size:15px'>{risk['type'].replace('_',' ').title()} Risk</b>
                            <span style='float:right;background:{clr};color:white;padding:2px 10px;
                            border-radius:12px;font-size:12px'>{lvl.upper()}</span><br>
                            <span style='color:#aaa;font-size:13px'>Score: <b>{risk['score']}</b></span>
                            {adj_line}<br>
                            <ul style='margin:6px 0 0 0;padding-left:16px'>{factors_html}</ul>
                            </div>""", unsafe_allow_html=True
                        )
            else:
                st.success("No significant risks identified.")

            # ── Correlations ──────────────────────────────────────────────────
            if model2.get('correlations'):
                st.markdown("---")
                st.subheader("🔗 Parameter Correlations")
                for corr in model2['correlations']:
                    st.info(
                        f"**{' & '.join(p.replace('_',' ').title() for p in corr['parameters'])}** — "
                        f"{corr['implication'].replace('_', ' ').title()}"
                    )

            # ── Contextual Analysis ───────────────────────────────────────────
            if contextual.get('adjustments'):
                st.markdown("---")
                st.subheader("👤 Contextual Analysis")
                age_group = contextual.get('age_group', 'N/A').replace('_', ' ').title()
                st.markdown(f"**Age Group:** {age_group}")
                for adj in contextual['adjustments']:
                    clr = '#d32f2f' if adj['priority'] == 'high' else '#f9a825'
                    icon = '🔴' if adj['priority'] == 'high' else '🟡'
                    st.markdown(
                        f"""<div style='border-left:4px solid {clr};padding:8px 12px;
                        margin-bottom:6px;background:#1e1e2e;border-radius:5px'>
                        {icon} {adj['message']}</div>""",
                        unsafe_allow_html=True
                    )

            # ── Recommendations ───────────────────────────────────────────────
            st.markdown("---")
            st.subheader("💡 Personalized Recommendations")

            recs = result['recommendations']
            if isinstance(recs, list):
                category_icons = {'diet': '🥗', 'lifestyle': '🏃', 'follow_up': '🩺'}
                cat_colors     = {'diet': '#2e7d32', 'lifestyle': '#1565c0', 'follow_up': '#6a1b9a'}
                grouped = {}
                for r in recs:
                    grouped.setdefault(r['category'], []).append(r)

                for cat in ['diet', 'lifestyle', 'follow_up']:
                    if cat not in grouped:
                        continue
                    icon = category_icons[cat]
                    clr  = cat_colors[cat]
                    st.markdown(
                        f"""<div style='background:{clr};padding:6px 14px;border-radius:6px;
                        color:white;font-weight:600;font-size:15px;margin:10px 0 6px'>
                        {icon} {cat.replace('_',' ').title()}</div>""",
                        unsafe_allow_html=True
                    )
                    for r in grouped[cat]:
                        fid = r.get('finding_id', '')
                        tag = (
                            f" <span style='font-size:11px;color:#90caf9;font-style:italic'>"
                            f"↳ {fid.replace('_',' ')}</span>"
                        ) if fid and fid not in ('general', 'llm_enriched') else ''
                        st.markdown(
                            f"<div style='padding:6px 12px;margin-bottom:4px;border-radius:4px;"
                            f"background:#1e1e2e'>• {r['advice']}{tag}</div>",
                            unsafe_allow_html=True
                        )
            else:
                st.write(recs)

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

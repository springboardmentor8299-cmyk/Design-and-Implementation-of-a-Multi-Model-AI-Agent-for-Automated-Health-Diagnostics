import streamlit as st
import json
import os
import pandas as pd

from scanner.ocr_engine import scan_pdf, scan_image
from processing.extractor import extract_parameters_from_text
from processing.comparator import compare_with_ranges
from processing.risk_analyzer import analyze_risk
from api.medical_api import fetch_reference_ranges
from evaluation.evaluate import evaluate_single_report


st.set_page_config(
    page_title="Blood Report Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #f4f9ff !important;
    color: black !important;
}

.header {
    text-align:center;
    font-size:48px;
    font-weight:bold;
    color:#b71c1c;
}

.sub {
    text-align:center;
    font-size:20px;
    color:#333;
    margin-bottom:30px;
}

.card {
    padding:25px;
    border-radius:15px;
    text-align:center;
    box-shadow:0 4px 15px rgba(0,0,0,0.15);
    margin:15px;
}

.card * {
    color:black !important;
}

.param {
    font-size:22px;
    font-weight:bold;
}

.value {
    font-size:32px;
    font-weight:bold;
}

.status {
    font-size:18px;
    margin-top:10px;
    font-weight:bold;
}

.normal {
    background-color:#c8e6c9;
}

.low {
    background-color:#fff9c4;
}

.high {
    background-color:#ffcdd2;
}

</style>
""", unsafe_allow_html=True)



st.markdown('<div class="header">Blood Report Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">AI-Powered Medical Diagnostic Dashboard</div>', unsafe_allow_html=True)


uploaded_file = st.file_uploader(
    "Upload Report",
    type=["pdf","png","jpg","jpeg","json"]
)



if uploaded_file:

    file_extension = uploaded_file.name.split(".")[-1].lower()

    temp_file = f"temp.{file_extension}"

    with open(temp_file,"wb") as f:
        f.write(uploaded_file.read())


    if file_extension == "pdf":
        scanned_text = scan_pdf(temp_file)

    elif file_extension in ["png","jpg","jpeg"]:
        scanned_text = scan_image(temp_file)

    elif file_extension == "json":

        with open(temp_file) as f:
            scanned_text = json.load(f)

    else:
        st.error("Unsupported File")
        st.stop()



    with st.expander("📄 View Extracted Raw Text"):

        if isinstance(scanned_text, dict):
            st.json(scanned_text)
        else:
            st.text_area("OCR Extracted Text", scanned_text, height=300)



    if isinstance(scanned_text, dict):

        df = pd.DataFrame(
            list(scanned_text.items()),
            columns=["Parameter","Value"]
        )

    else:

        df = extract_parameters_from_text(scanned_text)



    if df.empty:

        st.error("No parameters detected")
        st.stop()



    reference = fetch_reference_ranges()

    df = compare_with_ranges(df, reference)



    st.subheader("📊 Health Dashboard")

    cols = st.columns(4)

    for index,row in df.iterrows():

        if row["Status"] == "Normal":
            style="normal"
            icon="🟢"

        elif row["Status"] == "Low":
            style="low"
            icon="🟡"

        else:
            style="high"
            icon="🔴"


        card_html = f"""
        <div class="card {style}">
            <div class="param">{icon} {row['Parameter']}</div>
            <div class="value">{row['Value']}</div>
            <div class="status">Status : {row['Status']}</div>
        </div>
        """

        cols[index % 4].markdown(card_html, unsafe_allow_html=True)



    st.subheader("🧠 Risk Assessment (Pattern Recognition Model)")

    risk = analyze_risk(df)

    rcols = st.columns(4)

    i = 0

    for key,value in risk.items():

        if value == "LOW RISK":
            style="normal"
            icon="🟢"

        elif value == "MODERATE RISK":
            style="low"
            icon="🟡"

        else:
            style="high"
            icon="🔴"


        html = f"""
        <div class="card {style}">
            <div class="param">{icon} {key}</div>
            <div class="status">{value}</div>
        </div>
        """

        rcols[i].markdown(html, unsafe_allow_html=True)

        i+=1


    st.subheader("📋 Detailed Report")

    st.dataframe(df,use_container_width=True)


    st.subheader("🎯 Model Accuracy")

    report_name = os.path.splitext(uploaded_file.name)[0]

    gt_path = os.path.join(
        os.getcwd(),
        "evaluation",
        "ground_truth",
        f"{report_name}.json"
    )


    if os.path.isfile(gt_path):

        with open(gt_path, "r") as f:

            ground_truth = json.load(f)



        extraction_acc, classification_acc = evaluate_single_report(
            df,
            ground_truth
        )



        col1, col2 = st.columns(2)

        col1.metric(
            "Extraction Accuracy",
            f"{round(extraction_acc,2)}%"
        )

        col2.metric(
            "Classification Accuracy",
            f"{round(classification_acc,2)}%"
        )

        st.success("Ground truth loaded successfully ✅")



        overall_acc = (extraction_acc + classification_acc) / 2


        st.metric(
            "Overall Accuracy",
            f"{round(overall_acc,2)}%"
        )



        st.write("Extraction Accuracy")
        st.progress(int(extraction_acc))


        st.write("Classification Accuracy")
        st.progress(int(classification_acc))


        st.write("Overall Accuracy")
        st.progress(int(overall_acc))



        if overall_acc >= 90:

            st.success("✅ Excellent Performance — Model is highly reliable")

           

        elif overall_acc >= 75:

            st.info("👍 Good Performance")

        elif overall_acc >= 60:

            st.warning("⚠ Moderate Performance")

        else:

            st.error("❌ Low Performance")



        with st.expander("ℹ What does this mean?"):

            st.write("""
Extraction Accuracy → Correct value extraction

Classification Accuracy → Correct health prediction

Overall Accuracy → Combined performance
            """)


    else:

        st.warning("⚠ Ground truth report not found")

        st.info("Upload ground truth file to:")

        # st.code(f"evaluation/ground_truth/{report_name}.json")

        st.write("After uploading, accuracy will appear automatically ✅")
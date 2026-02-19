import streamlit as st
import json
import os
import pandas as pd

from scanner.ocr_engine import scan_pdf, scan_image
from processing.extractor import extract_parameters_from_text
from processing.comparator import compare_with_ranges
from api.medical_api import fetch_reference_ranges
from evaluation.evaluate import evaluate_single_report


# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="Blood Report Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ================= CUSTOM CSS =================

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #f4f9ff !important;
    color: black !important;
}

/* HEADER */

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


/* CARD */

.card {

    padding:25px;
    border-radius:15px;
    text-align:center;
    box-shadow:0 4px 15px rgba(0,0,0,0.15);
    margin:15px;

}


/* FORCE BLACK TEXT INSIDE CARD */

.card * {
    color:black !important;
}


/* TEXT */

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


/* STATUS COLORS */

.normal {
    background-color:#c8e6c9;
}

.low {
    background-color:#fff9c4;
}

.high {
    background-color:#ffcdd2;
}


/* EXPANDER */

.streamlit-expanderHeader {
    font-size:20px;
    font-weight:bold;
    color:#0d47a1;
}

</style>
""", unsafe_allow_html=True)



# ================= HEADER =================

st.markdown('<div class="header">🩸 Blood Report Analyzer</div>', unsafe_allow_html=True)

st.markdown('<div class="sub">AI-Powered Medical Diagnostic Dashboard</div>', unsafe_allow_html=True)



# ================= FILE UPLOAD =================

uploaded_file = st.file_uploader(
    "Upload Report",
    type=["pdf","png","jpg","jpeg","json"]
)



# ================= MAIN =================

if uploaded_file:

    file_extension = uploaded_file.name.split(".")[-1].lower()

    temp_file = f"temp.{file_extension}"

    with open(temp_file,"wb") as f:
        f.write(uploaded_file.read())



    # ================= SCAN =================

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



    # ================= RAW TEXT EXPANDABLE =================

    with st.expander("📄 View Extracted Raw Text", expanded=False):

        if isinstance(scanned_text, dict):

            st.json(scanned_text)

        else:

            st.text_area(

                "OCR Extracted Text",

                scanned_text,

                height=300

            )



    # ================= EXTRACTION =================

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



    # ================= DASHBOARD =================

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



    # ================= TABLE =================

    st.subheader("📋 Detailed Report")

    st.dataframe(df,use_container_width=True)



    # ================= ACCURACY =================

    st.subheader("🎯 Model Accuracy")


    report_name = os.path.splitext(uploaded_file.name)[0]


    gt_path = os.path.join(
        os.getcwd(),
        "evaluation",
        "ground_truth",
        f"{report_name}.json"
    )


    st.write("Looking for:", gt_path)



    if os.path.isfile(gt_path):

        with open(gt_path,"r") as f:

            ground_truth = json.load(f)


        extraction_acc, classification_acc = evaluate_single_report(
            df,
            ground_truth
        )


        col1,col2 = st.columns(2)


        col1.metric(
            "Extraction Accuracy",
            f"{round(extraction_acc,2)}%"
        )


        col2.metric(
            "Classification Accuracy",
            f"{round(classification_acc,2)}%"
        )


        st.success("Ground truth loaded successfully ✅")


    else:

        st.error("Ground truth file NOT found ❌")

        st.write("Expected:", f"{report_name}.json")

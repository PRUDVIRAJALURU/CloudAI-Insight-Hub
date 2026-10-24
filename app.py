import os
import json
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd
from PIL import Image

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

APP_DIR = Path(__file__).parent
UPLOAD_DIR = APP_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="CloudAI Insight Hub", page_icon="☁️", layout="wide")

st.markdown("""
<style>
.main {background: #f6f8fc;}
.block-container {padding-top: 1.6rem; max-width: 1250px;}
.hero {padding: 1.4rem 1.6rem; border-radius: 18px; color: white;
       background: linear-gradient(120deg,#172554,#2563eb,#06b6d4); margin-bottom: 1rem;}
.hero h1 {color:white; margin-bottom:0.25rem;}
.hero p {color:#e0f2fe; margin-bottom:0;}
.small-note {color:#64748b;font-size:0.9rem;}
</style>
<div class="hero">
<h1>☁️ CloudAI Insight Hub</h1>
<p>A student prototype exploring cloud storage, AI text analysis, image labels, and chatbot integration.</p>
</div>
""", unsafe_allow_html=True)

def get_aws_client(service):
    """Return an AWS client when credentials/configuration are available."""
    if not BOTO3_AVAILABLE:
        return None, "boto3 is not installed. Install dependencies from requirements.txt."
    try:
        region = st.session_state.get("aws_region", "us-east-1")
        return boto3.client(service, region_name=region), None
    except Exception as exc:
        return None, str(exc)

def aws_ready():
    if not BOTO3_AVAILABLE:
        return False
    try:
        session = boto3.Session()
        return bool(session.get_credentials())
    except Exception:
        return False

def demo_sentiment(text):
    positive = {"good", "great", "excellent", "happy", "love", "helpful", "fast",
                "easy", "amazing", "wonderful", "best", "satisfied", "thank"}
    negative = {"bad", "poor", "terrible", "hate", "slow", "broken", "worst",
                "angry", "problem", "difficult", "late", "disappointed", "fail"}
    words = [w.strip(".,!?;:()[]{}").lower() for w in text.split()]
    score = sum(w in positive for w in words) - sum(w in negative for w in words)
    if score > 0:
        return "POSITIVE", min(0.99, 0.65 + 0.08 * score)
    if score < 0:
        return "NEGATIVE", min(0.99, 0.65 + 0.08 * abs(score))
    return "NEUTRAL", 0.60

def analyze_text(text, use_aws):
    if use_aws and aws_ready():
        client, error = get_aws_client("comprehend")
        if client:
            try:
                result = client.detect_sentiment(Text=text[:5000], LanguageCode="en")
                scores = result.get("SentimentScore", {})
                label = result.get("Sentiment", "NEUTRAL")
                confidence = float(scores.get(label.title(), 0))
                return label, confidence, "Amazon Comprehend"
            except Exception as exc:
                st.warning(f"Amazon Comprehend request failed; showing demo result instead. Details: {exc}")
    label, confidence = demo_sentiment(text)
    return label, confidence, "Local demo analyzer (not an AWS model)"

def analyze_image(image, use_aws):
    if use_aws and aws_ready():
        client, error = get_aws_client("rekognition")
        if client:
            try:
                import io
                buffer = io.BytesIO()
                image.save(buffer, format="JPEG")
                result = client.detect_labels(Image={"Bytes": buffer.getvalue()}, MaxLabels=10, MinConfidence=60)
                return [(x["Name"], x["Confidence"]) for x in result.get("Labels", [])], "Amazon Rekognition"
            except Exception as exc:
                st.warning(f"Rekognition request failed; showing demo labels instead. Details: {exc}")
    width, height = image.size
    return [(f"Uploaded image ({width} × {height})", 99.0), ("Image file detected", 95.0)], "Demo labels (not AI predictions)"

def save_upload(uploaded_file):
    safe_name = Path(uploaded_file.name).name.replace(" ", "_")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = UPLOAD_DIR / f"{stamp}_{safe_name}"
    path.write_bytes(uploaded_file.getvalue())
    return path

with st.sidebar:
    st.header("⚙️ Configuration")
    st.selectbox("AWS Region", ["us-east-1", "us-east-2", "us-west-2", "ap-south-1", "eu-west-1"],
                 index=0, key="aws_region")
    use_aws = st.toggle("Use real AWS services", value=False,
                        help="Requires valid AWS credentials and permissions configured outside this app.")
    if use_aws and aws_ready():
        st.success("AWS credentials detected")
    elif use_aws:
        st.warning("AWS credentials not detected. Demo mode will be used.")
    else:
        st.info("Demo mode: works without an AWS account.")
    st.caption("Never paste AWS access keys into this app or commit them to GitHub.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "💬 Text Sentiment", "🖼️ Image Labels", "🗂️ File Storage", "🤖 Chatbot Demo"
])

with tab1:
    st.subheader("Project Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cloud platform", "AWS")
    c2.metric("AI focus", "Text + Image")
    c3.metric("Run mode", "AWS" if use_aws and aws_ready() else "Demo")
    st.markdown("""
    This prototype connects the topics in the **AWS with AI** internship report to a small interactive application.

    - **Amazon Comprehend:** sentiment analysis of customer feedback.
    - **Amazon Rekognition:** image-label detection.
    - **Amazon S3 concept:** upload and store files in a local prototype folder.
    - **Amazon Lex concept:** a simple FAQ chatbot demonstration.
    - **AWS IAM and Regions:** learn about permissions and regional service configuration.

    **Important:** Local demo results are illustrative. They are not generated by AWS AI services.
    """)
    st.info("For real AWS use, configure credentials using an AWS profile or environment/host role, then enable 'Use real AWS services'.")

with tab2:
    st.subheader("Customer Feedback Sentiment Analyzer")
    st.write("Enter a short English sentence. In AWS mode, the app calls Amazon Comprehend; otherwise, it uses a simple keyword-based demo.")
    text_input = st.text_area("Feedback", "The service was fast and helpful. I am very happy with the experience.", height=120)
    if st.button("Analyze sentiment", type="primary", key="analyze_text"):
        if not text_input.strip():
            st.error("Please enter some feedback first.")
        else:
            label, confidence, engine = analyze_text(text_input.strip(), use_aws)
            left, middle, right = st.columns(3)
            left.metric("Sentiment", label)
            middle.metric("Confidence", f"{confidence:.1%}")
            right.metric("Analyzer", engine)
            st.caption("The local demo analyzer uses a small word list and is not suitable for production decisions.")

    st.markdown("#### Analyze a CSV file")
    st.caption("Upload a CSV containing a column named `text` or `feedback`.")
    csv_file = st.file_uploader("Choose CSV", type=["csv"], key="sentiment_csv")
    if csv_file:
        try:
            df = pd.read_csv(csv_file)
            candidates = [c for c in df.columns if c.lower() in ("text", "feedback", "review", "comment")]
            if not candidates:
                st.error("No text column found. Name one column text, feedback, review, or comment.")
            else:
                chosen = st.selectbox("Text column", candidates)
                if st.button("Analyze CSV", key="analyze_csv"):
                    output = []
                    for item in df[chosen].fillna("").astype(str):
                        label, confidence, engine = analyze_text(item, use_aws)
                        output.append({"sentiment": label, "confidence": round(confidence, 4), "engine": engine})
                    result_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(output)], axis=1)
                    st.dataframe(result_df, use_container_width=True)
                    st.download_button("Download analyzed CSV", result_df.to_csv(index=False).encode("utf-8"),
                                       "sentiment_results.csv", "text/csv")
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")

with tab3:
    st.subheader("Image Label Explorer")
    st.write("Upload a JPG or PNG image. With AWS enabled and configured, Amazon Rekognition can return labels.")
    image_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], key="image_upload")
    if image_file:
        try:
            img = Image.open(image_file).convert("RGB")
            st.image(img, caption=image_file.name, width=420)
            if st.button("Detect image labels", type="primary"):
                labels, engine = analyze_image(img, use_aws)
                st.write(f"**Engine:** {engine}")
                st.dataframe(pd.DataFrame(labels, columns=["Label", "Confidence (%)"]), use_container_width=True)
        except Exception as exc:
            st.error(f"Could not open image: {exc}")

with tab4:
    st.subheader("Cloud File Storage Prototype")
    st.write("This tab demonstrates file upload and storage locally. Optional S3 upload is included for configured AWS accounts.")
    bucket = st.text_input("S3 bucket name (only needed for real S3 upload)", "")
    uploaded = st.file_uploader("Select a file to store", key="storage_upload")
    if uploaded:
        st.write(f"Selected: **{uploaded.name}** ({uploaded.size:,} bytes)")
        if st.button("Save file to prototype storage", type="primary"):
            saved_path = save_upload(uploaded)
            st.success(f"Saved locally: data/uploads/{saved_path.name}")
            st.session_state["last_saved_file"] = str(saved_path)
        if use_aws and aws_ready() and bucket.strip():
            if st.button("Upload file to Amazon S3"):
                try:
                    s3, error = get_aws_client("s3")
                    s3.upload_fileobj(uploaded, bucket.strip(), Path(uploaded.name).name)
                    st.success(f"Uploaded {uploaded.name} to S3 bucket {bucket.strip()}.")
                except Exception as exc:
                    st.error(f"S3 upload failed: {exc}")
        elif use_aws:
            st.caption("Enter a bucket name and configure AWS credentials to enable S3 upload.")
    saved_files = sorted(UPLOAD_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    st.markdown("#### Files stored in this local prototype")
    if saved_files:
        st.dataframe(pd.DataFrame([{"File": p.name, "Size (bytes)": p.stat().st_size} for p in saved_files]),
                     use_container_width=True)
    else:
        st.caption("No files saved yet.")

with tab5:
    st.subheader("FAQ Chatbot Demo")
    st.write("A small rule-based chatbot that demonstrates conversational application flow. This is not connected to Amazon Lex.")
    question = st.text_input("Ask a question", placeholder="What is AWS?")
    if st.button("Send message", key="chat_send"):
        q = question.lower().strip()
        if not q:
            st.warning("Type a question first.")
        elif "aws" in q or "amazon web services" in q:
            answer = "AWS is a cloud platform that provides computing, storage, databases, networking, and AI services."
        elif "s3" in q or "storage" in q or "bucket" in q:
            answer = "Amazon S3 is object storage. Files are stored as objects inside buckets."
        elif "ec2" in q or "server" in q or "virtual machine" in q:
            answer = "Amazon EC2 provides resizable virtual computing capacity in the cloud."
        elif "comprehend" in q or "sentiment" in q:
            answer = "Amazon Comprehend uses natural language processing to analyze text, including sentiment and key phrases."
        elif "rekognition" in q or "image" in q:
            answer = "Amazon Rekognition analyzes images and videos to identify labels and other visual information."
        elif "iam" in q or "security" in q or "permission" in q:
            answer = "AWS IAM helps manage identities and permissions. Follow least privilege and never publish credentials."
        elif "lex" in q or "chatbot" in q:
            answer = "Amazon Lex can be used to build conversational interfaces. This screen is a local FAQ demo, not a Lex bot."
        else:
            answer = "I can answer basic questions about AWS, S3, EC2, IAM, Amazon Comprehend, Rekognition, and Lex."
        st.chat_message("user").write(question)
        st.chat_message("assistant").write(answer)

st.divider()
st.markdown('<p class="small-note">Student prototype • AWS with AI internship learning project • Configure permissions and review AWS costs before enabling live services.</p>', unsafe_allow_html=True)

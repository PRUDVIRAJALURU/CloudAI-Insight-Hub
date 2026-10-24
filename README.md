# CloudAI Insight Hub

A beginner-friendly **AWS with AI** internship prototype built with Python and Streamlit. It demonstrates cloud-storage concepts and AI-powered text/image analysis through a simple web dashboard.

> **Academic honesty:** This is a learning prototype, not evidence that a production AWS deployment has been completed. The default mode runs locally. The local sentiment and image outputs are clearly labeled demo results. Real AWS service calls require your own AWS account, credentials, permissions, and may incur charges.

## Features

- **Text sentiment analysis:** Analyze a sentence or a CSV of customer feedback.
  - Demo mode: small keyword-based illustrative classifier.
  - AWS mode: calls Amazon Comprehend when AWS credentials are configured.
- **Image label explorer:**
  - Demo mode: shows basic image information only; it does not claim to detect image objects.
  - AWS mode: calls Amazon Rekognition to detect labels.
- **File storage prototype:** save files locally in `data/uploads/`; optional upload to an existing Amazon S3 bucket.
- **FAQ chatbot:** a small rule-based assistant that explains common AWS topics. It is not connected to Amazon Lex.
- **AWS region selector** and safety reminders for credentials.

## Technology stack

- Python
- Streamlit
- Pandas
- Pillow
- Boto3 (AWS SDK for Python)
- Optional AWS services: Amazon Comprehend, Amazon Rekognition, Amazon S3

## Project structure

```text
aws-with-ai-insight-hub/
├── app.py
├── requirements.txt
├── README.md
├── sample_feedback.csv
├── .gitignore
└── data/
    └── uploads/
        └── .gitkeep
```

## Run locally

### 1. Install Python

Use Python 3.10 or newer.

### 2. Download or clone this repository

```bash
git clone https://github.com/YOUR-USERNAME/aws-with-ai-insight-hub.git
cd aws-with-ai-insight-hub
```

### 3. Create a virtual environment (recommended)

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install packages and start the app

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local address (normally `http://localhost:8501`) to open in your browser.

## Optional: connect real AWS services

The project works without AWS credentials. Only enable **Use real AWS services** after you have set up an AWS account and understand permissions and billing.

1. Configure credentials using a named AWS CLI profile, environment variables, or an attached role in a suitable hosting environment.
2. Choose the correct AWS region in the sidebar.
3. Enable **Use real AWS services**.
4. For S3 uploads, enter the name of an existing bucket.

Typical IAM permissions needed (scope them to only the resources you use):
- Amazon Comprehend: `comprehend:DetectSentiment`
- Amazon Rekognition: `rekognition:DetectLabels`
- Amazon S3 upload: `s3:PutObject` on the target bucket's intended prefix

For local development, a named AWS CLI profile can be configured with `aws configure --profile your-profile`, then selected by setting the `AWS_PROFILE` environment variable before starting the app. Do not put access keys in source code, screenshots, README files, or GitHub commits. Use least-privilege permissions and check regional availability and costs. Do not enable public access on an S3 bucket just to make this demo work.

## Try the demo

1. Open **Text Sentiment** and analyze the default sentence.
2. Upload `sample_feedback.csv` and select the `feedback` column.
3. Open **Image Labels**, upload a JPG or PNG, and run the demo.
4. Open **File Storage**, upload a file, and save it locally.
5. Ask the FAQ chatbot “What is Amazon S3?”

## Deploy (optional)

You can deploy the app through Streamlit Community Cloud by connecting your GitHub repository and selecting `app.py` as the main file. Start in demo mode. If you later configure cloud credentials for a hosted app, use the hosting platform's secret-management facility or an appropriate IAM role—never commit secrets.

## Limitations and future improvements

- Demo sentiment uses a tiny keyword list and is not a trained ML model.
- Demo image mode does not perform object recognition.
- The FAQ chatbot is rule-based, not an Amazon Lex bot.
- Local uploaded files are stored on the machine running the app; this is not durable cloud storage.
- Possible extensions: integrate Amazon Lex, add authentication, store analysis history in a database, add unit tests, and deploy with a secure AWS architecture.

## Screenshots

Run the app and add your own screenshots here before submitting, for example:

- `screenshots/overview.png`
- `screenshots/sentiment.png`
- `screenshots/image-labels.png`

## Author

**Aluru Prudviraj**  
B.Tech Computer Science and Engineering  
Mohan Babu University

Update this section if you want to include your GitHub profile, internship dates, or faculty details.

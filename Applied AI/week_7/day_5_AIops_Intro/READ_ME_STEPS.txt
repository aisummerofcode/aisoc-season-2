Multi-Platform Post Rewriter: Complete Setup Guide
Prerequisites
Google Cloud account with billing enabled
Access to Google Cloud Shell or local machine with gcloud CLI
Step 1: Project Setup
bash
Copy
# Create new project (replace with your preferred name)
gcloud projects create doc-rewriter-project-$(date +%s)

# Set as active project
gcloud config set project doc-rewriter-project-TIMESTAMP

# Enable billing (required for Cloud Functions)
# Go to: https://console.cloud.google.com/billing
# Link your project to a billing account
Step 2: Enable Required APIs
bash
Copy
# Enable Cloud Functions API
gcloud services enable cloudfunctions.googleapis.com

# Enable Vertex AI API for Gemini access
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Run API (auto-enabled with Cloud Functions Gen2)
gcloud services enable run.googleapis.com

# Enable Cloud Build API (for function deployment)
gcloud services enable cloudbuild.googleapis.com
Step 3: Fix Service Account Permissions (New Projects)
bash
Copy
# Get project number
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")

# Create default service accounts if missing
gcloud beta services identity create \
    --service=cloudfunctions.googleapis.com

# Grant necessary IAM roles to default compute service account
SA=${PROJECT_NUMBER}-compute@developer.gserviceaccount.com

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${SA}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${SA}" \
  --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${SA}" \
  --role="roles/iam.serviceAccountUser"
Step 4: Create Function Files
bash
Copy
# Create project directory
mkdir simple-llm-api
cd simple-llm-api

# Create main.py (copy content from Document 1)
nano main.py

# Create requirements.txt (copy content from Document 2)
nano requirements.txt

# Update project ID in main.py
# Replace "doc-rewriter-project" with your actual project ID
Step 5: Deploy Cloud Function
bash
Copy
gcloud functions deploy simple-llm-api \
  --gen2 \
  --runtime python310 \
  --trigger-http \
  --region us-central1 \
  --entry-point process_csv \
  --allow-unauthenticated \
  --memory=2Gi \
  --timeout=300s
Deployment flags explained:

--gen2: Use Cloud Functions 2nd generation (required for Vertex AI)
--runtime python310: Python 3.10 runtime environment
--trigger-http: HTTP trigger for file uploads
--region us-central1: Deploy in US Central region
--entry-point process_csv: Function name to call
--allow-unauthenticated: Allow public access (no auth required)
--memory=2Gi: 2GB RAM (prevents OOM with pandas/Excel processing)
--timeout=300s: 5-minute timeout (allows processing larger CSVs)
Step 6: Test the Function
Create sample input CSV:
bash
Copy
cat > input.csv <<EOF
id,source,post
1,linkedin,"Exciting news! 🎉
We're expanding our AI team — apply now!"
2,twitter,"AI is eating the world 🌍"
3,instagram,"Photo from our AI hackathon — what an event!"
4,slack,"Reminder: infra upgrade window Friday midnight."
5,email,"FYI – client requested AI use-case proposal by next week."
EOF
Upload and process:
bash
Copy
# Get your function URL
FUNCTION_URL=$(gcloud functions describe simple-llm-api --region=us-central1 --format="value(url)")

# Send CSV and save Excel output
curl -X POST $FUNCTION_URL \
  -F file=@input.csv \
  -o rewritten_posts.xlsx

# Verify output file was created
ls -lh rewritten_posts.xlsx
Download to local machine (if using Cloud Shell):
bash
Copy
cloudshell download rewritten_posts.xlsx
Step 7: Verify Results
Open rewritten_posts.xlsx in Excel or Google Sheets. You should see:

Sheet name: "RewrittenPosts"
Columns: id, source, rewritten_post
Content: Professional, brand-consistent rewrites of your original posts
Common Troubleshooting
Error	Cause	Solution
PERMISSION_DENIED on API enable	Insufficient IAM roles	Grant roles/editor to your account
billing account associated	No billing linked	Enable billing in Cloud Console
service account can not be accessed	New project IAM propagation	Run Step 3 service account fixes
upstream request timeout	Function timeout (>60s)	Already fixed with --timeout=300s
gemini model not found	Using retired model	Code uses current gemini-2.5-flash
Extensions for Advanced Users
Add sentiment analysis: Include emotion detection in output
Configurable tone: Accept tone parameter (formal/casual/playful)
Batch processing: Connect to Cloud Storage for large file processing
Analytics integration: Send results to BigQuery for insights
Multi-language support: Detect and preserve language in rewrites
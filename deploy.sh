#!/bin/bash
# ElectBot — Google Cloud Run Deployment Script
# Usage: ./deploy.sh YOUR_PROJECT_ID YOUR_GEMINI_API_KEY

PROJECT_ID=${1:-"your-project-id"}
API_KEY=${2:-"your-gemini-api-key"}
SERVICE_NAME="electbot"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🗳️  Deploying ElectBot to Google Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region:  $REGION"

echo ""
echo "📦 Building Docker image..."
gcloud builds submit --tag $IMAGE

echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 60 \
  --set-env-vars "GEMINI_API_KEY=$API_KEY" \
  --project $PROJECT_ID

echo ""
echo "✅ Deployment complete!"

# Vertex AI Model
resource "google_vertex_ai_model" "recommendation_model" {
  name          = var.vertex_ai_model_name
  display_name  = var.vertex_ai_model_name
  description   = "Recommendation model for personalized content"
  region        = var.gcp_region
  project       = var.gcp_project_id

  container_spec {
    image_uri = "gcr.io/${var.gcp_project_id}/recommendation-model:latest"
    
    env {
      name  = "MODEL_TYPE"
      value = "collaborative_filtering"
    }
  }
}

# Vertex AI Endpoint
resource "google_vertex_ai_endpoint" "recommendation_endpoint" {
  name         = var.vertex_ai_endpoint_name
  display_name = var.vertex_ai_endpoint_name
  description  = "Endpoint for serving recommendation predictions"
  region       = var.gcp_region
  project      = var.gcp_project_id
}

# Vertex AI Endpoint Model
resource "google_vertex_ai_endpoint_model" "endpoint_model" {
  endpoint = google_vertex_ai_endpoint.recommendation_endpoint.id
  model    = google_vertex_ai_model.recommendation_model.id
  display_name = "${var.vertex_ai_model_name}-endpoint"
  
  machine_type = var.vertex_ai_machine_type
  min_replica_count = 1
  max_replica_count = 3
  
  traffic_split = {
    "0" = 100
  }
}

# IAM Policy for Vertex AI
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.gcp_project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${var.gcp_project_id}@appspot.gserviceaccount.com"
}

# Cloud Storage Bucket for Model Artifacts
resource "google_storage_bucket" "model_artifacts" {
  name          = "${var.gcp_project_id}-model-artifacts"
  location      = var.gcp_region
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# Outputs
output "vertex_ai_endpoint_id" {
  value = google_vertex_ai_endpoint.recommendation_endpoint.id
}

output "model_artifacts_bucket" {
  value = google_storage_bucket.model_artifacts.name
} 
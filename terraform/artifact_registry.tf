resource "google_artifact_registry_repository" "chatbot" {
  location      = var.region
  repository_id = var.repository_name
  description   = "Docker repository for chatbot service"
  format        = "DOCKER"

  cleanup_policies {
    id     = "keep-latest-3"
    action = "KEEP"

    most_recent_versions {
      keep_count = 3
    }
  }
}

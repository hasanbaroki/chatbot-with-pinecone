variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "asia-southeast1"
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "chatbot-pinecone"
}

variable "repository_name" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "chatbot-repo"
}

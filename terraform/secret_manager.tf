resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "OPENAI_API_KEY"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "pinecone_api_key" {
  secret_id = "PINECONE_API_KEY"

  replication {
    auto {}
  }
}

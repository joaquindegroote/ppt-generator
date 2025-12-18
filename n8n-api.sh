#!/bin/bash
# n8n API Helper Script
# Usage: ./n8n-api.sh <command> [args]

N8N_URL="https://cis-ai-n8n.app.n8n.cloud"
API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTRjYWRkNy02NmRkLTQ0YmYtODM5Yy1kZGRkODljYjc5OTYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY0NzYwMTY0LCJleHAiOjE3NzI1MDY4MDB9.k1YGNErqowgmMqzjE4dqbTMr-K1M-MHrQ-5MyRLH3m8"

# Helper function for API calls
n8n_api() {
    local method=$1
    local endpoint=$2
    local data=$3

    if [ -z "$data" ]; then
        curl -s -X "$method" "${N8N_URL}/api/v1${endpoint}" \
            -H "X-N8N-API-KEY: ${API_KEY}" \
            -H "Content-Type: application/json"
    else
        curl -s -X "$method" "${N8N_URL}/api/v1${endpoint}" \
            -H "X-N8N-API-KEY: ${API_KEY}" \
            -H "Content-Type: application/json" \
            -d "$data"
    fi
}

case "$1" in
    "list")
        n8n_api GET "/workflows"
        ;;
    "get")
        n8n_api GET "/workflows/$2"
        ;;
    "update")
        n8n_api PUT "/workflows/$2" "$3"
        ;;
    "create")
        n8n_api POST "/workflows" "$2"
        ;;
    "activate")
        n8n_api POST "/workflows/$2/activate"
        ;;
    "deactivate")
        n8n_api POST "/workflows/$2/deactivate"
        ;;
    "execute")
        n8n_api POST "/workflows/$2/execute" "$3"
        ;;
    "executions")
        n8n_api GET "/executions?workflowId=$2"
        ;;
    *)
        echo "Usage: ./n8n-api.sh <command> [args]"
        echo "Commands: list, get <id>, update <id> <json>, create <json>, activate <id>, deactivate <id>, execute <id> [data], executions <id>"
        ;;
esac

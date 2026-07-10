#!/usr/bin/env bash
# Deploy the Grounded Prompt Columns web service to Azure Container Apps.
# Mirrors the team convention (imperative az containerapp, image in ACR).
# Prereqs: az login; an ACR and a Container Apps environment.
set -euo pipefail

RG="${RG:-gpc-rg}"
LOCATION="${LOCATION:-eastus}"
ENVNAME="${ENVNAME:-gpc-env}"
ACR="${ACR:-gpcacr}"                 # must be globally unique
APP="${APP:-gpc-web}"
TAG="${TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"
IMAGE="gpc-web:${TAG}"

# Build context is the web/ folder (Dockerfile lives there).
HERE="$(cd "$(dirname "$0")/.." && pwd)"
CTX="${HERE}/web"

echo "==> Building ${IMAGE} in ACR ${ACR}"
az acr build -r "$ACR" -t "$IMAGE" "$CTX"

LOGIN="$(az acr show -n "$ACR" --query loginServer -o tsv)"
ACR_USER="$(az acr credential show -n "$ACR" --query username -o tsv)"
ACR_PASS="$(az acr credential show -n "$ACR" --query "passwords[0].value" -o tsv)"

# App settings come from deploy/.env (GPC_MODE, DATAVERSE_URL, AZURE_*).
ENV_FILE="${HERE}/deploy/.env"
declare -a SECRETS=() ENVVARS=()
if [[ -f "$ENV_FILE" ]]; then
  # Live creds go in as Container App secrets; the rest as plain env vars.
  set -a; source "$ENV_FILE"; set +a
  [[ -n "${AZURE_CLIENT_SECRET:-}" ]] && SECRETS+=(azure-client-secret="$AZURE_CLIENT_SECRET")
  ENVVARS+=(GPC_MODE="${GPC_MODE:-mock}" DATAVERSE_URL="${DATAVERSE_URL:-}" \
            ACCOUNT_TOP="${ACCOUNT_TOP:-12}" CORS_ORIGINS="${CORS_ORIGINS:-*}" \
            AZURE_TENANT_ID="${AZURE_TENANT_ID:-}" AZURE_CLIENT_ID="${AZURE_CLIENT_ID:-}")
  [[ -n "${AZURE_CLIENT_SECRET:-}" ]] && ENVVARS+=(AZURE_CLIENT_SECRET=secretref:azure-client-secret)
fi

echo "==> Creating/updating container app ${APP}"
az containerapp create -n "$APP" -g "$RG" --environment "$ENVNAME" \
  --image "${LOGIN}/${IMAGE}" \
  --registry-server "$LOGIN" --registry-username "$ACR_USER" --registry-password "$ACR_PASS" \
  --ingress external --target-port 8000 --min-replicas 1 --max-replicas 3 \
  ${SECRETS:+--secrets "${SECRETS[@]}"} \
  ${ENVVARS:+--env-vars "${ENVVARS[@]}"} \
  --query properties.configuration.ingress.fqdn -o tsv

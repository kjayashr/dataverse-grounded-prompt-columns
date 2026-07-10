"""Live Dataverse client (only used in live mode).

Kept dependency-light: it uses stdlib urllib for HTTP and azure-identity only for
the access token. Mock mode never imports this, so the prototype runs with no
dependencies at all.

The `predict` method invokes a real AI Builder prompt through the Dataverse
`Predict` message, so grounded generation uses the actual platform engine, not a
bolted-on model. The exact payload shape should be validated against your org the
first time (Phase 1 of the plan); it is isolated here so that is the only place
to adjust.
"""
import json
import urllib.request


class DataverseClient:
    def __init__(self, config, credential=None):
        self.cfg = config
        self._cred = credential
        self._token = None

    # --- auth ---
    def _access_token(self):
        if self._token:
            return self._token
        if self._cred is None:
            try:
                from azure.identity import AzureCliCredential, InteractiveBrowserCredential
                try:
                    self._cred = AzureCliCredential()
                    self._cred.get_token(self._scope())  # probe
                except Exception:
                    self._cred = InteractiveBrowserCredential()
            except ImportError as e:
                raise SystemExit("Live mode needs azure-identity: pip install azure-identity") from e
        self._token = self._cred.get_token(self._scope()).token
        return self._token

    def _scope(self):
        return f"{self.cfg.org_url}/.default"

    def _request(self, method, path, body=None):
        url = path if path.startswith("http") else f"{self.cfg.api_base}/{path.lstrip('/')}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self._access_token()}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("OData-MaxVersion", "4.0")
        req.add_header("OData-Version", "4.0")
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}

    # --- operations ---
    def query(self, entity_set, select=None, filter=None, top=None):
        q = []
        if select: q.append("$select=" + ",".join(select))
        if filter: q.append("$filter=" + filter)
        if top: q.append("$top=" + str(top))
        path = entity_set + ("?" + "&".join(q) if q else "")
        return self._request("GET", path).get("value", [])

    def update_record(self, entity_set, row_id, patch):
        return self._request("PATCH", f"{entity_set}({row_id})", patch)

    def predict(self, model_name, request_v2):
        """Invoke an AI Builder prompt via the Predict message.
        Resolves the msdyn_aimodel id by name, then calls Predict."""
        models = self.query("msdyn_aimodels", select=["msdyn_aimodelid", "msdyn_name"],
                            filter=f"msdyn_name eq '{model_name}'", top=1)
        if not models:
            raise SystemExit(f"AI model '{model_name}' not found in this org.")
        model_id = models[0]["msdyn_aimodelid"]
        body = {"Request": {"@odata.type": "Microsoft.Dynamics.CRM.expando",
                            "Value": request_v2},
                "AIModelId": model_id}
        out = self._request("POST", "Predict", body)
        # Predict returns a structured response; surface the text field.
        return json.dumps(out) if isinstance(out, dict) else str(out)

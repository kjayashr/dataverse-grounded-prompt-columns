"""Live Dataverse access (GPC_MODE=live).

Uses a client-credentials app registration (via azure-identity) to get a token,
queries accounts with their related opportunities and contacts, and runs the
same summarize() as mock mode. Requires a Dataverse application user with a
security role. There is no prior Entra/managed-identity pattern in the team's
repos, so this is the one net-new dependency.
"""
import httpx

from .config import Settings
from .records import summarize

_EXPAND = (
    "opportunity_customer_accounts($select=name,estimatedvalue,statecode,"
    "closeprobability,opportunityid;$top=6),"
    "contact_customer_accounts($select=fullname,jobtitle,contactid;$top=5)"
)


def _token(s: Settings) -> str:
    from azure.identity import ClientSecretCredential
    cred = ClientSecretCredential(s.azure_tenant_id, s.azure_client_id, s.azure_client_secret)
    return cred.get_token(f"{s.dataverse_url.rstrip('/')}/.default").token


async def fetch_live(s: Settings) -> list[dict]:
    url = (f"{s.dataverse_url.rstrip('/')}/api/data/v9.2/accounts"
           f"?$select=name,revenue,accountid&$top={s.account_top}&$expand={_EXPAND}")
    headers = {
        "Authorization": f"Bearer {_token(s)}",
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        rows = r.json().get("value", [])

    out = []
    for a in rows:
        opps = [{"name": o.get("name"), "val": o.get("estimatedvalue"),
                 "state": o.get("statecode"), "prob": o.get("closeprobability"),
                 "id": o.get("opportunityid")}
                for o in a.get("opportunity_customer_accounts", [])]
        contacts = [{"name": c.get("fullname"), "title": c.get("jobtitle"),
                     "id": c.get("contactid")}
                    for c in a.get("contact_customer_accounts", [])]
        out.append(summarize(a.get("name"), a.get("revenue"), opps, contacts, s.org_web_base))
    return out

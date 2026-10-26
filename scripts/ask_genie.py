"""Ask a Genie space a question as a CLI profile; print the text answer and the generated SQL (verification helper)."""
import sys, time
from databricks.sdk import WorkspaceClient

def ask(profile, space, question):
    w = WorkspaceClient(profile=profile)
    m = w.api_client.do("POST", f"/api/2.0/genie/spaces/{space}/start-conversation", body={"content": question})
    conv, mid = m["conversation_id"], m["message_id"]
    for _ in range(60):
        r = w.api_client.do("GET", f"/api/2.0/genie/spaces/{space}/conversations/{conv}/messages/{mid}")
        if r.get("status") in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(3)
    out = []
    for a in r.get("attachments") or []:
        if a.get("text"): out.append("TEXT: " + a["text"]["content"])
        if a.get("query"):
            out.append("SQL: " + a["query"]["query"].replace("\n", " ")[:300])
            try:
                res = w.api_client.do("GET", f"/api/2.0/genie/spaces/{space}/conversations/{conv}/messages/{mid}/attachments/{a['attachment_id']}/query-result")
                out.append("ROWS: " + str(res["statement_response"]["result"].get("data_array"))[:300])
            except Exception as e:
                out.append(f"ROWS: n/a ({str(e)[:80]})")
    return r.get("status"), out

if __name__ == "__main__":
    st, out = ask(*sys.argv[1:4])
    print(st); print("\n".join(out))

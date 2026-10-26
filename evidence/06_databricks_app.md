# Databricks App — surface it to the business
_Captured 2026-10-26 06:34 UTC from workspace `hunter` (catalog `harbourline`) by `scripts/collect_evidence.py`._

## Deployed app (status from the Apps API)

```json
{
  "name": "harbourline-dealroom",
  "url": "https://harbourline-dealroom-3311028655009738.18.azure.databricksapps.com",
  "app_status": {
    "message": "App has status: App is running",
    "state": "RUNNING"
  },
  "compute_status": {
    "message": "App compute is running.",
    "state": "ACTIVE"
  },
  "active_deployment": {
    "create_time": "2026-10-26T06:29:54Z",
    "creator": "jennifer.wang@databricks.com",
    "deployment_artifacts": {
      "source_code_path": "/Workspace/Users/b55e85ff-6c35-4f89-812a-80106438c2b6/src/01f1d106a8091685a3dfbb25aca93e40"
    },
    "deployment_id": "01f1d106a8091685a3dfbb25aca93e40",
    "mode": "SNAPSHOT",
    "source_code_path": "/Workspace/Users/jennifer.wang@databricks.com/apps/harbourline-dealroom",
    "status": {
      "message": "App started successfully",
      "state": "SUCCEEDED"
    },
    "update_time": "2026-10-26T06:30:30Z"
  },
  "resources": [
    {
      "name": "sql-warehouse",
      "sql_warehouse": {
        "id": "d451ee34130421c9",
        "permission": "CAN_USE"
      }
    },
    {
      "name": "postgres",
      "postgres": {
        "branch": "projects/harbourline/branches/production",
        "database": "projects/harbourline/branches/production/databases/databricks-postgres",
        "permission": "CAN_CONNECT_AND_CREATE"
      }
    }
  ],
  "user_api_scopes": [
    "sql",
    "dashboards.genie",
    "files.files",
    "serving.serving-endpoints"
  ]
}
```

## Unit tests (gate logic, widget spec validation, LLM client, ingest path parsing, data generator)

```
.....................................                                    [100%]
37 passed in 0.13s

```

"""deal room ingest: Auto Loader over SharePoint (UC connection) + deal-room + portal volumes -> file_register; then AI extraction."""
import re
from urllib.parse import unquote

ROOM_PORTFOLIO = {"Solace Grid Energy": "Fund I", "Kestrel Robotics": "Fund I", "Pier Nine Retail REIT": "Fund II"}
PHASE_STAGE = {"A_Pre-NDA": 1, "B_Due_Diligence": 2, "C_Investor_Portal": 3}

SP_ROOT = "Harbourline_DealRoom"                                   # SharePoint folder: Harbourline_DealRoom/<Room_Name>/<Phase>/<file>.pdf

def parse_path(path: str):
    if path.startswith("https://"):                  # SharePoint file URL -> same layout as the deal-room volume
        m = re.search(rf"/{SP_ROOT}/(.+)$", unquote(path))
        if not m:
            return None
        path = "/deal_rooms/" + m.group(1)
        sp = True
    else:
        sp = False
    m = re.search(r"/(deal_rooms|portal_uploads)/(.+)$", path)
    if not m or any(part.startswith("_") for part in m.group(2).split("/")):
        return None
    parts = m.group(2).split("/")
    room = parts[0].replace("_", " ")
    name = parts[-1]
    if m.group(1) == "deal_rooms":
        if len(parts) < 3:
            return None
        phase, stage, source = parts[1], PHASE_STAGE.get(parts[1]), "SharePoint" if sp else "internal"
    else:
        phase, stage, source = None, None, "external-party portal"
    return {"portfolio": ROOM_PORTFOLIO.get(room, "Fund I"), "deal_room": room, "phase": phase, "stage": stage,
            "name": name, "file_type": name.rsplit(".", 1)[-1].lower(), "source": source}

def main(catalog: str, prefix: str, sp_url: str = "", sp_conn: str = ""):
    from pyspark.sql import SparkSession, functions as F, types as T
    spark = SparkSession.builder.getOrCreate()
    vdr = f"{catalog}.{prefix}vdr"
    schema = T.StructType([T.StructField(k, t) for k, t in [("portfolio", T.StringType()), ("deal_room", T.StringType()),
              ("phase", T.StringType()), ("stage", T.IntegerType()), ("name", T.StringType()),
              ("file_type", T.StringType()), ("source", T.StringType())]])
    parse = F.udf(parse_path, schema)
    def write(batch, _):                          # MERGE on file_id: re-running after a checkpoint reset adds no duplicates
        from delta.tables import DeltaTable
        reg = batch.select("file_id", "portfolio", "deal_room", "name", "file_type", "path", "stage", "received_at",
                           "source", "uploaded_by", "classification", "status")
        for table, df in ((f"{vdr}.file_register", reg), (f"{vdr}.file_content", batch.select("file_id", "portfolio", "path", "content"))):
            (DeltaTable.forName(spark, table).alias("t").merge(df.alias("s"), "t.file_id = s.file_id")
             .whenNotMatchedInsertAll().execute())

    sources = [(vol, f"/Volumes/{catalog}/{prefix}vdr/{vol}/", {}) for vol in ("deal_rooms", "portal_uploads")]
    if sp_url and sp_conn:                            # optional: a SharePoint deal-room library, read through a Unity Catalog connection
        sources.insert(0, ("sharepoint", sp_url, {"databricks.connection": sp_conn}))
    def load(vol, src, opts):
        df = (spark.readStream.format("cloudFiles").option("cloudFiles.format", "binaryFile").options(**opts)
              .option("pathGlobFilter", "*.pdf").option("recursiveFileLookup", "true").load(src)
              .select("path", "modificationTime", "content"))
        parsed = df.withColumn("p", parse("path")).where("p IS NOT NULL")
        out = parsed.select(F.sha2("path", 256).alias("file_id"), "p.portfolio", "p.deal_room", "p.name", "p.file_type",
                            F.col("path"), "p.stage", F.col("modificationTime").alias("received_at"), "p.source",
                            F.lit(None).cast("string").alias("uploaded_by"), F.lit("Confidential").alias("classification"),
                            F.lit("Received").alias("status"), "content")
        (out.writeStream.option("checkpointLocation", f"/Volumes/{catalog}/{prefix}vdr/deal_rooms/_checkpoints/v3_{vol}")
            .trigger(availableNow=True).foreachBatch(write).start().awaitTermination())

    for vol, src, opts in sources:
        if vol == "sharepoint":                       # batch probe first: a failed stream would fail the whole run
            try:
                spark.read.format("binaryFile").options(**opts).option("pathGlobFilter", "*.pdf").option("recursiveFileLookup", "true").load(src).select("path").limit(1).collect()
            except Exception as e:
                print(f"SharePoint source skipped: {str(e)[:300]}")   # e.g. folder not created yet / connection expired
                continue
        load(vol, src, opts)

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])

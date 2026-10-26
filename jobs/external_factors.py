"""Daily external investment factors: FRED public CSV (no key) + seed CSV for HK/CN/EU series."""
import csv, io, urllib.request

FRED_SERIES = {
    "DFF": ("Fed funds effective rate", "pct", "portfolio:Fund I"),
    "DGS2": ("US Treasury 2Y yield", "pct", "portfolio:Fund I"),
    "DGS10": ("US Treasury 10Y yield", "pct", "portfolio:Fund I"),
    "DEXHKUS": ("USD/HKD", "fx", "portfolio:Fund I"),
    "DEXCHUS": ("USD/CNY", "fx", "sector:Energy"),
    "SP500": ("S&P 500", "index", "portfolio:Fund I"),
    "VIXCLS": ("VIX", "index", "portfolio:Fund I"),
    "DCOILBRENTEU": ("Brent crude", "usd_bbl", "sector:Energy"),
}

def parse_fred_csv(text: str, series: str):
    rows = [r for r in csv.DictReader(io.StringIO(text)) if r.get(series) not in (None, "", ".")]
    if not rows:
        return None
    last, prev = rows[-1], rows[-2] if len(rows) > 1 else rows[-1]
    return last["observation_date"], float(last[series]), float(prev[series])

def fetch(series: str):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return parse_fred_csv(r.read().decode(), series)

def main(catalog: str, prefix: str, seed_path: str):
    from pyspark.sql import SparkSession, functions as F
    spark = SparkSession.builder.getOrCreate()
    rows = []
    for sid, (label, unit, tag) in FRED_SERIES.items():
        try:
            got = fetch(sid)
        except Exception as e:                       # keep last value if the feed is unavailable
            print(f"skip {sid}: {e}"); continue
        if got:
            rows.append((sid, label, got[1], unit, got[0], f"https://fred.stlouisfed.org/series/{sid}", tag, got[2]))
    df = spark.createDataFrame(rows, "series string, label string, value double, unit string, observed_at string, source string, tag string, prev_value double")
    seed = spark.read.option("header", True).csv(seed_path).selectExpr(
        "series", "label", "CAST(value AS DOUBLE) value", "unit", "observed_at", "source", "tag", "CAST(prev_value AS DOUBLE) prev_value")
    allf = df.unionByName(seed).withColumn("observed_at", F.to_date("observed_at")).withColumn("loaded_at", F.current_timestamp()).select(
        "series", "label", "value", "unit", "observed_at", "source", "tag", "loaded_at", "prev_value")
    allf.createOrReplaceTempView("new_factors")
    spark.sql(f"""MERGE INTO {catalog}.{prefix}vdr.external_factors t USING new_factors s ON t.series = s.series
                  WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *""")

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2], sys.argv[3])

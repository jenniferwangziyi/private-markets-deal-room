"""Reset volumes for a fresh demo run (keeps the Stage 1 files, _staged and _staging_tables)."""
import glob, os, shutil, sys

def main(catalog, prefix):
    v = f"/Volumes/{catalog}/{prefix}"
    for d in (f"{v}vdr/deal_rooms/Solace_Grid_Energy/B_Due_Diligence", f"{v}vdr/deal_rooms/_checkpoints"):
        shutil.rmtree(d, ignore_errors=True)
    for p in glob.glob(f"{v}vdr/portal_uploads/*"):
        if not os.path.basename(p).startswith("_"):
            shutil.rmtree(p, ignore_errors=True)
    print("volumes reset")

if __name__ == "__main__":
    main(*sys.argv[1:])

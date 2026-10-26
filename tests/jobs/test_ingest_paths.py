import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("dealroom", pathlib.Path(__file__).resolve().parents[2] / "jobs/dealroom_ingest.py")
dealroom = importlib.util.module_from_spec(spec); spec.loader.exec_module(dealroom)

def test_deal_room_path():
    d = dealroom.parse_path("/Volumes/harbourline/vdr/deal_rooms/Solace_Grid_Energy/B_Due_Diligence/Valuation_&_Financials.pdf")
    assert d == {"portfolio": "Fund I", "deal_room": "Solace Grid Energy", "phase": "B_Due_Diligence", "stage": 2,
                 "name": "Valuation_&_Financials.pdf", "file_type": "pdf", "source": "internal"}

def test_portal_upload_path():
    d = dealroom.parse_path("/Volumes/harbourline/vdr/portal_uploads/Solace_Grid_Energy/Valuation.pdf")
    assert d["source"] == "external-party portal" and d["stage"] is None

def test_staged_and_tables_ignored():
    assert dealroom.parse_path("/Volumes/harbourline/vdr/deal_rooms/_staging_tables/investments.csv") is None
    assert dealroom.parse_path("/Volumes/harbourline/vdr/portal_uploads/_staged/Solace_Grid_Energy/x.pdf") is None

def test_sharepoint_url_maps_to_room_and_stage():
    d = dealroom.parse_path("https://databricksinc.sharepoint.com/sites/FEGDemo/Harbourline_DealRoom/Solace_Grid_Energy/B_Due_Diligence/Side%20letter%20template.pdf")
    assert (d["deal_room"], d["stage"], d["name"], d["source"]) == ("Solace Grid Energy", 2, "Side letter template.pdf", "SharePoint")

def test_sharepoint_outside_demo_folder_is_ignored():
    assert dealroom.parse_path("https://databricksinc.sharepoint.com/sites/FEGDemo/Shared%20Documents/SLA.pdf") is None

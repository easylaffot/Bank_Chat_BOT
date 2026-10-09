def test_product_list_detail_and_not_found(client):
    listing = client.get("/api/v1/products")
    assert listing.status_code == 200
    payload = listing.json()
    assert payload["total"] == 3
    assert payload["count"] == 3
    assert len(payload["items"]) == 3

    detail = client.get("/api/v1/products/LAP-001")
    assert detail.status_code == 200
    assert detail.json()["id"] == "LAP-001"

    missing = client.get("/api/v1/products/UNKNOWN")
    assert missing.status_code == 404

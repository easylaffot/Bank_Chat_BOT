def test_shopping_assistant_and_faq_apis(client, monkeypatch, mock_shopping_workflow, mock_faq_agent):
    from app.api.v1 import faq as faq_api
    from app.api.v1 import shopping_assistant as shopping_api

    monkeypatch.setattr(shopping_api._service, "workflow_runner", mock_shopping_workflow)
    monkeypatch.setattr(faq_api, "_faq_agent", mock_faq_agent)

    assistant = client.post(
        "/api/v1/shopping-assistant",
        json={"query": "programming laptop under 60000"},
    )
    assert assistant.status_code == 200
    assert assistant.json()["recommendation"]["id"] == "LAP-002"
    assert assistant.json()["alternatives"][0]["id"] == "LAP-001"
    assert assistant.json()["error"] is None
    mock_shopping_workflow.assert_called_once_with("programming laptop under 60000")

    faq = client.post("/api/v1/faq", json={"question": "What warranty is available?"})
    assert faq.status_code == 200
    assert faq.json()["sources"] == ["data/faq/warranty.txt"]
    mock_faq_agent.answer.assert_called_once_with("What warranty is available?")

"""Unit tests for deterministic leak scanner in backend/app/guard/scanner.py.

Tests run against hand-written sample bodies strictly mirroring docs/api.md.
"""

from __future__ import annotations

from backend.app.guard.scanner import is_response_safe, scan_response

# --- Fixtures mirroring docs/api.md sample bodies ---


def make_clean_inventory_text_response() -> dict:
    return {
        "contract_version": "0.1",
        "request_id": "req-101",
        "role": "inventory_manager",
        "thread_id": "thread-12345",
        "status": "answered",
        "reason_code": None,
        "answer_text": "Widget Alpha currently has 150 units in stock with 25 on reorder.",
        "presentation": {"type": "text"},
        "evidence": [
            {
                "id": "ev-1",
                "kind": "tool",
                "label": "Stock query",
                "detail": "get_stock_level(item_id='WA-01')",
                "columns": ["item_id", "stock_qty", "reorder_qty"],
                "row_count": 1,
                "rows_preview": [{"item_id": "WA-01", "stock_qty": 150, "reorder_qty": 25}],
                "executed_at": "2026-11-18T10:00:00Z",
            }
        ],
        "notes": [],
    }


def make_clean_inventory_table_response() -> dict:
    return {
        "contract_version": "0.1",
        "request_id": "req-102",
        "role": "inventory_manager",
        "thread_id": "thread-12345",
        "status": "answered",
        "reason_code": None,
        "answer_text": "Here are the current stock levels for widgets.",
        "presentation": {
            "type": "table",
            "columns": [
                {"key": "item_id", "label": "Item Code", "type": "string"},
                {"key": "item_name", "label": "Item Name", "type": "string"},
                {"key": "stock_qty", "label": "Quantity on Hand", "type": "integer"},
            ],
            "rows": [
                {"item_id": "WA-01", "item_name": "Widget Alpha", "stock_qty": 150},
                {"item_id": "WB-02", "item_name": "Widget Beta", "stock_qty": 75},
            ],
            "total_rows": 2,
            "truncated": False,
        },
        "evidence": [
            {
                "id": "ev-2",
                "kind": "sql_view",
                "label": "Inventory levels view",
                "detail": "SELECT item_id, item_name, stock_qty FROM v_inventory_items",
                "columns": ["item_id", "item_name", "stock_qty"],
                "row_count": 2,
                "rows_preview": [
                    {"item_id": "WA-01", "item_name": "Widget Alpha", "stock_qty": 150},
                ],
                "executed_at": "2026-11-18T10:00:00Z",
            }
        ],
        "notes": [],
    }


def make_clean_inventory_refusal_response() -> dict:
    return {
        "contract_version": "0.1",
        "request_id": "req-103",
        "role": "inventory_manager",
        "thread_id": "thread-12345",
        "status": "refused",
        "reason_code": "outside_role_access",
        "answer_text": (
            "Requested information is outside the inventory manager role access. "
            "I can assist with item quantities, stock levels, and reorder status."
        ),
        "presentation": {"type": "text"},
        "evidence": [],
        "notes": [],
    }


def make_clean_no_data_response() -> dict:
    return {
        "contract_version": "0.1",
        "request_id": "req-104",
        "role": "inventory_manager",
        "thread_id": "thread-12345",
        "status": "no_data",
        "reason_code": "data_not_available",
        "answer_text": (
            "The database contains factory stock levels, "
            "but does not track external market pricing."
        ),
        "presentation": {"type": "text"},
        "evidence": [],
        "notes": [],
    }


def make_clean_owner_pricing_response() -> dict:
    return {
        "contract_version": "0.1",
        "request_id": "req-201",
        "role": "owner",
        "thread_id": "thread-owner-1",
        "status": "answered",
        "reason_code": None,
        "answer_text": (
            "Widget Alpha selling price is $150.00 with unit cost $90.00 and margin $60.00."
        ),
        "presentation": {
            "type": "table",
            "columns": [
                {"key": "item_id", "label": "Item", "type": "string"},
                {"key": "price", "label": "Selling Price", "type": "number"},
                {"key": "cost", "label": "Unit Cost", "type": "number"},
            ],
            "rows": [{"item_id": "WA-01", "price": 150.0, "cost": 90.0}],
            "total_rows": 1,
            "truncated": False,
        },
        "evidence": [
            {
                "id": "ev-owner-1",
                "kind": "tool",
                "label": "Pricing tool",
                "detail": "get_item_pricing(item_id='WA-01')",
                "columns": ["item_id", "price", "cost"],
                "row_count": 1,
                "rows_preview": [{"item_id": "WA-01", "price": 150.0, "cost": 90.0}],
                "executed_at": "2026-11-18T10:00:00Z",
            }
        ],
        "notes": [],
    }


def make_clean_error_response() -> dict:
    return {
        "error": {
            "code": "invalid_role",
            "message": "Role 'supervisor' is not recognized.",
            "request_id": "req-err-1",
        }
    }


# --- Test Cases ---


class TestCleanResponses:
    def test_clean_inventory_manager_text_passes(self):
        resp = make_clean_inventory_text_response()
        result = scan_response(resp)
        assert result.passed is True
        assert len(result.violations) == 0

    def test_clean_inventory_manager_table_passes(self):
        resp = make_clean_inventory_table_response()
        result = scan_response(resp)
        assert result.passed is True
        assert is_response_safe(resp) is True

    def test_clean_inventory_manager_refusal_passes(self):
        resp = make_clean_inventory_refusal_response()
        result = scan_response(resp)
        assert result.passed is True

    def test_clean_no_data_passes(self):
        resp = make_clean_no_data_response()
        result = scan_response(resp)
        assert result.passed is True

    def test_clean_owner_with_monetary_fields_passes(self):
        # Owner is authorized to see monetary fields, so it must pass
        resp = make_clean_owner_pricing_response()
        result = scan_response(resp, role="owner")
        assert result.passed is True

    def test_clean_error_response_passes(self):
        resp = make_clean_error_response()
        result = scan_response(resp)
        assert result.passed is True


class TestMonetaryTextLeaks:
    def test_direct_currency_symbol_in_answer_fails(self):
        resp = make_clean_inventory_text_response()
        resp["answer_text"] = "Widget Alpha costs $25.00."
        result = scan_response(resp)
        assert result.passed is False
        assert any(v.rule == "monetary_value" for v in result.violations)

    def test_currency_code_with_amount_fails(self):
        resp = make_clean_inventory_text_response()
        resp["answer_text"] = "Widget Alpha has total value 1500 USD in warehouse."
        result = scan_response(resp)
        assert result.passed is False
        assert any(v.rule == "monetary_value" for v in result.violations)

    def test_qualitative_price_words_fail(self):
        resp = make_clean_inventory_text_response()
        resp["answer_text"] = "Widget Alpha is the cheapest item in category A."
        result = scan_response(resp)
        assert result.passed is False
        assert any(
            v.rule == "monetary_keyword" and "cheapest" in v.matched_term
            for v in result.violations
        )

    def test_expensive_word_fails(self):
        resp = make_clean_inventory_text_response()
        resp["answer_text"] = "This is a premium and expensive item."
        result = scan_response(resp)
        assert result.passed is False
        assert any("expensive" in v.matched_term for v in result.violations)

    def test_notes_field_leak_detected(self):
        resp = make_clean_inventory_text_response()
        resp["notes"] = ["Note: Item value estimated at $50 per unit."]
        result = scan_response(resp)
        assert result.passed is False
        assert any(v.path.startswith("notes") for v in result.violations)


class TestPresentationPayloadLeaks:
    def test_forbidden_column_key_in_table_fails(self):
        resp = make_clean_inventory_table_response()
        resp["presentation"]["columns"].append(
            {"key": "unit_price", "label": "Price", "type": "number"}
        )
        result = scan_response(resp)
        assert result.passed is False
        assert any(v.rule == "forbidden_monetary_field" for v in result.violations)

    def test_forbidden_column_label_in_table_fails(self):
        resp = make_clean_inventory_table_response()
        resp["presentation"]["columns"].append(
            {"key": "val_1", "label": "Sales Revenue", "type": "number"}
        )
        result = scan_response(resp)
        assert result.passed is False
        assert any(v.rule == "monetary_keyword" for v in result.violations)

    def test_forbidden_row_key_in_table_fails(self):
        resp = make_clean_inventory_table_response()
        resp["presentation"]["rows"][0]["price"] = 99.99
        result = scan_response(resp)
        assert result.passed is False
        assert any(v.rule == "forbidden_monetary_field" for v in result.violations)

    def test_chart_series_leak_fails(self):
        resp = make_clean_inventory_text_response()
        resp["presentation"] = {
            "type": "chart",
            "kind": "bar",
            "title": "Stock vs Revenue",
            "x": {"key": "item_id", "label": "Item", "type": "string"},
            "series": [{"key": "total_revenue", "label": "Total Revenue"}],
            "rows": [{"item_id": "WA-01", "total_revenue": 5000}],
            "truncated": False,
        }
        result = scan_response(resp)
        assert result.passed is False
        assert any(v.rule == "forbidden_monetary_field" for v in result.violations)


class TestEvidenceLeaks:
    def test_evidence_column_list_leak_fails(self):
        resp = make_clean_inventory_text_response()
        resp["evidence"][0]["columns"].append("cost_price")
        result = scan_response(resp)
        assert result.passed is False
        assert any("evidence[0].columns" in v.path for v in result.violations)

    def test_evidence_detail_monetary_leak_fails(self):
        resp = make_clean_inventory_text_response()
        resp["evidence"][0]["detail"] = "SELECT item_id, price FROM items WHERE price > 50"
        result = scan_response(resp)
        assert result.passed is False
        assert any(
            v.rule in ("monetary_field_in_text", "forbidden_monetary_field")
            for v in result.violations
        )

    def test_evidence_preview_row_leak_fails(self):
        resp = make_clean_inventory_text_response()
        resp["evidence"][0]["rows_preview"][0]["margin"] = 12.50
        result = scan_response(resp)
        assert result.passed is False


class TestErrorPayloadLeaks:
    def test_error_message_revealing_hidden_columns_fails(self):
        resp = {
            "error": {
                "code": "query_error",
                "message": "Column 'unit_price' cannot be accessed by inventory_manager.",
                "request_id": "req-err-2",
            }
        }
        result = scan_response(resp, role="inventory_manager")
        assert result.passed is False
        assert any("unit_price" in v.matched_term for v in result.violations)

    def test_error_message_with_monetary_value_fails(self):
        resp = {
            "error": {
                "code": "threshold_error",
                "message": "Filter threshold $500 exceeds policy.",
                "request_id": "req-err-3",
            }
        }
        result = scan_response(resp, role="inventory_manager")
        assert result.passed is False


class TestSecretAndCredentialLeaks:
    def test_openai_api_key_leak_detected_for_owner(self):
        mock_key = "".join(["s", "k", "-proj-1234567890abcdefghijklmnopqrstuvwxyz"])
        resp = make_clean_owner_pricing_response()
        resp["answer_text"] = f"Diagnostics: authenticated with {mock_key}."
        result = scan_response(resp, role="owner")
        assert result.passed is False
        assert any("secret_leak_openai_api_key" in v.rule for v in result.violations)

    def test_database_url_leak_detected_for_inventory(self):
        mock_url = "".join(["postgresql", "://testuser:secretpass@localhost:5432/factory"])
        resp = make_clean_inventory_text_response()
        resp["evidence"][0]["detail"] = f"Connecting to {mock_url}"
        result = scan_response(resp)
        assert result.passed is False
        assert any("secret_leak_database_connection_url" in v.rule for v in result.violations)

    def test_bearer_token_leak_detected(self):
        mock_jwt = "".join(["Bearer ", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abcdefghijk"])
        resp = make_clean_inventory_text_response()
        resp["notes"] = [f"Auth: {mock_jwt}"]
        result = scan_response(resp)
        assert result.passed is False
        assert any("secret_leak_bearer_token" in v.rule for v in result.violations)


class TestEdgeCases:
    def test_empty_response(self):
        result = scan_response({})
        assert result.passed is True

    def test_nested_empty_structures(self):
        result = scan_response({"presentation": {"rows": []}, "evidence": [], "notes": []})
        assert result.passed is True

    def test_proxy_fields_detected(self):
        resp = make_clean_inventory_text_response()
        resp["evidence"][0]["columns"].append("pricing_tier")
        result = scan_response(resp)
        assert result.passed is False
        assert any("pricing_tier" in v.matched_term for v in result.violations)

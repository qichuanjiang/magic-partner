from app.services.request_ids import build_request_id


def test_build_request_id_format():
    request_id = build_request_id()

    assert request_id.startswith("req_")
    assert len(request_id) == 16
    assert all(character in "0123456789abcdef" for character in request_id[4:])

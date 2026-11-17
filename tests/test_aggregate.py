import json

from news_aggregator import aggregate


def test_main_appends_to_pending_buffer(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "REPORTS_DIR", tmp_path)
    monkeypatch.setattr(aggregate, "SEEN_FILE", tmp_path / "seen.json")
    monkeypatch.setattr(aggregate, "PENDING_FILE", tmp_path / "pending.json")
    monkeypatch.setattr(aggregate, "load_feeds", lambda: {})
    (tmp_path / "pending.json").write_text(json.dumps([{"url": "old"}]))
    monkeypatch.setattr(aggregate, "fetch_feeds", lambda cutoff, seen, feeds: [{"url": "new"}])

    aggregate.main()

    assert json.loads((tmp_path / "pending.json").read_text()) == [{"url": "old"}, {"url": "new"}]

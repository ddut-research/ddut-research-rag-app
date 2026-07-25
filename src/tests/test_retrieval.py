from src.retrieval import retrieve_sources


def test_retrieve_sources_returns_list():
    results = retrieve_sources(
        district="All districts",
        question="test question",
        themes=["Political and Current Events"],
        tags=["Public services"],
    )
    assert isinstance(results, list)


def test_retrieve_sources_contains_expected_keys():
    results = retrieve_sources(
        district="All districts",
        question="test question",
        themes=["Political and Current Events"],
        tags=["Public services"],
    )
    assert len(results) > 0

    sample = results[0]
    expected_keys = {
        "id",
        "title",
        "url",
        "source_type",
        "published",
        "domain",
        "content",
        "relevance",
    }
    assert expected_keys.issubset(sample.keys())


def test_retrieve_sources_relevance_is_numeric():
    results = retrieve_sources(
        district="All districts",
        question="test question",
        themes=["Political and Current Events"],
        tags=["Public services"],
    )
    sample = results[0]
    assert isinstance(sample["relevance"], (int, float))

from ftui.filters import next_state_mode, parse_filter
from ftui.fleet import Machine


def machine(**kw):
    base = dict(account="starlogik", org="hp-71", app="hp-flows", id="148ed106c62289",
                name="dry-fire-42", state="started", region="fra", cpu_kind="shared",
                cpus=1, memory_mb=512, image="hp-flows:deployment-1", process_group="app",
                created_at="", updated_at="")
    base.update(kw)
    return Machine(**base)


def test_parse_tokens_and_terms():
    f = parse_filter("state:stopped region:fra region:AMS web")
    assert f.include == {"state": ["stopped"], "region": ["fra", "ams"]}
    assert f.terms == ["web"]


def test_aliases_negation_and_partial_tokens():
    f = parse_filter("acct:hp account:jewl -state:started org:")
    assert f.include == {"account": ["hp", "jewl"]}
    assert f.exclude == {"state": ["started"]}
    assert f.terms == []  # "org:" with no value is ignored while typing


def test_unknown_key_is_free_text_and_quotes():
    f = parse_filter('foo:bar "dry fire"')
    assert f.terms == ["foo:bar", "dry fire"]
    assert parse_filter('"unbalanced').terms == ['"unbalanced']


def test_matches():
    m = machine()
    assert parse_filter("").matches(m)
    assert parse_filter("state:started region:fra").matches(m)
    assert not parse_filter("state:stopped").matches(m)
    assert parse_filter("region:ams region:fra").matches(m)  # same key ORs
    assert parse_filter("app:hp-*").matches(m)                # glob
    assert not parse_filter("app:hp").matches(m)               # tokens match whole field
    assert parse_filter("acct:STARLOGIK dry").matches(m)       # case-insensitive
    assert not parse_filter("-state:started").matches(m)
    assert parse_filter("shared-1x").matches(m)


def test_state_mode_cycle():
    assert next_state_mode("all") == "started"
    assert next_state_mode("started") == "stopped"
    assert next_state_mode("stopped") == "all"

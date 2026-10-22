"""Split report HTML and preserve query strings when rewriting SQL-backed links."""

from user.sqlupload import HTMLdivide, SQLlastUpload


def test_html_split_and_link_rewrite():
    parser = HTMLdivide('<?php fixture ?>', ['day.html', 'chart.png'], divide_tag='body')
    parser.feed('<html><head><title>Fixture</title></head><body><a href="day.html?x=1">Zero: 0</a></body></html>')
    parser.close()
    assert '<title>Fixture</title>' in parser.php_data.replace('<title >', '<title>')
    assert '<?php fixture ?>' in parser.php_data
    assert 'Zero: 0' not in parser.php_data
    assert 'href="day.php?x=1"' in parser.db_data
    assert 'Zero: 0' in parser.db_data


def test_persistent_upload_hashes(tmp_path):
    first = SQLlastUpload(str(tmp_path))
    first.add_hash('day', 'abc123')
    first.save()
    second = SQLlastUpload(str(tmp_path))
    assert second.get_hash('day') == 'abc123'
    assert second.get_hash('unknown') is None

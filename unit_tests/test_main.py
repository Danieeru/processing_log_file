import pytest
import json
import sys
from io import StringIO
from src.main import check_json_line, check_correct_data, check_correct_file, write_data_in_report, create_report, main

@pytest.mark.parametrize("json_line, expected", [
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}, True),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": 100, "http_user_agent": "..."}, True),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": 0, "http_user_agent": "..."}, True),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "", "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}, False),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "     ", "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}, False),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": None, "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}, False),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}, False),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": "0.02", "http_user_agent": "..."}, False),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": True, "http_user_agent": "..."}, False),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": False, "http_user_agent": "..."}, False),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": -1, "http_user_agent": "..."}, False),
    ({"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET","http_user_agent": "..."}, False),
])
def test_check_json_line(json_line, expected):
    assert check_json_line(json_line) == expected


@pytest.mark.parametrize("line, expected", [
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}', True),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": 100, "http_user_agent": "..."}', True),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": 0, "http_user_agent": "..."}', True),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "", "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}', False),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "     ", "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}', False),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": None, "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}', False),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "request_method": "GET", "response_time": 0.02, "http_user_agent": "..."}', False),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": "0.02", "http_user_agent": "..."}', False),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": True, "http_user_agent": "..."}', False),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": False, "http_user_agent": "..."}', False),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET", "response_time": -1, "http_user_agent": "..."}', False),
    ('{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET","http_user_agent": "..."}', False),
])
def test_check_correct_data(line, expected):
    assert check_correct_data(line) == expected

@pytest.mark.parametrize("create_file, filename, content, expected", [
    (False, "nonexistent.log", None, False),
    (True, "test.txt", "content", False),
    (True, "test", "content", False),
    (True, "test.log.txt", "content", False),
    (True, "empty.log", "", False),
    (True, "valid.log", "some content", True),
])
def test_check_correct_file_parametrized(tmp_path, create_file, filename, content, expected):
    if create_file:
        file = tmp_path / filename
        file.write_text(content)
        file_path = str(file)
    else:
        file_path = filename
    assert check_correct_file(file_path) == expected


@pytest.mark.parametrize("test_case", [
    {
        "name": "первый запрос по URL",
        "initial_report": {},
        "line": '{"url": "/api/test", "response_time": 0.02}',
        "expected_report": {"/api/test": {"count": 1, "response_time": 0.02}}
    },
    {
        "name": "второй запрос по тому же URL",
        "initial_report": {"/api/test": {"count": 1, "response_time": 0.02}},
        "line": '{"url": "/api/test", "response_time": 0.04}',
        "expected_report": {"/api/test": {"count": 2, "response_time": 0.06}}
    },
    {
        "name": "новый URL",
        "initial_report": {"/api/existing": {"count": 1, "response_time": 0.1}},
        "line": '{"url": "/api/new", "response_time": 0.05}',
        "expected_report": {
            "/api/existing": {"count": 1, "response_time": 0.1},
            "/api/new": {"count": 1, "response_time": 0.05}
        }
    },
    {
        "name": "невалидный JSON",
        "initial_report": {"/api/test": {"count": 1, "response_time": 0.02}},
        "line": '{"invalid json"',
        "expected_exception": json.JSONDecodeError
    },
    {
        "name": "невалидные данные в JSON",
        "initial_report": {"/api/test": {"count": 1, "response_time": 0.02}},
        "line": '{"url": "", "response_time": 0.02}',
        "expected_report": {"/api/test": {"count": 1, "response_time": 0.02}}
    }
])

def test_write_data_in_report(test_case):
    report = {k: v.copy() for k, v in test_case["initial_report"].items()}
    if "expected_exception" in test_case:
        with pytest.raises(test_case["expected_exception"]):
            write_data_in_report(report, test_case["line"])
    else:
        write_data_in_report(report, test_case["line"])
        assert report == test_case["expected_report"]


@pytest.mark.parametrize("report, expected_content", [
    (
        {"/api/test": {"count": 2, "response_time": 0.04}},
        ["/api/test", "0.020"]
    ),
    (
        {
            "/api/popular": {"count": 5, "response_time": 0.15},
            "/api/rare": {"count": 1, "response_time": 0.02}
        },
        ["/api/popular", "0.030", "/api/rare", "0.020"]
    ),
    (
        {},
        []
    ),
    (
        {"/api/fast": {"count": 3, "response_time": 0}},
        ["/api/fast", "0.000"]
    )
])
def test_create_report(capsys, report, expected_content):
    create_report(report)
    captured = capsys.readouterr()
    output = captured.out
    if expected_content:
        for content in expected_content:
            assert content in output, f"Содержимое '{content}' не найдено в выводе"
    else:
        assert output.strip() == "" or "handler" not in output


@pytest.mark.parametrize("log_content, expected_strings", [
    (
        '{"url": "/api/test", "response_time": 0.02}\n'
        '{"url": "/api/test", "response_time": 0.04}\n',
        ["/api/test", "0.030"]
    ),
    (
        '{"url": "/api/first", "response_time": 0.01}\n'
        '{"url": "/api/second", "response_time": 0.03}\n'
        '{"url": "/api/first", "response_time": 0.01}\n',
        ["/api/first", "0.010", "/api/second", "0.030"]
    ),
    (
        "",
        []
    ),
    (
        '{"invalid": "json"\n'
        '{"url": "/api/test", "response_time": 0.02}\n'
        'not json at all\n',
        ["/api/test", "0.020"]
    )
])
def test_main_integration(tmp_path, log_content, expected_strings):
    log_file = tmp_path / "test.log"
    log_file.write_text(log_content)
    original_argv = sys.argv
    original_stdout = sys.stdout
    try:
        sys.argv = ['log_parser.py', '--file', str(log_file)]
        captured_output = StringIO()
        sys.stdout = captured_output
        main()
        output = captured_output.getvalue() 
        if expected_strings:
            for expected_str in expected_strings:
                assert expected_str in output, f"'{expected_str}' не найден в выводе"
        else:
            assert output.strip() == "" or "handler" not in output
    finally:
        sys.argv = original_argv
        sys.stdout = original_stdout
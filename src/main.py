import os
import json
import argparse
from tabulate import tabulate


def parser_init() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", action="append", nargs="+", help="Path to log file")
    parser.add_argument("--report", default="average", help="Report type")
    parser.add_argument("--date", help="Date")
    args = parser.parse_args()
    return args


def create_report(report: dict) -> None:
    if report == {}:
        return
    sorted_report = dict(sorted(report.items(),
                                key=lambda item: item[1]['count'],
                                reverse=True))
    headers = ["handler", "total", "avg_response_time"]
    rows = [(key, value['count'], value['response_time'] / value['count'])
            for key, value in sorted_report.items()]
    print(tabulate(rows, headers=headers,
                            showindex=1, floatfmt=".3f"))


def check_correct_file(file: str) -> bool:
    if (not os.path.exists(file) or not os.path.isfile(file) or
            os.path.getsize(file) == 0):
        return False
    if not file.endswith('.log'):
        return False
    return True


def check_json_line(json_line) -> bool:
    if not isinstance(json_line, dict):
        return False
    url = json_line.get('url')
    if not isinstance(url, str) or not url.strip():
        return False
    response_time = json_line.get('response_time')
    # исключаем bool, так как bool является подклассом int
    if (isinstance(response_time, bool) or
            not isinstance(response_time, (int, float))):
        return False
    if response_time < 0:
        return False
    return True


def check_correct_data(line: str) -> bool:
    try:
        json_line = json.loads(line)
    except json.JSONDecodeError:
        return False
    return check_json_line(json_line)


def write_data_in_report(report: dict, line: str) -> None:
    json_line = json.loads(line)
    if not check_json_line(json_line):
        return
    if json_line['url'] not in report:
        report[json_line['url']] = {
            'count': 1,
            'response_time': json_line['response_time']
        }
    else:
        report[json_line['url']]['count'] += 1
        report[json_line['url']]['response_time'] += json_line['response_time']


def main():
    report = {}
    args = parser_init()
    if args.file is None:
        return
    files = set([f for file in args.file for f in file])
    for file in files:
        if not check_correct_file(file):
            continue
        with open(file, 'r') as f:
            for line in f:
                if not check_correct_data(line):
                    continue
                write_data_in_report(report, line)
    create_report(report)


if __name__ == "__main__":
    main()

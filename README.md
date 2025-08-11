## Запуск программы

```
git clone https://github.com/Danieeru/processing_log_file.git
cd processing_log_file
python3 -m venv .venv
sourse .venv/bin/activate
pip install -r requirements.txt
cd src
python3 main.py --file example1.log  example2.log --report average
```
## Запуск тестов
Запуск тестов происходит из корневой директории
```
pytest -q
```
Отчёт о покрытии кода
```
pytest --cov=src.main --cov-report=term-missing
```
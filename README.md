# 국내주식 조회 웹앱

GitHub 첫 화면에 다음 3개 파일을 올립니다.
- app.py
- index.html
- requirements.txt

Render:
Build Command: `pip install -r requirements.txt`
Start Command: `gunicorn app:app`

종목명 또는 6자리 종목코드로 조회합니다.
예: 삼성전자 / 005930

네이버 증권 페이지 구조가 바뀌면 일부 값이 비어 있을 수 있습니다.

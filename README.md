# 국내주식 종목 조회

네이버증권 JSON API를 이용해 종목명/종목코드로 국내주식 정보를 조회합니다.

표시 항목:
- 현재가 / 전일대비 / 등락률
- 시가총액
- PER / EPS
- PBR / BPS
- 영업이익
- 멀티플 = 시가총액 ÷ 최신 연간 영업이익

Render:
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

주의: 네이버의 공개 웹 JSON 엔드포인트는 공식 API 문서가 없는 내부 엔드포인트이므로 향후 구조가 변경될 수 있습니다.

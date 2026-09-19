from flask import Flask, request, jsonify, send_file
import requests, re
from bs4 import BeautifulSoup

app = Flask(__name__)
HEADERS={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"}
COMMON={"삼성전자":"005930","SK하이닉스":"000660","한미반도체":"042700","두산에너빌리티":"034020","현대차":"005380","기아":"000270","LG에너지솔루션":"373220","삼성SDI":"006400","NAVER":"035420","카카오":"035720"}

def resolve(q):
    q=q.strip()
    if re.fullmatch(r"\d{6}",q): return q
    if q in COMMON: return COMMON[q]
    try:
        r=requests.get("https://m.stock.naver.com/api/search/searchList",params={"query":q},headers=HEADERS,timeout=8)
        d=r.json(); items=[]
        if isinstance(d,dict):
            for k in ("stocks","result","items"):
                if isinstance(d.get(k),list): items+=d[k]
        for x in items:
            if isinstance(x,dict):
                c=x.get("itemCode") or x.get("code") or x.get("stockCode")
                n=x.get("itemName") or x.get("name")
                if c and n==q: return str(c).zfill(6)
        for x in items:
            if isinstance(x,dict):
                c=x.get("itemCode") or x.get("code") or x.get("stockCode")
                if c: return str(c).zfill(6)
    except: pass
    return None

def field(h,names):
    for n in names:
        m=re.search(r'"'+re.escape(n)+r'"\s*:\s*"?([^",}\]]+)',h)
        if m:return m.group(1).replace("\\u002C",",").strip()
    return None

def stock(code):
    url=f"https://m.stock.naver.com/domestic/stock/{code}/total?domesticStockExchange=KRX"
    r=requests.get(url,headers=HEADERS,timeout=10); r.raise_for_status()
    h=r.text; s=BeautifulSoup(h,"html.parser")
    title=s.title.get_text(" ",strip=True) if s.title else ""
    return {"name":field(h,["stockName","itemName","name"]) or title.split(":")[0] or code,
            "code":code,"price":field(h,["closePrice","currentPrice","nowPrice"]),
            "change":field(h,["compareToPreviousClosePrice","changePrice"]),
            "change_rate":field(h,["fluctuationsRatio","changeRate"]),
            "market_cap":field(h,["marketValue","marketCap","marketCapitalization"]),
            "per":field(h,["per"]),"eps":field(h,["eps"]),"pbr":field(h,["pbr"]),
            "bps":field(h,["bps"]),"operating_profit":field(h,["operatingProfit","operatingIncome"]),
            "source":url}

@app.route("/")
def home(): return send_file("index.html")

@app.route("/api/stock")
def api():
    q=request.args.get("query","").strip()
    if not q:return jsonify({"error":"종목명 또는 6자리 종목코드를 입력하세요."}),400
    c=resolve(q)
    if not c:return jsonify({"error":"종목을 찾지 못했습니다. 6자리 종목코드를 입력해 보세요."}),404
    try:return jsonify(stock(c))
    except Exception as e:return jsonify({"error":"네이버 증권 데이터를 가져오지 못했습니다.","detail":str(e)}),502

if __name__=="__main__": app.run(host="0.0.0.0",port=10000)

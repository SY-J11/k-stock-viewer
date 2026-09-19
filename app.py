from flask import Flask,request,jsonify,send_file
import requests,re

app=Flask(__name__)
H={"User-Agent":"Mozilla/5.0","Referer":"https://m.stock.naver.com/"}

COMMON={
    "삼성전자":"005930","SK하이닉스":"000660","한미반도체":"042700",
    "두산에너빌리티":"034020","현대차":"005380","기아":"000270",
    "LG에너지솔루션":"373220","삼성SDI":"006400","NAVER":"035420",
    "카카오":"035720"
}

def J(u):
    r=requests.get(u,headers=H,timeout=10)
    r.raise_for_status()
    return r.json()

def code(q):
    q=q.strip()
    if re.fullmatch(r"\d{6}",q):
        return q
    if q in COMMON:
        return COMMON[q]
    try:
        d=J(
            "https://m.stock.naver.com/front-api/search/autoComplete"
            "?query="+requests.utils.quote(q)
            "&target=stock,index,marketindicator,coin,ipo"
        )
        items=d.get("result",{}).get("items",[])
        for x in items:
            if x.get("name")==q and x.get("code"):
                return str(x["code"]).zfill(6)
        for x in items:
            if x.get("code"):
                return str(x["code"]).zfill(6)
    except:
        pass

def info(d):
    return {x.get("code"):x.get("value") for x in d.get("totalInfos",[]) if x.get("code")}

def op_profit(d):
    fi=d.get("financeInfo",{})
    rows=fi.get("rowList",[])
    titles=fi.get("trTitleList",[])
    keys=[
        x.get("key") for x in titles
        if x.get("key") and str(x.get("isConsensus","N")).upper()=="N"
    ]
    for row in rows:
        t=str(row.get("title","")).replace(" ","")
        if "영업이익" in t:
            c=row.get("columns",{})
            for k in reversed(keys):
                if isinstance(c.get(k),dict) and c[k].get("value") not in (None,""):
                    return c[k]["value"]

def parse_money(s):
    """네이버의 조/억/만/원 표시 문자열을 원 단위 숫자로 변환."""
    if s is None:
        return None
    s=str(s).replace(",","").replace(" ","").replace("원","")
    if not s:
        return None
    total=0.0
    found=False
    m=re.search(r"([0-9.]+)조",s)
    if m:
        total += float(m.group(1))*1_0000_0000_0000
        found=True
    m=re.search(r"([0-9.]+)억",s)
    if m:
        total += float(m.group(1))*100_000_000
        found=True
    m=re.search(r"([0-9.]+)만",s)
    if m:
        total += float(m.group(1))*10_000
        found=True
    # 단위가 붙은 조/억/만이 없으면 숫자 자체로 간주
    if found:
        return total
    nums=re.sub(r"[^0-9.\-]","",s)
    return float(nums) if nums else None

def parse_operating_profit_won(s):
    """연간 재무제표 영업이익은 억원 단위."""
    if s is None:
        return None
    s=str(s).replace(",","").replace(" ","").replace("억원","")
    m=re.search(r"-?[0-9.]+",s)
    return float(m.group())*100_000_000 if m else None

def multiple(market_cap, operating_profit):
    mc=parse_money(market_cap)
    op=parse_operating_profit_won(operating_profit)
    if mc is None or op is None or op <= 0:
        return None
    return mc/op

def stock(c):
    q=(J(f"https://polling.finance.naver.com/api/realtime/domestic/stock/{c}").get("datas") or [{}])[0]
    i=info(J(f"https://m.stock.naver.com/api/stock/{c}/integration"))
    try:
        o=J(f"https://m.stock.naver.com/api/stock/{c}/finance/annual")
        p=op_profit(o)
    except:
        p=None

    return {
        "name":q.get("stockName") or c,
        "code":c,
        "price":q.get("closePrice"),
        "change":q.get("compareToPreviousClosePrice"),
        "rate":q.get("fluctuationsRatio"),
        "time":q.get("localTradedAt"),
        "market_cap":i.get("marketValue"),
        "per":i.get("per"),
        "eps":i.get("eps"),
        "pbr":i.get("pbr"),
        "bps":i.get("bps"),
        "operating_profit":p,
        "multiple":multiple(i.get("marketValue"),p),
        "foreign":i.get("foreignRate")
    }

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/api/stock")
def api():
    c=code(request.args.get("query",""))
    if not c:
        return jsonify(error="종목을 찾지 못했습니다."),404
    try:
        return jsonify(stock(c))
    except Exception as e:
        return jsonify(error="네이버 데이터 조회 실패",detail=str(e)),502

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)

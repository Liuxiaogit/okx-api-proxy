from flask import Flask, jsonify, request
import requests
import time

app = Flask(__name__)

OKX_BASE = "https://www.okx.com"

# ==================== 行情接口 ====================

@app.route("/api/eth-price", methods=["GET"])
def eth_price():
    """ETH-USDT 永续合约实时价格"""
    try:
        resp = requests.get(
            f"{OKX_BASE}/api/v5/market/ticker",
            params={"instId": "ETH-USDT-SWAP"},
            timeout=10
        )
        data = resp.json()
        if data.get("code") == "0" and data.get("data"):
            t = data["data"]
            return jsonify({
                "code": 0,
                "data": {
                    "instId": t["instId"],
                    "last": t["last"],
                    "bid": t.get("bidPx", ""),
                    "ask": t.get("askPx", ""),
                    "high24h": t.get("high24h", ""),
                    "low24h": t.get("low24h", ""),
                    "vol24h": t.get("vol24h", ""),
                    "ts": t["ts"]
                }
            })
        return jsonify({"code": -1, "msg": data.get("msg", "unknown error")}), 500
    except Exception as e:
        return jsonify({"code": -1, "msg": str(e)}), 500


@app.route("/api/eth-funding", methods=["GET"])
def eth_funding():
    """ETH-USDT 永续合约当前资金费率"""
    try:
        resp = requests.get(
            f"{OKX_BASE}/api/v5/public/funding-rate",
            params={"instId": "ETH-USDT-SWAP"},
            timeout=10
        )
        data = resp.json()
        if data.get("code") == "0" and data.get("data"):
            f = data["data"]
            return jsonify({
                "code": 0,
                "data": {
                    "instId": f["instId"],
                    "fundingRate": f["fundingRate"],
                    "fundingTime": f["fundingTime"],
                    "nextFundingRate": f.get("nextFundingRate", ""),
                    "nextFundingTime": f.get("nextFundingTime", "")
                }
            })
        return jsonify({"code": -1, "msg": data.get("msg", "unknown error")}), 500
    except Exception as e:
        return jsonify({"code": -1, "msg": str(e)}), 500


@app.route("/api/eth-kline", methods=["GET"])
def eth_kline():
    """ETH-USDT 永续合约 K 线数据"""
    bar = request.args.get("bar", "1H")      # 默认 1 小时
    limit = request.args.get("limit", "100")  # 默认 100 条
    try:
        resp = requests.get(
            f"{OKX_BASE}/api/v5/market/candles",
            params={"instId": "ETH-USDT-SWAP", "bar": bar, "limit": limit},
            timeout=10
        )
        data = resp.json()
        if data.get("code") == "0":
            # 原始数据格式：[ts, open, high, low, close, vol, volCcy, volCcyQuote, confirm]
            candles = []
            for c in data.get("data", []):
                candles.append({
                    "ts": c,
                    "open": c,
                    "high": c,
                    "low": c,
                    "close": c,
                    "vol": c
                })
            return jsonify({"code": 0, "data": candles})
        return jsonify({"code": -1, "msg": data.get("msg", "unknown error")}), 500
    except Exception as e:
        return jsonify({"code": -1, "msg": str(e)}), 500


@app.route("/api/eth-oi", methods=["GET"])
def eth_oi():
    """ETH-USDT 永续合约未平仓合约量"""
    try:
        resp = requests.get(
            f"{OKX_BASE}/api/v5/public/open-interest",
            params={"instId": "ETH-USDT-SWAP"},
            timeout=10
        )
        data = resp.json()
        if data.get("code") == "0" and data.get("data"):
            oi = data["data"]
            return jsonify({
                "code": 0,
                "data": {
                    "instId": oi["instId"],
                    "oi": oi["oi"],
                    "oiCcy": oi["oiCcy"],
                    "ts": oi["ts"]
                }
            })
        return jsonify({"code": -1, "msg": data.get("msg", "unknown error")}), 500
    except Exception as e:
        return jsonify({"code": -1, "msg": str(e)}), 500


# ==================== 健康检查 ====================

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "endpoints": [
            "/api/eth-price",
            "/api/eth-funding",
            "/api/eth-kline?bar=1H&limit=100",
            "/api/eth-oi"
        ]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

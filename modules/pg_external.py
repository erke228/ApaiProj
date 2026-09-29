"""modules/pg_external.py – External Bank page (dark)."""
import json
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.utils import load_metrics, load_models, plot_risk_histogram
from modules.i18n import t

ROOT    = Path(__file__).resolve().parent.parent
EXT_DIR = ROOT / "external_data"
EXT_DIR.mkdir(parents=True, exist_ok=True)
HIGH_RISK_COUNTRIES = {"RU","CN","NG","UA","KP","IR","BY","SY","VE","MM"}

_DEMO = {
    "transaction_id": "TXN-EXT-0001",
    "timestamp":      datetime.utcnow().isoformat(),
    "amount":         2500.00,
    "ip_address":     "185.220.101.5",
    "country_code":   "RU",
    "device_type":    "mobile",
    "session_risk":   0.72,
    "velocity_1h":    6,
    "account_age_days": 8,
    "previous_frauds":  1,
    "V1":-3.04,"V2":-3.16,"V3":4.20,"V4":1.77,"V5":-1.37,
    "V6":-0.33,"V7":-1.84,"V8":0.10,"V9":-0.71,"V10":-3.09,
    "V11":1.57,"V12":-3.49,"V13":0.65,"V14":-3.44,"V15":0.30,
    "V16":-0.67,"V17":-0.73,"V18":-0.29,"V19":0.22,"V20":0.61,
    "V21":-0.03,"V22":0.55,"V23":-0.03,"V24":-0.15,"V25":-0.09,
    "V26":-0.42,"V27":0.00,"V28":0.02,
    "Time":0,"Amount":2500.00,
}


def _ctx(rec: dict) -> tuple[float, list[str]]:
    score, reasons = 0.0, []
    if rec.get("country_code","").upper() in HIGH_RISK_COUNTRIES:
        score += 0.15; reasons.append(f"Risk Country ({rec['country_code']})")
    if rec.get("device_type","").lower() == "mobile":
        score += 0.05; reasons.append("Mobile Device")
    sr = float(rec.get("session_risk",0))
    if sr > 0.5:
        score += 0.20*sr; reasons.append(f"Session Risk {sr:.2f}")
    vel = int(rec.get("velocity_1h",0))
    if vel > 3:
        score += 0.15; reasons.append(f"High Velocity ({vel}/h)")
    age = int(rec.get("account_age_days",365))
    if age < 30:
        score += 0.10; reasons.append(f"New Account ({age} d)")
    pf = int(rec.get("previous_frauds",0))
    if pf > 0:
        score += 0.20; reasons.append(f"Past Frauds ({pf})")
    return min(score,1.0), reasons


def _get_feat(models: dict) -> list[str]:
    sm = next(iter(models.values()))
    if hasattr(sm,"feature_names_in_"): return list(sm.feature_names_in_)
    if hasattr(sm,"steps"):
        last = sm.steps[-1][1]
        if hasattr(last,"feature_names_in_"): return list(last.feature_names_in_)
    return []


def _score(rec: dict, models: dict, feat: list[str]) -> dict:
    row = {f: float(rec.get(f,0)) for f in feat}
    X   = pd.DataFrame([row])
    ml  = {}
    for nm, mdl in models.items():
        try: ml[nm] = float(mdl.predict_proba(X)[:,1][0])
        except: ml[nm] = 0.0
    ml_avg   = sum(ml.values())/max(len(ml),1)
    ctx, why = _ctx(rec)
    combined = round(0.70*ml_avg + 0.30*ctx, 4)
    return {
        "transaction_id": rec.get("transaction_id", str(uuid.uuid4())[:8]),
        "timestamp":      rec.get("timestamp", datetime.utcnow().isoformat()),
        "amount":         rec.get("amount",0),
        "ip_address":     rec.get("ip_address","-"),
        "country":        rec.get("country_code","-"),
        "device":         rec.get("device_type","-"),
        "session_risk":   rec.get("session_risk",0),
        "velocity_1h":    rec.get("velocity_1h",0),
        **{f"ml_{k}": round(v,4) for k,v in ml.items()},
        "ml_avg":         round(ml_avg,4),
        "context_score":  round(ctx,4),
        "combined_risk":  combined,
        "risk_reasons":   "; ".join(why) or "-",
        "verdict":        t("predict.fraud") if combined >= 0.5 else t("predict.legit"),
    }


def _save(results: list[dict]):
    day = datetime.utcnow().strftime("%Y-%m-%d")
    fp  = EXT_DIR / f"scored_{day}.jsonl"
    with open(fp,"a",encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False)+"\n")
    return fp


def _load_history() -> pd.DataFrame:
    rows = []
    for jl in sorted(EXT_DIR.glob("scored_*.jsonl")):
        with open(jl,encoding="utf-8") as f:
            for line in f:
                try: rows.append(json.loads(line))
                except: pass
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _show_single(r: dict):
    comb   = float(r.get("combined_risk",0))
    is_fr  = comb >= 0.5
    color  = "#EF4444" if is_fr else "#00D4B4"
    verdict= r.get("verdict","-")
    ml_avg = float(r.get("ml_avg",0))
    ctx    = float(r.get("context_score",0))

    st.markdown(f"""
    <div class="glass-card" style="border-left: 3px solid {color};">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
                <div style="font-size:0.65rem;color:#4d6690;font-weight:700;
                            text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">
                    ID транзакции
                </div>
                <div style="font-size:1.05rem;font-weight:700;color:#c8d6f0;">
                    {r.get('transaction_id','-')}
                </div>
                <div style="font-size:0.72rem;color:#4d6690;margin-top:2px;">
                    {r.get('timestamp','')}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:2rem;font-weight:900;color:{color};line-height:1;">
                    {comb:.0%}
                </div>
                <div style="font-size:0.8rem;font-weight:700;color:{color};">{verdict}</div>
                <div style="font-size:0.65rem;color:#4d6690;">Итоговый риск</div>
            </div>
        </div>
        <div style="border-top:1px solid rgba(76,139,245,0.1);margin:10px 0;"></div>
        <div style="display:flex;gap:1.2rem;flex-wrap:wrap;font-size:0.8rem;color:#6b85b8;">
            <span>Сумма: <b style="color:#c8d6f0;">${float(r.get('amount',0)):,.2f}</b></span>
            <span>IP: <b style="color:#c8d6f0;">{r.get('ip_address','-')}</b></span>
            <span>Страна: <b style="color:#c8d6f0;">{r.get('country','-')}</b></span>
            <span>Устройство: <b style="color:#c8d6f0;">{r.get('device','-')}</b></span>
            <span>Частота: <b style="color:#c8d6f0;">{r.get('velocity_1h',0)} тр/ч</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric(t("external.ml_prob"),  f"{ml_avg:.1%}")
    c2.metric(t("external.ctx_score"), f"{ctx:.1%}")
    c3.metric(t("external.combined"), f"{comb:.1%}")

    why = r.get("risk_reasons","-")
    if why and why != "-":
        st.markdown(f"**{t('external.risk_signals')}**")
        for reason in why.split(";"):
            st.markdown(f"""
            <div style="font-size:0.8rem;color:#f87171;padding:2px 0;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                     stroke="#EF4444" stroke-width="2" style="vertical-align:middle;margin-right:4px;">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {reason.strip()}
            </div>
            """, unsafe_allow_html=True)


def _show_batch(results: list[dict]):
    df     = pd.DataFrame(results)
    total  = len(results)
    fraud_n= sum(1 for r in results if float(r.get("combined_risk",0))>=0.5)
    c1,c2,c3 = st.columns(3)
    c1.metric(t("external.total"),  total)
    c2.metric(t("external.flagged"),fraud_n)
    c3.metric(t("external.fraud_rate"),f"{fraud_n/max(total,1):.1%}")
    if "combined_risk" in df.columns:
        st.plotly_chart(plot_risk_histogram(df), width='stretch',
                        config={"displayModeBar": False})
    show_cols = [c for c in ["transaction_id","amount","country","device",
                              "combined_risk","verdict","ml_avg","context_score",
                              "risk_reasons"] if c in df.columns]
    st.dataframe(df[show_cols], width='stretch', hide_index=True)


def render():
    st.markdown(f"## {t('external.title')}")
    st.caption(t("external.caption"))

    metrics = load_metrics()
    if not metrics:
        st.warning(t("predict.no_models"), icon=None); return

    ds_keys = list(metrics.keys())
    ds_tabs = st.tabs([k.replace("_"," ").title() for k in ds_keys])

    for i, ds_key in enumerate(ds_keys):
        with ds_tabs[i]:
            models = load_models(ds_key)
            if not models:
                st.warning(f"No models for `{ds_key}`.", icon=None); continue
            feat   = _get_feat(models)

            st.info(f"**{t('external.formula')}**: `combined_risk = 0.70 × ML_avg + 0.30 × context_score`")

            tab_m, tab_c, tab_a, tab_h = st.tabs([
                t("external.tab.manual"),
                t("external.tab.csv"),
                t("external.tab.api"),
                t("external.tab.history"),
            ])

            with tab_m:
                json_str = st.text_area("JSON:", value=json.dumps(_DEMO, indent=2), height=300, key=f"json_{ds_key}")
                if st.button(t("external.score_btn"), type="primary", key=f"sc_m_{ds_key}"):
                    try:
                        rec = json.loads(json_str)
                        res = _score(rec, models, feat)
                        _save([res])
                        _show_single(res)
                    except json.JSONDecodeError as e:
                        st.error(f"JSON Error: {e}")

            with tab_c:
                up = st.file_uploader("CSV", type="csv", key=f"ext_csv_{ds_key}")
                if up:
                    df_up = pd.read_csv(up)
                    st.dataframe(df_up.head(3), width='stretch')
                    if st.button(t("external.score_all"), type="primary", key=f"sc_c_{ds_key}"):
                        with st.spinner("Processing..."):
                            results = [_score(row.to_dict(), models, feat)
                                       for _, row in df_up.iterrows()]
                        _save(results)
                        st.success(f"Processed {len(results)} transactions.")
                        _show_batch(results)

            with tab_a:
                st.markdown("### REST API")
                st.markdown("""
                Send transactions via HTTP POST:
                ```
                POST http://<server>:8000/external/transactions
                Content-Type: application/json
                ```
                **Request:**
                ```json
                [{
                  "transaction_id": "TXN-001",
                  "amount": 250.00,
                  "ip_address": "185.220.101.5",
                  "country_code": "RU",
                  "device_type": "mobile",
                  "session_risk": 0.72,
                  "velocity_1h": 5,
                  "account_age_days": 8,
                  "previous_frauds": 1,
                  "V1": -1.35, "...": "..."
                }]
                ```
                **Response:**
                ```json
                {
                  "scored": 1,
                  "results": [{
                    "transaction_id": "TXN-001",
                    "combined_risk": 0.78,
                    "verdict": "Fraud",
                    "ml_avg": 0.82,
                    "context_score": 0.60,
                    "risk_reasons": "Risk Country (RU); Session Risk 0.72"
                  }]
                }
                ```
                """)

            with tab_h:
                st.markdown(f"### {t('external.tab.history')}")
                hist = _load_history()
                if hist.empty:
                    st.info(t("external.no_history"), icon=None)
                else:
                    _show_batch(hist.to_dict("records"))

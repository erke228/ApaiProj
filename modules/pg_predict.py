"""modules/pg_predict.py – Predict page (dark)."""
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.utils import load_metrics, load_models, plot_risk_gauge, _pretty
from modules.i18n import t

ROOT = Path(__file__).resolve().parent.parent


def _get_features(model):
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)
    if hasattr(model, "steps"):
        last = model.steps[-1][1]
        if hasattr(last, "feature_names_in_"):
            return list(last.feature_names_in_)
    return None


def render():
    st.markdown(f"## {t('predict.title')}")
    st.caption(t("predict.caption"))

    metrics = load_metrics()
    if not metrics:
        st.warning(t("predict.no_models"), icon=None)
        return

    ds_keys = list(metrics.keys())
    ds_tabs = st.tabs([k.replace("_"," ").title() for k in ds_keys])

    for i, ds_key in enumerate(ds_keys):
        with ds_tabs[i]:
            models  = load_models(ds_key)
            if not models:
                st.warning(f"Нет моделей для `{ds_key}`.", icon=None); continue

            sample_m = next(iter(models.values()))
            feat     = _get_features(sample_m)

            tab_m, tab_c = st.tabs([t("predict.method.manual"), t("predict.method.csv")])

            X_input = None

            # ── Manual ────────────────────────────────────────────────────────
            with tab_m:
                if feat is None:
                    st.info("Признаки модели недоступны. Используйте загрузку CSV.")
                else:
                    st.caption(f"{t('predict.features')}: **{len(feat)}**")
                    _DEF = {"Amount": 50.0, "amount": 50.0, "Time": 3600.0}

                    with st.form(f"pred_form_{ds_key}"):
                        inputs = {}
                        vis    = feat[:30]
                        cols3  = st.columns(3)
                        for idx_f, f_name in enumerate(vis):
                            with cols3[idx_f % 3]:
                                inputs[f_name] = st.number_input(
                                    f_name, value=float(_DEF.get(f_name, 0.0)),
                                    format="%.4f", key=f"fi_{ds_key}_{f_name}")
                        for f_name in feat[30:]:
                            inputs[f_name] = 0.0
                        if len(feat) > 30:
                            st.caption(f"{t('predict.showing')} {len(feat)} {t('predict.rest_zero')}")
                        submitted = st.form_submit_button(t("predict.btn"), type="primary",
                                                          use_container_width=False)
                        if submitted:
                            X_input = pd.DataFrame([inputs])

            # ── CSV ───────────────────────────────────────────────────────────
            with tab_c:
                uploaded = st.file_uploader("CSV", type="csv", key=f"up_{ds_key}")
                if uploaded:
                    X_input = pd.read_csv(uploaded)
                    for drop_col in ("fraud", "Class", "isFraud", "isFlaggedFraud"):
                        if drop_col in X_input.columns:
                            X_input = X_input.drop(columns=[drop_col])
                    st.dataframe(X_input.head(5), width='stretch')
                    if not st.button(t("predict.btn.all"), type="primary", key=f"btn_{ds_key}"):
                        X_input = None

            # ── Predictions ───────────────────────────────────────────────────
            if X_input is not None:
                if feat:
                    X_al = X_input.reindex(columns=feat, fill_value=0).fillna(0)
                else:
                    X_al = X_input.fillna(0)

                results: dict[str, list[float]] = {}
                for mn, mdl in models.items():
                    try:
                        results[mn] = mdl.predict_proba(X_al)[:, 1].tolist()
                    except Exception as e:
                        st.error(f"{mn}: {e}")

                if not results: continue

                st.markdown("---")
                n_rows = len(X_al)

                # ── Single transaction ────────────────────────────────────────
                if n_rows == 1:
                    st.markdown(f"### {t('predict.results')}")

                    cols = st.columns(len(results))
                    avg_p = sum(v[0] for v in results.values()) / len(results)

                    for idx_res, (col, (mn, proba_list)) in enumerate(zip(cols, results.items())):
                        p = proba_list[0]
                        color = "#EF4444" if p >= 0.5 else "#00D4B4"
                        verdict = t("predict.fraud") if p >= 0.5 else t("predict.legit")
                        delay = idx_res * 0.08
                        col.markdown(f"""
                        <div class="glass-metric" style="animation-delay:{delay}s;padding:1rem;">
                            <div style="font-size:0.62rem;font-weight:700;letter-spacing:1.2px;
                                        color:#4d6690;text-transform:uppercase;margin-bottom:8px;">
                                {_pretty(mn)}
                            </div>
                            <div style="font-size:2rem;font-weight:900;color:{color};line-height:1;">
                                {p:.1%}
                            </div>
                            <div style="font-size:0.75rem;font-weight:700;color:{color};margin-top:4px;">
                                {verdict}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    _, gc, _ = st.columns([1, 2, 1])
                    with gc:
                        st.plotly_chart(plot_risk_gauge(avg_p), width='stretch',
                                        config={"displayModeBar": False})

                    if avg_p >= 0.7:
                        st.error(t("predict.high_risk"), icon=None)
                    elif avg_p >= 0.5:
                        st.warning(t("predict.mid_risk"), icon=None)
                    else:
                        st.success(t("predict.low_risk"), icon=None)

                # ── Batch ──────────────────────────────────────────────────────
                else:
                    st.markdown(f"### {t('predict.results')} · {n_rows}")
                    out = X_al.copy()
                    for mn, pl in results.items():
                        out[f"{mn}_prob"] = pl
                    p_cols = [f"{mn}_prob" for mn in results]
                    out["avg_risk"] = out[p_cols].mean(axis=1).round(4)
                    out["verdict"]  = out["avg_risk"].apply(
                        lambda p: t("predict.fraud") if p >= 0.5 else t("predict.legit")
                    )
                    fraud_n = (out["avg_risk"] >= 0.5).sum()
                    c1, c2, c3 = st.columns(3)
                    c1.metric(t("predict.total"),   n_rows)
                    c2.metric(t("predict.flagged"), fraud_n)
                    c3.metric(t("predict.fraud_rate"), f"{fraud_n/n_rows:.1%}")
                    st.dataframe(out[["avg_risk","verdict"]+p_cols].round(4),
                                 width='stretch', hide_index=True)


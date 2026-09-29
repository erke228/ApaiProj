"""modules/pg_models.py – Model Comparison page (dark)."""
import pandas as pd
import streamlit as st

from modules.utils import (
    load_metrics, plot_confusion, plot_grouped_bars,
    plot_fraud_bars, plot_metric_bars, plot_scatter_pr, _pretty,
)
from modules.i18n import t


def render():
    st.markdown(f"## {t('comparison.title')}")
    st.caption(t("comparison.caption"))

    metrics = load_metrics()
    if not metrics:
        st.warning(t("common.no_metrics"), icon=None)
        return

    ds_keys = list(metrics.keys())
    ds_tabs = st.tabs([k.replace("_"," ").title() for k in ds_keys])

    for i, ds_key in enumerate(ds_keys):
        with ds_tabs[i]:
            ds_m = metrics[ds_key]

            tab1, tab2, tab3, tab4 = st.tabs([
                t("comparison.tab.all"),
                t("comparison.tab.fraud"),
                t("comparison.tab.cm"),
                t("comparison.tab.report"),
            ])

            # ── All metrics ───────────────────────────────────────────────────
            with tab1:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(plot_grouped_bars(ds_m), width='stretch',
                                    config={"displayModeBar": False})
                with c2:
                    st.plotly_chart(plot_metric_bars(ds_m, "roc_auc", "ROC-AUC"),
                                    width='stretch', config={"displayModeBar": False})

                rows = []
                for mn, m in ds_m.items():
                    rows.append({
                        t("common.model"): _pretty(mn),
                        "Precision":       round(m.get("precision",0), 4),
                        "Recall":          round(m.get("recall",0), 4),
                        "F1":              round(m.get("f1",0), 4),
                        "ROC-AUC":         round(m.get("roc_auc",0), 4),
                        "Avg Precision":   round(m.get("avg_precision",0), 4),
                    })
                st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)

            # ── Fraud focus ───────────────────────────────────────────────────
            with tab2:
                st.markdown(f"""
                <div class="glass-card" style="border-left:3px solid #F59E0B;padding:0.8rem 1rem;background:rgba(245,158,11,0.05);">
                    <div style="font-size:0.78rem;color:#fbbf24;line-height:1.6;">
                        💡 <b>Бизнес-правило:</b> Пропущенный фрод (False Negative) обходится значительно дороже ложной тревоги.<br>
                        Целевой показатель системы — <b>Fraud Recall &gt; 0.85</b>.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(plot_fraud_bars(ds_m), width='stretch',
                                    config={"displayModeBar": False})
                with c2:
                    st.plotly_chart(plot_scatter_pr(ds_m), width='stretch',
                                    config={"displayModeBar": False})

            # ── Confusion matrices ────────────────────────────────────────────
            with tab3:
                cols = st.columns(len(ds_m))
                for col, (mn, m) in zip(cols, ds_m.items()):
                    cm = m.get("confusion_matrix", [[0,0],[0,0]])
                    col.plotly_chart(plot_confusion(cm, mn), width='stretch',
                                     config={"displayModeBar": False})
                    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
                    col.markdown(f"""
                    <div class="glass-card" style="padding:0.6rem 0.9rem;text-align:center;
                                 font-size:0.78rem;color:#6b85b8;">
                        <span style="color:#00D4B4;">TN {tn:,}</span> &nbsp;|&nbsp;
                        <span style="color:#EF4444;">FP {fp:,}</span><br/>
                        <span style="color:#F59E0B;">FN {fn:,}</span> &nbsp;|&nbsp;
                        <span style="color:#4C8BF5;">TP {tp:,}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Full report ───────────────────────────────────────────────────
            with tab4:
                sel = st.radio(t("comparison.model"), list(ds_m.keys()),
                               format_func=_pretty, key=f"rep_sel_{ds_key}", horizontal=True)
                m   = ds_m[sel]

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Precision",  f"{m.get('precision',0):.4f}")
                c2.metric("Recall",     f"{m.get('recall',0):.4f}")
                c3.metric("F1",         f"{m.get('f1',0):.4f}")
                c4.metric("ROC-AUC",    f"{m.get('roc_auc',0):.4f}")

                st.markdown("#### Метрики класса Fraud")
                d1, d2, d3 = st.columns(3)
                d1.metric("Fraud Precision", f"{m.get('fraud_precision',0):.4f}")
                d2.metric("Fraud Recall",    f"{m.get('fraud_recall',0):.4f}")
                d3.metric("Fraud F1",        f"{m.get('fraud_f1',0):.4f}")

                st.markdown("#### Классификационный отчёт")
                report = m.get("classification_report", {})
                label_map = {"0": t("common.legit"), "1": t("common.fraud"),
                             "accuracy": "Accuracy", "macro avg": "Macro Avg",
                             "weighted avg": "Weighted Avg"}
                rows = []
                for cls, vals in report.items():
                    if isinstance(vals, dict):
                        rows.append({
                            "Класс":     label_map.get(str(cls), str(cls)),
                            "Precision": f"{vals.get('precision',0):.4f}",
                            "Recall":    f"{vals.get('recall',0):.4f}",
                            "F1":        f"{vals.get('f1-score',0):.4f}",
                            "Support":   int(vals.get("support",0)),
                        })
                if rows:
                    st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)

                t_sec = m.get("training_time_sec")
                if t_sec is not None:
                    st.caption(f"{t('comparison.train_time')}: {t_sec:.1f} {t('common.seconds')}")

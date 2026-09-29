"""modules/pg_training.py – Model Training page with detailed model descriptions."""
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.utils import load_metrics, _pretty
from modules.i18n import t

ROOT = Path(__file__).resolve().parent.parent

# ── SVG icons for models ──────────────────────────────────────────────────────
SVG_LR  = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#4C8BF5" stroke-width="1.6" stroke-linecap="round"><line x1="3" y1="20" x2="21" y2="4"/><circle cx="7" cy="16" r="2" fill="rgba(76,139,245,0.2)"/><circle cx="14" cy="9" r="2" fill="rgba(76,139,245,0.2)"/><circle cx="20" cy="5" r="2" fill="rgba(76,139,245,0.2)"/></svg>'
SVG_RF  = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#00D4B4" stroke-width="1.6" stroke-linecap="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>'
SVG_XGB = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="1.6" stroke-linecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'

MODEL_INFO = [
    {
        "key":    "lr",
        "svg":    SVG_LR,
        "color":  "#4C8BF5",
        "params": "max_iter=1000, solver=saga, class_weight=balanced",
    },
    {
        "key":    "rf",
        "svg":    SVG_RF,
        "color":  "#00D4B4",
        "params": "n_estimators=200, max_depth=15, class_weight=balanced_subsample, n_jobs=-1",
    },
    {
        "key":    "xgb",
        "svg":    SVG_XGB,
        "color":  "#F59E0B",
        "params": "n_estimators=300, max_depth=6, learning_rate=0.05, scale_pos_weight=auto",
    },
]


def render():
    st.markdown(f"## {t('training.title')}")
    st.caption(t("training.caption"))

    # ── Dataset cards ─────────────────────────────────────────────────
    st.markdown(f"### {t('training.datasets')}")
    ds_dir = ROOT / "DataSets"
    csvs   = sorted(ds_dir.glob("*.csv")) if ds_dir.exists() else []
    icons  = [
        '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4C8BF5" stroke-width="1.6"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
        '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4B4" stroke-width="1.6"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
        '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="1.6"><path d="M3 3h18v18H3z"/><path d="M3 9h18M3 15h18M9 3v18"/></svg>',
    ]
    if csvs:
        cols = st.columns(len(csvs))
        for col, csv_file, icon in zip(cols, csvs, icons):
            size_mb   = csv_file.stat().st_size / 1_048_576
            row_est   = int(size_mb * 6000)  # rough estimate
            with col:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center; padding:1.2rem 1rem;">
                    <div style="margin-bottom:10px;">{icon}</div>
                    <div style="font-weight:700;color:#c8d6f0;font-size:0.82rem;
                                word-break:break-all;margin-bottom:4px;">
                        {csv_file.name}
                    </div>
                    <div style="color:#4d6690;font-size:0.72rem;">{size_mb:.0f} MB</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("CSV файлы не найдены в папке DataSets/")

    st.markdown("---")

    # ── Detailed model descriptions ───────────────────────────────────
    st.markdown(f"### {t('training.models_section')}")
    cols3 = st.columns(3)
    for col, info in zip(cols3, MODEL_INFO):
        k = info["key"]
        with col:
            st.markdown(f"""
            <div class="glass-card" style="border-top:2px solid {info['color']}; padding:1.2rem;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                    {info['svg']}
                    <div style="font-weight:700;color:#dde6f8;font-size:0.9rem;">
                        {t(f'model.{k}.name')}
                    </div>
                </div>
                <div style="font-size:0.8rem;color:#7a95c0;line-height:1.6;margin-bottom:12px;">
                    {t(f'model.{k}.desc')}
                </div>
                <div style="margin-bottom:8px;">
                    <div style="font-size:0.65rem;font-weight:700;color:{info['color']};
                                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">
                        {t('model.hyperparams')}
                    </div>
                    <div style="font-size:0.72rem;color:#4d6690;
                                background:rgba(0,0,0,0.3);border-radius:8px;padding:6px 8px;
                                font-family:monospace;">
                        {info['params']}
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:6px;margin-top:10px;">
                    <div style="font-size:0.72rem;">
                        <span style="color:#00D4B4;font-weight:600;">+ {t('model.pros')}: </span>
                        <span style="color:#6b85b8;">{t(f'model.{k}.pros')}</span>
                    </div>
                    <div style="font-size:0.72rem;">
                        <span style="color:#EF4444;font-weight:600;">- {t('model.cons')}: </span>
                        <span style="color:#6b85b8;">{t(f'model.{k}.cons')}</span>
                    </div>
                    <div style="font-size:0.72rem;">
                        <span style="color:#F59E0B;font-weight:600;">✦ {t('model.usecase')}: </span>
                        <span style="color:#6b85b8;">{t(f'model.{k}.use')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Training controls ─────────────────────────────────────────────
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(f"""
        <div class="glass-card" style="padding:1rem 1.2rem;">
            <div style="font-size:0.72rem;font-weight:700;color:#4C8BF5;
                        text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">
                Pipeline обучения
            </div>
            <div style="font-size:0.82rem;color:#7a95c0;line-height:1.8;">
                <div>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                         stroke="#4C8BF5" stroke-width="2" style="vertical-align:middle;margin-right:6px;">
                        <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Стратифицированное разделение: 75% обучение / 10% валидация / 15% тест
                </div>
                <div>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                         stroke="#4C8BF5" stroke-width="2" style="vertical-align:middle;margin-right:6px;">
                        <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Балансировка классов (fraud крайне редок: 0.2–1%)
                </div>
                <div>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                         stroke="#4C8BF5" stroke-width="2" style="vertical-align:middle;margin-right:6px;">
                        <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Метрики: Precision, Recall, F1, ROC-AUC, Confusion Matrix
                </div>
                <div>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                         stroke="#4C8BF5" stroke-width="2" style="vertical-align:middle;margin-right:6px;">
                        <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Модели сохраняются в <code style="color:#8ab4f8;background:rgba(76,139,245,0.1);
                    padding:1px 5px;border-radius:4px;">models/&lt;датасет&gt;/*.pkl</code>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        train_btn = st.button(t("training.start_btn"), type="primary",
                              use_container_width=False, key="train_main_btn")

    # ── Run training ──────────────────────────────────────────────────
    if train_btn:
        st.markdown("---")
        st.markdown(f"### {t('training.log_title')}")
        log_box = st.empty()
        status  = st.empty()
        status.info(t("training.running"), icon=None)
        log_lines: list[str] = []
        try:
            proc = subprocess.Popen(
                [sys.executable, str(ROOT / "backend" / "models" / "train.py")],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, cwd=str(ROOT), bufsize=1,
                encoding="utf-8", errors="replace",
            )
            for line in proc.stdout:
                log_lines.append(line.rstrip())
                log_box.code("\n".join(log_lines[-60:]), language="bash")
            proc.wait()
            if proc.returncode == 0:
                status.success(t("training.done"), icon=None)
            else:
                status.warning(t("training.warning"), icon=None)
            st.cache_resource.clear()
            st.cache_data.clear()
        except Exception as e:
            status.error(str(e), icon=None)

    # ── Latest results ────────────────────────────────────────────────
    metrics = load_metrics()
    if metrics:
        st.markdown("---")
        st.markdown(f"### {t('training.results')}")
        for ds_key, ds_metrics in metrics.items():
            with st.expander(f"  {ds_key}", expanded=True):
                rows = []
                for mn, m in ds_metrics.items():
                    rows.append({
                        t("training.col.model"): _pretty(mn),
                        t("training.col.prec"):  f"{m.get('precision',0):.4f}",
                        t("training.col.rec"):   f"{m.get('recall',0):.4f}",
                        t("training.col.f1"):    f"{m.get('f1',0):.4f}",
                        t("training.col.auc"):   f"{m.get('roc_auc',0):.4f}",
                        t("training.col.fraud_rec"):  f"{m.get('fraud_recall',0):.4f}",
                        t("training.col.fraud_prec"): f"{m.get('fraud_precision',0):.4f}",
                        t("training.col.time"):  f"{m.get('training_time_sec',0):.1f}",
                    })
                st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)
    else:
        st.caption(t("training.no_metrics"))

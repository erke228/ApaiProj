"""modules/utils.py – Shared utilities with dark Plotly theme."""
import json
from pathlib import Path

import joblib
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

ROOT         = Path(__file__).resolve().parent.parent
MODEL_DIR    = ROOT / "models"
METRICS_PATH = ROOT / "metrics.json"

_PALETTE = ["#4C8BF5", "#00D4B4", "#F59E0B", "#EF4444", "#A78BFA", "#34D399"]

_DARK_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="#a8bcd8"),
    margin=dict(l=10, r=30, t=48, b=20),
    hoverlabel=dict(
        bgcolor="#0a1228",
        bordercolor="rgba(76,139,245,0.3)",
        font=dict(size=13, color="#c8d6f0", family="Inter, sans-serif")
    ),
    legend=dict(
        bgcolor="rgba(10,18,40,0.6)",
        bordercolor="rgba(76,139,245,0.2)",
        borderwidth=1,
        font=dict(color="#8ab4f8"),
        orientation="h",
        y=-0.22, x=0.5, xanchor="center",
    ),
)


def _ax(**kwargs):
    """Return a dark-styled axis dict merged with kwargs."""
    base = dict(
        gridcolor="rgba(76,139,245,0.08)",
        zerolinecolor="rgba(76,139,245,0.12)",
        tickfont=dict(color="#6b85b8"),
        linecolor="rgba(76,139,245,0.1)",
        zeroline=False,
    )
    base.update(kwargs)
    return base


def _pretty(name: str) -> str:
    return name.replace("_", " ").title()


# ── Cached loaders ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_models(dataset_key: str) -> dict:
    ds_dir = MODEL_DIR / dataset_key
    if not ds_dir.exists():
        return {}
    return {pkl.stem: joblib.load(pkl) for pkl in sorted(ds_dir.glob("*.pkl"))}


@st.cache_data(show_spinner=False, ttl=30)
def load_metrics() -> dict:
    if not METRICS_PATH.is_file():
        return {}
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Charts ────────────────────────────────────────────────────────────────────

def plot_confusion(cm: list, model_name: str, labels=None) -> go.Figure:
    if labels is None:
        labels = ["Легит.", "Фрод"]
    z    = np.array(cm)
    text = [[f"{v:,}" for v in row] for row in cm]
    fig  = go.Figure(go.Heatmap(
        z=z, x=labels, y=labels,
        text=text, texttemplate="<b>%{text}</b>",
        textfont=dict(size=18, color="white"),
        colorscale=[[0,"rgba(5,12,26,0.8)"],[0.4,"rgba(76,139,245,0.4)"],[1,"rgba(76,139,245,0.95)"]],
        showscale=False, hoverongaps=False,
        hovertemplate="Факт: %{y}<br>Предсказано: %{x}<br>Кол-во: %{text}<extra></extra>",
    ))
    fig.update_layout(**_DARK_BASE)
    fig.update_layout(
        title=dict(text=f"<b>{_pretty(model_name)}</b>",
                   font=dict(size=13, color="#8ab4f8")),
        xaxis=_ax(title=dict(text="Предсказано", font=dict(color="#6b85b8")),
                  side="bottom", tickfont=dict(color="#8ab4f8", size=11)),
        yaxis=_ax(title=dict(text="Фактически", font=dict(color="#6b85b8")),
                  autorange="reversed", tickfont=dict(color="#8ab4f8", size=11)),
        height=280,
    )
    return fig


def plot_grouped_bars(ds_metrics: dict, title: str = "Сравнение моделей – все метрики") -> go.Figure:
    names  = [_pretty(m) for m in ds_metrics]
    keys   = ["precision", "recall", "f1", "roc_auc"]
    labels = ["Precision", "Recall", "F1", "ROC-AUC"]
    fig    = go.Figure()
    for i, (k, lab) in enumerate(zip(keys, labels)):
        vals = [ds_metrics[m].get(k, 0) for m in ds_metrics]
        fig.add_trace(go.Bar(
            name=lab, x=names, y=vals,
            marker=dict(color=_PALETTE[i], opacity=0.85, line=dict(width=0)),
            text=[f"{v:.3f}" for v in vals],
            textposition="outside",
            textfont=dict(size=11, color="#c8d6f0"),
            hovertemplate=f"<b>%{{x}}</b><br>{lab}: %{{y:.4f}}<extra></extra>",
        ))
    fig.update_layout(**_DARK_BASE)
    fig.update_layout(
        barmode="group", bargap=0.18, bargroupgap=0.06,
        title=dict(text=f"<b>{title}</b>", font=dict(size=14, color="#dde6f8")),
        xaxis=_ax(),
        yaxis=_ax(range=[0, 1.2]),
    )
    return fig


def plot_fraud_bars(ds_metrics: dict) -> go.Figure:
    names  = [_pretty(m) for m in ds_metrics]
    keys   = ["fraud_precision", "fraud_recall", "fraud_f1"]
    labels = ["Fraud Precision", "Fraud Recall", "Fraud F1"]
    fig    = go.Figure()
    for i, (k, lab) in enumerate(zip(keys, labels)):
        vals = [ds_metrics[m].get(k, 0) for m in ds_metrics]
        fig.add_trace(go.Bar(
            name=lab, x=names, y=vals,
            marker=dict(color=_PALETTE[i], opacity=0.85, line=dict(width=0)),
            text=[f"{v:.3f}" for v in vals],
            textposition="outside",
            textfont=dict(size=11, color="#c8d6f0"),
            hovertemplate=f"<b>%{{x}}</b><br>{lab}: %{{y:.4f}}<extra></extra>",
        ))
    fig.update_layout(**_DARK_BASE)
    fig.update_layout(
        barmode="group", bargap=0.18, bargroupgap=0.06,
        title=dict(text="<b>Fraud-класс: Precision / Recall / F1</b>",
                   font=dict(size=14, color="#dde6f8")),
        xaxis=_ax(),
        yaxis=_ax(range=[0, 1.2]),
    )
    return fig


def plot_metric_bars(ds_metrics: dict, metric_key: str, title: str) -> go.Figure:
    names  = [_pretty(m) for m in ds_metrics]
    values = [ds_metrics[m].get(metric_key, 0) for m in ds_metrics]
    colors = [_PALETTE[i % len(_PALETTE)] for i in range(len(names))]
    fig    = go.Figure(go.Bar(
        x=values, y=names, orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{v:.4f}" for v in values],
        textposition="outside",
        textfont=dict(size=12, color="#c8d6f0"),
        hovertemplate=f"<b>%{{y}}</b><br>{title}: %{{x:.4f}}<extra></extra>",
    ))
    fig.update_layout(**_DARK_BASE)
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=14, color="#dde6f8")),
        xaxis=_ax(range=[0, 1.12]),
        yaxis=_ax(autorange="reversed", tickfont=dict(color="#8ab4f8")),
        height=max(180, 75 * len(names)),
        legend=dict(visible=False),
    )
    return fig


def plot_risk_gauge(avg_p: float) -> go.Figure:
    color = "#EF4444" if avg_p >= 0.7 else ("#F59E0B" if avg_p >= 0.5 else "#00D4B4")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_p * 100,
        title={"text": "<b>Средний риск</b>", "font": {"size": 14, "color": "#8ab4f8"}},
        number={"suffix": "%", "font": {"size": 30, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1,
                     "tickcolor": "rgba(76,139,245,0.3)",
                     "tickfont": {"color": "#6b85b8"}},
            "bar":  {"color": color, "thickness": 0.24},
            "bgcolor": "rgba(10,18,40,0.5)",
            "borderwidth": 1, "bordercolor": "rgba(76,139,245,0.2)",
            "steps": [
                {"range": [0, 30],  "color": "rgba(0,212,180,0.08)"},
                {"range": [30, 60], "color": "rgba(245,158,11,0.08)"},
                {"range": [60,100], "color": "rgba(239,68,68,0.08)"},
            ],
            "threshold": {
                "line": {"color": "#EF4444", "width": 2.5},
                "thickness": 0.75, "value": 50,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#a8bcd8"),
        height=240, margin=dict(l=30, r=30, t=40, b=10),
    )
    return fig


def plot_scatter_pr(ds_metrics: dict) -> go.Figure:
    names = [_pretty(m) for m in ds_metrics]
    prec  = [ds_metrics[m].get("fraud_precision", 0) for m in ds_metrics]
    rec   = [ds_metrics[m].get("fraud_recall", 0)    for m in ds_metrics]
    f1v   = [ds_metrics[m].get("fraud_f1", 0)        for m in ds_metrics]
    colors= _PALETTE[:len(names)]

    fig = go.Figure(go.Scatter(
        x=prec, y=rec, mode="markers+text",
        text=names, textposition="top center",
        textfont=dict(size=11, color="#8ab4f8"),
        marker=dict(
            size=[v * 50 + 20 for v in f1v],
            color=colors, opacity=0.85,
            line=dict(width=1.5, color="rgba(255,255,255,0.15)"),
        ),
        hovertemplate="<b>%{text}</b><br>Precision: %{x:.3f}<br>Recall: %{y:.3f}<extra></extra>",
    ))
    fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                  line=dict(dash="dot", color="rgba(76,139,245,0.2)", width=1))
    fig.update_layout(**_DARK_BASE)
    fig.update_layout(
        title=dict(text="<b>Fraud: Precision vs Recall</b><br>"
                        "<sup>Размер точки = F1-Score</sup>",
                   font=dict(size=13, color="#dde6f8")),
        xaxis=_ax(title="Precision", range=[0, 1.1]),
        yaxis=_ax(title="Recall",    range=[0, 1.1]),
        legend=dict(visible=False),
    )
    return fig


def plot_risk_histogram(df) -> go.Figure:
    fig = px.histogram(df, x="combined_risk", nbins=30,
                       color_discrete_sequence=["#4C8BF5"])
    fig.add_vline(x=0.5, line_dash="dash", line_color="#EF4444",
                  annotation_text="Порог (0.5)",
                  annotation_font_color="#EF4444",
                  annotation_position="top right")
    fig.update_layout(**_DARK_BASE)
    fig.update_layout(
        title=dict(text="<b>Распределение рисков</b>", font=dict(size=14, color="#dde6f8")),
        xaxis=_ax(title="Итоговый риск"),
        yaxis=_ax(title="Количество"),
        bargap=0.05,
    )
    return fig

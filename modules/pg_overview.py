"""modules/pg_overview.py"""
import streamlit as st
from modules.utils import load_metrics, plot_grouped_bars, plot_fraud_bars, _pretty
from modules.i18n import t


def render():
    st.markdown(f"## {t('overview.title')}")
    st.caption(t("overview.caption"))

    metrics = load_metrics()
    if not metrics:
        st.warning(t("overview.no_metrics"), icon=None)
        return

    for ds_key, ds_metrics in metrics.items():
        st.markdown(f"### {t('overview.dataset')} · `{ds_key}`")

        cols = st.columns(len(ds_metrics))
        for idx, (col, (mn, m)) in enumerate(zip(cols, ds_metrics.items())):
            roc  = m.get("roc_auc", 0)
            rec  = m.get("fraud_recall", 0)
            prec = m.get("fraud_precision", 0)
            f1   = m.get("fraud_f1", 0)
            status_color = "#00D4B4" if roc >= 0.95 else ("#F59E0B" if roc >= 0.85 else "#EF4444")
            delay = idx * 0.1
            with col:
                st.markdown(f"""
                <div class="glass-metric" style="animation-delay:{delay}s;">
                    <div style="font-size:0.65rem;font-weight:700;letter-spacing:1.2px;
                                color:#4d6690;text-transform:uppercase;margin-bottom:10px;">
                        {_pretty(mn)}
                    </div>
                    <div style="font-size:2.1rem;font-weight:900;color:{status_color};
                                line-height:1;margin-bottom:2px;">
                        {roc:.3f}
                    </div>
                    <div style="font-size:0.68rem;color:#3d5278;margin-bottom:12px;">
                        {t('overview.roc_auc')}
                    </div>
                    <div style="border-top:1px solid rgba(76,139,245,0.1);
                                padding-top:10px;display:flex;justify-content:space-around;">
                        <div>
                            <div style="font-weight:700;color:#4C8BF5;font-size:0.9rem;">{rec:.3f}</div>
                            <div style="font-size:0.62rem;color:#3d5278;">{t('overview.recall')}</div>
                        </div>
                        <div>
                            <div style="font-weight:700;color:#00D4B4;font-size:0.9rem;">{prec:.3f}</div>
                            <div style="font-size:0.62rem;color:#3d5278;">{t('overview.precision')}</div>
                        </div>
                        <div>
                            <div style="font-weight:700;color:#F59E0B;font-size:0.9rem;">{f1:.3f}</div>
                            <div style="font-size:0.62rem;color:#3d5278;">{t('overview.f1')}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_grouped_bars(ds_metrics), width='stretch',
                            config={"displayModeBar": False})
        with c2:
            st.plotly_chart(plot_fraud_bars(ds_metrics), width='stretch',
                            config={"displayModeBar": False})
        st.markdown("---")

    st.markdown(f"""
    <div class="glass-card" style="border-left:3px solid #4C8BF5;">
        <div style="font-size:0.7rem;font-weight:700;color:#4C8BF5;
                    text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">
            Аналитика
        </div>
        <div style="font-size:0.88rem;color:#8ab4f8;line-height:1.6;">
            {t('overview.tip')}
        </div>
    </div>
    """, unsafe_allow_html=True)

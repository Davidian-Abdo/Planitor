"""
Performance table components for French construction
"""
import streamlit as st
import pandas as pd
from typing import Dict, List

def render_kpi_table(performance_metrics: Dict) -> None:
    """
    Render KPI performance table for French construction
    """
    if not performance_metrics:
        st.info("📈 Aucune métrique de performance disponible")
        return
    
    st.subheader("📈 Indicateurs de Performance Clés")
    
    kpi_data = [
        {'KPI': 'Indice Performance Planning (SPI)', 'Valeur': performance_metrics.get('spi', 0), 'Cible': '≥ 0.9'},
        {'KPI': 'Indice Performance Coût (CPI)', 'Valeur': performance_metrics.get('cpi', 0), 'Cible': '≥ 0.9'},
        {'KPI': 'Valeur Planifiée (PV)', 'Valeur': f"€{performance_metrics.get('pv', 0):,.0f}", 'Cible': '-'},
        {'KPI': 'Valeur Acquise (EV)', 'Valeur': f"€{performance_metrics.get('ev', 0):,.0f}", 'Cible': '-'},
        {'KPI': 'Coût Réel (AC)', 'Valeur': f"€{performance_metrics.get('ac', 0):,.0f}", 'Cible': '-'},
        {'KPI': 'Budget à l\'Achèvement (BAC)', 'Valeur': f"€{performance_metrics.get('bac', 0):,.0f}", 'Cible': '-'},
        {'KPI': 'Estimation à l\'Achèvement (EAC)', 'Valeur': f"€{performance_metrics.get('eac', 0):,.0f}", 'Cible': '≤ BAC'}
    ]
    
    df = pd.DataFrame(kpi_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

def render_evm_table(earned_value_data: Dict) -> None:
    """
    Render Earned Value Management table
    """
    if not earned_value_data:
        st.info("💰 Aucune donnée de valeur acquise disponible")
        return
    
    st.subheader("💰 Analyse de la Valeur Acquise")
    
    evm_data = [
        {'Paramètre': 'Variance des Coûts (CV)', 'Valeur': f"€{earned_value_data.get('cv', 0):,.0f}", 'Interprétation': 'Favorable' if earned_value_data.get('cv', 0) >= 0 else 'Défavorable'},
        {'Paramètre': 'Variance du Planning (SV)', 'Valeur': f"€{earned_value_data.get('sv', 0):,.0f}", 'Interprétation': 'Favorable' if earned_value_data.get('sv', 0) >= 0 else 'Défavorable'},
        {'Paramètre': 'Variance à l\'Achèvement (VAC)', 'Valeur': f"€{earned_value_data.get('vac', 0):,.0f}", 'Interprétation': 'Favorable' if earned_value_data.get('vac', 0) >= 0 else 'Défavorable'},
        {'Paramètre': 'Indice Performance Planning (SPI)', 'Valeur': earned_value_data.get('spi', 0), 'Interprétation': 'Dans les temps' if earned_value_data.get('spi', 0) >= 1 else 'En retard'},
        {'Paramètre': 'Indice Performance Coût (CPI)', 'Valeur': earned_value_data.get('cpi', 0), 'Interprétation': 'Dans le budget' if earned_value_data.get('cpi', 0) >= 1 else 'Dépassement'}
    ]
    
    df = pd.DataFrame(evm_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

def render_risk_register(risk_data: Dict) -> None:
    """
    Render risk register table for French construction
    """
    if not risk_data:
        st.info("⚠️ Aucun registre de risques disponible")
        return
    
    st.subheader("⚠️ Registre des Risques")
    
    risk_matrix = risk_data.get('risk_matrix', pd.DataFrame())
    
    if not risk_matrix.empty:
        st.dataframe(
            risk_matrix,
            use_container_width=True,
            hide_index=True,
            column_config={
                "probability": st.column_config.NumberColumn("Probabilité", format="%.2f"),
                "impact": st.column_config.NumberColumn("Impact", format="%.2f"),
                "severity": st.column_config.NumberColumn("Sévérité", format="%.1f")
            }
        )
    
    # Risk statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Risques Élevés", risk_data.get('high_risks', 0))
    with col2:
        st.metric("Risques Moyens", risk_data.get('medium_risks', 0))
    with col3:
        st.metric("Risques Faibles", risk_data.get('low_risks', 0))
    with col4:
        st.metric("Exposition aux Risques", f"€{risk_data.get('risk_exposure', 0):,.0f}")
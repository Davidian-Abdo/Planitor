"""
Progress table components for French construction
"""
import streamlit as st
import pandas as pd
from typing import Dict, List

def render_progress_table(progress_data: pd.DataFrame) -> None:
    """
    Render progress tracking table for French construction
    """
    if progress_data.empty:
        st.info("📊 Aucune donnée de progression disponible")
        return
    
    st.subheader("📊 Suivi de la Progression")
    
    st.dataframe(
        progress_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date"),
            "Progress": st.column_config.ProgressColumn(
                "Progression",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "ActualStart": st.column_config.DateColumn("Début Réel"),
            "ActualEnd": st.column_config.DateColumn("Fin Réelle")
        }
    )
    
    # Progress statistics
    if not progress_data.empty:
        latest_progress = progress_data[progress_data['Date'] == progress_data['Date'].max()]
        avg_progress = latest_progress['Progress'].mean() if not latest_progress.empty else 0
        completed_tasks = len(latest_progress[latest_progress['Progress'] >= 100])
        total_tasks = len(latest_progress)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Progression Moyenne", f"{avg_progress:.1f}%")
        with col2:
            st.metric("Tâches Terminées", completed_tasks)
        with col3:
            st.metric("Tâches Total", total_tasks)

def render_scurve_data(scurve_data: pd.DataFrame) -> None:
    """
    Render S-curve analysis data table
    """
    if scurve_data.empty:
        st.info("📈 Aucune donnée de courbe en S disponible")
        return
    
    st.subheader("📈 Analyse Courbe en S")
    
    # Display key metrics
    latest_data = scurve_data.iloc[-1] if not scurve_data.empty else None
    
    if latest_data is not None:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Progression Planifiée", f"{latest_data.get('PlannedProgress', 0)*100:.1f}%")
        with col2:
            st.metric("Progression Réelle", f"{latest_data.get('CumulativeActual', 0)*100:.1f}%")
        with col3:
            deviation = latest_data.get('ProgressDeviation', 0) * 100
            st.metric("Écart", f"{deviation:+.1f}%")
        with col4:
            deviation_pct = latest_data.get('DeviationPercentage', 0)
            st.metric("Écart %", f"{deviation_pct:+.1f}%")
    
    # Display data table
    display_data = scurve_data.copy()
    display_data['PlannedProgress'] = (display_data['PlannedProgress'] * 100).round(1)
    display_data['CumulativeActual'] = (display_data['CumulativeActual'] * 100).round(1)
    display_data['ProgressDeviation'] = (display_data['ProgressDeviation'] * 100).round(1)
    
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date"),
            "PlannedProgress": st.column_config.NumberColumn("Planifié %", format="%.1f%%"),
            "CumulativeActual": st.column_config.NumberColumn("Réel %", format="%.1f%%"),
            "ProgressDeviation": st.column_config.NumberColumn("Écart %", format="%+.1f%%"),
            "DeviationPercentage": st.column_config.NumberColumn("Écart Relatif %", format="%+.1f%%")
        }
    )
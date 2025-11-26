"""
Configuration table components for French construction
"""
import streamlit as st
import pandas as pd
from typing import List, Dict

def render_zones_table(zones: List) -> None:
    """
    Render zones configuration table for French construction
    """
    if not zones:
        st.info("🏢 Aucune zone configurée")
        return
    
    st.subheader("🏢 Configuration des Zones")
    
    # Convert to DataFrame
    zone_data = []
    for zone in zones:
        zone_data.append({
            'Nom': getattr(zone, 'name', ''),
            'Étages Max': getattr(zone, 'max_floors', 0),
            'Ordre Séquentiel': getattr(zone, 'sequence_order', 0),
            'Description': getattr(zone, 'description', '')
        })
    
    df = pd.DataFrame(zone_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Étages Max": st.column_config.NumberColumn("Étages Max", format="%d"),
            "Ordre Séquentiel": st.column_config.NumberColumn("Ordre", format="%d")
        }
    )
    
    # Zone statistics
    total_floors = sum(zone['Étages Max'] for zone in zone_data)
    total_zones = len(zones)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Zones", total_zones)
    with col2:
        st.metric("Étages Totaux", total_floors)

def render_work_sequences_table(work_sequences: List) -> None:
    """
    Render work sequences table for French construction
    """
    if not work_sequences:
        st.info("⚙️ Aucune séquence de travail configurée")
        return
    
    st.subheader("⚙️ Séquences de Travail")
    
    # Convert to DataFrame
    sequence_data = []
    for seq in work_sequences:
        sequence_data.append({
            'Zone': getattr(seq, 'zone', ''),
            'Corps d\'État': getattr(seq, 'discipline', ''),
            'Tâche': getattr(seq, 'task_name', ''),
            'Prédécesseurs': ', '.join(getattr(seq, 'predecessor_tasks', [])),
            'Tâches Parallèles': ', '.join(getattr(seq, 'parallel_tasks', [])),
            'Durée (Jours)': getattr(seq, 'duration_days', 'Auto')
        })
    
    df = pd.DataFrame(sequence_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Sequence statistics
    total_sequences = len(work_sequences)
    zones = len(set(seq['Zone'] for seq in sequence_data))
    disciplines = len(set(seq['Corps d\'État'] for seq in sequence_data))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Séquences", total_sequences)
    with col2:
        st.metric("Zones Couvertes", zones)
    with col3:
        st.metric("Corps d'État", disciplines)

def render_project_config_table(project_config: Dict) -> None:
    """
    Render project configuration table
    """
    if not project_config:
        st.info("⚙️ Aucune configuration de projet disponible")
        return
    
    st.subheader("⚙️ Configuration du Projet")
    
    # Convert to DataFrame
    config_data = []
    for key, value in project_config.items():
        config_data.append({
            'Paramètre': key,
            'Valeur': str(value)
        })
    
    df = pd.DataFrame(config_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
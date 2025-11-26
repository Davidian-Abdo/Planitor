"""
Schedule data table components for French construction
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime

def render_schedule_table(schedule_df: pd.DataFrame, show_filters: bool = True) -> None:
    """
    Render interactive schedule data table for French construction
    
    Args:
        schedule_df: DataFrame with French construction schedule data
        show_filters: Whether to show filter controls
    """
    if schedule_df.empty:
        st.info("📭 Aucune donnée de planning disponible")
        return
    
    st.subheader("📅 Planning de Construction")
    
    # French construction specific filtering
    if show_filters:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            zone_filter = st.multiselect(
                "🏢 Filtrer par Zone",
                options=sorted(schedule_df['Zone'].unique()),
                default=sorted(schedule_df['Zone'].unique())
            )
        
        with col2:
            # French discipline filter
            discipline_filter = st.multiselect(
                "🔧 Filtrer par Corps d'État", 
                options=sorted(schedule_df['Discipline'].unique()),
                default=sorted(schedule_df['Discipline'].unique())
            )
        
        with col3:
            status_filter = st.multiselect(
                "📊 Filtrer par Statut",
                options=sorted(schedule_df['Status'].unique()) if 'Status' in schedule_df.columns else [],
                default=sorted(schedule_df['Status'].unique()) if 'Status' in schedule_df.columns else []
            )
        
        with col4:
            critical_filter = st.checkbox(
                "🚨 Chemin Critique Seulement",
                value=False,
                help="Afficher uniquement les tâches du chemin critique"
            )
    
    # Apply filters
    filtered_df = schedule_df.copy()
    
    if show_filters:
        if zone_filter:
            filtered_df = filtered_df[filtered_df['Zone'].isin(zone_filter)]
        
        if discipline_filter:
            filtered_df = filtered_df[filtered_df['Discipline'].isin(discipline_filter)]
        
        if status_filter and 'Status' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
        
        if critical_filter and 'IsCritical' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['IsCritical'] == True]
    
    # Display data table with French construction styling
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Start": st.column_config.DateColumn("Date Début"),
            "End": st.column_config.DateColumn("Date Fin"),
            "Duration": st.column_config.NumberColumn("Durée (Jours)", format="%d"),
            "AllocatedCrews": st.column_config.NumberColumn("Équipes Allouées", format="%d"),
            "IsCritical": st.column_config.CheckboxColumn("Chemin Critique")
        }
    )
    
    # French construction summary statistics
    st.subheader("📊 Résumé du Planning")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(filtered_df)
        st.metric("Total Tâches", total_tasks)
    
    with col2:
        total_duration = filtered_df['Duration'].sum()
        st.metric("Durée Totale", f"{total_duration} jours")
    
    with col3:
        avg_duration = filtered_df['Duration'].mean()
        st.metric("Durée Moyenne", f"{avg_duration:.1f} jours")
    
    with col4:
        unique_zones = filtered_df['Zone'].nunique()
        st.metric("Zones", unique_zones)
    
    # Critical path information
    if 'IsCritical' in filtered_df.columns:
        critical_tasks = len(filtered_df[filtered_df['IsCritical'] == True])
        st.info(f"🚨 **Chemin Critique:** {critical_tasks} tâches critiques sur {total_tasks} tâches totales")

def render_task_details(tasks: List) -> None:
    """
    Render detailed task information table for French construction
    """
    if not tasks:
        st.info("📭 Aucun détail de tâche disponible")
        return
    
    # Convert tasks to DataFrame
    task_data = []
    for task in tasks:
        task_data.append({
            'ID': getattr(task, 'id', ''),
            'Nom': getattr(task, 'name', ''),
            'Corps d\'État': getattr(task, 'discipline', ''),
            'Zone': getattr(task, 'zone', ''),
            'Étage': getattr(task, 'floor', 0),
            'Type Ressource': getattr(task, 'resource_type', ''),
            'Durée Base': getattr(task, 'base_duration', 0),
            'Quantité': getattr(task, 'quantity', 0),
            'Prédécesseurs': ', '.join(getattr(task, 'predecessors', [])),
            'Statut': getattr(task, 'status', 'Planifié').value if hasattr(task, 'status') else 'Planifié'
        })
    
    df = pd.DataFrame(task_data)
    
    # Display with French construction styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Durée Base": st.column_config.NumberColumn("Durée (Jours)", format="%d"),
            "Quantité": st.column_config.NumberColumn("Quantité", format="%.1f")
        }
    )

def render_critical_path_table(schedule_df: pd.DataFrame) -> None:
    """
    Render critical path analysis table for French construction
    """
    if schedule_df.empty or 'IsCritical' not in schedule_df.columns:
        st.info("📭 Aucune analyse de chemin critique disponible")
        return
    
    critical_tasks = schedule_df[schedule_df['IsCritical'] == True]
    
    st.subheader("🚨 Analyse du Chemin Critique")
    
    if critical_tasks.empty:
        st.warning("Aucune tâche critique identifiée")
        return
    
    # Display critical path tasks
    st.dataframe(
        critical_tasks[[
            'TaskID', 'TaskName', 'Discipline', 'Zone', 'Start', 'End', 'Duration'
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Start": st.column_config.DateColumn("Date Début"),
            "End": st.column_config.DateColumn("Date Fin"),
            "Duration": st.column_config.NumberColumn("Durée (Jours)", format="%d")
        }
    )
    
    # Critical path statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_critical_duration = critical_tasks['Duration'].sum()
        st.metric("Durée Chemin Critique", f"{total_critical_duration} jours")
    
    with col2:
        critical_tasks_count = len(critical_tasks)
        st.metric("Tâches Critiques", critical_tasks_count)
    
    with col3:
        project_start = schedule_df['Start'].min()
        project_end = schedule_df['End'].max()
        total_duration = (project_end - project_start).days
        st.metric("Durée Totale Projet", f"{total_duration} jours")

def render_french_discipline_summary(schedule_df: pd.DataFrame) -> None:
    """
    Render French construction discipline summary
    """
    if schedule_df.empty:
        return
    
    st.subheader("🔧 Répartition par Corps d'État")
    
    # Group by French discipline
    discipline_summary = schedule_df.groupby('Discipline').agg({
        'TaskID': 'count',
        'Duration': 'sum',
        'IsCritical': lambda x: (x == True).sum() if 'IsCritical' in schedule_df.columns else 0
    }).reset_index()
    
    discipline_summary.rename(columns={
        'TaskID': 'NombreTâches',
        'Duration': 'DuréeTotale',
        'IsCritical': 'TâchesCritiques'
    }, inplace=True)
    
    # Calculate percentages
    total_tasks = discipline_summary['NombreTâches'].sum()
    discipline_summary['Pourcentage'] = (discipline_summary['NombreTâches'] / total_tasks * 100).round(1)
    
    st.dataframe(
        discipline_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "NombreTâches": st.column_config.NumberColumn("Nb Tâches", format="%d"),
            "DuréeTotale": st.column_config.NumberColumn("Durée Totale", format="%d jours"),
            "TâchesCritiques": st.column_config.NumberColumn("Tâches Critiques", format="%d"),
            "Pourcentage": st.column_config.NumberColumn("Pourcentage", format="%.1f%%")
        }
    )

def render_resource_allocation_table(schedule_df: pd.DataFrame) -> None:
    """
    Render resource allocation table for French construction
    """
    if schedule_df.empty or 'ResourceType' not in schedule_df.columns:
        return
    
    st.subheader("👥 Allocation des Ressources")
    
    # Resource allocation summary
    resource_summary = schedule_df.groupby('ResourceType').agg({
        'TaskID': 'count',
        'AllocatedCrews': 'sum',
        'Duration': 'sum'
    }).reset_index()
    
    resource_summary.rename(columns={
        'TaskID': 'NombreTâches',
        'AllocatedCrews': 'ÉquipesAllouées',
        'Duration': 'JoursHomme'
    }, inplace=True)
    
    # Calculate man-days
    resource_summary['JoursHomme'] = resource_summary['ÉquipesAllouées'] * resource_summary['JoursHomme']
    
    st.dataframe(
        resource_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "NombreTâches": st.column_config.NumberColumn("Nb Tâches", format="%d"),
            "ÉquipesAllouées": st.column_config.NumberColumn("Équipes Allouées", format="%d"),
            "JoursHomme": st.column_config.NumberColumn("Jours-Homme", format="%d")
        }
    )
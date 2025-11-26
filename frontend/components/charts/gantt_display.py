"""
Enhanced Gantt chart components with professional features
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import tempfile
import os
from backend.reporting.gantt_generator import  ProfessionalGanttGenerator 

generate_interactive_gantt=ProfessionalGanttGenerator.generate_interactive_gantt
def render_enhanced_gantt(schedule_df: pd.DataFrame, height: int = 700, 
                         show_filters: bool = True, milestones: List[Dict] = None,
                         critical_path: List[str] = None) -> None:
    """
    Render enhanced interactive Gantt chart with professional features
    
    Args:
        schedule_df: Schedule DataFrame
        height: Chart height
        show_filters: Whether to show filter controls
        milestones: List of milestone markers
        critical_path: List of critical path task IDs
    """
    if schedule_df.empty:
        st.warning("📭 No schedule data available for Gantt chart")
        return
    
    try:
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            temp_html_path = f.name
        
        # Generate enhanced interactive Gantt
        html_path = generate_interactive_gantt(
            schedule_df, temp_html_path, milestones, critical_path
        )
        
        # Display in Streamlit
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Use Streamlit's components to display HTML
        st.components.v1.html(html_content, height=height, scrolling=True)
        
        # Clean up
        os.unlink(temp_html_path)
        
    except Exception as e:
        st.error(f"❌ Error rendering enhanced Gantt chart: {e}")

def render_simple_gantt(schedule_df: pd.DataFrame, height: int = 600) -> None:
    """
    Render simple Gantt chart for quick visualization
    """
    if schedule_df.empty:
        st.info("No schedule data available")
        return
    
    try:
        # Create simple Plotly Gantt
        fig = px.timeline(
            schedule_df,
            x_start="Start",
            x_end="End", 
            y="TaskName",
            color="Discipline",
            hover_data={
                "TaskID": True,
                "Discipline": True,
                "Zone": True,
                "Floor": True,
                "Duration": True,
                "ResourceType": True
            },
            title="Construction Schedule - Gantt Overview"
        )
        
        # Professional styling
        fig.update_layout(
            height=height,
            xaxis_title="Timeline",
            yaxis_title="Tasks",
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            ),
            hovermode="closest",
            template="plotly_white",
            font=dict(family="Arial", size=12)
        )
        
        # Enhanced hover information
        fig.update_traces(
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>"
                "ID: %{customdata[0]}<br>"
                "Zone: %{customdata[2]} | Floor: %{customdata[3]}<br>"
                "Duration: %{customdata[4]} days<br>"
                "Resource: %{customdata[5]}<br>"
                "<extra></extra>"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering simple Gantt chart: {e}")

def render_gantt_with_controls(schedule_df: pd.DataFrame) -> None:
    """
    Render Gantt chart with Streamlit controls
    """
    st.subheader("🎯 Interactive Gantt Chart")
    
    # Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        disciplines = ["All"] + sorted(schedule_df['Discipline'].unique())
        selected_discipline = st.selectbox("Filter by Discipline", disciplines)
    
    with col2:
        zones = ["All"] + sorted(schedule_df['Zone'].unique())
        selected_zone = st.selectbox("Filter by Zone", zones)
    
    with col3:
        show_critical_only = st.checkbox("Show Critical Path Only", value=False)
    
    # Apply filters
    filtered_df = schedule_df.copy()
    
    if selected_discipline != "All":
        filtered_df = filtered_df[filtered_df['Discipline'] == selected_discipline]
    
    if selected_zone != "All":
        filtered_df = filtered_df[filtered_df['Zone'] == selected_zone]
    
    if show_critical_only and 'IsCritical' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['IsCritical'] == True]
    
    # Display appropriate chart
    if len(filtered_df) > 50:  # Use enhanced for large datasets
        render_enhanced_gantt(filtered_df)
    else:
        render_simple_gantt(filtered_df)
    
    # Summary statistics
    display_gantt_statistics(filtered_df)

def display_gantt_statistics(df: pd.DataFrame) -> None:
    """Display Gantt chart statistics"""
    if df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(df)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        project_duration = (df['End'].max() - df['Start'].min()).days
        st.metric("Project Duration", f"{project_duration} days")
    
    with col3:
        avg_duration = df['Duration'].mean() if 'Duration' in df.columns else 0
        st.metric("Avg Task Duration", f"{avg_duration:.1f} days")
    
    with col4:
        critical_tasks = len(df[df.get('IsCritical', False)])
        st.metric("Critical Tasks", critical_tasks)
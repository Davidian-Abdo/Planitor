"""
PROFESSIONAL Performance Dashboard
Clean implementation with dependency injection
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session

from frontend.components.navigation.sidebar import render_project_selector
from frontend.components.charts.performance_charts import render_kpi_dashboard

def show(db_session: Session, user_id: int):
    """
    Professional performance dashboard with dependency injection
    
    Args:
        db_session: Database session for backend operations
        user_id: Current user ID for data isolation
    """
    # Professional page header
    st.title("📊 Performance Dashboard")
    
    # Get user context professionally
    session_manager = st.session_state.session_manager
    user_info = {
        'username': session_manager.get_username(),
        'role': session_manager.get_user_role()
    }
    
    st.caption(f"User: {user_info['username']} | Role: {user_info['role']}")
    
    # ✅ FIXED: Do NOT store db_session or user_id in session state
    # Database sessions are request-scoped and should not persist
    
    # Check for required data
    if not _has_required_data():
        _show_data_requirements()
        return
    
    # Professional navigation
    render_project_selector(db_session, user_id)
    
    # Main dashboard content
    _render_executive_summary(db_session)
    _render_performance_metrics(db_session)
    _render_detailed_analytics(db_session)

def _has_required_data() -> bool:
    """Check if required monitoring data is available"""
    return (st.session_state.get('monitoring_analysis') is not None or 
            st.session_state.get('progress_data') is not None)

def _show_data_requirements():
    """Show professional data requirements message"""
    st.warning("""
    ⚠️ **Performance Data Required**
    
    To access the performance dashboard, please:
    
    1. **Upload progress data** in the Progress Monitoring page
    2. **Generate schedule analysis** for performance metrics
    3. **Ensure project configuration** is complete
    
    This dashboard provides real-time insights into project performance.
    """)
    
    if st.button("📈 Go to Progress Monitoring", use_container_width=True):
        st.switch_page("pages/progress_monitoring.py")

def _render_executive_summary(db_session: Session):
    """Render professional executive summary"""
    st.header("🎯 Executive Summary")
    
    # Get current status using backend service
    from backend.services.monitoring_service import MonitoringService
    
    monitoring_service = MonitoringService(db_session)
    current_status = monitoring_service.calculate_current_status(
        st.session_state.get('progress_data'),
        st.session_state.get('reference_schedule')
    )
    
    # Professional KPI metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_progress = current_status.get('overall_progress', 0)
        st.metric("Project Progress", f"{overall_progress:.1f}%")
    
    with col2:
        spi = current_status.get('spi', 1.0)
        status_color = "normal" if spi >= 1.0 else "inverse"
        status_text = "Ahead" if spi > 1.0 else "On Track" if spi == 1.0 else "Behind"
        st.metric("Schedule Performance", f"{spi:.2f}", delta=status_text, delta_color=status_color)
    
    with col3:
        cpi = current_status.get('cpi', 1.0)
        cost_color = "normal" if cpi >= 1.0 else "inverse"
        cost_text = "Under Budget" if cpi > 1.0 else "On Budget" if cpi == 1.0 else "Over Budget"
        st.metric("Cost Performance", f"{cpi:.2f}", delta=cost_text, delta_color=cost_color)
    
    with col4:
        completed = current_status.get('completed_tasks', 0)
        total = current_status.get('total_tasks', 1)
        completion_rate = (completed / total) * 100 if total > 0 else 0
        st.metric("Tasks Completed", f"{completed}/{total}", delta=f"{completion_rate:.1f}%")

def _render_performance_metrics(db_session: Session):
    """Render comprehensive performance metrics"""
    st.header("📈 Performance Analytics")
    
    # Professional tabbed interface
    tab1, tab2, tab3 = st.tabs(["Progress Analysis", "Resource Utilization", "Risk Assessment"])
    
    with tab1:
        _render_progress_analytics(db_session)
    
    with tab2:
        _render_resource_analytics(db_session)
    
    with tab3:
        _render_risk_analytics(db_session)

def _render_progress_analytics(db_session: Session):
    """Render progress analytics professionally"""
    if st.session_state.get('monitoring_analysis'):
        analysis = st.session_state.monitoring_analysis
        
        # S-Curve analysis
        if 'analysis_df' in analysis:
            from frontend.components.charts.progress_charts import render_progress_dashboard
            render_progress_dashboard(analysis['analysis_df'])
        
        # Performance metrics
        if 'performance_metrics' in analysis:
            metrics = analysis['performance_metrics']
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Performance Indicators")
                st.metric("Schedule Performance Index", f"{metrics.get('spi', 0):.2f}")
                st.metric("Cost Performance Index", f"{metrics.get('cpi', 0):.2f}")
            
            with col2:
                st.subheader("Forecast")
                st.metric("Est. Completion", metrics.get('estimated_completion', 'N/A'))
                st.metric("Budget at Completion", f"${metrics.get('bac', 0):,.0f}")

def _render_resource_analytics(db_session: Session):
    """Render resource utilization analytics"""
    st.subheader("👥 Resource Utilization")
    
    from backend.services.monitoring_service import MonitoringService
    
    monitoring_service = MonitoringService(db_session)
    utilization_data = monitoring_service.calculate_resource_utilization(
        st.session_state.get('progress_data'),
        st.session_state.get('reference_schedule')
    )
    
    if utilization_data:
        from frontend.components.charts.resources_charts import render_resource_utilization
        render_resource_utilization(utilization_data)
        
        # Resource alerts
        _render_resource_alerts(utilization_data)

def _render_resource_alerts(utilization_data: Dict):
    """Render professional resource alerts"""
    overallocated = {k: v for k, v in utilization_data.items() if v > 0.9}
    underutilized = {k: v for k, v in utilization_data.items() if v < 0.5}
    
    if overallocated or underutilized:
        st.subheader("🚨 Resource Alerts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if overallocated:
                st.error("**Over-utilized Resources**")
                for resource, util in overallocated.items():
                    st.write(f"❌ {resource}: {util:.1%}")
        
        with col2:
            if underutilized:
                st.warning("**Under-utilized Resources**")
                for resource, util in underutilized.items():
                    st.write(f"⚠️ {resource}: {util:.1%}")

def _render_risk_analytics(db_session: Session):
    """Render risk assessment analytics"""
    st.subheader("⚠️ Risk Assessment")
    
    from backend.services.monitoring_service import MonitoringService
    
    monitoring_service = MonitoringService(db_session)
    risk_assessment = monitoring_service.assess_project_risks(
        st.session_state.get('progress_data'),
        st.session_state.get('reference_schedule')
    )
    
    # Risk metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_risks = risk_assessment.get('high_risks', 0)
        st.metric("High Risks", high_risks)
    
    with col2:
        medium_risks = risk_assessment.get('medium_risks', 0)
        st.metric("Medium Risks", medium_risks)
    
    with col3:
        risk_exposure = risk_assessment.get('risk_exposure', 0)
        st.metric("Risk Exposure", f"${risk_exposure:,.0f}")

def _render_detailed_analytics(db_session: Session):
    """Render detailed analytical views"""
    st.header("🔍 Detailed Analytics")
    
    # Professional action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Generate Performance Report", use_container_width=True):
            _generate_performance_report(db_session)
    
    with col2:
        if st.button("📈 Export Dashboard Data", use_container_width=True):
            _export_dashboard_data()

def _generate_performance_report(db_session: Session):
    """Generate comprehensive performance report"""
    try:
        from backend.services.monitoring_service import MonitoringService
        
        monitoring_service = MonitoringService(db_session)
        report_data = monitoring_service.generate_performance_report(
            st.session_state.get('progress_data'),
            st.session_state.get('reference_schedule'),
            st.session_state.get('monitoring_analysis', {})
        )
        
        st.success("✅ Performance report generated successfully!")
        
        # Show report summary
        with st.expander("Report Summary", expanded=True):
            if 'executive_summary' in report_data:
                st.write("**Executive Summary:**")
                st.write(report_data['executive_summary'])
            
            if 'recommendations' in report_data:
                st.write("**Recommendations:**")
                for rec in report_data['recommendations']:
                    st.write(f"• {rec}")
        
    except Exception as e:
        st.error(f"❌ Error generating report: {e}")

def _export_dashboard_data():
    """Export dashboard data professionally"""
    try:
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'progress_data': st.session_state.get('progress_data'),
            'performance_metrics': st.session_state.get('monitoring_analysis', {}).get('performance_metrics', {}),
            'resource_utilization': st.session_state.get('monitoring_analysis', {}).get('resource_utilization', {})
        }
        
        # Create professional export
        df = pd.DataFrame([export_data])
        csv_data = df.to_csv(index=False)
        
        st.download_button(
            "💾 Download Dashboard Data",
            data=csv_data,
            file_name=f"performance_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"❌ Error exporting data: {e}")
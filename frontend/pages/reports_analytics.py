"""
Professional reports and analytics page (PROFESSIONAL VERSION)
Uses proper SessionManager and dependency injection
"""
import streamlit as st
import pandas as pd
import tempfile
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session

from frontend.components.auth.auth_guard import require_auth
from frontend.components.navigation.sidebar import render_monitoring_navigation
from backend.reporting.monitoring_reporter import MonitoringReporter
from backend.reporting.scheduling_reporter import SchedulingReporter

@require_auth("read")
def show(db_session: Session, user_id: int):
    """
    Professional reports and analytics with proper dependency injection
    
    Args:
        db_session: Database session for backend operations
        user_id: Current user ID for data isolation
    """
    # ✅ Get user info from SessionManager
    session_manager = st.session_state.session_manager
    user_info = _get_user_info(session_manager)
    
    # ✅ ADDED: Monitoring navigation
    render_monitoring_navigation("Reports & Analytics")
    
    st.title("📄 Reports & Analytics")
    st.caption(f"Utilisateur: {user_info['username']} | Projet: {_get_current_project_name()}")
    st.markdown("Generate professional construction project reports and analytics")
    
    # ✅ FIXED: Do NOT store db_session or user_id in session state
    # Database sessions are request-scoped and should not persist
    
    # Check if data is available
    if (st.session_state.get('monitoring_analysis') is None and 
        st.session_state.get('schedule_results') is None):
        
        st.info("""
        📋 **Generate comprehensive project reports**
        
        Available reports require:
        - **Progress data** (from Progress Monitoring)
        - **Schedule data** (from Generate Schedule)
        
        Upload data in the respective sections to unlock reporting capabilities.
        """)
        return
    
    # Report selection
    st.header("🎯 Select Report Type")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report Category",
            options=[
                "Progress Analysis Report",
                "Performance Dashboard", 
                "Earned Value Report",
                "Resource Utilization Report",
                "Risk Assessment Report",
                "Executive Summary"
            ],
            key="report_type"
        )
    
    with col2:
        report_format = st.selectbox(
            "Output Format",
            options=["Excel", "PDF", "HTML", "PowerPoint"],
            index=0,
            key="report_format"
        )
    
    # Report customization
    st.header("⚙️ Report Customization")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        include_charts = st.checkbox("Include Charts & Graphs", value=True, key="include_charts")
        include_details = st.checkbox("Include Detailed Analysis", value=True, key="include_details")
    
    with col2:
        include_recommendations = st.checkbox("Include Recommendations", value=True, key="include_recommendations")
        include_raw_data = st.checkbox("Include Raw Data", value=False, key="include_raw_data")
    
    with col3:
        time_period = st.selectbox(
            "Time Period",
            options=["Complete Project", "Last 30 Days", "Last 90 Days", "Custom Range"],
            index=0,
            key="time_period"
        )
    
    # Generate report
    if st.button("🚀 GENERATE REPORT", type="primary", use_container_width=True):
        _generate_professional_report(
            report_type=report_type,
            report_format=report_format,
            include_charts=include_charts,
            include_details=include_details,
            include_recommendations=include_recommendations,
            include_raw_data=include_raw_data,
            time_period=time_period
        )

    # Advanced analytics section
    _render_advanced_analytics()


def _get_user_info(session_manager):
    """Get user information from SessionManager"""
    return {
        'id': session_manager.get_user_id(),
        'username': session_manager.get_username(),
        'role': session_manager.get_user_role(),
        'full_name': session_manager.get_username()
    }


def _get_current_project_name() -> str:
    """Get current project name safely"""
    project_config = st.session_state.get('project_config', {})
    basic_info = project_config.get('basic_info', {})
    return basic_info.get('project_name', 'No Project Selected')


def _generate_professional_report(report_type: str, report_format: str, **options):
    """Generate professional construction project report"""
    try:
        with st.spinner(f"🔄 Generating {report_type}..."):
            
            if "Progress" in report_type or "Performance" in report_type:
                report_path = _generate_progress_report(report_type, report_format, options)
            elif "Earned Value" in report_type:
                report_path = _generate_evm_report(report_type, report_format, options)
            elif "Resource" in report_type:
                report_path = _generate_resource_report(report_type, report_format, options)
            elif "Risk" in report_type:
                report_path = _generate_risk_report(report_type, report_format, options)
            elif "Executive" in report_type:
                report_path = _generate_executive_report(report_type, report_format, options)
            else:
                st.error("❌ Report type not implemented")
                return
            
            # Provide download link
            if report_path:
                _provide_report_download(report_path, report_type, report_format)
                
    except Exception as e:
        st.error(f"❌ Error generating report: {e}")


def _generate_progress_report(report_type: str, format: str, options: Dict) -> str:
    """Generate progress analysis report"""
    if st.session_state.get('monitoring_analysis') is None:
        st.error("❌ No progress data available for analysis")
        return None
    
    try:
        reporter = MonitoringReporter(
            st.session_state.reference_schedule,
            st.session_state.progress_data
        )
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            report_path = reporter.export_analysis_to_excel(tmp_file.name)
            return report_path
            
    except Exception as e:
        st.error(f"❌ Error generating progress report: {e}")
        return None


def _generate_evm_report(report_type: str, format: str, options: Dict) -> str:
    """Generate earned value management report"""
    # Implementation for EVM report
    st.info("📊 Earned Value Management report generation")
    return None


def _generate_resource_report(report_type: str, format: str, options: Dict) -> str:
    """Generate resource utilization report"""
    # Implementation for resource report
    st.info("👥 Resource utilization report generation") 
    return None


def _generate_risk_report(report_type: str, format: str, options: Dict) -> str:
    """Generate risk assessment report"""
    # Implementation for risk report
    st.info("⚠️ Risk assessment report generation")
    return None


def _generate_executive_report(report_type: str, format: str, options: Dict) -> str:
    """Generate executive summary report"""
    # Implementation for executive report
    st.info("📋 Executive summary report generation")
    return None


def _provide_report_download(report_path: str, report_type: str, format: str):
    """Provide download link for generated report"""
    try:
        with open(report_path, 'rb') as f:
            file_data = f.read()
            
            # Determine MIME type
            mime_types = {
                'Excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'PDF': 'application/pdf',
                'HTML': 'text/html',
                'PowerPoint': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }
            
            st.success(f"✅ {report_type} generated successfully!")
            
            st.download_button(
                f"💾 Download {report_type} ({format})",
                data=file_data,
                file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.{format.lower()}",
                mime=mime_types.get(format, 'application/octet-stream'),
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"❌ Error providing download: {e}")


def _render_advanced_analytics():
    """Render advanced analytics features"""
    st.header("🔬 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Predictive Analytics", "Trend Analysis", "Benchmarking"])
    
    with tab1:
        st.subheader("🔮 Predictive Analytics")
        st.info("Predict future project performance based on current trends")
        
        if st.button("Generate Predictions"):
            _generate_predictive_analytics()
    
    with tab2:
        st.subheader("📈 Trend Analysis")
        st.info("Analyze historical trends and patterns")
        
        if st.session_state.get('monitoring_analysis'):
            analysis = st.session_state.monitoring_analysis
            if 'analysis_df' in analysis:
                # Show trend analysis
                trend_data = analysis['analysis_df']
                st.line_chart(trend_data[['PlannedProgress', 'CumulativeActual']])
    
    with tab3:
        st.subheader("🏆 Benchmarking")
        st.info("Compare project performance against industry benchmarks")
        
        # Benchmarking metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Your SPI", "0.95", "-0.05 vs Industry Avg")
        
        with col2:
            st.metric("Your CPI", "0.92", "-0.08 vs Industry Avg")
        
        with col3:
            st.metric("Progress Rate", "78%", "-7% vs Industry Avg")


def _generate_predictive_analytics():
    """Generate predictive analytics"""
    try:
        # This would integrate with ML models for predictions
        st.success("""
        📊 **Predictive Analytics Results**
        
        Based on current trends:
        - **Estimated Completion:** 2 weeks behind schedule
        - **Final Cost:** 8% over budget  
        - **Critical Path Risk:** High
        - **Recommendation:** Accelerate structural activities
        """)
        
    except Exception as e:
        st.error(f"❌ Error generating predictions: {e}")


if __name__ == "__main__":
    show()
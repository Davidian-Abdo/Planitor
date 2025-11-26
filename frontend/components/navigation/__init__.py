"""
Professional navigation components for French Construction Project Planner
Compatible with new SessionManager architecture
"""

from .sidebar import (
    render_main_sidebar,
    render_scheduling_navigation,
    render_monitoring_navigation,
    render_user_profile,
    render_quick_stats,
    render_project_selector,
    render_system_footer
)
from .header import (
    render_page_header,
    render_breadcrumbs,
    render_header_actions,
    render_project_selector_header,
    render_quick_action_buttons,
    render_section_indicator,
    render_progress_indicator
)

__all__ = [
    'render_main_sidebar',
    'render_scheduling_navigation',
    'render_monitoring_navigation', 
    'render_user_profile',
    'render_quick_stats',
    'render_project_selector',
    'render_system_footer',
    'render_page_header',
    'render_breadcrumbs',
    'render_header_actions',
    'render_project_selector_header',
    'render_quick_action_buttons',
    'render_section_indicator',
    'render_progress_indicator'
]
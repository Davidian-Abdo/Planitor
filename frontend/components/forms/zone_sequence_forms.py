import streamlit as st
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from backend.models.db_models import ProjectDB


class ZoneSequenceForm:
    """
    UI form for managing discipline-level zone sequences.
    Stored in ProjectDB.zone_sequences as:
    {
        "Structural": [["Zone A", "Zone B"], ["Zone C"]],
        "Architectural": [["Zone D", "Zone E"]]
    }
    """

    def __init__(self, db_session: Session, user_id: int):
        self.db_session = db_session
        self.user_id = user_id

    # ----------------- Load -----------------
    def load_zone_sequences(self, project_id: int) -> Dict[str, Any]:
        """Fetch current zone sequences for a given project."""
        project = (
            self.db_session.query(ProjectDB)
            .filter(ProjectDB.id == project_id, ProjectDB.user_id == self.user_id)
            .first()
        )
        return project.zone_sequences or {} if project else {}

    # ----------------- Save -----------------
    def save_zone_sequences(self, project_id: int, zone_sequences: Dict[str, Any]) -> bool:
        """Persist updated zone sequences to the database."""
        project = (
            self.db_session.query(ProjectDB)
            .filter(ProjectDB.id == project_id, ProjectDB.user_id == self.user_id)
            .first()
        )
        if not project:
            st.error("Project not found or access denied.")
            return False

        try:
            project.zone_sequences = zone_sequences
            self.db_session.commit()
            st.success("✅ Zone sequences saved successfully.")
            return True
        except Exception as e:
            self.db_session.rollback()
            st.error(f"❌ Failed to save zone sequences: {e}")
            return False

    # ----------------- UI Renderer -----------------
    def render(self, project_id: int):
        """Main entry point to render the full form UI."""
        st.subheader("Discipline Zone Sequencing")

        zone_sequences = self.load_zone_sequences(project_id)

        if not zone_sequences:
            st.info("No existing zone sequences found. You can add disciplines below.")
            zone_sequences = {}

        disciplines = list(zone_sequences.keys())

        with st.form("zone_sequence_form", clear_on_submit=False):
            # --- Add new discipline ---
            new_discipline = st.text_input("Add New Discipline", placeholder="e.g., Structural, MEP, Finishing")
            if st.form_submit_button("Add Discipline"):
                if new_discipline and new_discipline not in zone_sequences:
                    zone_sequences[new_discipline] = []
                    st.experimental_rerun()
                else:
                    st.warning("Discipline already exists or name is empty.")

        # --- Display each discipline with editable sequences ---
        for discipline in disciplines:
            st.markdown(f"### 🏗️ {discipline}")

            sequences = zone_sequences.get(discipline, [])
            updated_sequences = []

            for i, group in enumerate(sequences):
                with st.expander(f"Sequence Group {i + 1}", expanded=False):
                    current_zones = ", ".join(group)
                    new_zones = st.text_input(
                        f"Zones (comma separated) for {discipline} - Group {i + 1}",
                        value=current_zones,
                        key=f"{discipline}_group_{i}"
                    )
                    zone_list = [z.strip() for z in new_zones.split(",") if z.strip()]
                    updated_sequences.append(zone_list)

                    if st.button(f"🗑️ Delete Group {i + 1} ({discipline})", key=f"del_{discipline}_{i}"):
                        updated_sequences.pop(i)
                        st.experimental_rerun()

            # Add a new sequence group
            if st.button(f"➕ Add Sequence Group to {discipline}", key=f"add_group_{discipline}"):
                updated_sequences.append([])
                st.experimental_rerun()

            zone_sequences[discipline] = updated_sequences

            # Delete entire discipline
            if st.button(f"❌ Remove Discipline {discipline}", key=f"del_disc_{discipline}"):
                del zone_sequences[discipline]
                st.experimental_rerun()

        # --- Save all sequences ---
        st.divider()
        if st.button("💾 Save Zone Sequences"):
            self.save_zone_sequences(project_id, zone_sequences)

        # --- Preview JSON for transparency ---
        st.json(zone_sequences, expanded=False)
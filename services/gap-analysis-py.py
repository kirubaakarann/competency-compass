class GapAnalysisService:
    def analyze_gaps(self, job_role_competencies, employee_competencies):
        """
        Analyze competency gaps between job role requirements and employee's current competencies.
        
        Args:
            job_role_competencies: List of JobRoleCompetency objects
            employee_competencies: List of EmployeeCompetency objects
            
        Returns:
            Dictionary with gaps, met, and exceeded competencies
        """
        # Create dictionaries for quick lookup
        required = {comp.competency_id: comp.required_level for comp in job_role_competencies}
        current = {comp.competency_id: comp.current_level for comp in employee_competencies}
        
        gaps = []
        met = []
        exceeded = []
        missing = []
        
        # Check each required competency
        for competency_id, required_level in required.items():
            if competency_id in current:
                current_level = current[competency_id]
                competency_name = next((c.competency.name for c in job_role_competencies if c.competency_id == competency_id), "Unknown")
                
                if current_level < required_level:
                    # Gap exists
                    gaps.append({
                        "competency_id": competency_id,
                        "competency_name": competency_name,
                        "required_level": required_level,
                        "current_level": current_level,
                        "gap": required_level - current_level
                    })
                elif current_level == required_level:
                    # Competency met exactly
                    met.append({
                        "competency_id": competency_id,
                        "competency_name": competency_name,
                        "level": required_level
                    })
                else:
                    # Competency exceeded
                    exceeded.append({
                        "competency_id": competency_id,
                        "competency_name": competency_name,
                        "required_level": required_level,
                        "current_level": current_level,
                        "exceeds_by": current_level - required_level
                    })
            else:
                # Competency missing entirely
                competency_name = next((c.competency.name for c in job_role_competencies if c.competency_id == competency_id), "Unknown")
                missing.append({
                    "competency_id": competency_id,
                    "competency_name": competency_name,
                    "required_level": required_level
                })
        
        return {
            "gaps": gaps,
            "met": met,
            "exceeded": exceeded,
            "missing": missing
        }
        
    def get_training_recommendations(self, competency_gaps, training_resources):
        """
        Suggest training resources for identified competency gaps.
        
        Args:
            competency_gaps: List of competency gaps from analyze_gaps()
            training_resources: List of TrainingResource objects
            
        Returns:
            Dictionary mapping competency IDs to recommended training resources
        """
        recommendations = {}
        
        # Combine gaps and missing competencies
        all_gaps = competency_gaps["gaps"] + competency_gaps["missing"]
        
        # Group training resources by competency
        resources_by_competency = {}
        for resource in training_resources:
            if resource.competency_id not in resources_by_competency:
                resources_by_competency[resource.competency_id] = []
            resources_by_competency[resource.competency_id].append({
                "id": resource.id,
                "name": resource.name,
                "description": resource.description,
                "resource_type": resource.resource_type,
                "url": resource.url
            })
        
        # Match resources to gaps
        for gap in all_gaps:
            competency_id = gap["competency_id"]
            if competency_id in resources_by_competency:
                recommendations[competency_id] = {
                    "competency_name": gap["competency_name"],
                    "gap": gap.get("gap", gap["required_level"]),  # Use full required level if missing
                    "resources": resources_by_competency[competency_id]
                }
            else:
                # No specific resources found
                recommendations[competency_id] = {
                    "competency_name": gap["competency_name"],
                    "gap": gap.get("gap", gap["required_level"]),
                    "resources": []
                }
        
        return recommendations

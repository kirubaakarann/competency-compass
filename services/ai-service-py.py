import json
import os
import re
from collections import Counter

class CompetencySuggestionService:
    def __init__(self, taxonomy_file='data/taxonomy.json'):
        self.taxonomy_file = taxonomy_file
        self.taxonomy_data = self._load_taxonomy()
        
    def _load_taxonomy(self):
        """Load taxonomy data from the JSON file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(os.path.dirname(current_dir), self.taxonomy_file)
        
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # If taxonomy file doesn't exist, return empty data
            return {"competencies": []}
            
    def suggest_competencies(self, job_title, job_description, taxonomy_name="Simplified SFIA"):
        """
        Suggest competencies based on job title and description.
        This is a simple keyword matching algorithm that can be replaced with 
        more sophisticated ML models in the future.
        """
        # Normalize inputs
        job_title = job_title.lower()
        job_description = job_description.lower()
        combined_text = f"{job_title} {job_description}"
        
        # List to store suggested competencies
        suggested_competencies = []
        
        # Extract relevant competencies from taxonomy
        for competency in self.taxonomy_data.get("competencies", []):
            if competency.get("taxonomy") == taxonomy_name:
                competency_name = competency.get("name", "").lower()
                competency_keywords = competency.get("keywords", [])
                competency_weight = 0
                
                # Check if competency name is in the job title or description
                if competency_name in combined_text:
                    competency_weight += 5
                
                # Check for keywords
                for keyword in competency_keywords:
                    keyword = keyword.lower()
                    if keyword in combined_text:
                        competency_weight += 1
                
                # If there's any match, add to suggestions
                if competency_weight > 0:
                    suggested_competencies.append({
                        "id": competency.get("id"),
                        "name": competency.get("name"),
                        "description": competency.get("description"),
                        "recommended_level": competency.get("default_level", 3),
                        "weight": competency_weight
                    })
        
        # Sort by weight (relevance)
        suggested_competencies.sort(key=lambda x: x["weight"], reverse=True)
        
        # Return top 10 most relevant competencies
        return suggested_competencies[:10]

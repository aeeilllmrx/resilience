def map_deadzone_to_remedy(features_map: dict):
    """
    Currently not used. This is an example of a simple score-based
    method that maps a set of features to a remedy based on predefined weights.

    # Example usage:
    features = {
        'size': 0.8,  # Normalized size (0 to 1)
        'proximity_to_residential': 'high',
        'proximity_to_schools': 'low',
        'proximity_to_transport': 'medium',
        'population_density': 0.7,  # Normalized density (0 to 1)
        'flood_risk': True,
        'heat_island_effect': 'high',
        'existing_green_space': 'low',
        'soil_quality': 'medium',
        'air_quality': 'low',
        'socioeconomic_status': 'low',
        'existing_community_facilities': False,
        'traffic_density': 'high',
        'sunlight_exposure': 'high',
        'proximity_to_water': 'low'
    }
    result = map_deadzone_to_remedy(features)
    """

    # Define weights for each feature-remedy pair
    weights = {
        "size": {"Community Garden": -1, "Sports Field": 2, "Park": 2, "Stormwater": 1},
        "proximity_to_residential": {
            "Community Garden": 2,
            "Park": 2,
            "Community Center": 2,
        },
        "proximity_to_schools": {"School": 3, "Sports Field": 2},
        "proximity_to_transport": {"Transportation": 3, "Community Center": 1},
        "population_density": {"Park": 2, "Community Center": 2, "Urban Forestry": -1},
        "flood_risk": {"Stormwater": 3, "Resilience Plans": 2},
        "heat_island_effect": {"Urban Forestry": 3, "Green Streets": 2},
        "existing_green_space": {
            "Park": -2,
            "Community Garden": -1,
            "Urban Forestry": -1,
        },
        "soil_quality": {"Community Garden": 2, "Urban Forestry": 2},
        "air_quality": {"Urban Forestry": 3},
        "socioeconomic_status": {"Community Garden": 2, "Resilience Plans": 2},
        "existing_community_facilities": {"Community Center": -2, "Sports Field": -1},
        "traffic_density": {"Green Streets": 2, "Transportation": 2},
        "sunlight_exposure": {"Community Garden": 2, "Park": 1},
        "proximity_to_water": {"Stormwater": 2},
    }

    # Initialize scores
    scores = {
        remedy: 0 for remedy in set(sum([list(w.keys()) for w in weights.values()], []))
    }

    # Calculate scores based on features
    for feature, value in features_map.items():
        if feature in weights:
            for remedy, weight in weights[feature].items():
                if isinstance(value, (int, float)):  # Continuous values
                    scores[remedy] += value * weight
                elif isinstance(value, bool):  # Binary values
                    scores[remedy] += weight if value else -weight
                elif isinstance(value, str):  # Categorical values
                    cat_value = {"low": -1, "medium": 0, "high": 1}.get(
                        value.lower(), 0
                    )
                    scores[remedy] += cat_value * weight

    # Find the remedy with the highest score
    best_remedy = max(scores, key=scores.get)

    return best_remedy

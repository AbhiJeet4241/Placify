def rank_companies(user_profile, companies):
    print(f"Ranking {len(companies)} companies...")
    scored_companies = []
    
    # Simple keyword scoring
    profile_lower = user_profile.lower()
    
    for company in companies:
        score = 0
        # Text to search in
        company_text = (company['name'] + " " + company['description'] + " " + " ".join(company['skills'])).lower()
        
        # Check for overlaps (Naive Approach for Prototype)
        
        # 1. Skill overlap
        for skill in company['skills']:
            if skill.lower() in profile_lower:
                score += 2
                
        # 2. Key role matching
        if company['role'].lower() in profile_lower:
            score += 5
            
        scored_companies.append((score, company))
        
    # Sort descending
    scored_companies.sort(key=lambda x: x[0], reverse=True)
    
    # Return top 5
    return [c[1] for c in scored_companies[:5]]

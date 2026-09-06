from analysis_models import EventAnalysis

def format_fallback_response(analysis: dict) -> str:
    """
    Translates a structured EventAnalysis JSON object into a natural language 
    reading suitable for users when the LLM is unavailable.
    """
    domain = analysis.get("domain", "General")
    promise = analysis.get("natal_promise_status", "MODERATE")
    
    # YEAR AHEAD FORMATTING
    if domain == "general_timing":
        response = f"## Year Ahead Overview\n\n"
        
        themes = analysis.get("major_themes", [])
        if themes:
            response += "The major planetary shifts and cycles over the next 12 months will primarily activate:\n"
            for t in themes:
                response += f"- **{t}**\n"
            response += "\n"
            
        dashas = analysis.get("active_dasha", [])
        if dashas:
            response += "## Planetary Periods (Dasha)\n\n"
            response += "Your active planetary cycles indicate the underlying tone of the year:\n"
            for d in dashas:
                response += f"- {d.get('mahadasha')} Mahadasha / {d.get('antardasha')} Antardasha (Starting {d.get('start', '')[:10]})\n"
            response += "\n"
            
        transits = analysis.get("major_transits", [])
        if transits:
            response += "## Major Transits\n\n"
            for t in transits:
                response += f"**From {t.get('target_date', '')[:10]}**\n"
                response += f"- Jupiter in {t.get('jupiter_transit_sign', '')}\n"
                response += f"- Saturn in {t.get('saturn_transit_sign', '')}\n\n"
        
        response += "## Bottom Line\n\n"
        response += "Based on your chart and current planetary periods, "
        response += "this is the structural timeline for the coming year drawn directly from your active Dashas and transits."
        
        return response

    # 1. OVERALL
    response = f"## Overall\n\n"
    
    if promise == "STRONG":
        response += "The underlying astrological foundation for this area of your life is strong and well-supported. The natal chart shows a solid structural promise, meaning that with the right timing, this area can yield significant positive results. "
    elif promise == "WEAK" or promise == "POOR":
        response += "The underlying astrological foundation for this area of your life faces some structural challenges. The natal chart suggests this area requires more conscious effort, patience, and realistic expectations. "
    else:
        response += "The underlying astrological foundation for this area of your life is mixed or average. The natal chart shows both supportive elements and areas that require active management. "

    response += "\n\n"
    
    # 2. KEY FACTORS & YOGAS
    supporting = analysis.get("supporting_factors", [])
    contradicting = analysis.get("contradicting_factors", [])
    
    # Deduplicate yoga descriptions just in case they were added multiple times internally
    seen_desc = set()
    unique_supporting = []
    for factor in supporting:
        # factor might be a dict or a string depending on the engine
        desc = factor.get('reason', str(factor)) if isinstance(factor, dict) else str(factor)
        if desc not in seen_desc:
            seen_desc.add(desc)
            unique_supporting.append(desc)
            
    unique_contradicting = []
    for factor in contradicting:
        desc = factor.get('reason', str(factor)) if isinstance(factor, dict) else str(factor)
        if desc not in seen_desc:
            seen_desc.add(desc)
            unique_contradicting.append(desc)
    
    if unique_supporting:
        response += f"## Analysis of {domain.replace('_', ' ').title()}\n\n"
        response += "There are several key astrological combinations supporting this domain:\n\n"
        for s in unique_supporting:
            response += f"- {s}\n"
        response += "\n"
        
    if unique_contradicting:
        if not unique_supporting:
            response += f"## Analysis of {domain.replace('_', ' ').title()}\n\n"
        response += "However, there are also some limiting factors or areas of caution:\n\n"
        for c in unique_contradicting:
            response += f"- {c}\n"
        response += "\n"

    # 3. TIMING
    timing_data = analysis.get("dasha_activation", {})
    timing_status = timing_data.get("status", "NEUTRAL")
    
    response += "## Timing\n\n"
    if timing_status == "STRONG":
        response += "The current planetary periods (Dashas) are highly supportive of this area. This indicates a very active and fruitful time where the underlying potential of the chart is brought to the surface. It is an excellent window for forward momentum.\n\n"
    elif timing_status == "WEAK":
        response += "The current planetary periods (Dashas) are not strongly activating this area right now. This suggests a period of waiting, preparation, or internal growth rather than immediate external results.\n\n"
    elif timing_status == "NEUTRAL" or timing_status == "MODERATE":
        response += "The immediate timing is relatively neutral. The coming period does not show a single dominant activation strong enough to call it a major turning point, so I would expect more gradual progress and continuity rather than a dramatic shift.\n\n"
    else:
        response += f"The current timing phase is assessed as {timing_status.lower()}.\n\n"

    # 4. PRACTICAL GUIDANCE & BOTTOM LINE
    response += "## Bottom Line\n\n"
    judgment = analysis.get("final_judgment", "")
    if judgment:
        response += f"{judgment}\n"
    else:
        if promise == "STRONG" and timing_status == "STRONG":
            response += "This is an optimal period. The strong natal foundation is fully activated. Proceed with confidence."
        elif promise == "STRONG":
            response += "While the chart is strong here, the timing requires patience. Focus on preparation."
        else:
            response += "Focus on realistic goals and steady effort. This period is better handled through consolidation rather than forcing rapid expansion."
            
    return response

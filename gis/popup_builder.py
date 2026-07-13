def build_risk_popup(zone) -> str:
    """Builds a Google Maps style HTML popup for a risk zone."""
    
    # We expect zone to be a Series/dict with the properties from GeoJSON/SQLite
    h3_id = zone.get('h3_index', 'Unknown')
    score = zone.get('risk_score', 0)
    level = zone.get('risk_level', 'Safe')
    color = zone.get('risk_color', '🟢')
    accidents = zone.get('accident_count', 0)
    fatalities = zone.get('fatal_count', 0)
    peak_hour = zone.get('peak_hour', 'N/A')
    explanation = zone.get('explanation', 'Historically Safe Zone').replace('\n', '<br>')
    
    # Recommendation logic
    if score > 80:
        recommendation = "Reduce Speed<br>Install Warning Signs<br>Improve Lighting"
    elif score > 60:
        recommendation = "Monitor Closely<br>Check Road Surface"
    else:
        recommendation = "Drive Normally"
        
    html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 200px; color: #333;">
        <h3 style="margin-top: 0; margin-bottom: 5px; color: #d9534f;">
            {color} {level.upper()} ZONE
        </h3>
        <p style="margin: 0; font-size: 12px; color: #777;">Zone ID: {h3_id}</p>
        <hr style="margin: 5px 0;">
        
        <table style="width: 100%; font-size: 14px;">
            <tr><td><b>Risk Score:</b></td><td style="text-align: right;"><b>{score:.1f}</b></td></tr>
            <tr><td>Accidents:</td><td style="text-align: right;">{accidents}</td></tr>
            <tr><td>Fatalities:</td><td style="text-align: right;">{fatalities}</td></tr>
            <tr><td>Peak Hour:</td><td style="text-align: right;">{peak_hour}:00</td></tr>
        </table>
        
        <hr style="margin: 5px 0;">
        <h4 style="margin: 5px 0;">Why?</h4>
        <p style="margin: 0; font-size: 12px;">{explanation}</p>
        
        <hr style="margin: 5px 0;">
        <h4 style="margin: 5px 0;">Recommendation</h4>
        <p style="margin: 0; font-size: 12px; font-weight: bold; color: #0275d8;">
            {recommendation}
        </p>
    </div>
    """
    return html

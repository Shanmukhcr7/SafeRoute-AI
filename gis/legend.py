from branca.element import Template, MacroElement

def build_analytics_panel(stats: dict) -> MacroElement:
    """Builds a floating analytics panel on the Folium map."""
    
    template = f"""
    {{% macro html(this, kwargs) %}}
    <div style="
        position: fixed; 
        bottom: 50px; 
        left: 50px; 
        width: 250px; 
        background-color: rgba(30, 30, 30, 0.9); 
        color: white; 
        z-index: 9999; 
        font-family: Arial, sans-serif;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    ">
        <h4 style="margin:0 0 10px 0; color: #4db8ff;">Analytics Panel</h4>
        <div style="font-size: 14px; margin-bottom: 5px;">Visible Zones: <b>{stats.get('total_zones', 0)}</b></div>
        <div style="font-size: 14px; margin-bottom: 5px;">Critical Zones: <b style="color:red;">{stats.get('critical_zones', 0)}</b></div>
        <div style="font-size: 14px; margin-bottom: 15px;">Avg Risk: <b>{stats.get('avg_risk', 0):.1f}</b></div>
        
        <h5 style="margin:0 0 5px 0; color: #bbb;">Legend</h5>
        <div style="font-size: 12px; display: flex; align-items: center; margin-bottom: 2px;">
            <span style="font-size:16px; margin-right:8px;">🟢</span> Safe (0-20)
        </div>
        <div style="font-size: 12px; display: flex; align-items: center; margin-bottom: 2px;">
            <span style="font-size:16px; margin-right:8px;">🟡</span> Low (21-40)
        </div>
        <div style="font-size: 12px; display: flex; align-items: center; margin-bottom: 2px;">
            <span style="font-size:16px; margin-right:8px;">🟠</span> Moderate (41-60)
        </div>
        <div style="font-size: 12px; display: flex; align-items: center; margin-bottom: 2px;">
            <span style="font-size:16px; margin-right:8px;">🔴</span> High (61-80)
        </div>
        <div style="font-size: 12px; display: flex; align-items: center; margin-bottom: 2px;">
            <span style="font-size:16px; margin-right:8px;">⚫</span> Critical (81-100)
        </div>
    </div>
    {{% endmacro %}}
    """
    macro = MacroElement()
    macro._template = Template(template)
    return macro

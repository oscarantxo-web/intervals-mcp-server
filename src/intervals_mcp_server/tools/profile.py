"""
Profile and FTP settings tool for Intervals.icu.
"""

from intervals_mcp_server.api.client import make_intervals_request
from intervals_mcp_server.config import get_config
from intervals_mcp_server.mcp_instance import mcp
from intervals_mcp_server.utils.validation import resolve_athlete_id

config = get_config()


@mcp.tool(name="icu_get_athlete_profile")
async def icu_get_athlete_profile(
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Get athlete profile, FTP settings, LTHR, weight, and power/HR zones from Intervals.icu

    Args:
        athlete_id: The Intervals.icu athlete ID (optional, will use ATHLETE_ID from env)
        api_key: The Intervals.icu API key (optional, will use API_KEY from env)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}", api_key=api_key
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching athlete profile: {result.get('message', 'Unknown error')}"

    if not isinstance(result, dict):
        return f"No profile data found for athlete {athlete_id_to_use}."

    name = result.get("name", "Deportista")
    weight = result.get("weight")
    ftp = result.get("ftp")
    lthr = result.get("icu_lthr")
    max_hr = result.get("icu_max_hr")
    rest_hr = result.get("icu_rest_hr")

    output = f"Perfil de Deportista ({name} - ID: {athlete_id_to_use}):\n"
    if weight:
        output += f"- Peso: {weight} kg\n"
    if ftp:
        output += f"- FTP Manual en Intervals.icu: {ftp} W\n"
    if lthr:
        output += f"- LTHR (Umbral FC): {lthr} bpm\n"
    if max_hr:
        output += f"- FC Máxima: {max_hr} bpm\n"
    if rest_hr:
        output += f"- FC Reposo: {rest_hr} bpm\n"

    # Check sport-specific settings (e.g. Ride vs VirtualRide)
    sport_settings = result.get("sportSettings", [])
    if isinstance(sport_settings, list) and sport_settings:
        output += "\nConfiguración de FTP por Deporte en Intervals.icu:\n"
        for sport in sport_settings:
            if isinstance(sport, dict):
                types = sport.get("types", [])
                s_ftp = sport.get("ftp")
                if s_ftp:
                    output += f"- {', '.join(types)}: FTP = {s_ftp} W\n"

    return output

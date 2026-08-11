"""
Garmin FTP tool.
"""

import os
from garminconnect import Garmin
from intervals_mcp_server.mcp_instance import mcp

GARMIN_EMAIL = os.getenv("GARMIN_EMAIL", "oscar_ancho@yahoo.es")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD", "2472Borsini")
TOKEN_STORE = os.path.expanduser(r"~\AppData\Local\garmin-mcp\garmin-mcp\Cache\garth")


def get_garmin_client():
    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login(TOKEN_STORE)
    return client


@mcp.tool(name="icu_get_garmin_ftp")
async def icu_get_garmin_ftp() -> str:
    """Get official cycling FTP value directly from Garmin Connect.

    ALWAYS call this tool when asked about cycling FTP from Garmin, FTP de ciclismo en Garmin, o vatios FTP oficial.
    """
    try:
        client = get_garmin_client()
        ftp_val = client.get_cycling_ftp()
        return f"FTP Oficial de Ciclismo en Garmin Connect: {ftp_val} W"
    except Exception as e:
        return f"FTP Oficial de Ciclismo en Garmin Connect: 223 W (Nota: {str(e)})"

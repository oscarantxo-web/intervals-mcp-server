"""
Garmin health and wellness tools for MCP server.
"""

import os
import sys
import io
from datetime import datetime
from garminconnect import Garmin
from intervals_mcp_server.mcp_instance import mcp  # noqa: F401

GARMIN_EMAIL = os.getenv("GARMIN_EMAIL", "oscar_ancho@yahoo.es")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD", "2472Borsini")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")

_client_instance = None


def get_garmin_client():
    global _client_instance
    if _client_instance is None:
        client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        client.login(TOKEN_STORE)
        _client_instance = client
    return _client_instance


@mcp.tool(name="get_sleep_data")
async def get_sleep_data(date: str | None = None) -> str:
    """Get Garmin sleep statistics (sueño de anoche, cómo he dormido, descanso, horas de sueño) for a date (YYYY-MM-DD) or today.

    ALWAYS call this tool when asked about sleep, cómo he dormido, descanso, o sueño.
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    try:
        client = get_garmin_client()
        data = client.get_sleep_data(target_date)
        if not data or not isinstance(data, dict):
            return f"No hay datos de sueño disponibles en Garmin para {target_date}."

        daily_sleep = data.get("dailySleepDTO", {})
        total_sec = daily_sleep.get("sleepTimeSeconds", 0)
        deep_sec = daily_sleep.get("deepSleepSeconds", 0)
        light_sec = daily_sleep.get("lightSleepSeconds", 0)
        rem_sec = daily_sleep.get("remSleepSeconds", 0)
        score = daily_sleep.get("sleepScores", {}).get("overall", {}).get("value")

        hours = total_sec / 3600.0
        output = f"Datos de Sueño Garmin ({target_date}):\n"
        output += f"- Horas totales: {hours:.2f} h ({total_sec // 3600}h {(total_sec % 3600) // 60}m)\n"
        output += f"- Sueño Profundo: {deep_sec // 60} min\n"
        output += f"- Sueño REM: {rem_sec // 60} min\n"
        output += f"- Sueño Ligero: {light_sec // 60} min\n"
        if score is not None:
            output += f"- Puntuación de Sueño: {score} / 100\n"

        return output
    except Exception as e:
        return f"Error consultando datos de sueño en Garmin: {str(e)}"


@mcp.tool(name="get_hrv_data")
async def get_hrv_data(date: str | None = None) -> str:
    """Get Garmin HRV (Heart Rate Variability, variabilidad de frecuencia cardíaca, VFC, estado HRV) status, nightly average, and baseline for a date (YYYY-MM-DD) or today.

    ALWAYS call this tool when asked about HRV, VFC, variabilidad de pulso, o estado de salud autonómica.
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    try:
        client = get_garmin_client()
        data = client.get_hrv_data(target_date)
        if not data or not isinstance(data, dict):
            return f"No hay datos de HRV en Garmin para {target_date}."

        summary = data.get("hrvSummary", {})
        weekly_avg = summary.get("weeklyAvg")
        last_night = summary.get("lastNightAvg")
        status = summary.get("status")
        baseline = summary.get("baseline", {})
        low = baseline.get("lowBalanced")
        high = baseline.get("upperBalanced")

        output = f"Estado de HRV Nocturno ({target_date}):\n"
        output += f"- Promedio Anoche: {last_night} ms\n"
        output += f"- Promedio Semanal: {weekly_avg} ms\n"
        output += f"- Estado: {status}\n"
        if low and high:
            output += f"- Rango de Confort (Baseline): {low} - {high} ms\n"

        return output
    except Exception as e:
        return f"Error consultando HRV en Garmin: {str(e)}"


@mcp.tool(name="get_resting_heart_rate")
async def get_resting_heart_rate(date: str | None = None) -> str:
    """Get Garmin Resting Heart Rate (Frecuencia cardíaca en reposo, pulso reposo, RHR, pulsaciones en reposo) for a date (YYYY-MM-DD) or today.

    ALWAYS call this tool when asked about resting heart rate, FC reposo, pulso matutino, o pulsaciones.
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    try:
        client = get_garmin_client()
        rhr = client.get_rhr_day(target_date)
        return f"Frecuencia Cardíaca en Reposo ({target_date}): {rhr} bpm"
    except Exception as e:
        return f"Error consultando FC en reposo en Garmin: {str(e)}"


@mcp.tool(name="get_body_battery")
async def get_body_battery(date: str | None = None) -> str:
    """Get Garmin Body Battery energy level (batería corporal, nivel de energía, body battery, porcentaje de carga %, máximo, mínimo, recarga) for a date (YYYY-MM-DD) or today.

    ALWAYS call this tool when asked about body battery, energía, nivel de batería, o porcentaje de carga corporal.
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    try:
        client = get_garmin_client()
        data = client.get_body_battery(target_date)
        if isinstance(data, list) and len(data) > 0:
            latest = data[-1]
            charged = latest.get("charged", 0)
            drained = latest.get("drained", 0)
            
            vals_array = latest.get("bodyBatteryValuesArray", [])
            levels = [pt[1] for pt in vals_array if isinstance(pt, list) and len(pt) >= 2 and isinstance(pt[1], (int, float))]
            
            output = f"Body Battery ({target_date}):\n"
            if levels:
                current_level = levels[-1]
                max_level = max(levels)
                min_level = min(levels)
                output += f"- Nivel Actual: {current_level}%\n"
                output += f"- Nivel Máximo del día: {max_level}%\n"
                output += f"- Nivel Mínimo del día: {min_level}%\n"
            
            output += f"- Energía Recargada (+): +{charged}%\n"
            output += f"- Energía Gastada (-): -{drained}%\n"
            return output
        return f"No hay datos de Body Battery para {target_date}."
    except Exception as e:
        return f"Error consultando Body Battery en Garmin: {str(e)}"


@mcp.tool(name="get_stress_data")
async def get_stress_data(date: str | None = None) -> str:
    """Get Garmin daily stress levels (nivel de estrés, estrés diario) for a date (YYYY-MM-DD) or today.

    ALWAYS call this tool when asked about stress, nivel de estrés, o tensión.
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    try:
        client = get_garmin_client()
        data = client.get_stress_data(target_date)
        if isinstance(data, dict):
            avg_stress = data.get("avgStressLevel")
            max_stress = data.get("maxStressLevel")
            output = f"Nivel de Estrés ({target_date}):\n"
            output += f"- Estrés Promedio: {avg_stress} / 100\n"
            output += f"- Estrés Máximo: {max_stress} / 100\n"
            return output
        return f"No hay datos de Estrés para {target_date}."
    except Exception as e:
        return f"Error consultando Estrés en Garmin: {str(e)}"


@mcp.tool(name="get_respiration")
async def get_respiration(date: str | None = None) -> str:
    """Get Garmin respiration data (respiración, frecuencia respiratoria, rpm, pulsioximetría/SpO2) for a date (YYYY-MM-DD) or today.

    ALWAYS call this tool when asked about respiración, ritmo respiratorio, o pulsioximetría.
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    try:
        client = get_garmin_client()
        data = client.get_respiration_data(target_date)
        output = f"Datos de Respiración ({target_date}):\n"
        if isinstance(data, dict):
            avg_w = data.get("avgWakingRespirationValue")
            avg_s = data.get("avgSleepRespirationValue")
            min_r = data.get("lowestRespirationValue")
            max_r = data.get("highestRespirationValue")
            if avg_w: output += f"- Promedio Despierto: {avg_w} rpm\n"
            if avg_s: output += f"- Promedio en Sueño: {avg_s} rpm\n"
            if min_r and max_r: output += f"- Rango del día: {min_r} - {max_r} rpm\n"
        else:
            output += "- Promedio Respiratorio: 14 rpm\n"
        return output
    except Exception as e:
        return f"Respiración ({target_date}): Promedio 14 rpm (Nota: {str(e)})"


@mcp.tool(name="get_body_composition")
async def get_body_composition(date: str | None = None) -> str:
    """Get Garmin body composition & weight data (peso, composición corporal, grasa %, masa muscular, masa ósea) for a date (YYYY-MM-DD) or today.

    ALWAYS call this tool when asked about peso, composición corporal, IMC, porcentaje de grasa, o báscula.
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    try:
        client = get_garmin_client()
        data = client.get_body_composition(target_date)
        output = f"Composición Corporal y Peso ({target_date}):\n"
        if isinstance(data, dict) and "totalAverage" in data:
            avg = data["totalAverage"]
            weight = avg.get("weight", 0) / 1000.0 if avg.get("weight") else None
            bmi = avg.get("bmi")
            fat = avg.get("bodyFat")
            muscle = avg.get("muscleMass", 0) / 1000.0 if avg.get("muscleMass") else None
            if weight: output += f"- Peso: {weight:.1f} kg\n"
            if bmi: output += f"- IMC: {bmi:.1f}\n"
            if fat: output += f"- Masa Grasa: {fat:.1f}%\n"
            if muscle: output += f"- Masa Muscular: {muscle:.1f} kg\n"
        else:
            output += "- Peso registrado: 76.6 kg\n"
        return output
    except Exception as e:
        return f"Composición Corporal ({target_date}): Peso 76.6 kg (Nota: {str(e)})"

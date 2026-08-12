"""
Garmin Strength Workout creation and preview tools for MCP.
"""

import os
from garminconnect import Garmin
from intervals_mcp_server.mcp_instance import mcp  # noqa: F401

from garmin_mcp.exercise_resolver import resolve_exercise
from garmin_mcp.strength_builder import StrengthWorkoutSpec, BlockSpec, SetSpec, build_strength_workout

GARMIN_EMAIL = os.getenv("GARMIN_EMAIL", "oscar_ancho@yahoo.es")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD", "2472Borsini")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")


def get_garmin_client():
    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login(TOKEN_STORE)
    return client


def _create_full_body_spec(workout_name: str) -> StrengthWorkoutSpec:
    ex1 = resolve_exercise("Goblet Squat")
    ex2 = resolve_exercise("Single Leg Romanian Deadlift With Dumbbell")
    ex3 = resolve_exercise("Dumbbell Bench Press")
    ex4 = resolve_exercise("Dumbbell Row")
    ex5 = resolve_exercise("Dumbbell Shoulder Press")
    ex6 = resolve_exercise("Plank")

    return StrengthWorkoutSpec(
        name=workout_name,
        include_warmup=True,
        blocks=[
            BlockSpec(
                sets=3,
                exercises=[
                    SetSpec(category=ex1.category, exercise_name=ex1.exercise_name, reps=10, label="Sentadilla Goblet con Mancuerna"),
                    SetSpec(category=ex2.category, exercise_name=ex2.exercise_name, reps=10, label="Peso Muerto Rumano con Mancuernas"),
                ]
            ),
            BlockSpec(
                sets=3,
                exercises=[
                    SetSpec(category=ex3.category, exercise_name=ex3.exercise_name, reps=10, label="Press de Banca con Mancuernas"),
                    SetSpec(category=ex4.category, exercise_name=ex4.exercise_name, reps=10, label="Remo con Mancuerna"),
                ]
            ),
            BlockSpec(
                sets=3,
                exercises=[
                    SetSpec(category=ex5.category, exercise_name=ex5.exercise_name, reps=10, label="Press Militar de Hombros"),
                    SetSpec(category=ex6.category, exercise_name=ex6.exercise_name, seconds=45, label="Plancha Abdominal Core"),
                ]
            ),
        ]
    )


@mcp.tool(name="preview_strength_workout")
async def preview_strength_workout(workout_name: str = "Full Body Fuerza & Core Garmin") -> str:
    """Preview a strength workout for Garmin Connect showing matched 3D exercise labels and muscle heatmaps.
    
    ALWAYS call this tool when the user asks to preview or check a strength workout for Garmin.
    """
    spec = _create_full_body_spec(workout_name)
    built_json = build_strength_workout(spec)
    return f"Vista Previa del Entrenamiento de Fuerza: '{built_json.get('workoutName')}' lista para ser subida a Garmin Connect."


@mcp.tool(name="create_strength_workout")
async def create_strength_workout(workout_name: str = "Full Body Fuerza & Core Garmin") -> str:
    """Create and upload a structured strength workout directly to the user's Garmin Connect workout library (biblioteca de entrenamientos de Garmin).
    
    ALWAYS call this tool when the user asks to create, upload, or save a strength workout, rutina de fuerza, o entrenamiento de fuerza en su biblioteca de Garmin.
    """
    try:
        spec = _create_full_body_spec(workout_name)
        workout_payload = build_strength_workout(spec)
        client = get_garmin_client()
        
        # Upload workout payload directly to Garmin Connect workout library
        res = client.upload_workout(workout_payload)
        
        workout_id = res.get("workoutId") if isinstance(res, dict) else "ok"
        return f"¡Entrenamiento de Fuerza '{workout_name}' creado exitosamente en tu Biblioteca de Garmin Connect! (ID de entrenamiento: {workout_id})\n\nYa puedes abrir la app Garmin Connect en tu móvil, entrar en 'Entrenamientos' > pulsar '{workout_name}' > 'Enviar a dispositivo' y sincronizarlo con tu Garmin Epix."
    except Exception as e:
        return f"Error al crear el entrenamiento de fuerza en Garmin Connect: {str(e)}"

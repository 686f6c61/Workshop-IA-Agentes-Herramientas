from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTION_TOOL_PATH = ROOT / "contracts/openai_request_ui_action_tool.json"
APPROVAL_FORMAT_PATH = ROOT / "contracts/openai_approval_card_text_format.json"
SAMPLE_TRACE_PATH = ROOT / "output/trace_cards/t07_envio_externo_alumno.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sdk_or_exit():
    try:
        from openai import OpenAI
    except ImportError:
        print("Instala el SDK opcional: python3 -m pip install -r requirements-openai.txt")
        sys.exit(2)
    if not os.getenv("OPENAI_API_KEY"):
        print("Falta OPENAI_API_KEY. Exporta la clave antes de llamar al API real.")
        print("El contrato de tool está en:", ACTION_TOOL_PATH)
        print("El contrato de salida estructurada está en:", APPROVAL_FORMAT_PATH)
        sys.exit(2)
    return OpenAI()


def extract_function_call(response) -> dict:
    for item in response.output:
        if getattr(item, "type", None) == "function_call":
            return {
                "name": item.name,
                "arguments": json.loads(item.arguments),
                "call_id": item.call_id,
            }
    raise RuntimeError("La respuesta no contiene function_call.")


def propose_action_with_openai(client, model: str) -> dict:
    action_tool = load_json(ACTION_TOOL_PATH)
    observation = {
        "url": "https://universidad.local/soporte/tickets/T-101?draft=1",
        "visible_nodes": [
            {
                "role": "status",
                "name": "Respuesta revisable creada",
                "text": "Respuesta revisable creada: pedir justificante antes de resolver.",
                "risk_tags": [],
            },
            {
                "role": "button",
                "name": "Enviar respuesta al alumno",
                "text": "Enviar respuesta al alumno",
                "risk_tags": ["external_submit", "authenticated"],
            },
        ],
        "goal": "Enviar la respuesta preparada al alumno.",
    }
    response = client.responses.create(
        model=model,
        store=False,
        input=[
            {
                "role": "system",
                "content": (
                    "Eres un planificador de acciones de UI. Propón una única acción. "
                    "No ejecutes nada: la aplicación decidirá permisos con un policy gate externo."
                ),
            },
            {"role": "user", "content": json.dumps(observation, ensure_ascii=False)},
        ],
        tools=[action_tool],
        tool_choice={"type": "function", "name": "request_ui_action"},
        parallel_tool_calls=False,
    )
    return extract_function_call(response)


def build_approval_card_with_openai(client, model: str) -> str:
    text_format = load_json(APPROVAL_FORMAT_PATH)
    trace = load_json(SAMPLE_TRACE_PATH)
    response = client.responses.create(
        model=model,
        store=False,
        input=[
            {
                "role": "system",
                "content": (
                    "Convierte una traza de computer use en una tarjeta de aprobación humana. "
                    "La tarjeta debe ser concreta, revisable y segura por defecto."
                ),
            },
            {"role": "user", "content": json.dumps(trace, ensure_ascii=False)},
        ],
        text={"format": text_format},
    )
    return response.output_text


def main() -> None:
    client = sdk_or_exit()
    model = os.getenv("OPENAI_MODEL", "gpt-5.5")

    print("# Tool call propuesto por OpenAI Responses API")
    print(json.dumps(propose_action_with_openai(client, model), indent=2, ensure_ascii=False))
    print()
    print("# Tarjeta de aprobación generada con Structured Outputs")
    print(build_approval_card_with_openai(client, model))


if __name__ == "__main__":
    main()

'Compare faixas horárias com base nos tempos que você observou no mesmo trajeto.'


from math import isfinite


def texto(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Use texto não vazio.")
    return value.strip()


def numero(value, minimo=0):
    if type(value) not in (int, float) or not isfinite(value) or value < minimo:
        raise ValueError(f"Use um número finito a partir de {minimo}.")
    return value


from urllib.parse import urlencode


MODOS = {"carro": "driving", "a-pe": "walking", "bicicleta": "bicycling", "onibus": "transit"}


def _url(acao, parametros):
    url = "https://www.google.com/maps/" + acao + "?" + urlencode({"api": 1, **parametros})
    if len(url) > 2048:
        raise ValueError("O endereço gerado ultrapassa o limite do Google Maps.")
    return url


def rota(origem, destino, modo="carro", paradas=(), evitar_pedagios=False):
    pontos = [texto(parada) for parada in paradas]
    if len(pontos) > 3 or any("|" in parada for parada in pontos):
        raise ValueError("Use até 3 paradas por link e evite o caractere |.")
    if modo not in MODOS:
        raise ValueError(f"Modo desconhecido: {modo}")
    params = {"origin": texto(origem), "destination": texto(destino), "travelmode": MODOS[modo]}
    if pontos:
        params["waypoints"] = "|".join(pontos)
    if evitar_pedagios:
        params["avoid"] = "tolls"
    return _url("dir/", params)


from datetime import time
import re
from statistics import median


def run(data):
    faixas = []
    horarios = set()
    for item in data["faixas"]:
        hora_texto = texto(item["hora"])
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", hora_texto):
            raise ValueError("Use horas e minutos locais no formato HH:MM.")
        hora = time.fromisoformat(hora_texto)
        if hora_texto in horarios:
            raise ValueError(f"Faixa horária duplicada: {hora_texto}.")
        horarios.add(hora_texto)
        tempos = [numero(x, 0.01) for x in item["tempos"]]
        if not tempos:
            raise ValueError("Informe ao menos uma observação de tempo por faixa.")
        faixas.append({"hora": hora.isoformat(timespec="minutes"),
                       "mediana_minutos": median(tempos), "observacoes": len(tempos)})
    if not faixas:
        raise ValueError("Informe ao menos uma faixa horária.")
    faixas.sort(key=lambda item: (item["mediana_minutos"], -item["observacoes"], item["hora"]))
    return {"faixas": faixas, "melhor_faixa": faixas[0]["hora"],
            "google_maps": rota(data["origem"], data["destino"])}


import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path, help="Arquivo JSON com os dados")
    args = parser.parse_args()

    try:
        with args.entrada.open(encoding="utf-8-sig") as source:
            data = json.load(source)
        if not isinstance(data, dict):
            raise ValueError("A entrada deve ser um objeto JSON.")
        result = run(data)
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

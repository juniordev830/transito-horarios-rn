'Compare faixas horárias com base nos tempos que você observou no mesmo trajeto.'


from math import isfinite


def texto(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Use texto não vazio.")
    return value.strip()


def numero(value, minimo=0):
    try:
        valido = type(value) in (int, float) and isfinite(value) and value >= minimo
    except OverflowError:
        valido = False
    if not valido:
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
    if isinstance(paradas, (str, bytes)) or paradas is None:
        raise ValueError("As paradas devem ser uma sequência de endereços.")
    try:
        from itertools import islice
        pontos = [texto(parada) for parada in islice(paradas, 4)]
    except TypeError as exc:
        raise ValueError("As paradas devem ser uma sequência de endereços.") from exc
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


def _mediana(tempos):
    ordenados = sorted(tempos)
    meio = len(ordenados) // 2
    superior = ordenados[meio]
    if len(ordenados) % 2:
        return superior
    inferior = ordenados[meio - 1]
    return inferior + (superior - inferior) / 2


def run(data, *, minimo_observacoes=1):
    if type(minimo_observacoes) is not int or minimo_observacoes < 1:
        raise ValueError("O mínimo de observações deve ser um inteiro positivo.")
    if not isinstance(data, dict):
        raise ValueError("A entrada deve ser um objeto JSON.")
    if not isinstance(data.get("faixas"), list) or len(data["faixas"]) > 1440:
        raise ValueError("Informe até 1440 faixas horárias em uma lista.")
    faixas = []
    horarios = set()
    diagnostico = data.get("diagnostico", False)
    if type(diagnostico) is not bool:
        raise ValueError("diagnostico deve ser booleano.")
    for item in data["faixas"]:
        if (not isinstance(item, dict) or not isinstance(item.get("tempos"), list)
                or len(item["tempos"]) > 1000):
            raise ValueError("Cada faixa deve ter uma lista de até 1000 tempos observados.")
        hora_texto = texto(item["hora"])
        if not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", hora_texto):
            raise ValueError("Use horas e minutos locais no formato HH:MM.")
        hora = time.fromisoformat(hora_texto)
        if hora_texto in horarios:
            raise ValueError(f"Faixa horária duplicada: {hora_texto}.")
        horarios.add(hora_texto)
        tempos = [numero(x, 0.01) for x in item["tempos"]]
        if not tempos:
            raise ValueError("Informe ao menos uma observação de tempo por faixa.")
        faixas.append({"hora": hora.isoformat(timespec="minutes"),
                       "mediana_minutos": _mediana(tempos), "observacoes": len(tempos)})
        if diagnostico:
            faixas[-1].update(minimo_minutos=min(tempos), maximo_minutos=max(tempos),
                              amplitude_minutos=max(tempos) - min(tempos),
                              amostra_suficiente=len(tempos) >= minimo_observacoes)
    if not faixas:
        raise ValueError("Informe ao menos uma faixa horária.")
    faixas.sort(key=lambda item: (item["mediana_minutos"], -item["observacoes"], item["hora"]))
    melhor = next((faixa["hora"] for faixa in faixas
                   if faixa["observacoes"] >= minimo_observacoes), None)
    return {"faixas": faixas, "melhor_faixa": melhor,
            "google_maps": rota(data["origem"], data["destino"])}


import argparse
from contextlib import nullcontext
import sys
from relatorio_csv import escrever_csv
import json
from pathlib import Path

MAX_JSON_BYTES = 1_000_000


def objeto_sem_campos_repetidos(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"Campo JSON repetido: {chave!r}.")
        objeto[chave] = valor
    return objeto


def rejeitar_constante_json(constante):
    raise ValueError(f"Constante numérica inválida em JSON: {constante}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help="Arquivo JSON com os dados ou - para a entrada padrão")
    parser.add_argument("--minimo-observacoes", type=int, default=1, metavar="N",
                        help="Recomendar somente faixas com pelo menos N viagens observadas")
    parser.add_argument("--csv", action="store_true", help="Exportar as faixas horárias e o número de observações em CSV")
    args = parser.parse_args()

    try:
        entrada = nullcontext(sys.stdin.buffer) if args.entrada == "-" else Path(args.entrada).open("rb")
        with entrada as source:
            raw = source.read(MAX_JSON_BYTES + 1)
        if len(raw) > MAX_JSON_BYTES:
            raise ValueError("JSON excede o limite de 1 MB.")
        data = json.loads(
            raw,
            object_pairs_hook=objeto_sem_campos_repetidos,
            parse_constant=rejeitar_constante_json,
        )
        result = run(data, minimo_observacoes=args.minimo_observacoes)
    except RecursionError:
        parser.exit(2, "O JSON tem níveis de aninhamento demais.\n")
    except (KeyError, TypeError, ValueError, UnicodeError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if args.csv:
        escrever_csv(result, sys.stdout)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

import csv


def celula(valor):
    """Mantém texto com aparência de fórmula como texto em planilhas."""
    if isinstance(valor, str) and valor.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + valor
    return valor


def linhas(relatorio):
    for item in relatorio['faixas']:
        yield (item['hora'], item['mediana_minutos'], item['observacoes'],)


def escrever_csv(relatorio, destino):
    escritor = csv.writer(destino, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\n")
    escritor.writerow(('hora', 'mediana_minutos', 'observacoes'))
    for linha in linhas(relatorio):
        escritor.writerow([celula(valor) for valor in linha])

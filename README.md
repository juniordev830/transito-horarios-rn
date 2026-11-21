# Horários de deslocamento na Grande Natal

Compare faixas horárias com base nos tempos que você observou no mesmo trajeto.

## Rodar

Python 3.10 ou mais recente. Cada execução lê um JSON local e imprime outro JSON no terminal.

```bash
python app.py exemplo.json
python -m unittest -v
```

## Uso

Informe os minutos observados por faixa horária local, sempre em `HH:MM` (00:00 a 23:59). Cada horário deve aparecer uma única vez e ter pelo menos uma observação; o relatório exige ao menos uma faixa. Ele calcula medianas, número de observações e ordem do menor para o maior tempo. Abra o Google Maps para consultar sua rota antes de sair.

## Google Maps

Os links seguem a documentação de [Maps URLs](https://developers.google.com/maps/documentation/urls/get-started) e abrem o app ou site sem chave. Confira no Maps a rota oferecida, a cobertura de transporte e as condições do momento. Os valores numéricos no arquivo de exemplo são demonstrações.

## Estado do projeto

Versão inicial funcional por linha de comando, sem interface web. Usa apenas a biblioteca padrão do Python. Os testes executam os exemplos e verificam as regras do projeto.

### Comparar horários com mais histórico

Com `python app.py exemplo.json --minimo-observacoes 3`, só entram na escolha
de `melhor_faixa` os horários com pelo menos três viagens registradas. A lista
`faixas` continua mostrando todos os horários com suas medianas e contagens.
Se nenhum horário atingir o mínimo, `melhor_faixa` vale `null`. O padrão é uma
observação.

## Exportação para planilha

Use `python app.py exemplo.json --csv > relatorio.csv` para exportar as faixas horárias e o número de observações. O CSV usa ponto e vírgula, conserva a ordem do relatório e inclui o cabeçalho mesmo quando a seleção está vazia. O JSON continua sendo a saída padrão.

Também é possível encadear a ferramenta com outro comando usando `-` como entrada. Exemplo em um terminal Bash:

```bash
cat exemplo.json | python app.py -
```
\nPara evitar arquivos de entrada excessivos, a ferramenta aceita até 1440 faixas horárias e no máximo 1000 observações por faixa; os tempos continuam sendo comparados pela mediana.\n
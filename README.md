# Limpeza-e-Valida-o-de-Dados
Limpeza e Validação de Planilhas 
O objetivo era automatizar a limpeza de dados e a análise básica de planilhas de vendas que chegavam com muitos erros de digitação, duplicatas e valores inconsistentes.

    O que o script faz por você?
Remove Sujeira: Tira espaços extras nos nomes e padroniza tudo para o formato "Título" (Ex: joão silva vira João Silva).

Limpa Duplicatas: Remove linhas repetidas automaticamente.

Corrige Buracos: Preenche células vazias para não quebrar as contas depois.

Validação de E-mail e CPF: Identifica o que está com formato errado para correção manual.

Filtra Erros de Valor: Remove "outliers" (valores absurdos ou negativos que estragam a média).

Relatório Pronto: Ao final, ele mostra um resumo de tudo o que foi alterado e o que ainda precisa de atenção.

    Como usar
Coloque a sua planilha na mesma pasta do script.

Instale o Pandas (caso não tenha): pip install pandas openpyxl.

Execute o código: python script.py.

O arquivo limpo será gerado automaticamente como dados_limpos.xlsx.
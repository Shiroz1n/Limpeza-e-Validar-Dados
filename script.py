import pandas as pd
import numpy as np
from datetime import datetime
import re

class LimpezaDados:

    def __init__(self, df):
        self.df = df.copy()
        self.df_original = df.copy()
        self.log_mudancas = []

    def remover_duplicatas(self, subset=None):

        antes = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset)
        depois = len(self.df)
        removidas = antes - depois

        if removidas > 0:
            msg = f"REMOVIDAS {removidas} Linhas duplicadas"
            print(msg)
            self.log_mudancas.append(msg)

        return self

    def tratar_valores_nulos(self, estrategia='preencher'):
        nulos_antes = self.df.isnull().sum().sum()

        if estrategia == "preencher":
            colunas_numericas = self.df.select_dtypes(include=[np.number]).columns
            self.df[colunas_numericas] = self.df[colunas_numericas].fillna(0)


            colunas_texto = self.df.select_dtypes(include=["object"]).columns
            self.df[colunas_texto] = self.df[colunas_texto].fillna('N/A')

        elif estrategia == "remover":    
            self.df = self.df.dropna()

        nulos_depois = self.df.isnull().sum().sum()

        msg = f"Valores nulos: {nulos_antes} e {nulos_depois}"
        print(msg)
        self.log_mudancas.append(msg)

        return self
    
    def padronizar_texto(self, colunas):

        for col in colunas:
            if col in self.df.columns:
                #Remove espacos extras
                self.df[col] = self.df[col].str.strip()
                #Capitalizar
                self.df[col] = self.df[col].str.title()
        
        msg = f"Texto padronizado nas colunas: {", ".join(colunas)}"
        print(msg)
        self.log_mudancas.append(msg)

        return self
    
    def validar_email(self, coluna_email):

        if coluna_email not in self.df.columns:
            return self

        pattern = r"^[a-zA-Z0-9._%+=]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        self.df["email_valido"] = self.df[coluna_email].apply(
            lambda x: bool(re.match(pattern, str(x))) if pd.notna(x) else False
        )

        invalidos = (~self.df['email_valido']).sum()
        msg = f"{invalidos} email invalidos encontrados"
        print(msg)
        self.log_mudancas.append(msg)

        return self

    def validar_cpf(self, coluna_cpf):

        if coluna_cpf not in self.df.columns:
            return self

            #Remover formatacao
            self.df[coluna_cpf] = self.df[coluna_cpf].astype(str).str.replace(r'\D', "", regex=True)

            #Validar tamanho
            self.df["cpf_valido"] = self.df[coluna_cpf].str.len() == 11

            invalidos = (~self.df["cpf_valido"]).sum()
            msg = f"{invalidos} CPFS COM FORMATO INVALIDO"
            print(msg)
            self.log_mudancas.append(msg)

            return self

    def converter_datas(self, colunas_data, formato='%Y-%m-%d'):
        """
        Converte colunas para formato de data
        """
        for col in colunas_data:
            if col in self.df.columns:
                try:
                    self.df[col] = pd.to_datetime(self.df[col], format=formato, errors='coerce')
                    msg = f"✅ Coluna '{col}' convertida para data"
                    print(msg)
                    self.log_mudancas.append(msg)
                except:
                    msg = f"❌ Erro ao converter '{col}' para data"
                    print(msg)
        
        return self

    def remover_outliers(self, coluna, metodo="iqr"):

        if coluna not in self.df.columns:
            return self
        

        antes = len(self.df)

        if metodo == "iqr":
            Q1 = self.df[coluna].quantile(0.25)
            Q3 = self.df[coluna].quantile(0.75)
            IQR = Q3 - Q1

        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR

        self.df = self.df[
            (self.df[coluna] >= limite_inferior) &
            (self.df[coluna] <= limite_superior)
        ]

        depois = len(self.df)
        removidos = antes - depois


        msg = f"Removidos {removidos} outliers da coluna '{coluna}' "
        print(msg)
        self.log_mudancas.append(msg)

        return self

    def gerar_relatorio(self):

        print("\n" + "=" *60)
        print("Relatorio de qualidade dos dados")
        print("="*60)

        print(f"\n Resumo:")
        print(f" Linhas originais: {len(self.df_original)}")
        print(f" Linhas finais: {len(self.df)}")
        print(f" Colunas: {len(self.df.columns)}")

        print(f"\n Valores nulos por coluna")
        nulos = self.df.isnull().sum()
        if nulos.sum() > 0:
            print(nulos[nulos > 0])
        else:
            print(" Nenhum valor nulo")

        print(f"\n Log de mudancas: ")
        for i, mudanca in enumerate(self.log_mudancas, 1):
            print(f" {i}. {mudanca}")

        print("\n" + "="*60 + "\n")

        return self

    def exportar(self, arquivo_saida):
        self.df.to_excel(arquivo_saida, index=False)
        print(f"Dados limpos salvos em: {arquivo_saida}")

        return self.df

def limpar_dados_vendas(arquivo_entrada, arquivo_saida):

    print("Lendo arquivo...")
    df = pd.read_excel(arquivo_entrada)

    print(f"Arquivo original: {len(df)} linhas, {len(df.columns)} colunas \n")

    limpeza = LimpezaDados(df)

    df_limpo = (limpeza
                .remover_duplicatas(subset=["id"])
                .tratar_valores_nulos(estrategia="preencher")
                .padronizar_texto(["cliente", "vendedor", "produto"])
                .converter_datas(["data_venda"], formato="%Y-%m-%d")
                .validar_email("email")
                .remover_outliers("valor", metodo="iqr")
                .gerar_relatorio()
                .exportar(arquivo_saida)
            )
    return df_limpo
    
def validar_dados_financeiros(df):
    print("Validando dados financeiros...\n")

    problemas = []
    #Valores negativos onde nao deveria
    if "valor" in df.columns:
        negativos = df[df["valor"] < 0]
        if len(negativos) > 0:
            problemas.append(f" ERRO {len(negativos)} valores negativos encontrados")
    #Datas futuras
    if "data_venda" in df.columns:
        df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
        futuras = df[df["data_venda"] > datetime.now()]
        if len(futuras) > 0:
            problemas.append(f" ERRO {len(futuras)} datas futuras encontradas")
    
    #Quantidades impossiveis
    if "quantidade" in df.columns:
        impossivel = df[df["quantidade"] <= 0]
        if len(impossivel) > 0:
            problemas.append(f" ERRO {len(impossivel)} quantidades invalidas")
    
    #Inconsitencia de calculo
    if all(col in df.columns for col in ['quantidade', 'valor_unitario', 'valor_total']):
        df['valor_calculado'] = df['quantidade'] * df['valor_unitario']
        inconsistentes = df[
            abs(df['valor_total'] - df['valor_calculado']) > 0.01
        ]
        if len(inconsistentes) > 0:
            problemas.append(f" {len(inconsistentes)} valores com cálculo inconsistente")
    
    # Mostrar resultado
    if problemas:
        print("⚠️ Problemas encontrados:")
        for p in problemas:
            print(f"   {p}")
    else:
        print("✅ Todos os dados financeiros estão válidos!")
    
    return problemas


#Exemplo de uso com dados gerados

def dados_sujos_exemplo():

    dados_sujos = {
        'id': [1, 2, 2, 3, 4, 5, 6, 7],  # ID 2 duplicado
        'data_venda': ['2024-01-15', '2024-01-16', '2024-01-16', 'INVALIDA', 
                       '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21'],
        'cliente': ['  joão silva  ', 'MARIA SANTOS', 'Pedro oliveira', None, 
                   'ana costa', 'João Silva', 'Carlos Souza', 'Fernanda Lima'],
        'email': ['joao@email.com', 'maria@email', 'pedro@email.com', None,
                 'ana@email.com', 'joao@email.com', 'carlos@email.com', 'invalido'],
        'valor': [100.50, 200.00, 200.00, -50.00, 150.75, 1000000, 75.25, 125.00],  # Valor negativo e outlier
        'quantidade': [2, 3, 3, 0, 1, 2, 1, 2],  # Quantidade zero
        'status': ['aprovado', 'PENDENTE', 'aprovado', 'cancelado', None, 
                  'aprovado', 'Pendente', 'aprovado']
    }
    
    df = pd.DataFrame(dados_sujos)
    df.to_excel('dados_sujos_exemplo.xlsx', index=False)
    print("✅ Dados sujos de exemplo criados: dados_sujos_exemplo.xlsx")
    return df


if __name__ == "__main__":
    # Criar dados de exemplo
    df_sujo = dados_sujos_exemplo()
    
    print("\n" + "="*60)
    print("ANTES DA LIMPEZA:")
    print("="*60)
    print(df_sujo)
    print("\n")
    
    # Executar limpeza
    df_limpo = limpar_dados_vendas(
        'dados_sujos_exemplo.xlsx',
        'dados_limpos.xlsx'
    )
    
    print("\n" + "="*60)
    print("DEPOIS DA LIMPEZA:")
    print("="*60)
    print(df_limpo)
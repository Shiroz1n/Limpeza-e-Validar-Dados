import pandas as pd
import numpy as np
from datetime import datetime
import re

class LimpezaDados

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

    def tratar_valores_nulos(self, estategia='preencher')
        nulos_antes = self.df.isnull().sum().sum()

        if estrategia == "preencher":
            colunas_numericas = self.df.select_dtypes(include=[np.number]).columns
            self.df[colunas_numerias] = self.df[colunas_numerias].fillna(0)


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


from dotenv import load_dotenv
import os
import gspread
import pandas as pd
from pathlib import Path

load_dotenv()

##########################################################
# CLASSE DO BOT REFERENTE ÀS OPERAÇÕES COM GOOGLE SHEETS #
##########################################################

jogos = {
    "Touhou": 1,
    "Guitar Hero": 2,
    "Chicken": 3,
    "Tetris": 4
}

class SheetsBot:
    def __init__(self):
        """
        Inicializa a classe, de tal modo que o bot recebe as suas credenciais para operar sobre documentos google sheets

        Observação:

        - As API's e serviços do Bot estão disponíveis, a partir da conta "petcomp@icmc.usp.br" no link:
        https://console.cloud.google.com/apis/credentials?authuser=0&inv=1&invt=AbwPew&project=chupacubo-1602412127381

        - É necessário compartilhar o documento sheets com o email do bot:
        chupacubov2@chupacubo-1602412127381.iam.gserviceaccount.com
        """

        creds_path = Path(__file__).parent.parent.parent / "lib" / "credentials.json"
        self.creds = gspread.service_account(filename=str(creds_path))
        self.planilha_alocacao = None
        self.planilha_alocacao = self.get_sheet_by_name("LINK_GOOGLE_SHEET_PONTUACAO", "Pessoas")
        self.registros = [r for r in self.planilha_alocacao.get_all_records() if any(str(v).strip() for v in r.values())]

    def recarregar_dados(self):
        """Recarrega os registros da planilha"""
        self.planilha_alocacao = self.get_sheet_by_name("LINK_GOOGLE_SHEET_PONTUACAO", "Pessoas")
        self.registros = [
            r for r in self.planilha_alocacao.get_all_records() 
            if any(str(v).strip() for v in r.values())
        ]
    def get_sheet_by_name(self, spreadsheet_name, sheet_name):
            """
            Lê uma planilha com o id pelo nome da aba

            Argumentos:
                spreadsheet_id (str): ID da planilha Google Sheets.
                sheet_name (str): Nome exato da aba/sheet

            Returns:
                pd.DataFrame: DataFrame com os dados da planilha

            Observação:
                - O spreadsheet_id é a parte do link que está entre o "d/{spreadsheet_id}/"
                Por exemplo:
                    https://docs.google.com/spreadsheets/d/1iztgt38QpdIoMbQguvnwwEMj_oh-F0viRuUVo6v2Uow/edit?gid=305230612#gid=305230612
                    spreadsheet_id = 1iztgt38QpdIoMbQguvnwwEMj_oh-F0viRuUVo6v2Uow
            """

            try:
                # Pega no .env o campo "LINK_GOOGLE_SHEET_XXXX"
                env_path = Path(__file__).parent.parent.parent / "lib" / ".env"
                load_dotenv(env_path)
                spreadsheet_id = os.getenv(spreadsheet_name)
                # Abre a planilha e a aba específica, criando um dataFrame
                spreadsheet = self.creds.open_by_key(spreadsheet_id)
                worksheet = spreadsheet.worksheet(sheet_name)

                # 
                return worksheet

            # Em caso de não encontrar a aba desejada, printa as disponíveis
            except gspread.WorksheetNotFound:
                available_sheets = [ws.title for ws in spreadsheet.worksheets()]
                raise ValueError(
                    f"Aba '{sheet_name}' não encontrada. "
                    f"Abas disponíveis: {', '.join(available_sheets)}"
                )
            # Em caso de erro ao acessar a planilha
            except Exception as e:
                raise Exception(f"Erro ao acessar a planilha: {str(e)}")
        
    def buscar_jogador(self, id=None, nome=None, contato=None):
        self.recarregar_dados()
        for i, registro in enumerate(self.registros, start=2):  # começa na linha 2
            if id is not None and str(registro.get("Id")) == str(id):
                return i, registro
            elif nome and contato:
                if (
                    str(registro.get("Nome")).strip().lower() == str(nome).strip().lower()
                    or str(registro.get("Contato (telegram/numero)")).strip() == str(contato).strip()
                ):                    
                    return i, registro
        return None, None  # não encontrado

    def atualizar_pontuacao(self, linha, coluna_pontos, coluna_timestamp, nova_pontuacao, horario, monitor):
        """Atualiza a pontuação e timestamp de uma linha existente"""
        self.planilha_alocacao.update_cell(linha, coluna_pontos, float(nova_pontuacao))
        self.planilha_alocacao.update_cell(linha, coluna_timestamp, f"{horario}")

    def addPlayer(self, id=None, nome=None, contato=None, jogo=None, pontuacao=None, monitor=None, horario=None):
        colunas_pontos = {
            "Touhou": "Pontuação (Touhou)",
            "Guitar Hero": "Pontuação (Guitar Hero)",
            "Chicken": "Pontuação (Chicken)",
            "Tetris": "Pontuação (Tetris)"
        }
        colunas_timestamp = {
            "Touhou": "Timestamp (Touhou)",
            "Guitar Hero": "Timestamp (Guitar Hero)",
            "Chicken": "Timestamp (Chicken)",
            "Tetris": "Timestamp (Tetris)"
        }

        coluna_pontos = colunas_pontos[jogo]
        coluna_timestamp = colunas_timestamp[jogo]
        cabecalho = self.planilha_alocacao.row_values(1)
        col_idx_pontos = cabecalho.index(coluna_pontos) + 1
        col_idx_timestamp = cabecalho.index(coluna_timestamp) + 1

        linha_existente, jogador_atual = self.buscar_jogador(id, nome, contato)

        try:
            nova_pontuacao = float(pontuacao)
        except ValueError:
            return f"❌ **Pontuação inválida:** `{pontuacao}`"

        if linha_existente:
            pontos_atuais = jogador_atual.get(coluna_pontos, 0) or 0
            try:
                pontos_atuais = float(pontos_atuais)
            except ValueError:
                pontos_atuais = 0.0

            if nova_pontuacao > pontos_atuais:
                self.atualizar_pontuacao(linha_existente, col_idx_pontos, col_idx_timestamp, nova_pontuacao, horario, monitor)
                return (
                    f"🏆 **Parabéns, {nome or jogador_atual.get('Nome')}!**\n"
                    f"🎮 Jogo: {jogo}\n"
                    f"⬆️ Pontos antigos: {pontos_atuais}\n"
                    f"✨ Pontos novos: {nova_pontuacao}\n"
                    f"🕒 Atualizado por @{monitor} às {horario}"
                )
            else:
                return (
                    f"⚠️ **Nada mudou para {nome or jogador_atual.get('Nome')}**\n"
                    f"🎮 Jogo: {jogo}\n"
                    f"Pontuação atual: {pontos_atuais}\n"
                    f"Tentativa de registro: {nova_pontuacao} (não foi suficiente para atualizar)"
                )
        else:
            novo_id = len(self.registros) + 1
            nova_linha = [novo_id, nome or "", contato or "", "", "", "", "", "", "", "", ""]
            nova_linha[col_idx_pontos - 1] = nova_pontuacao
            nova_linha[col_idx_timestamp - 1] = f"{horario}"
            self.planilha_alocacao.append_row(nova_linha)
            return (
                f"🆕 **Novo jogador registrado!**\n"
                f"🆔 ID: {novo_id}\n"
                f"👤 Nome: {nome}\n"
                f"📞 Contato: {contato}\n"
                f"🎮 Jogo: {jogo}\n"
                f"🏅 Pontuação inicial: {nova_pontuacao}\n"
                f"🕒 Registrado por @{monitor} às {horario}"
            )

    def ajustarPontuacao(self, id=None, nome=None, contato=None, jogo=None, nova_pontuacao=None, monitor=None, horario=None):
        linha_existente, jogador_atual = self.buscar_jogador(id, nome, contato)
        if not linha_existente:
            return f"❌ **Jogador não encontrado.**"

        colunas_pontos = {
            "Touhou": "Pontuação (Touhou)",
            "Guitar Hero": "Pontuação (Guitar Hero)",
            "Chicken": "Pontuação (Chicken)",
            "Tetris": "Pontuação (Tetris)"
        }
        colunas_timestamp = {
            "Touhou": "Timestamp (Touhou)",
            "Guitar Hero": "Timestamp (Guitar Hero)",
            "Chicken": "Timestamp (Chicken)",
            "Tetris": "Timestamp (Tetris)"
        }

        cabecalho = self.planilha_alocacao.row_values(1)
        coluna_pontos = colunas_pontos[jogo]
        coluna_timestamp = colunas_timestamp[jogo]
        col_idx_pontos = cabecalho.index(coluna_pontos) + 1
        col_idx_timestamp = cabecalho.index(coluna_timestamp) + 1

        if id is not None:
            if nome is not None and contato is not None:
                self.planilha_alocacao.update_cell(linha_existente, cabecalho.index("Nome") + 1, f"{nome}")
                self.planilha_alocacao.update_cell(linha_existente,  cabecalho.index("Contato (telegram/numero)") + 1, f"{contato}")

        self.atualizar_pontuacao(linha_existente, col_idx_pontos, col_idx_timestamp, nova_pontuacao, horario, monitor)

        return (
            f"🛠️ **Pontuação ajustada com sucesso!**\n"
            f"👤 Jogador: {nome or jogador_atual.get('Nome')}\n"
            f"🎮 Jogo: {jogo}\n"
            f"🏅 Nova pontuação: {nova_pontuacao}\n"
            f"🕒 Alterado manualmente por @{monitor} às {horario}"
        )
import threading
import time
import telebot
from src.modules.sheets import SheetsBot
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import pytz

class TelegramBot:
    def __init__(self):
        self.ativo = True
        self._setup_config()
        self._init_bot()
        self._register_handlers()

    def _setup_config(self):
        """Configura variáveis de ambiente e paths"""
        env_path = Path(__file__).parent.parent.parent / "lib" / ".env"
        load_dotenv(env_path)
        self.TOKEN = os.getenv("API_KEY_TELEGRAM")
        if not self.TOKEN:
            raise ValueError("API_KEY_TELEGRAM não encontrado. Verifique .env")

    def _init_bot(self):
        """Inicializa o bot e serviços auxiliares"""
        self.bot = telebot.TeleBot(self.TOKEN)
        self.sheets_bot = SheetsBot()
        self.planilha_alocacao = None
        self.planilha_membros = None

    def _register_handlers(self):
        """Registra todos os handlers de mensagens"""

        @self.bot.message_handler(commands=["info_mensagem"])
        def start_handler(message):
            self._handle_msg_info(message)

        @self.bot.message_handler(commands=["start"])
        def start_handler(message):
            self._handle_start(message)

        @self.bot.message_handler(commands=["help", "ajuda"])
        def help_handler(message):
            self._handle_help(message)

        @self.bot.message_handler(commands=["add"])
        def add_handler(message):
            self.sheets_bot.recarregar_dados()
            self._handle_add(message)

        @self.bot.message_handler(commands=["busca"])
        def busca_handler(message):
            self.sheets_bot.recarregar_dados()
            self._handle_busca(message)

        @self.bot.message_handler(commands=["ajuste"])
        def ajuste_handler(message):
            self.sheets_bot.recarregar_dados()
            self._handle_ajuste(message)

    def _handle_msg_info(self, message):
        try:
            print(message.forum_topic_created.name)
            # Informações básicas da mensagem
            tz_brasil = pytz.timezone("America/Sao_Paulo")
            data_hora = datetime.fromtimestamp(message.date, tz=pytz.utc).astimezone(
                tz_brasil
            )
            data_hora = data_hora.strftime("%d/%m/%Y %H:%M:%S")
            debug_info = (
                f"📝 *Informações da Mensagem* 📝\n"
                f"• *Conteúdo*: `{message.text if message.text else 'Sem texto'}`\n"
                f"• *Tipo de Chat*: `{message.chat.type}`\n"
                f"• *ID do Chat*: `{message.chat.id}`\n"
                f"• *ID da Mensagem*: `{message.message_id}`\n"
                f"• *Data/Hora*: `{data_hora}`\n"
            )

            # Informações do remetente
            if message.from_user:
                debug_info += (
                    f"\n👤 *Informações do Remetente* 👤\n"
                    f"• *ID*: `{message.from_user.id}`\n"
                    f"• *Nome*: `{message.from_user.first_name}`\n"
                    f"• *Sobrenome*: `{message.from_user.last_name if message.from_user.last_name else 'Não informado'}`\n"
                    f"• *Username*: @{message.from_user.username if message.from_user.username else 'Não informado'}\n"
                    f"• *É bot?*: {'Sim' if message.from_user.is_bot else 'Não'}\n"
                )

            # Informações adicionais para grupos/canais
            if message.chat.type in ["group", "supergroup", "channel"]:
                debug_info += (
                    f"\n👥 *Informações do Grupo/Canal* 👥\n"
                    f"• *Título*: `{message.chat.title}`\n"
                    f"• *Username*: @{message.chat.username if message.chat.username else 'Não informado'}\n"
                )

            # Entidades da mensagem (comandos, menções, etc)
            if message.entities:
                debug_info += "\n🔍 *Entidades na Mensagem* 🔍\n"
                for entity in message.entities:
                    entity_text = message.text[
                        entity.offset : entity.offset + entity.length
                    ]
                    debug_info += (
                        f"• *Tipo*: `{entity.type}`\n"
                        f"• *Texto*: `{entity_text}`\n"
                        f"• *Posição*: {entity.offset}-{entity.offset + entity.length}\n"
                    )

            # Envia a mensagem de debug formatada
            self.bot.reply_to(message, debug_info)

        except Exception as e:
            self.bot.reply_to(message, f"⚠️ Erro ao gerar debug: {str(e)}")

    def _handle_start(self, message):
        """Handler para o comando /start, imprimindo a mensagem de início do bot"""
        welcome_msg = (
            "Falaa, meu fii! Eu sou o Bot do Semcomp! "
            "Se quiser saber de algum comando, clique aqui -> /help\n"
        )
        self.bot.reply_to(message, welcome_msg)

    def _handle_help(self, message):
        """Handler para os comandos /help e /ajuda"""
        help_msg = (
            "📌 **Bot da Semcomp - Comandos Principais**\n\n"
            "⚠️ **ATENTE-SE ÀS VÍRGULAS**\n\n"
            "🎯 **Comando /add** – Adicionar pontos de jogadores\n"
            "Existem **3 formas de usar**:\n"
            "1️⃣ `/add id, nome, contato, pontuação`\n"
            "2️⃣ `/add nome, contato, pontuação`\n"
            "3️⃣ `/add id, pontuação`\n\n"
            "ℹ️ Observação: este comando **só aumenta a pontuação** se a nova for maior que a anterior. "
            "Então, use sempre que quiser registrar a tentativa do jogador.\n\n"
            "🔍 **Comando /busca** – Consulta informações do jogador na planilha\n\n"
            "🛠️ **Comando /ajuste** – Ajusta pontuação manualmente, caso algo dê errado"
    )
        self.bot.reply_to(message, help_msg)

    def _handle_add(self, message):
        texto = message.text.strip()
        if texto.startswith("/add"):
            texto = texto[4:].strip()  # remove o '/add' e possíveis espaços

        # Divide os argumentos por vírgula e remove espaços extras
        partes = [p.strip() for p in texto.split(",") if p.strip()]
        # print(partes)
        if len(partes) == 3:
            # /add nome, contato, pontuacao
            nome, contato, pontuacao = partes
            id_player = None

        elif len(partes) == 2:
            # /add id, pontuacao
            id_player, pontuacao = partes
            nome = contato = None

        elif len(partes) == 4:
            # /add id, nome, contato, pontuacao
            id_player, nome, contato, pontuacao = partes

        else:
            self.bot.reply_to(
                message,
                "⚠️ Use o comando no formato:\n"
                "`/add id, nome, contato, pontuação`\n"
                "`/add nome, contato, pontuação`\n"
                "`/add id, pontuação`"
            )
            return

        jogo = message.reply_to_message.forum_topic_created.name
        monitor = message.from_user.username

        tz_brasil = pytz.timezone("America/Sao_Paulo")
        data_hora = datetime.fromtimestamp(message.date, tz=pytz.utc).astimezone(tz_brasil)
        data_hora = data_hora.strftime("%d/%m/%Y %H:%M:%S")

        resposta = self.sheets_bot.addPlayer(id_player, nome, contato, jogo, pontuacao, monitor, data_hora)
        self.bot.reply_to(message,resposta)

    def _handle_busca(self, message):
        texto = message.text.strip()
        if texto.startswith("/busca"):
            texto = texto[6:].strip()  # remove o '/busca'

        partes = [p.strip() for p in texto.split(",") if p.strip()]

        if len(partes) == 1:
            id_player = partes[0]
            nome = contato = None
        elif len(partes) == 2:
            nome, contato = partes
            id_player = None
        else:
            self.bot.reply_to(message, "⚠️ Formato: `/busca id` ou `/busca nome, contato`")
            return

        linha, jogador = self.sheets_bot.buscar_jogador(id_player, nome, contato)

        if not jogador:
            self.bot.reply_to(message, "❌ Jogador não encontrado.")
            return

        msg = (
            f"🏆 **Jogador encontrado na linha {linha}:**\n"
            f"🆔 ID: {jogador.get('Id')}\n"
            f"👤 Nome: {jogador.get('Nome')}\n"
            f"📞 Contato: {jogador.get('Contato (telegram/numero)')}\n\n"
            f"🎮 **Pontuações:**\n"
            f"• Touhou: {jogador.get('Pontuação (Touhou)') or '0'} às {jogador.get('Timestamp (Touhou)') or '-'}\n"
            f"• Guitar Hero: {jogador.get('Pontuação (Guitar Hero)') or '0'}  às {jogador.get('Timestamp (Guitar Hero)') or '-'}\n"
            f"• Chicken: {jogador.get('Pontuação (Chicken)') or '0'} às {jogador.get('Timestamp (Chicken)') or '-'}\n"
            f"• Tetris: {jogador.get('Pontuação (Tetris)') or '0'} às {jogador.get('Timestamp (Tetris)') or '-'}\n"
        )

        self.bot.reply_to(message, msg)



    def _handle_ajuste(self, message):
        texto = message.text.strip()
        if texto.startswith("/ajuste"):
            texto = texto[7:].strip()

        partes = [p.strip() for p in texto.split(",") if p.strip()]

        if len(partes) == 2:
            id_player, pontuacao = partes
            nome = contato = None
        elif len(partes) == 3:
            nome, contato, pontuacao = partes
            id_player = None
        elif len(partes) == 4:
            id_player, nome, contato, pontuacao = partes
        else:
            self.bot.reply_to(message, "⚠️ Formato: `/ajuste id, pontuação` ou `/ajuste nome, contato, pontuação` ou `/ajuste id, nome, contato, pontuacao`")
            return

        jogo = message.reply_to_message.forum_topic_created.name
        monitor = message.from_user.username

        tz_brasil = pytz.timezone("America/Sao_Paulo")
        data_hora = datetime.fromtimestamp(message.date, tz=pytz.utc).astimezone(tz_brasil)
        data_hora = data_hora.strftime("%d/%m/%Y %H:%M:%S")

        resposta = self.sheets_bot.ajustarPontuacao(id_player, nome, contato, jogo, pontuacao, monitor, data_hora)
        self.bot.reply_to(message, resposta)


    def start(self):
        """Inicia o bot e o monitor de comandos"""
        # threading.Thread(target=self._monitorar_comando, daemon=True).start()

        while self.ativo:
            try:
                print("Bot está ativo!")
                self.bot.polling()
            except requests.exceptions.ReadTimeout:
                print("Erro de timeout. Reiniciando...")
                time.sleep(5)
            except Exception as e:
                print(f"Erro inesperado: {e}. Reiniciando...")
                time.sleep(5)

    # def _monitorar_comando(self):
    #     """Monitora o terminal por comandos de parada"""
    #     while self.ativo:
    #         if input("Digite '#' para parar: ").strip().lower() == "#":
    #             print("Encerrando bot...")
    #             self.ativo = False
    #             self.bot.stop_polling()
    #             break
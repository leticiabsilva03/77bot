# cogs/reports_cog.py
import discord
from discord import app_commands
from discord.ext import commands, tasks
import gspread
import pandas as pd
from datetime import datetime, timedelta
import logging
from config import CONFIG # Importa a configuração central

# --- CONFIGURAÇÕES ---
SERVICE_ACCOUNT_FILE = 'credentials/bot-integration-464319-78fb375d86ee.json'
SPREADSHEET_NAME = 'CONTROLE PRESENÇA'
WORKSHEET_NAMES = [cat_config["worksheet_name"] for cat_config in CONFIG.values()]

# --- FUNÇÃO AUXILIAR ---
def get_data_as_dataframe(worksheet_name: str) -> pd.DataFrame:
    """Busca dados de uma aba específica de forma robusta e retorna como um DataFrame pandas."""
    try:
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
        sh = gc.open(SPREADSHEET_NAME)
        worksheet = sh.worksheet(worksheet_name)
        
        all_values = worksheet.get_all_values()
        
        if len(all_values) < 2:
            return pd.DataFrame()

        headers = ['DIA', 'EVENTO', 'HORA', 'NICK']
        raw_data = all_values[1:]
        data = [row[:4] for row in raw_data]
        
        df = pd.DataFrame(data, columns=headers)
        
        df['DIA'] = pd.to_datetime(df['DIA'], format='%d/%m/%Y', errors='coerce')
        df.dropna(subset=['DIA'], inplace=True)
        return df
    except Exception as e:
        logging.error(f"Erro ao buscar dados da aba '{worksheet_name}': {e}")
        return pd.DataFrame()

# --- COG DE RELATÓRIOS ---
class ReportsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # O cache começa vazio e será populado no on_ready
        self.player_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """Este evento é chamado quando o Cog está pronto."""
        await self.populate_initial_cache()

    async def populate_initial_cache(self):
        """Popula o cache de jogadores uma vez na inicialização do bot."""
        logging.info("A popular o cache inicial de jogadores para o autocomplete...")
        for server_name in WORKSHEET_NAMES:
            df = get_data_as_dataframe(server_name)
            if not df.empty:
                self.player_cache[server_name] = df['NICK'].dropna().unique().tolist()
        logging.info("Cache inicial de jogadores populado com sucesso.")

    def clear_player_cache(self):
        """Limpa o cache de jogadores (chamado pela tarefa diária)."""
        logging.info("A limpar o cache de jogadores do autocomplete.")
        self.player_cache.clear()

    def add_player_to_cache(self, server_name: str, player_name: str):
        """Adiciona um novo jogador ao cache em memória dinamicamente."""
        if server_name not in self.player_cache:
            self.player_cache[server_name] = []

        if player_name not in self.player_cache[server_name]:
            self.player_cache[server_name].append(player_name)
            logging.info(f"Jogador '{player_name}' adicionado dinamicamente ao cache de autocomplete para '{server_name}'.")

    async def player_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        server_choice = interaction.namespace.servidor
        if not server_choice or server_choice not in self.player_cache:
            return []
            
        all_nicks = self.player_cache[server_choice]
        
        return [
            app_commands.Choice(name=nick, value=nick)
            for nick in all_nicks if nick and current.lower() in nick.lower()
        ][:25]

    @app_commands.command(name="presenca", description="Verifica a presença detalhada de um jogador.")
    @app_commands.describe(servidor="Escolha a divisão/servidor.", jogador="Comece a digitar o nick do jogador.")
    @app_commands.choices(servidor=[app_commands.Choice(name=name, value=name) for name in WORKSHEET_NAMES])
    @app_commands.autocomplete(jogador=player_autocomplete)
    @app_commands.default_permissions(administrator=True) # <-- MUDANÇA APLICADA AQUI
    async def presenca(self, interaction: discord.Interaction, servidor: str, jogador: str):
        await interaction.response.defer(ephemeral=True)
        
        df = get_data_as_dataframe(servidor)
        if df.empty:
            await interaction.followup.send(f"Não há dados de presença para a divisão '{servidor}'.", ephemeral=True)
            return

        today = datetime.now()
        start_of_week = (today - timedelta(days=(today.weekday() + 1) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=6)
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        player_df = df[df['NICK'].str.lower() == jogador.lower()]
        if player_df.empty:
            await interaction.followup.send(f"Nenhum registro encontrado para o jogador '{jogador}' na divisão '{servidor}'.", ephemeral=True)
            return

        weekly_player_df = player_df[player_df['DIA'] >= start_of_week]
        wb_semanal = weekly_player_df[weekly_player_df['EVENTO'].str.contains("WB", na=False)].shape[0]
        pico_praca_semanal = weekly_player_df[weekly_player_df['EVENTO'].str.contains("Pico|Praça", na=False)].shape[0]

        monthly_player_df = player_df[player_df['DIA'] >= start_of_month]
        wb_mensal = monthly_player_df[monthly_player_df['EVENTO'].str.contains("WB", na=False)].shape[0]
        eventos_mensal = monthly_player_df[~monthly_player_df['EVENTO'].str.contains("WB|Pico|Praça", na=False)].shape[0]

        meses = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        nome_mes = meses[today.month]

        embed = discord.Embed(title=f"📊 Relatório de Presença - {jogador}", description=f"Dados da divisão: **{servidor}**", color=discord.Color.blue())
        embed.add_field(name="WB (Semanal)", value=f"`{wb_semanal}/35`", inline=True)
        embed.add_field(name="Praça/Pico (Semanal)", value=f"`{pico_praca_semanal}/56`", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="WB (Mensal)", value=f"`{wb_mensal}` presenças", inline=True)
        embed.add_field(name="Eventos (Mensal)", value=f"`{eventos_mensal}` presenças", inline=True)
        
        semana_str = f"{start_of_week.strftime('%d/%m')} a {end_of_week.strftime('%d/%m')}"
        embed.set_footer(text=f"Semana: {semana_str} | Mês: {nome_mes} de {today.year}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="presencas", description="Mostra os rankings de presença para uma divisão.")
    @app_commands.describe(servidor="Escolha a divisão/servidor para ver os rankings.")
    @app_commands.choices(servidor=[app_commands.Choice(name=name, value=name) for name in WORKSHEET_NAMES])
    @app_commands.default_permissions(administrator=True) # <-- MUDANÇA APLICADA AQUI
    async def presencas(self, interaction: discord.Interaction, servidor: str):
        await interaction.response.defer(ephemeral=True)
        
        df = get_data_as_dataframe(servidor)
        if df.empty:
            await interaction.followup.send(f"Não há dados de presença para a divisão '{servidor}'.", ephemeral=True)
            return

        today = datetime.now()
        start_of_week = (today - timedelta(days=(today.weekday() + 1) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=6)
        weekly_df = df[df['DIA'] >= start_of_week]

        top_10_wb = weekly_df[weekly_df['EVENTO'].str.contains("WB", na=False)]['NICK'].value_counts().nlargest(10)
        top_10_pico_praca = weekly_df[weekly_df['EVENTO'].str.contains("Pico|Praça", na=False)]['NICK'].value_counts().nlargest(10)
        top_10_eventos = weekly_df[~weekly_df['EVENTO'].str.contains("WB|Pico|Praça", na=False)]['NICK'].value_counts().nlargest(10)

        semana_str = f"{start_of_week.strftime('%d/%m')} a {end_of_week.strftime('%d/%m')}"
        embed = discord.Embed(
            title=f"🏆 Rankings de Presença - {servidor}",
            description=f"**Período Semanal:** {semana_str}",
            color=discord.Color.gold()
        )
        
        wb_text = "\n".join([f"{i}. **{name}** (`{count}`)" for i, (name, count) in enumerate(top_10_wb.items(), 1)]) or "Nenhum registro."
        pico_praca_text = "\n".join([f"{i}. **{name}** (`{count}`)" for i, (name, count) in enumerate(top_10_pico_praca.items(), 1)]) or "Nenhum registro."
        eventos_text = "\n".join([f"{i}. **{name}** (`{count}`)" for i, (name, count) in enumerate(top_10_eventos.items(), 1)]) or "Nenhum registro."

        embed.add_field(name="WB (Top 10)", value=wb_text, inline=True)
        embed.add_field(name="Praça/Pico (Top 10)", value=pico_praca_text, inline=True)
        embed.add_field(name="Eventos (Top 10)", value=eventos_text, inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReportsCog(bot))

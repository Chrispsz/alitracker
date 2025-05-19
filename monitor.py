import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

class TelegramBot:
    def _init_(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        
    def send_message(self, text):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

class PriceMonitor:
    def _init_(self, bot):
        self.bot = bot
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.last_price = None

    def extract_price(self, html):
        try:
            # Tenta encontrar o preço na página
            soup = BeautifulSoup(html, 'html.parser')
            # Procura por padrões de preço comuns
            price_pattern = re.compile(r'US\s*\$\s*(\d+\.?\d*)')
            text = soup.get_text()
            match = price_pattern.search(text)
            if match:
                return float(match.group(1))
            return None
        except Exception as e:
            print(f"Erro ao extrair preço: {e}")
            return None

    def check_price(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            now = datetime.now()
            
            price = self.extract_price(response.text)
            
            message = f"🕒 Horário: {now.strftime('%d/%m/%Y %H:%M:%S')}\n"
            message += f"🔗 Produto: {url}\n"
            
            if price:
                message += f"💰 Preço: US$ {price:.2f}\n"
                
                if self.last_price:
                    diff = price - self.last_price
                    if diff != 0:
                        emoji = "📈" if diff > 0 else "📉"
                        message += f"{emoji} Variação: US$ {abs(diff):.2f} "
                        message += "mais caro\n" if diff > 0 else "mais barato\n"
                
                self.last_price = price
            else:
                message += "❌ Não foi possível extrair o preço\n"
            
            self.bot.send_message(message)
            
            with open('price_log.txt', 'a') as f:
                f.write(f"{message}\n---\n")
                
        except Exception as e:
            error_msg = f"❌ Erro: {e}"
            self.bot.send_message(error_msg)
            print(error_msg)

def main():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = os.environ.get('PRODUCT_URL')
    
    bot = TelegramBot(token, chat_id)
    monitor = PriceMonitor(bot)
    
    while True:
        monitor.check_price(url)
        time.sleep(30)  # 1 hora

if _name_ == "_main_":
    main()

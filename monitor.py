import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import os

class TelegramBot:
    def __init__(self, token, chat_id):
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
    def __init__(self, bot):
        self.bot = bot
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def check_price(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            now = datetime.now()
            message = f"🔍 Verificação: {now}\n"
            message += f"🔗 URL: {url}\n"
            
            self.bot.send_message(message)
            
            with open('price_log.txt', 'a') as f:
                f.write(f"{now}: Verificação realizada\n")
                
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
        time.sleep(3600)  # 1 hora

if __name__ == "__main__":
    main()

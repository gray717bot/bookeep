import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class PrizeManager:
    """
    負責從「財政部稅務入口網」抓取中獎號碼並進行對獎
    """
    def __init__(self):
        self.url = "https://invoice.etax.nat.gov.tw/"
        self.winning_numbers = {} # { 'period': { 'special': '...', 'grand': '...', 'first': [...] } }

    def fetch_winning_numbers(self):
        """
        爬取官方網頁獲取最新兩期的中獎號碼
        """
        try:
            response = requests.get(self.url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 定義開獎區塊
            # 官方頁面通常有「本期」與「上期」
            periods = soup.find_all('h2', class_='etw-period')
            tables = soup.find_all('table', class_='etw-table-bg')
            
            for i in range(min(len(periods), 2)):
                period_text = periods[i].get_text(strip=True) # 例如 "112年11-12月"
                # 轉為 YYYY-MM 格式供簡化比較 (這裡簡化處理)
                
                rows = tables[i].find_all('tr')
                data = {
                    'special': rows[1].find('span', class_='etw-color-red').get_text(strip=True), # 特別獎
                    'grand': rows[2].find('span', class_='etw-color-red').get_text(strip=True),   # 特獎
                    'first': [n.strip() for n in rows[3].get_text().split('\n') if len(n.strip()) == 8] # 頭獎 (多組)
                }
                self.winning_numbers[period_text] = data
            return True
        except Exception as e:
            print(f"Fetch Prize Error: {e}")
            return False

    def check_prize(self, invoice_number):
        """
        對獎邏輯 (傳入 8 位數字字串)
        回傳: (是否中獎, 獎項名稱)
        """
        if not self.winning_numbers:
            self.fetch_winning_numbers()
        
        # 遍歷目前抓到的所有期別 (通常是最近兩期)
        for period, numbers in self.winning_numbers.items():
            # 1. 特別獎 (全中) 1000萬
            if invoice_number == numbers['special']:
                return True, "🎉 1000萬 (特別獎)！太強了！"
            
            # 2. 特獎 (全中) 200萬
            if invoice_number == numbers['grand']:
                return True, "🎊 200萬 (特獎)！恭喜！"
            
            # 3. 頭獎及其他獎 (從末位開始比)
            for first in numbers['first']:
                if invoice_number == first:
                    return True, "💰 20萬元 (頭獎)！"
                if invoice_number[-7:] == first[-7:]:
                    return True, "💰 4萬元 (二獎)！"
                if invoice_number[-6:] == first[-6:]:
                    return True, "💰 1萬元 (三獎)！"
                if invoice_number[-5:] == first[-5:]:
                    return True, "💰 4千元 (四獎)！"
                if invoice_number[-4:] == first[-4:]:
                    return True, "💰 1千元 (五獎)！"
                if invoice_number[-3:] == first[-3:]:
                    return True, "🧧 200元 (六獎)！"
                    
        return False, "再接再厲，下一張就會中！💪"

prize_manager = PrizeManager()

if __name__ == "__main__":
    pm = PrizeManager()
    if pm.fetch_winning_numbers():
        print("最新期別:", list(pm.winning_numbers.keys())[0])
        print("號碼預覽:", pm.winning_numbers[list(pm.winning_numbers.keys())[0]])

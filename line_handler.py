from datetime import datetime
from linebot.models import FlexSendMessage, BubbleContainer, BoxComponent, TextComponent, ButtonComponent, SeparatorComponent

class LineHandler:
    @staticmethod
    def parse_message(text):
        """
        解析訊息，例如：
        「早餐 100」-> category="早餐", amount=100
        「100 晚餐」-> category="晚餐", amount=100
        「午餐 150 今天很熱」-> category="午餐", amount=150, note="今天很熱"
        """
        # 尋找數字 (金額)
        amount_match = re.search(r'\d+', text)
        if not amount_match:
            return None
        
        amount = int(amount_match.group())
        
        # 移除數字後的剩餘文字作為類別與備註
        parts = text.replace(str(amount), '').split()
        category = parts[0] if len(parts) > 0 else "未分類"
        note = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": category,
            "amount": amount,
            "note": note
        }
    @staticmethod
    def get_flex_message(record):
        """
        將記帳紀錄轉換為漂亮的 Flex Message
        """
        category = record.get('category', '未分類')
        amount = str(record.get('amount', 0))
        note = record.get('note', '')
        date = record.get('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        bubble = BubbleContainer(
            direction='ltr',
            header=BoxComponent(
                layout='vertical',
                background_color='#1DB446',
                contents=[
                    TextComponent(text='記帳成功', weight='bold', size='lg', color='#ffffff', align='center')
                ]
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=f'NT$ {amount}', weight='bold', size='xxl', margin='md', align='center'),
                    SeparatorComponent(margin='md'),
                    BoxComponent(
                        layout='vertical',
                        margin='md',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    TextComponent(text='類別', size='sm', color='#555555', flex=1),
                                    TextComponent(text=category, size='sm', color='#111111', align='end', flex=4)
                                ]
                            ),
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    TextComponent(text='備註', size='sm', color='#555555', flex=1),
                                    TextComponent(text=note if note else '-', size='sm', color='#111111', align='end', flex=4)
                                ]
                            ),
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    TextComponent(text='時間', size='sm', color='#555555', flex=1),
                                    TextComponent(text=date, size='sm', color='#111111', align='end', flex=4)
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        return FlexSendMessage(alt_text=f"記帳成功: {category} {amount}元", contents=bubble)

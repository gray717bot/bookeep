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
    def get_batch_summary_flex(records):
        """
        生成批次記帳成功的彙總卡片
        """
        count = len(records)
        total = sum(float(r.get('amount', 0)) for r in records)
        
        # 建立前 5 筆預覽
        preview_rows = []
        for r in records[:5]:
            preview_rows.append(
                BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(text=f"• {r.get('category')}", size='xs', color='#888888', flex=1),
                        TextComponent(text=f"{r.get('amount')}元", size='xs', color='#555555', align='end', flex=2)
                    ]
                )
            )
        if count > 5:
            preview_rows.append(TextComponent(text=f"...以及其他 {count-5} 筆交易", size='xxs', color='#AAAAAA', align='center', margin='sm'))

        bubble = BubbleContainer(
            direction='ltr',
            header=BoxComponent(
                layout='vertical',
                background_color='#FFB2B2',
                padding_all='20px',
                contents=[
                    TextComponent(text='📝 批次記帳成功 📝', weight='bold', size='md', color='#ffffff', align='center')
                ]
            ),
            body=BoxComponent(
                layout='vertical',
                padding_all='20px',
                contents=[
                    TextComponent(text='總計匯入筆數', size='xs', color='#AAAAAA', align='center'),
                    TextComponent(text=f'{count} 筆', weight='bold', size='xl', color='#FF6B6B', align='center', margin='xs'),
                    TextComponent(text=f'總金額：NT$ {total}', size='sm', color='#FF8888', align='center', margin='xs'),
                    SeparatorComponent(margin='xl', color='#FFEEEE'),
                    TextComponent(text='資料預覽：', size='xs', weight='bold', margin='md', color='#888888'),
                    BoxComponent(
                        layout='vertical',
                        margin='sm',
                        spacing='xs',
                        contents=preview_rows
                    )
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='已成功同步至 Google Sheets！✨', size='xxs', color='#FFB2B2', align='center', margin='md')
                ]
            )
        )
        return FlexSendMessage(alt_text=f"📝 批次記帳成功！共 {count} 筆", contents=bubble)

    @staticmethod
    def get_summary_flex(summary_data):
        """
        生成統計報表的 Flex Message
        """
        title = summary_data.get('title', '消費月報')
        month = summary_data.get('month')
        total = summary_data.get('total')
        count = summary_data.get('count')
        cat_details = summary_data.get('category_details', {})

        # 建立類別列表組件
        cat_rows = []
        for cat, amt in cat_details.items():
            cat_rows.append(
                BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(text=cat, size='sm', color='#555555', flex=1),
                        TextComponent(text=f'{amt} 元', size='sm', color='#111111', align='end', flex=4)
                    ]
                )
            )

        bubble = BubbleContainer(
            direction='ltr',
            header=BoxComponent(
                layout='vertical',
                background_color='#1DB446',
                contents=[
                    TextComponent(text=title, weight='bold', size='lg', color='#ffffff', align='center')
                ]
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='總支出金額', size='xs', color='#AAAAAA', align='center'),
                    TextComponent(text=f'NT$ {total}', weight='bold', size='xxl', margin='md', align='center', color='#1DB446'),
                    SeparatorComponent(margin='xl'),
                    TextComponent(text='類別統計明細', size='sm', weight='bold', margin='lg', color='#555555'),
                    BoxComponent(
                        layout='vertical',
                        margin='md',
                        spacing='sm',
                        contents=cat_rows
                    ),
                    SeparatorComponent(margin='xl'),
                    BoxComponent(
                        layout='horizontal',
                        margin='md',
                        contents=[
                            TextComponent(text='總計筆數', size='xs', color='#AAAAAA', flex=1),
                            TextComponent(text=f'{count} 筆', size='xs', color='#AAAAAA', align='end', flex=4)
                        ]
                    )
                ]
            )
        )
        return FlexSendMessage(alt_text=f"{month} 消費月報", contents=bubble)

    @staticmethod
    def get_flex_message(record):
        """
        將記帳紀錄轉換為超可愛的 Flex Message
        """
        category = record.get('category', '未分類')
        amount = str(record.get('amount', 0))
        note = record.get('note', '')
        date = record.get('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # 根據金額給予不同的小評價 (讓它更有趣)
        comment = "省錢小達人！✨" if int(amount) < 100 else "花錢有理，記帳萬歲！🎈"

        bubble = BubbleContainer(
            direction='ltr',
            header=BoxComponent(
                layout='vertical',
                background_color='#FFB2B2',  # 奶油粉紅色
                padding_all='20px',
                contents=[
                    TextComponent(text='🌸 記帳漂亮成功 🌸', weight='bold', size='md', color='#ffffff', align='center')
                ]
            ),
            body=BoxComponent(
                layout='vertical',
                padding_all='20px',
                contents=[
                    # 大大圓圓的金額顯示
                    BoxComponent(
                        layout='vertical',
                        background_color='#FFF0F0',
                        border_radius='20px',
                        padding_all='15px',
                        contents=[
                            TextComponent(text=f'NT$ {amount}', weight='bold', size='xxl', color='#FF6B6B', align='center'),
                            TextComponent(text=comment, size='xs', color='#FFAAAA', align='center', margin='sm')
                        ]
                    ),
                    BoxComponent(
                        layout='vertical',
                        margin='xl',
                        spacing='md',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    TextComponent(text='🐾 類別', size='sm', color='#888888', flex=1),
                                    TextComponent(text=category, size='sm', color='#555555', align='end', flex=4, weight='bold')
                                ]
                            ),
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    TextComponent(text='📝 備註', size='sm', color='#888888', flex=1),
                                    TextComponent(text=note if note else '無', size='sm', color='#555555', align='end', flex=4)
                                ]
                            ),
                            SeparatorComponent(margin='md', color='#FFEEEE'),
                            BoxComponent(
                                layout='horizontal',
                                margin='md',
                                contents=[
                                    TextComponent(text='⏰ 時間', size='xs', color='#AAAAAA', flex=1),
                                    TextComponent(text=date, size='xs', color='#AAAAAA', align='end', flex=4)
                                ]
                            )
                        ]
                    )
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='繼續保持唷！加油！🍰', size='xs', color='#FFB2B2', align='center', margin='md')
                ]
            )
        )
        return FlexSendMessage(alt_text=f"🌸 記帳成功囉！花了 {amount} 元", contents=bubble)

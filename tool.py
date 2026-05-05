import aiohttp
import asyncio
import g4f


class Ozon_tool:
    def __init__(self, today, kolvo_rub, val):
        self.today = today
        self.kolvo_rub = kolvo_rub
        self.val = val
    
    def calc(self): #калькулятор валют
        result = 0
        if self.kolvo_rub.isdigit():
            self.kolvo_rub = int(self.kolvo_rub)
            result = round(self.kolvo_rub / self.today, 2)
        return f"{self.kolvo_rub}₽  = {result} {self.val}"
    
class Valute_Manager:
    def __init__(self, val_code):
        self.url = 'https://www.cbr-xml-daily.ru/daily_json.js'
        self.kurs = None
        self.val_code = val_code
        
    async def get_info(self):   #получаем огромный словарь с валютами
        async with aiohttp.ClientSession() as session: #создаем сессию
            try:
                async with session.get(self.url, timeout=10) as response: #создаем запрос
                    if response.status == 200:
                        self.kurs = await response.json(content_type=None)
                        return self.kurs
            except aiohttp.ClientError as e:
                return(f"Ошибка {e}. Сообщите об ошибке по почте \namiyume@gmail.com")
            except asyncio.TimeoutError:
                return('Упс...\nЧто-то с сайтом РФ ЦБ. Сообщите об ошибке по почте \namiyume@gmail.com')
                
            
    async def get_need_info(self):
        if not self.kurs: #проверка 1
            await self.get_info() 
            
        if self.kurs is None: #проверка 2
            return 0, 0
            
        valute_data = self.kurs["Valute"][self.val_code]
        nominal = valute_data['Nominal']
        today = valute_data['Value'] / nominal
        yesterday = valute_data['Previous'] / nominal
        today = round(today * 1.02, 2)
        yesterday = round(yesterday * 1.02, 2)
        #комиссия 2%
        return today, yesterday

        


class AI_Assistant:
    def __init__(self):
        self.model = g4f.models.gpt_4o_mini 
        self.last_request_time = 0

    async def get_answer(self, prompt):
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_request_time < 20:
            return "⏳ Подождите еще немного перед следующим прогнозом (защита от спама)."

        try:
            client = g4f.client.AsyncClient()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            self.last_request_time = asyncio.get_event_loop().time()
            answer = response.choices[0].message.content
            
            if answer:
                if "Need proxies" in answer:
                    answer = answer.split("Need proxies")[0]
                return answer.strip()
            return "🤖 Облако временно не отвечает."
                
        except Exception as e:
            if "rate_limit" in str(e).lower() or "RetryProvider" in str(e):
                return "🤖 Серверы ИИ немного устали. Попробуйте нажать кнопку через 30-60 секунд."
            return "🤖 Ошибка связи с облаком. Повторите попытку позже."
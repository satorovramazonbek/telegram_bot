import logging
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = '7453422613:AAEN3KRm8EiT1c4ogTljgss0ZhG1h5rRYv4'
CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"

# Loggingni sozlaymiz
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Reply tugmalarni yaratish
menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
btn_usd = KeyboardButton("💵 Dollar kursi")
btn_eur = KeyboardButton("💶 Yevro kursi")
btn_rub = KeyboardButton("🇷🇺 Rubl kursi") # Qo'shimcha rubl tugmasi
menu_keyboard.add(btn_usd, btn_eur, btn_rub)


# /start komandasi uchun handler
@dp.message_handler(commands=['start', 'help'])
async def start_cmd(message: types.Message):
    await message.reply(
        "Markaziy Bank (CBU) valyuta botiga xush kelibsiz!\n"
        "Kursni bilish uchun quyidagi tugmalardan birini bosing:",
        reply_markup=menu_keyboard
    )


# Tugmalar bosilganda ishlovchi handler
@dp.message_handler(lambda message: message.text in ["💵 Dollar kursi", "💶 Yevro kursi", "🇷🇺 Rubl kursi"])
async def get_cbu_currency(message: types.Message):
    # Foydalanuvchi tanloviga qarab qidiriladigan kodni aniqlaymiz
    if "Dollar" in message.text:
        target_ccy = "USD"
    elif "Yevro" in message.text:
        target_ccy = "EUR"
    else:
        target_ccy = "RUB"
    
    # Asinxron so'rov yuboramiz
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(CBU_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # API'dan kelgan massiv ichidan kerakli valyutani qidiramiz
                    for item in data:
                        if item["Ccy"] == target_ccy:
                            name = item["CcyNm_UZ"]
                            rate = item["Rate"]
                            diff = item["Diff"]
                            date = item["Date"]
                            
                            # O'zgarish musbat yoki manfiyligiga qarab belgi qo'yamiz
                            # diff satr (string) ko'rinishida kelgani uchun uni float ga o'giramiz
                            arrow = "🔺" if float(diff) >= 0 else "🔻"
                            
                            text = (
                                f"🏛 **Markaziy Bank rasmiy kursi**\n"
                                f"📅 Sana: {date}\n\n"
                                f"💱 {name}: **{rate}** so'm\n"
                                f"{arrow} O'zgarish: {diff} so'm"
                            )
                            
                            await message.answer(text, parse_mode="Markdown")
                            return
                else:
                    await message.answer(f"Markaziy Bank serverida xatolik. Status kod: {response.status}")
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")
            await message.answer("API so'rovida texnik xatolik yuz berdi.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from pydub import AudioSegment

# TOKENNI TO'G'RIDAN-TO'G'RI O'ZGARUVCHIDAN OLAMIZ
TOKEN = os.getenv("BOT_TOKEN")

# Agar token topilmasa, botni ishga tushirmaslik
if not TOKEN:
    print("XATOLIK: BOT_TOKEN o'zgaruvchisi topilmadi!")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def change_voice(input_path, output_path):
    sound = AudioSegment.from_file(input_path)
    # Ovozni baland (sincap) qilish uchun frame_rate ni oshiramiz
    new_sample_rate = int(sound.frame_rate * 1.5)
    altered_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    altered_sound = altered_sound.set_frame_rate(sound.frame_rate)
    altered_sound.export(output_path, format="ogg", codec="libopus")

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salom! Menga ovozli xabar yoki musiqa yuboring.")

@dp.message(F.voice | F.audio)
async def handle_audio(message: types.Message):
    msg = await message.answer("Ishlov berilmoqda...")
    
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(file_id)
    
    input_file = f"in_{file_id}.ogg"
    output_file = f"out_{file_id}.ogg"
    
    await bot.download_file(file.file_path, input_file)
    
    try:
        change_voice(input_file, output_file)
        voice_file = types.FSInputFile(output_file)
        await message.answer_voice(voice=voice_file)
    except Exception as e:
        await message.answer(f"Xatolik: {e}")
    finally:
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(output_file): os.remove(output_file)
        await msg.delete()

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

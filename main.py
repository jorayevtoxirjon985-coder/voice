import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from pydub import AudioSegment


# Railway Variables'dan o'qiydi
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ovozni o'zgartirish funksiyasi
def change_voice(input_path, output_path):
    sound = AudioSegment.from_file(input_path)
    
    # Ovozni o'zgartirish (masalan: tezlikni oshirish - robot yoki sincap ovozi)
    # 1.2 koeffitsient ovozni balandroq va tezroq qiladi
    new_sample_rate = int(sound.frame_rate * 1.5)
    altered_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    altered_sound = altered_sound.set_frame_rate(sound.frame_rate)
    
    altered_sound.export(output_path, format="ogg", codec="libopus")

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salom! Menga ovozli xabar yoki musiqa yuboring, men uni o'zgartirib beraman!")

@dp.message(F.voice | F.audio)
async def handle_audio(message: types.Message):
    msg = await message.answer("Ovoz qayta ishlanmoqda, kuting...")
    
    # Faylni yuklab olish
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(file_id)
    input_file = f"input_{file_id}.ogg"
    output_file = f"output_{file_id}.ogg"
    
    await bot.download_file(file.file_path, input_file)
    
    try:
        # Ovozni o'zgartirish
        change_voice(input_file, output_file)
        
        # Yuborish
        voice_file = types.FSInputFile(output_file)
        await message.answer_voice(voice=voice_file, caption="O'zgartirilgan ovoz!")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")
    finally:
        # Fayllarni o'chirish
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(output_file): os.remove(output_file)
        await msg.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

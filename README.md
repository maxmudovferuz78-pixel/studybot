# Mustaqil ish / Referat bot

## O'rnatish

```bash
pip install -r requirements.txt
```

## Sozlash

`config.py` faylida yoki muhit o'zgaruvchilari orqali:

```bash
export BOT_TOKEN="123456:AAExample-BotFatherdan-olingan-token"
export OPENAI_API_KEY="sk-...sizning-openai-keyingiz..."
```

## Ishga tushirish

```bash
python bot.py
```

## Ishlash tartibi

1. Foydalanuvchi "Yangi Mustaqil ish" yoki "Yangi Referat" tugmasini bosadi.
2. Mavzu, ism-familiya, universitet, guruh, o'qituvchi ma'lumotlari so'raladi.
3. Reja bo'limlari soni tugmalar orqali tanlanadi: **3 / 4 / 5**.
4. Hujjat hajmi tugmalar orqali tanlanadi: **10-15 / 15-20 / 20-25** varoq.
5. `ai_service.py` OpenAI (`gpt-4o-mini`) orqali:
   - avval reja (bo'lim nomlari) generatsiya qilinadi,
   - so'ng har bir bo'lim (Kirish, bo'limlar, Xulosa) parallel generatsiya qilinadi.
6. `doc_generator.py` natijani titul varag'i + reja + matn bilan Word (.docx) fayliga joylaydi.
7. Tayyor fayl foydalanuvchiga yuboriladi.

## Keyingi bosqichlar (pullik versiya uchun)

- Baza (PostgreSQL/SQLite) qo'shib, foydalanuvchi balansi/limitini saqlash.
- Bepul foydalanuvchilar uchun oyiga N ta hujjat limiti qo'yish (`config.py` dagi `FREE_MODE` shu yerda ishlatiladi).
- Payme/Click integratsiyasi orqali to'lov qabul qilish.
- PDF eksport qo'shish (masalan `docx2pdf` yoki LibreOffice orqali serverda konvertatsiya).

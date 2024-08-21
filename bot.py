import telebot
from telebot import types
from random import randint, choice
from collections import defaultdict

# توكن البوت الخاص بك من BotFather
TOKEN = "7430906263:AAEBZ7lDAdi5tJ4nzq4AaojrTb6NPRs7eEM"
bot = telebot.TeleBot(TOKEN)

# قاعدة بيانات بسيطة في الذاكرة
users = {}
properties = {
    "قصر": 650000,
    "سيارة": 560000,
    "مطعم": 560000,
    "ماسة": 560000,
    "قطار": 560000
}
stock_prices = {
    "شركة_A": 100,
    "شركة_B": 150,
    "شركة_C": 200
}

# تخزين نشاط الأعضاء
user_activity = defaultdict(int)

# دالة لتجهيز الحساب إذا كان المستخدم جديدًا
def initialize_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "properties": defaultdict(int),
            "stocks": defaultdict(int),
            "bank_account": None,
            "card_type": None
        }

# دالة للتحقق من إذا ما كان المستخدم مشرفًا
def is_admin(user_id, chat_id):
    chat_admins = bot.get_chat_administrators(chat_id)
    for admin in chat_admins:
        if admin.user.id == user_id:
            return True
    return False

# رسالة ترحيب بالأعضاء الجدد في المجموعة
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_members(message):
    for new_member in message.new_chat_members:
        bot.send_message(message.chat.id, f"مرحبًا بك يا {new_member.first_name} في المجموعة! 🌟")

# التعامل مع الأوامر النصية بدون /
@bot.message_handler(func=lambda message: True)
def handle_text_commands(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    initialize_user(user_id)
    
    text = message.text.strip().lower()

    # تسجيل النشاط
    user_activity[user_id] += 1

    if text == "جمع":
        collect_money(message)
    elif text == "فلوسي":
        check_balance(message)
    elif text.startswith("تحويل رصيد"):
        transfer_money(message)
    elif text.startswith("شراء"):
        buy_property(message)
    elif text.startswith("بيع"):
        sell_property(message)
    elif text == "حظ":
        try_luck(message)
    elif text.startswith("شراء أسهم"):
        buy_stocks(message)
    elif text.startswith("بيع أسهم"):
        sell_stocks(message)
    elif text == "تفاعلي":
        check_activity(message)
    elif text == "التفاعل":
        check_top_activity(message)
    elif text == "ممتلكاتي":
        show_properties(message)
    elif text.startswith("ممتلكات"):
        show_other_properties(message)
    elif text == "حسابي":
        show_bank_account(message)
    elif text == "توب فلوس":
        show_top_balances(message)
    else:
        bot.reply_to(message, "الأمر غير معروف. تأكد من كتابة الأمر بشكل صحيح.")

# أمر جمع الفلوس
def collect_money(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if is_admin(user_id, chat_id):
        users[user_id]["balance"] = float('inf')
        bot.reply_to(message, "أنت مشرف! لديك رصيد لانهائي. 💸")
    else:
        amount = randint(10, 100)
        users[user_id]["balance"] += amount
        bot.reply_to(message, f"لقد جمعت {amount} دينار! رصيدك الحالي هو {users[user_id]['balance']} دينار. 💸")

# أمر التحقق من الرصيد
def check_balance(message):
    user_id = message.from_user.id
    balance = users[user_id]["balance"]
    bot.reply_to(message, f"رصيدك الحالي هو {balance} دينار. 💸")

# أمر تحويل الرصيد
def transfer_money(message):
    try:
        user_id = message.from_user.id

        _, amount_str, recipient_username = message.text.split()
        amount = int(amount_str.replace("دينار", "").strip())
        
        recipient_id = None
        for uid, info in users.items():
            if bot.get_chat(uid).username == recipient_username.replace("@", ""):
                recipient_id = uid
                break
        
        if recipient_id is None:
            bot.reply_to(message, "لم أتمكن من العثور على المستخدم المستلم.")
            return

        if users[user_id]["balance"] >= amount:
            users[user_id]["balance"] -= amount
            users[recipient_id]["balance"] += amount
            bot.reply_to(message, f"تم تحويل {amount} دينار إلى {recipient_username}.")
            bot.send_message(recipient_id, f"لقد استلمت {amount} دينار من {message.from_user.username}.")
        else:
            bot.reply_to(message, "رصيدك غير كافٍ لإتمام هذه العملية.")

    except Exception as e:
        bot.reply_to(message, "تأكد من استخدام الصيغة الصحيحة: تحويل رصيد [المبلغ] [@اسم_المستخدم]")

# أمر شراء الممتلكات بنظام جديد
def buy_property(message):
    try:
        user_id = message.from_user.id
        parts = message.text.split()
        command = parts[0]
        quantity = int(parts[1])
        property_name = " ".join(parts[2:])
        
        if property_name not in properties:
            bot.reply_to(message, "الممتلكات غير متوفرة.")
            return
        
        property_price = properties[property_name] * quantity

        if users[user_id]["balance"] >= property_price:
            users[user_id]["balance"] -= property_price
            users[user_id]["properties"][property_name] += quantity

            bot.reply_to(message, f"تم شراء {quantity} {property_name} مقابل {property_price} دينار. رصيدك المتبقي هو {users[user_id]['balance']} دينار. 💸")
        else:
            bot.reply_to(message, "رصيدك غير كافٍ لإتمام عملية الشراء.")
    
    except Exception as e:
        bot.reply_to(message, "تأكد من استخدام الصيغة الصحيحة: شراء [الكمية] [اسم_الممتلكات]")

# أمر بيع الممتلكات
def sell_property(message):
    try:
        user_id = message.from_user.id
        parts = message.text.split()
        command = parts[0]
        quantity = int(parts[1])
        property_name = " ".join(parts[2:])
        
        if property_name not in users[user_id]["properties"] or users[user_id]["properties"][property_name] < quantity:
            bot.reply_to(message, "لا تمتلك هذه الممتلكات لبيعها.")
            return
        
        property_price = properties[property_name] * quantity * 0.7
        users[user_id]["balance"] += int(property_price)
        users[user_id]["properties"][property_name] -= quantity

        bot.reply_to(message, f"تم بيع {quantity} {property_name} مقابل {int(property_price)} دينار. رصيدك الحالي هو {users[user_id]['balance']} دينار. 💸")
    
    except Exception as e:
        bot.reply_to(message, "تأكد من استخدام الصيغة الصحيحة: بيع [الكمية] [اسم_الممتلكات]")

# أمر الحظ
def try_luck(message):
    user_id = message.from_user.id
    
    luck = choice(["ربحت", "خسرت"])
    if luck == "ربحت":
        amount = randint(100, 1000)
        users[user_id]["balance"] += amount
        bot.reply_to(message, f"حظك اليوم رائع! لقد ربحت {amount} دينار. رصيدك الحالي هو {users[user_id]['balance']} دينار. 💸")
    else:
        amount = randint(50, 500)
        users[user_id]["balance"] -= amount
        bot.reply_to(message, f"حظك سيء! لقد خسرت {amount} دينار. رصيدك الحالي هو {users[user_id]['balance']} دينار. 💸")

# شراء الأسهم
def buy_stocks(message):
    try:
        user_id = message.from_user.id
        parts = message.text.split()
        command = parts[0]
        amount = int(parts[1])
        stock_name = " ".join(parts[2:])
        
        if stock_name not in stock_prices:
            bot.reply_to(message, "اسم السهم غير صحيح.")
            return
        
        stock_price = stock_prices[stock_name]
        total_price = stock_price * amount

        if users[user_id]["balance"] >= total_price:
            users[user_id]["balance"] -= total_price
            users[user_id]["stocks"][stock_name] += amount

            # تعديل سعر السهم بشكل عشوائي بعد الشراء
            stock_prices[stock_name] = max(10, stock_price + randint(-20, 20))

            bot.reply_to(message, f"تم شراء {amount} من أسهم {stock_name} مقابل {total_price} دينار. رصيدك المتبقي هو {users[user_id]['balance']} دينار. 💸")
        else:
            bot.reply_to(message, "رصيدك غير كافٍ لإتمام عملية الشراء.")
    
    except Exception as e:
        bot.reply_to(message, "تأكد من استخدام الصيغة الصحيحة: شراء أسهم [الكمية] [اسم_السهم]")

# بيع الأسهم
def sell_stocks(message):
    try:
        user_id = message.from_user.id
        parts = message.text.split()
        command = parts[0]
        amount = int(parts[1])
        stock_name = " ".join(parts[2:])
        
        if stock_name not in users[user_id]["stocks"] or users[user_id]["stocks"][stock_name] < amount:
            bot.reply_to(message, "لا تمتلك هذه الأسهم لبيعها.")
            return
        
        stock_price = stock_prices[stock_name]
        total_price = stock_price * amount * 0.7
        users[user_id]["balance"] += int(total_price)
        users[user_id]["stocks"][stock_name] -= amount

        # تعديل سعر السهم بشكل عشوائي بعد البيع
        stock_prices[stock_name] = max(10, stock_price + randint(-20, 20))

        bot.reply_to(message, f"تم بيع {amount} من أسهم {stock_name} مقابل {int(total_price)} دينار. رصيدك الحالي هو {users[user_id]['balance']} دينار. 💸")
    
    except Exception as e:
        bot.reply_to(message, "تأكد من استخدام الصيغة الصحيحة: بيع أسهم [الكمية] [اسم_السهم]")

# عرض ممتلكات المستخدم
def show_properties(message):
    user_id = message.from_user.id
    properties_list = users[user_id]["properties"]
    if not properties_list:
        bot.reply_to(message, "لا تمتلك أي ممتلكات.")
    else:
        properties_str = ", ".join(f"{name}: {quantity}" for name, quantity in properties_list.items())
        bot.reply_to(message, f"ممتلكاتك: {properties_str}")

# عرض ممتلكات شخص آخر
def show_other_properties(message):
    try:
        parts = message.text.split()
        target_username = parts[1]
        target_id = None

        for uid, info in users.items():
            if bot.get_chat(uid).username == target_username.replace("@", ""):
                target_id = uid
                break

        if target_id is None:
            bot.reply_to(message, "لم أتمكن من العثور على المستخدم.")
            return

        properties_list = users[target_id]["properties"]
        if not properties_list:
            bot.reply_to(message, f"{target_username} لا يمتلك أي ممتلكات.")
        else:
            properties_str = ", ".join(f"{name}: {quantity}" for name, quantity in properties_list.items())
            bot.reply_to(message, f"ممتلكات {target_username}: {properties_str}")

    except Exception as e:
        bot.reply_to(message, "تأكد من استخدام الصيغة الصحيحة: ممتلكات [اسم_المستخدم]")

# عرض الحساب البنكي للمستخدم
def show_bank_account(message):
    user_id = message.from_user.id
    bank_account = users[user_id]["bank_account"]
    card_type = users[user_id]["card_type"]
    
    if bank_account:
        bot.reply_to(message, f"رقم حسابك البنكي هو: {bank_account}\nنوع البطاقة: {card_type}")
    else:
        bot.reply_to(message, "لم تقم بإنشاء حساب بنكي بعد.")

# عرض تفاعل العضو
def check_activity(message):
    user_id = message.from_user.id
    activity_count = user_activity[user_id]
    bot.reply_to(message, f"تفاعلك في المجموعة: {activity_count} تفاعل.")

# عرض لوحة التفاعل
def check_top_activity(message):
    top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:5]
    top_users_str = "\n".join(f"{bot.get_chat(uid).username if bot.get_chat(uid).username else uid}: {activity} تفاعل" for uid, activity in top_users)
    bot.reply_to(message, f"لوحة التفاعل:\n{top_users_str}")

# عرض توب فلوس
def show_top_balances(message):
    top_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)[:5]
    top_users_str = "\n".join(f"{bot.get_chat(uid).username if bot.get_chat(uid).username else uid}: {info['balance']} دينار" for uid, info in top_users)
    bot.reply_to(message, f"توب فلوس:\n{top_users_str}")

# بدء تشغيل البوت
bot.polling()


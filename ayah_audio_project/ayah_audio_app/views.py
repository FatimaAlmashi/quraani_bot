from django.shortcuts import render
import requests 

from telegram import ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,CallbackQueryHandler, ConversationHandler)

from data import (surah_keyboard_ar, surah_list_ar, surah_list_en,
                 shaikh_keyboard_ar, shaikh_list_en, ar_surah_numbers,
                 get_exact_shaikh_name, get_server_num, shaikh_list,
                 surah_list)

SURAH_NAME, SHAIKH_NAME, BACK_TO_SURAH = range(3)
CALLBACK = SURAH_NAME
bot_timeout = 6000

selected_surah = None
selected_shaikh = None

surah_id = None
shaikh_id = None
chat_id = None

# correct_surah = False
# correct_shaikh = False


def start(update, context):
    print('\n\n-----------------------------  start -----------------------------')
    global chat_id
    chat_id = update.message.chat_id
    welcome_msg_1 = 'أهلا بك '+ update.message.chat.first_name + ' ' + update.message.chat.last_name + ' 👋'
    welcome_msg_2 = '''أنا المساعد الذكي لخدمة أهل القرآن 🤖\nيسعدني أن أوفر لك الوصول السريع لجميع تسجيلات سور القرآن الكريم بتلاوات مميزة لكبار القراء 🎙❤️.. 📚.. \nتفضل بالبدء وسأكون هنا لمساعدتك 👍🤖..'''
    context.bot.sendMessage(chat_id, welcome_msg_1)
    context.bot.sendMessage(chat_id, welcome_msg_2)
    return select_surah(update, context)


def select_surah(update, context):
    print('\n\n-----------------------------  select_surah -----------------------------')
    global CALLBACK
    CALLBACK = SURAH_NAME
    markup = ReplyKeyboardMarkup(surah_keyboard_ar, one_time_keyboard=True,resize_keyboard=True)
    update.message.reply_text("اختر السورة من القائمة ",reply_markup=markup)
    return CALLBACK


def select_shaikh(update, context):
    print('\n\n-----------------------------  select_shaikh -----------------------------')
    global CALLBACK, selected_surah, surah_id
    user_msg = update.message.text
    # if user_msg == 'الرجوع إلى قائمة السور':
    #     CALLBACK = SURAH_NAME
    #     markup = ReplyKeyboardMarkup(surah_keyboard_ar, one_time_keyboard=True,resize_keyboard=True)
    #     update.message.reply_text("اختر السورة من القائمة ",reply_markup=markup)
    #     return CALLBACK
    selected_surah = user_msg
    if selected_surah not in surah_list:
        CALLBACK = SURAH_NAME
        selected_surah = None
        markup = ReplyKeyboardMarkup(surah_keyboard_ar, one_time_keyboard=True,resize_keyboard=True)
        update.message.reply_text('عفواً، لا يمكنك الكتابة! قم بالإختيار من القائمة  🤖❗️',reply_markup=markup)
        return CALLBACK
    surah_id = ar_surah_numbers[selected_surah]
    markup = ReplyKeyboardMarkup(shaikh_keyboard_ar, one_time_keyboard=True,resize_keyboard=True)
    update.message.reply_text("اختر القارئ من القائمة ",reply_markup=markup)
    CALLBACK = SHAIKH_NAME
    return CALLBACK


def get_audio(update, context):
    print('\n\n-----------------------------  get_audio -----------------------------')
    global CALLBACK, selected_shaikh, selected_surah, shaikh_id, chat_id
    user_msg = update.message.text

    if user_msg == 'الرجوع إلى قائمة السور':
        CALLBACK = SURAH_NAME
        markup = ReplyKeyboardMarkup(surah_keyboard_ar, one_time_keyboard=True,resize_keyboard=True)
        update.message.reply_text("اختر السورة من القائمة ",reply_markup=markup)
        return CALLBACK

    selected_shaikh = user_msg

    if selected_shaikh not in shaikh_list:
        CALLBACK = SHAIKH_NAME
        selected_shaikh = None
        markup = ReplyKeyboardMarkup(shaikh_keyboard_ar, one_time_keyboard=True,resize_keyboard=True)
        update.message.reply_text('عفواً، لا يمكنك الكتابة! قم بالإختيار من القائمة  🤖❗️.',reply_markup=markup) 
        return CALLBACK

    context.bot.sendMessage(chat_id, 'انتظر قليلاً لحين إرسال الملف الصوتي')

    server_num = get_server_num(selected_shaikh)
    shaikh_id = get_exact_shaikh_name(selected_shaikh)

    URL = "https://"+server_num+".mp3quran.net/"+shaikh_id+"/"+surah_id+".mp3"
    try:
        r = requests.get(URL)
    except:
        print("Request Error !!!")

    print('\nURL = ', URL , '\nrequest url = ', r.url)
    try:
        context.bot.sendAudio(chat_id=chat_id, audio=URL)
        print('\nsendAudio without errors :)', r.url)
    except:
        context.bot.sendMessage(chat_id, 'عفوا! لقد حصل خطأ أثناء الإرسال 💔🤖 الرجاء المحاولة مرة أخرى 👍')
    selected_surah = None
    selected_shaikh = None 
    CALLBACK = SURAH_NAME
    markup = ReplyKeyboardMarkup(surah_keyboard_ar, one_time_keyboard=True,resize_keyboard=True)
    update.message.reply_text("اختر السورة من القائمة ",reply_markup=markup)
    return CALLBACK



def timeout(update, context):
    print('\n\n-----------------------------  timeout -----------------------------')
    global CALLBACK
    CALLBACK = SURAH_NAME
    markup = ReplyKeyboardMarkup(directories_keyboard, one_time_keyboard=True,resize_keyboard=True)
    update.message.reply_text(" ⏱ عذراً، تم انتهاء الوقت المحدد للمحادثه ، يمكنك البدء من جديد بالضغط على القائمة أدنى الشاشة",reply_markup=markup)
    return CALLBACK


def done(update, context):
    print('\n\n-----------------------------  done -----------------------------')
    update.message.reply_text("إلى اللقاء")
    return ConversationHandler.END


updater = Updater("1850351541:AAHemu_d0h0G4S-u8-WU-PmBt16AYCEyvPc", use_context=True)
dp = updater.dispatcher

timeout_handler = [MessageHandler(Filters.regex('^r$'), timeout)]

conv_handler = ConversationHandler(
    entry_points = [
        CommandHandler('start',start),

        MessageHandler((Filters.regex('عبدالباسط عبدالصمد') ^ Filters.regex('عبدالرحمن السديس') ^ Filters.regex('محمود الحصري')
                        ^ Filters.regex('علي الحذيفي') ^ Filters.regex('محمد المنشاوي') ^ Filters.regex('ابراهيم الأخضر')
                        ^ Filters.regex('ياسر الدوسري') ^ Filters.regex('عبدالله الجهني') ^ Filters.regex('سعد الغامدي')
                        ^ Filters.regex('بندر بليلة') ^ Filters.regex('عبدالله بصفر') ^ Filters.regex('عبدالله خياط')
                        ^ Filters.regex('عبدالولي الأركاني') ^ Filters.regex('أحمد الحذيفي') ^ Filters.regex('علي جابر')
                        ^ Filters.regex('هزاع البلوشي') ^ Filters.regex('ادريس أبكر') ^ Filters.regex('خالد الجليل')
                        ^ Filters.regex('ناصر القطامي') ^ Filters.regex('صالح آل طالب')), get_audio),

        MessageHandler((Filters.regex('سُورَةُ ٱلْفَاتِحَةِ') ^ Filters.regex('سُورَةُ البَقَرَةِ') ^ Filters.regex('سُورَةُ آلِ عِمۡرَانَ') 
                        ^ Filters.regex('سُورَةُ المَائـِدَةِ') ^ Filters.regex('سُورَةُ الأَنۡعَامِ') ^ Filters.regex('سُورَةُ الأَعۡرَافِ') 
                        ^ Filters.regex('سُورَةُ التَّوۡبَةِ') ^ Filters.regex('سُورَةُ يُونُسَ') ^ Filters.regex('سُورَةُ هُودٍ') 
                        ^ Filters.regex('سُورَةُ الرَّعۡدِ') ^ Filters.regex('سُورَةُ إِبۡرَاهِيمَ') ^ Filters.regex('سُورَةُ الحِجۡرِ') 
                        ^ Filters.regex('سُورَةُ الإِسۡرَاءِ') ^ Filters.regex('سُورَةُ الكَهۡفِ') ^ Filters.regex('سُورَةُ مَرۡيَمَ') 
                        ^ Filters.regex('سُورَةُ الأَنبِيَاءِ') ^ Filters.regex('سُورَةُ الحَجِّ') ^ Filters.regex('سُورَةُ المُؤۡمِنُونَ') 
                        ^ Filters.regex('سُورَةُ الفُرۡقَانِ') ^ Filters.regex('سُورَةُ الشُّعَرَاءِ') ^ Filters.regex('سُورَةُ النَّمۡلِ') 
                        ^ Filters.regex('سُورَةُ العَنكَبُوتِ') ^ Filters.regex('سُورَةُ الرُّومِ') ^ Filters.regex('سُورَةُ لُقۡمَانَ') 
                        ^ Filters.regex('سُورَةُ الأَحۡزَابِ') ^ Filters.regex('سُورَةُ سَبَإٍ') ^ Filters.regex('سُورَةُ فَاطِرٍ') 
                        ^ Filters.regex('سُورَةُ الصَّافَّاتِ') ^ Filters.regex('سُورَةُ صٓ') ^ Filters.regex('سُورَةُ الزُّمَرِ') 
                        ^ Filters.regex('سُورَةُ فُصِّلَتۡ') ^ Filters.regex('سُورَةُ الشُّورَىٰ') ^ Filters.regex('سُورَةُ الزُّخۡرُفِ') 
                        ^ Filters.regex('سُورَةُ الجَاثِيَةِ') ^ Filters.regex('سُورَةُ الأَحۡقَافِ') ^ Filters.regex('سُورَةُ مُحَمَّدٍ') 
                        ^ Filters.regex('سُورَةُ الحُجُرَاتِ') ^ Filters.regex('سُورَةُ قٓ') ^ Filters.regex('سُورَةُ الذَّارِيَاتِ') 
                        ^ Filters.regex('سُورَةُ النَّجۡمِ') ^ Filters.regex('سُورَةُ القَمَرِ') ^ Filters.regex('سُورَةُ الرَّحۡمَٰن') 
                        ^ Filters.regex('سُورَةُ الحَدِيدِ') ^ Filters.regex('سُورَةُ المُجَادلَةِ') ^ Filters.regex('سُورَةُ الحَشۡرِ') 
                        ^ Filters.regex('سُورَةُ الصَّفِّ') ^ Filters.regex('سُورَةُ الجُمُعَةِ') ^ Filters.regex('سُورَةُ المُنَافِقُونَ') 
                        ^ Filters.regex('سُورَةُ الطَّلَاقِ') ^ Filters.regex('سُورَةُ التَّحۡرِيمِ') ^ Filters.regex('سُورَةُ المُلۡكِ') 
                        ^ Filters.regex('سُورَةُ الحَاقَّةِ') ^ Filters.regex('سُورَةُ المَعَارِجِ') ^ Filters.regex('سُورَةُ نُوحٍ') 
                        ^ Filters.regex('سُورَةُ المُزَّمِّلِ') ^ Filters.regex('سُورَةُ المُدَّثِّرِ') ^ Filters.regex('سُورَةُ القِيَامَةِ') 
                        ^ Filters.regex('سُورَةُ المُرۡسَلَاتِ') ^ Filters.regex('سُورَةُ النَّبَإِ') ^ Filters.regex('سُورَةُ النَّازِعَاتِ') 
                        ^ Filters.regex('سُورَةُ التَّكۡوِيرِ') ^ Filters.regex('سُورَةُ الانفِطَارِ') ^ Filters.regex('سُورَةُ المُطَفِّفِينَ') 
                        ^ Filters.regex('سُورَةُ البُرُوجِ') ^ Filters.regex('سُورَةُ الطَّارِقِ') ^ Filters.regex('سُورَةُ الأَعۡلَىٰ') 
                        ^ Filters.regex('سُورَةُ الفَجۡرِ') ^ Filters.regex('سُورَةُ البَلَدِ') ^ Filters.regex('سُورَةُ الشَّمۡسِ') 
                        ^ Filters.regex('سُورَةُ الضُّحَىٰ') ^ Filters.regex('سُورَةُ الشَّرۡحِ') ^ Filters.regex('سُورَةُ التِّينِ') 
                        ^ Filters.regex('سُورَةُ القَدۡرِ') ^ Filters.regex('سُورَةُ البَيِّنَةِ') ^ Filters.regex('سُورَةُ الزَّلۡزَلَةِ') 
                        ^ Filters.regex('سُورَةُ القَارِعَةِ') ^ Filters.regex('سُورَةُ التَّكَاثُرِ') ^ Filters.regex('سُورَةُ العَصۡرِ') 
                        ^ Filters.regex('سُورَةُ الفِيلِ') ^ Filters.regex('سُورَةُ قُرَيۡشٍ') ^ Filters.regex('سُورَةُ المَاعُونِ') 
                        ^ Filters.regex('سُورَةُ الكَافِرُونَ') ^ Filters.regex('سُورَةُ النَّصۡرِ') ^ Filters.regex('سُورَةُ المَسَدِ') 
                        ^ Filters.regex('سُورَةُ الإخلاص') ^ Filters.regex('سُورَةُ الفلق') ^ Filters.regex('سُورَةُ الناس')), select_surah),

        ],
    states = {
        SURAH_NAME: [MessageHandler(Filters.text, select_shaikh)],
        SHAIKH_NAME: [MessageHandler(Filters.text, get_audio)]
    },
    fallbacks = [ MessageHandler(Filters.regex('^Done$'), done)],
    # allow_reentry=True,
    conversation_timeout = bot_timeout 
)

dp.add_handler(conv_handler)
updater.start_polling()
updater.idle()
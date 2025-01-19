import telebot 
from telebot import types 
import wikipedia 
import requests 
import json

wikipedia.set_lang("ru") 

API_TOKEN = '7557871345:AAGM_rJ2OvyEaRLe0cVx4fpBXeNTaSQXPLA'
bot = telebot.TeleBot(API_TOKEN) 

def load_companies():
    with open('C:/Users/neuda_memxnfg/OneDrive/Desktop/dijson.json', 'r', encoding='utf-8') as f:
        return json.load(f)
 
@bot.message_handler(commands=['button']) 
def button(message): 
    markup = types.InlineKeyboardMarkup(row_width=1) 
    item = types.InlineKeyboardButton('Название компании', callback_data='Task_1') 
    item2 = types.InlineKeyboardButton('Компании в стране', callback_data='Task_2') 
    markup.add(item, item2) 
     
    bot.send_message(message.chat.id, 'Предлагаю вам:', reply_markup=markup) 
 
@bot.callback_query_handler(func=lambda call: True) 
def callback(call): 
    if call.message: 
        if call.data == 'Task_1': 
            bot.send_message(call.message.chat.id, 'Напишите название компании и уточняющее слово.') 
            bot.register_next_step_handler(call.message, handle_message)
        elif call.data == 'Task_2': 
            bot.send_message(call.message.chat.id, 'Напишите название страны.')
            bot.register_next_step_handler(call.message, handle_country_input) 
 
@bot.message_handler(commands=['help']) 
def help(message): 
    bot.send_message(message.chat.id, 'Напишите команду /button') 
 
@bot.message_handler(func=lambda message: True) 
def handle_country_input(message):  
    country_name = message.text.strip() 
    companies_data = load_companies() 

    if country_name in companies_data['companies']: 
        country_companies = companies_data['companies'][country_name] 
        if len(country_companies) > 5: 
            country_companies = country_companies[:5] 

        response_message = f"Вот 5 компаний в {country_name}:\n" 
        for company in country_companies: 
            response_message += f"- {company['name']} ({company['industry']})\n" 
         
        bot.send_message(message.chat.id, response_message) 
    else: 
        bot.send_message(message.chat.id, f"В стране {country_name} нет компаний в базе данных.")


def handle_message(message): 
    company_name = message.text 

    try: 

        summary = wikipedia.summary(company_name, sentences=3) 
        bot.send_message(message.chat.id, summary)


        page = wikipedia.page(company_name)
        bot.send_message(message.chat.id, f"Ссылка на официальный сайт компании: {page.url}")


        reviews = get_company_reviews(company_name) 
        

        rating = get_company_rating(company_name)  
        if rating: 
            bot.send_message(message.chat.id, f"Рейтинг компании {company_name}: {rating}") 
        else: 

            bot.send_message(message.chat.id, f"{company_name} не состоит в рейтинге.") 

        if reviews:  
            review_messages = "\n".join(reviews)  
            bot.send_message(message.chat.id, f"Отзывы о компании {company_name}:\n{review_messages}")  
        else:  

            bot.send_message(message.chat.id, f"О {company_name} нет отзывов.")
 
    except wikipedia.exceptions.DisambiguationError as e: 
        bot.send_message(message.chat.id, f"Уточните, пожалуйста, что именно вы имеете в виду. Доступные варианты: {', '.join(e.options)}") 
    except wikipedia.exceptions.PageError: 
        bot.send_message(message.chat.id, "Извините, информация о такой компании не найдена.") 
    except Exception as e: 
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}") 
 
def get_company_reviews(company_name):  
    api_url = f"https://vakansii.pro/articles/name={company_name}" 
    response = requests.get(api_url)  
     
    if response.status_code == 200:  
        data = response.json()  
        return data.get('reviews') 
    else:  
        return None  
 
def get_company_rating(company_name): 
    api_url = f"https://vakansii.pro/articles/company_rating+name={company_name}" 
    response = requests.get(api_url) 
     
    if response.status_code == 200: 
        data = response.json() 
        return data.get('rating') 
    else: 
        return None 
 
bot.polling()

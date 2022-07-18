# OUR FILES IMPORT
from messages import *
from bot_info import *
from defs import Defs
from admins import *
from State_m import *
from keyboards_info import *
# Libraries import
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor
from aiogram import types
from aiogram.types import *
from aiogram.utils.markdown import hlink
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

bot = Bot(token=BOT_TOKEN, parse_mode='html')
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands="start")
async def ComandStart(message: types.Message):
    permission = False
    print(f"{datetime.now()}  log--> GET IN  {message.from_user.id}")
    # with open("users_info.json") as f:
    #     info = json.load(f)
    # for i in range(len(info['users-active'])):
    #     if int(info['users-active'][i]['id']) == int(message.from_user.id):
    #         permission = True
    #         break

    if str(message.from_user.id) in admin_ids:
        await message.answer('Добро пожаловать Администратор☺️', reply_markup=Defs().admin_keyb_main_menu())
        await States.admin.set()
    else:
        # await message.answer('Введите пожалуйста код  - доступа')
        # await States.enter_code.set()
        await message.answer('Вас приветствует бот ОЛХ', reply_markup=Defs().main_menu())
        await States.normal_permission.set()


# Admin Panel
@dp.callback_query_handler(state=States.admin)
async def MainMenu(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()

    if callback == 'settings':
        await call.message.answer('Выберите категорию для парсинга', reply_markup=Defs().keyb_categories())
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await States.settings.set()
    elif callback == 'parse':
        await call.message.answer('Считывание данных началось...')
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        # await States.parse.set()
        # TODO
    elif callback == 'Make_code':
        await call.message.answer('Выберите врямя работы токена', reply_markup=Defs().make_code_keyb())
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await States.make_code.set()
    elif callback == 'add_token':
        await call.message.answer('Считывание данных началось...')
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        # await States.add_token.set()
        # TODO
    else:
        await call.message.answer('Используйте представленные вам кнопки')


@dp.callback_query_handler(state=States.make_code)
async def make_code(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    number = Defs().generate_code()
    with open("key_db.json") as f:
        codes = json.load(f)
    while number in codes["used_keys"]:
        number = Defs().generate_code()
    time_out = ''
    if callback == "one_hour":
        time_out = '1 hours'
        codes["keys"].append({f"id": f"{number}", "time_out": f"{time_out}"})
    elif callback == "three_hours":
        time_out = '3 hours'
        codes["keys"].append({f"id": f"{number}", "time_out": f"{time_out}"})
    elif callback == "five_hours":
        time_out = '5 hours'
        codes["keys"].append({f"id": f"{number}", "time_out": f"{time_out}"})
    elif callback == "twelve_hours":
        time_out = '12 hours'
        codes["keys"].append({f"id": f"{number}", "time_out": f"{time_out}"})
    elif callback == "one_day":
        time_out = '1 day'
        codes["keys"].append({f"id": f"{number}", "time_out": f"{time_out}"})
    elif callback == "three_days":
        time_out = '3 days'
        codes["keys"].append({f"id": f"{number}", "time_out": f"{time_out}"})
    elif callback == "Forever":
        time_out = 'Forever'
        codes["keys"].append({f"id": f"{number}", "time_out": f"{time_out}"})
    with open("key_db.json", "w") as f:
        json.dump(codes, f, indent=3)
    await call.message.answer(f"Сгенерированный код :\n\n" + f"{'<code>'} {number} {'</code>'} \n\n"
                                                             f"Время действия : {time_out}\n"
                                                             f"Нажмите на код чтобы его скопировать.",
                              parse_mode='HTML')
    await call.message.answer(f"Главное меню", reply_markup=Defs().admin_keyb_main_menu())
    await States.admin.set()


@dp.message_handler(state=States.enter_code)
async def enter_code(message: types.Message, state: FSMContext):
    code = message.text
    is_code_true = False
    await state.finish()

    with open("key_db.json") as f:
        codes = json.load(f)

    time_out = ''
    for i in range(len(codes['keys'])):
        if int(codes['keys'][i]['id']) == int(code):
            time_out = codes['keys'][i]['time_out']
            is_code_true = True
            codes["used_keys"].append(codes['keys'][i]['id'])
            del codes['keys'][i]
            with open("key_db.json", "w") as f:
                json.dump(codes, f, indent=3)
            break
    if is_code_true:
        date_finish = ''
        with open("users_info.json") as f:
            users = json.load(f)
        if time_out == "1 hours":
            date_finish = str(datetime.now() + timedelta(hours=1)).split('.')[0]
        elif time_out == "3 hours":
            date_finish = str(datetime.now() + timedelta(hours=3)).split('.')[0]
        elif time_out == "5 hours":
            date_finish = str(datetime.now() + timedelta(hours=5)).split('.')[0]
        elif time_out == "12 hours":
            date_finish = str(datetime.now() + timedelta(hours=12)).split('.')[0]
        elif time_out == "1 day":
            date_finish = str(datetime.now() + timedelta(days=1)).split('.')[0]
        elif time_out == "3 days":
            date_finish = str(datetime.now() + timedelta(days=3)).split('.')[0]
        elif time_out == "Forever":
            date_finish = "Forever"

        users["users-active"].append({
            "id": message.from_user.id,
            "username": message.from_user.username,
            "Date-finish": date_finish})
        with open("users_info.json", "w") as f:
            json.dump(users, f, indent=3)
        for admin in admin_ids:
            await bot.send_message(admin,
                                   f"Пользователь @{hlink(message.from_user.first_name, 'tg://user?id=' + str(message.from_user.id))} активировал код")
        await message.answer('Главное меню', reply_markup=Defs().main_menu())
        await States.normal_permission.set()
    else:
        await message.answer('К сожалению код не действителен\n'
                             'Введите другой код:')
        await States.enter_code.set()


# USER PANEL


@dp.callback_query_handler(state=States.normal_permission)
async def MainMenu(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'settings':
        await call.message.answer('Выберите категорию для парсинга', reply_markup=Defs().keyb_categories())
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await States.settings.set()
    elif callback == 'profile':
        with open("users_info.json") as f:
            users = json.load(f)
        date = ''
        for i in range (len( users['users-active'])) :
            if str(users['users-active'][i]['id']) == str(call.from_user.id) :
                date = str(users['users-active'][i]['date'])
        date_2 = str(datetime.now()).split('.')[0]
        if date == 'Forever':
            time_line = "Forever"
        else:
            time_line = (str(datetime.strptime(date_2, '%Y-%m-%d %H:%M:%S') - datetime.strptime(date, '%Y-%m-%d %H:%M:%S')))
        if time_line[0] != '-':
            time_line = '0 days 0 hours'
        else:
            time_line = str(time_line)
        await call.message.answer('Ваш профиль:')
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await call.message.answer(f'👤Username : @{call.from_user.username}\n'
                                  f'🆔Telegram ID : {call.from_user.id}\n'
                                  f'🕗Статус подписки : {time_line}',reply_markup=Defs().main_menu() )
        await States.normal_permission.set()
    elif callback == "subscription" :
        await call.message.answer('Меню подписки:',reply_markup=Defs().subscription())
        await States.subscription.set()
    else:
        await call.message.answer('Используйте представленные вам кнопки')


@dp.callback_query_handler(state = States.subscription)
async def subscription(call:types.CallbackQuery,state:FSMContext):
    callback = call.data
    if callback == 'to_subscribe' :
        await call.message.answer("Для приобритения кода подписки напишите @vas_realo",reply_markup=Defs().subscription())
        await States.subscription.set()
    elif callback == 'enter_code':
        await call.message.answer('Введите код доступа:')
        await States.enter_code.set()
    elif callback == 'back_to_menu':
        await call.message.answer('Главное меню:',reply_markup=Defs().main_menu())
        await States.normal_permission.set()
@dp.callback_query_handler(state=States.settings)
async def categories(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'transport':
        await call.message.answer(f'Категория "{category_dict.get(callback)}"',
                                  reply_markup=Defs().keyb_sub_categories(callback))
        await States.transport.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'nedvizhimost':
        await call.message.answer(f'Категория "{category_dict.get(callback)}"',
                                  reply_markup=Defs().keyb_sub_categories(callback))
        await States.nedvizhimost.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'zapchasti-dlya-transporta':
        await call.message.answer(f'Категория "{category_dict.get(callback)}"',
                                  reply_markup=Defs().keyb_sub_categories(callback))
        await States.zapchasti_dlya_transporta.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'zhivotnye':
        await call.message.answer(f'Категория "{category_dict.get(callback)}"',
                                  reply_markup=Defs().keyb_sub_categories(callback))
        await States.zhivotnye.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'dom-i-sad':
        await call.message.answer(f'Категория "{category_dict.get(callback)}"',
                                  reply_markup=Defs().keyb_sub_categories(callback))
        await States.dom_i_sad.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'detskiy-mir':
        await call.message.answer(f'Категория "{category_dict.get(callback)}"',
                                  reply_markup=Defs().keyb_sub_categories(callback))
        await States.detskiy_mir.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'elektronika':
        await call.message.answer(f'Категория "{category_dict.get(callback)}"',
                                  reply_markup=Defs().keyb_sub_categories(callback))
        await States.elektronika.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'moda-i-stil':
        await call.message.answer(f'Категория "{category_dict.get(callback)}"',
                                  reply_markup=Defs().keyb_sub_categories(callback))
        await States.moda_i_stil.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'hobbi-otdyh-i-sport':
        await call.message.answer(f'Категория "{category_dict.get(callback)}"',
                                  reply_markup=Defs().keyb_sub_categories(callback))
        await States.hobbi_otdyh_i_sport.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_menu':
        if str(call.message.from_user.id) in admin_ids:
            await call.message.answer('Главное меню', reply_markup=Defs().admin_keyb_main_menu())
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await States.admin.set()
        else:
            await call.message.answer('Главное меню', reply_markup=Defs().main_menu())
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await States.normal_permission.set()
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.settings.set()


@dp.callback_query_handler(state=States.transport)
async def transport_category(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'legkovye-avtomobili':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'spetstehnika':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'selhoztehnika':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'moto':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'avtomobili-iz-polshi':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'avtobusy':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'vodnyy-transport':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'pritsepy-doma-na-kolesah':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'vozdushnyy-transport':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'drugoy-transport':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'gruzovye-avtomobili':
        await call.message.answer(subcategory.get('transport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_categories':
        await call.message.answer('Категории', reply_markup=Defs().keyb_categories())
        await States.settings.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.transport.set()


@dp.callback_query_handler(state=States.nedvizhimost)
async def nedvizhimost_category(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'posutochno-pochasovo':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'nedvizhimost-za-rubezhom':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'komnaty':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'zemlya':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'kommercheskaya-nedvizhimost':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'kwatery-pracownicze':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'doma':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'kvartiry/novostroyki':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'hale-magazyny':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'garazhy-parkovki':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'kvartiry':
        await call.message.answer(subcategory.get('nedvizhimost').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_categories':
        await call.message.answer('Категории', reply_markup=Defs().keyb_categories())
        await States.settings.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.nedvizhimost.set()


@dp.callback_query_handler(state=States.zapchasti_dlya_transporta)
async def zapchasti_dya_transporta_category(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'avtozapchasti-i-aksessuary':
        await call.message.answer(subcategory.get('zapchasti-dlya-transporta').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'shiny-diski-i-kolesa':
        await call.message.answer(subcategory.get('zapchasti-dlya-transporta').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'zapchasti-dlya-spets-sh-tehniki':
        await call.message.answer(subcategory.get('zapchasti-dlya-transporta').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'motozapchasti-i-aksessuary':
        await call.message.answer(subcategory.get('zapchasti-dlya-transporta').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'prochie-zapchasti':
        await call.message.answer(subcategory.get('zapchasti-dlya-transporta').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_categories':
        await call.message.answer('Категории', reply_markup=Defs().keyb_categories())
        await States.settings.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.zapchasti_dlya_transporta.set()


@dp.callback_query_handler(state=States.zhivotnye)
async def zapchasti_dya_transporta_category(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'sobaki':
        await call.message.answer(subcategory.get('zhivotnye').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'selskohozyaystvennye-zhivotnye':
        await call.message.answer(subcategory.get('zhivotnye').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'akvariumnye-rybki':
        await call.message.answer(subcategory.get('zhivotnye').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'koshki':
        await call.message.answer(subcategory.get('zhivotnye').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'ptitsy':
        await call.message.answer(subcategory.get('zhivotnye').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'drugie-zhivotnye':
        await call.message.answer(subcategory.get('zhivotnye').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'gryzuny':
        await call.message.answer(subcategory.get('zhivotnye').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'reptilii':
        await call.message.answer(subcategory.get('zhivotnye').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'tovary-dlya-zhivotnyh':
        await call.message.answer(subcategory.get('zhivotnye').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_categories':
        await call.message.answer('Категории', reply_markup=Defs().keyb_categories())
        await States.settings.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.zhivotnye.set()


@dp.callback_query_handler(state=States.dom_i_sad)
async def dom_i_sad_category(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'mebel':
        await call.message.answer(subcategory.get('dom-i-sad').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'stroitelstvo-remont':
        await call.message.answer(subcategory.get('dom-i-sad').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'sprzet-agd':
        await call.message.answer(subcategory.get('dom-i-sad').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'kantstovary-rashodnye-materialy':
        await call.message.answer(subcategory.get('dom-i-sad').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'produkty-pitaniya-napitki':
        await call.message.answer(subcategory.get('dom-i-sad').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'sad-ogorod':
        await call.message.answer(subcategory.get('dom-i-sad').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'predmety-interera':
        await call.message.answer(subcategory.get('dom-i-sad').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'instrumenty':
        await call.message.answer(subcategory.get('dom-i-sad').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'prochie-tovary-dlya-doma':
        await call.message.answer(subcategory.get('dom-i-sad').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_categories':
        await call.message.answer('Категории', reply_markup=Defs().keyb_categories())
        await States.settings.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.dom_i_sad.set()


@dp.callback_query_handler(state=States.detskiy_mir)
async def zapchasti_dya_transporta_category(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'igrushki':
        await call.message.answer(subcategory.get('detskiy-mir').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'detskaya-odezhda':
        await call.message.answer(subcategory.get('detskiy-mir').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'detskie-kolyaski':
        await call.message.answer(subcategory.get('detskiy-mir').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'detskaya-obuv':
        await call.message.answer(subcategory.get('detskiy-mir').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'akcesoria-dla-niemowlat':
        await call.message.answer(subcategory.get('detskiy-mir').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'detskaya-mebel':
        await call.message.answer(subcategory.get('detskiy-mir').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'detskie-avtokresla':
        await call.message.answer(subcategory.get('detskiy-mir').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'prochie-detskie-tovary':
        await call.message.answer(subcategory.get('detskiy-mir').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_categories':
        await call.message.answer('Категории', reply_markup=Defs().keyb_categories())
        await States.settings.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.detskiy_mir.set()


@dp.callback_query_handler(state=States.elektronika)
async def zapchasti_dya_transporta_category(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'telefony-i-aksesuary':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'planshety-el-knigi-i-aksessuary':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'foto-video':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'aksessuary-i-komplektuyuschie':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'tehnika-dlya-doma':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'audiotehnika':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'kompyutery-i-komplektuyuschie':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'igry-i-igrovye-pristavki':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'prochaja-electronika':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'tehnika-dlya-kuhni':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'noutbuki-i-aksesuary':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'klimaticheskoe-oborudovanie':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'individualnyy-uhod':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'tv-videotehnika':
        await call.message.answer(subcategory.get('elektronika').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_categories':
        await call.message.answer('Категории', reply_markup=Defs().keyb_categories())
        await States.settings.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.elektronika.set()


@dp.callback_query_handler(state=States.moda_i_stil)
async def zapchasti_dya_transporta_category(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'odezhda':
        await call.message.answer(subcategory.get('moda-i-stil').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'naruchnye-chasy':
        await call.message.answer(subcategory.get('moda-i-stil').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'podarki':
        await call.message.answer(subcategory.get('moda-i-stil').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'aksessuary':
        await call.message.answer(subcategory.get('moda-i-stil').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'krasota-zdorove':
        await call.message.answer(subcategory.get('moda-i-stil').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'moda-raznoe':
        await call.message.answer(subcategory.get('moda-i-stil').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_categories':
        await call.message.answer('Категории', reply_markup=Defs().keyb_categories())
        await States.settings.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.moda_i_stil.set()


@dp.callback_query_handler(state=States.hobbi_otdyh_i_sport)
async def zapchasti_dya_transporta_category(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    await state.finish()
    if callback == 'muzykalnye-instrumenty':
        await call.message.answer(subcategory.get('hobbi-otdyh-i-sport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'sport-otdyh':
        await call.message.answer(subcategory.get('hobbi-otdyh-i-sport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'drugoe':
        await call.message.answer(subcategory.get('hobbi-otdyh-i-sport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'antikvariat-kollektsii':
        await call.message.answer(subcategory.get('hobbi-otdyh-i-sport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'knigi-zhurnaly':
        await call.message.answer(subcategory.get('hobbi-otdyh-i-sport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'cd-dvd-plastinki':
        await call.message.answer(subcategory.get('hobbi-otdyh-i-sport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'bilety':
        await call.message.answer(subcategory.get('hobbi-otdyh-i-sport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'poisk-poputchikov':
        await call.message.answer(subcategory.get('hobbi-otdyh-i-sport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'poisk-grupp-muzykantov':
        await call.message.answer(subcategory.get('hobbi-otdyh-i-sport').get(callback))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    elif callback == 'back_to_categories':
        await call.message.answer('Категории', reply_markup=Defs().keyb_categories())
        await States.settings.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.message.answer('Используйте представленные вам кнопки')
        await States.hobbi_otdyh_i_sport.set()


executor.start_polling(dp, skip_updates=True)

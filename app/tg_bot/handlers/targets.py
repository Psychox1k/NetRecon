from aiogram import Router, F, types
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.tg_bot.states import AddTarget
from app.tg_bot.utils.validators import is_valid_domain
from app.tg_bot.keyboards.reply import get_target_create_menu, get_main_menu

from app.worker.tasks import scan_and_save_domain
router = Router()

@router.message(F.text == "🎯 My targets")
async def show_targets(message: Message):
    await message.answer("Your targets list  on your monitoring")

@router.message(F.text == "➕ Add target")
async def add_domain_start(message: Message, state: FSMContext):
    await message.answer(
        "Send target name you want to add",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddTarget.waiting_for_name)

@router.message(AddTarget.waiting_for_name)
async def process_target_name(message: types.Message, state: FSMContext):
    await state.update_data(target_name=message.text)
    await message.answer("Great! Now sendthe domain to scan (e.g, example.com):")
    await state.set_state(AddTarget.waiting_for_domain)

@router.message(AddTarget.waiting_for_domain)
async def process_domain_name(message: types.Message, state: FSMContext):
    domain = message.text

    if not is_valid_domain(domain):
        await message.answer("⚠️ Invalid domain! Please try again:")
        return

    data = await state.get_data()

    target_name = data.get("target_name")

    scan_and_save_domain.delay(
        target_name=target_name,
        domain_name=domain,
        chat_id=message.from_user.id
    )
    await message.answer(
        f"✅ Target <b>{target_name}</b> added!\n🚀 Scan started for <b>{domain}</b>.",
        reply_markup=get_main_menu()
    )

    await state.clear()
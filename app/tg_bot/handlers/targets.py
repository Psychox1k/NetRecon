import json
from aiogram.filters import StateFilter
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.tg_bot.states import AddTarget
from app.tg_bot.utils.validators import is_valid_domain
from app.tg_bot.keyboards.reply import get_target_create_menu, get_main_menu, get_cancel_rkb

from app.worker.tasks import scan_and_save_domain
from app.tg_bot.keyboards.inline import (
    get_domains_ikb,
    get_targets_ikb,
    get_confirm_delete_ikb,
    get_domain_info_ikb
)

from app.database import async_session
from app.database.models import TargetModel, DomainModel, IPAddressModel, TargetStatus
from app.tg_bot.states import AddDomainToExisting
from app.tg_bot.utils.formatters import format_domain_results
from app.tg_bot.keyboards.inline import get_results_ikb

router = Router()

@router.message(F.text == "🎯 My targets")
async def show_targets(message: Message):

    async with async_session() as db:
        query = select(TargetModel).options(selectinload(TargetModel.domains))
        result = await db.execute(query)
        real_targets = result.scalars().all()

    if not real_targets:
        await message.answer("You don't have any targets yet. Click '➕ Add target' to create one.")
        return

    await message.answer(
        "Here are your active targets:",
        reply_markup=get_targets_ikb(real_targets)
    )


@router.message(F.text == "➕ Add target")
async def add_domain_start(message: Message, state: FSMContext):
    await message.answer(
        "Send target name you want to add",
        reply_markup=get_cancel_rkb()
    )
    await state.set_state(AddTarget.waiting_for_name)

@router.message(F.text == "❌ Cancel", StateFilter('*'))
async def process_cancel_text(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text="❌ Action canceled.",
        reply_markup=get_main_menu()
    )



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

@router.callback_query(F.data.startswith("show_target_"))
async def process_target_click(callback: CallbackQuery):
    target_id = int(callback.data.split("_")[-1])

    async with async_session() as db:
        query = select(TargetModel).where(TargetModel.id == target_id).options(selectinload(TargetModel.domains))
        result = await db.execute(query)
        target = result.scalar_one_or_none()

    if not target:
        await callback.answer("Target not found!", show_alert=True)
        return

    if not target.domains:
        await callback.message.edit_text(
            text=f"Target <b>{target.name}</b> doesn't have any domains yet.",
            reply_markup=get_domains_ikb(target_id, target.domains, target.status),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        text=f"Domains for target <b>{target.name}</b>:",
        reply_markup=get_domains_ikb(target_id, target.domains, target.status),
        parse_mode="HTML"
    )

    await callback.answer()


@router.callback_query(F.data.startswith("back_to_targets_list"))
async def process_back_to_targets(callback: CallbackQuery):
    async with async_session() as db:
        query = select(TargetModel).options(selectinload(TargetModel.domains))
        result = await db.execute(query)
        real_targets = result.scalars().all()

    if not real_targets:
        await callback.message.edit_text(
            text="You don't have any active targets.",
            reply_markup=None
        )
        await callback.answer()
        return


    await callback.message.edit_text(
        text="Here are your active targets:",
        reply_markup=get_targets_ikb(real_targets)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("scan_new_domain"))
async def process_scan_new_domain(callback: CallbackQuery, state: FSMContext):
    target_id = int(callback.data.split("_")[-1])

    async with async_session() as db:
        target = await db.get(TargetModel, target_id)
        if not target:
            await callback.answer("Target not found!", show_alert=True)
            return
        target_name = target.name

    await state.update_data(target_name=target_name)

    await state.set_state(AddDomainToExisting.waiting_for_domain)

    await callback.message.answer(
        text=f"Send the new domain you want to scan for <b>{target_name}</b> (e.g., example.com):",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("show_domain_"))
async def process_domain_click(callback: CallbackQuery):
    parts = callback.data.split("_")

    target_id = int(parts[-2])
    domain_id = int(parts[-1])

    async with async_session() as db:
        domain = await db.get(DomainModel, domain_id)
        if not domain:
            await callback.answer("Domain not found!", show_alert=True)
            return

    text = (
        f"🌐 <b>Domain:</b> {domain.domain_name}\n"
        f"Scan status and details you can see below."
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=get_domain_info_ikb(target_id, domain_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("view_results_"))
async def process_view_results(callback: CallbackQuery):
    domain_id = int(callback.data.split("_")[-1])

    async with async_session() as db:
        query = select(DomainModel).where(DomainModel.id == domain_id).options(
            selectinload(DomainModel.ips).selectinload(IPAddressModel.ports),
            selectinload(DomainModel.ips).selectinload(IPAddressModel.certificate)
        )
        domain = (await db.execute(query)).scalar_one_or_none()

    if not domain:
        await callback.answer("Results not found!", show_alert=True)
        return

    pretty_text = format_domain_results(domain)

    await callback.message.edit_text(
        text=pretty_text,
        reply_markup=get_results_ikb(domain.target_id, domain_id),
        parse_mode="HTML"
    )
    await callback.answer()



@router.message(AddDomainToExisting.waiting_for_domain)
async def process_new_domain_input(message: types.Message, state: FSMContext):
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
        f"🚀 Scan started for <b>{domain}</b> (Target: {target_name}).",
        parse_mode="HTML"
    )

    await state.clear()


@router.callback_query(F.data.startswith("ask_delete_target_"))
async def ask_delete_target(callback: CallbackQuery):
    target_id = int(callback.data.split("_")[-1])

    await callback.message.edit_text(
        text="⚠️ <b>Are you absolutely sure you want to delete this target?</b>\n"
             "<i>All associated domains and scan results will be permanently lost!</i>",
        reply_markup=get_confirm_delete_ikb(item_type="target", item_id=target_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ask_delete_domain_"))
async def ask_delete_domain(callback: CallbackQuery):
    parts = callback.data.split("_")

    target_id = int(parts[-2])
    domain_id = int(parts[-1])

    await callback.message.edit_text(
        text="⚠️ <b>Are you absolutely sure you want to delete this domain?</b>\n"
             "<i>All associated data scan results will be permanently lost!</i>",
        reply_markup=get_confirm_delete_ikb(item_type="domain", item_id=domain_id, target_id=target_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_item(callback: CallbackQuery):
    parts = callback.data.split("_")

    item_type = parts[-2]
    item_id = int(parts[-1])

    async with async_session() as db:
        if item_type == "target":
            target = await db.get(TargetModel, item_id)
            if target:
                await db.delete(target)
                await db.commit()
            await process_back_to_targets(callback)
        elif item_type == "domain":
            domain = await db.get(DomainModel, item_id)
            if domain:
                target_id = domain.target_id
                await db.delete(domain)
                await db.commit()

                query = select(TargetModel).where(TargetModel.id == target_id).options(selectinload(TargetModel.domains))
                target = (await db.execute(query)).scalar_one_or_none()

                if target:
                    await callback.message.edit_text(
                        text=f"✅ Domain deleted.\n\nDomains for target <b>{target.name}</b>:",
                        reply_markup=get_domains_ikb(target_id, target.domains, target.status),
                        parse_mode="HTML"
                    )

    await callback.answer("Successfully deleted!", show_alert=False)


@router.callback_query(F.data.startswith("download_json_"))
async def process_download_json(callback: CallbackQuery):
    parts = callback.data.split("_")
    domain_id = int(parts[-1])


    async with async_session() as db:
        query = select(DomainModel).where(DomainModel.id == domain_id).options(
            selectinload(DomainModel.ips).selectinload(IPAddressModel.ports),
            selectinload(DomainModel.ips).selectinload(IPAddressModel.certificate)
        )
        domain = (await db.execute(query)).scalar_one_or_none()

    if not domain:
        await callback.answer("Error: Data not found!", show_alert=True)
        return
    scan_data = {
        "status": "SUCCESS",
        "domain": domain.domain_name,
        "ips": []
    }

    for ip_obj in domain.ips:
        ip_version = "ipv6" if ":" in ip_obj.ip else "ipv4"

        ip_report = {
            "ip": ip_obj.ip,
            "version": ip_version,
            "open_ports": [],
            "ssl_cert": None
        }


        if ip_obj.ports:
            for port_obj in ip_obj.ports:
                ip_report["open_ports"].append({
                    "port": port_obj.port_number,
                    "banner": getattr(port_obj, "banner", "")
                })

        if ip_obj.certificate:
            cert = ip_obj.certificate
            ip_report["ssl_cert"] = {
                "port": 443,
                "status": "SUCCESS",
                "serial_number": getattr(cert, "serial_number", None),
                "public_key": getattr(cert, "public_key", None),
                "subject": getattr(cert, "subject", None),
                "issuer": getattr(cert, "issuer", None),
                "not_before": str(cert.not_before) if cert.not_before else None,
                "not_after": str(cert.not_after) if cert.not_after else None,
                "subdomains": getattr(cert, "subdomains", []),
                "error": getattr(cert, "error", None)
            }

        scan_data["ips"].append(ip_report)

    json_string = json.dumps(scan_data, indent=4, ensure_ascii=False)

    file_bytes = json_string.encode("utf-8")
    virtual_file = BufferedInputFile(
        file=file_bytes,
        filename=f"{domain.domain_name}_scan.json"
    )

    await callback.message.answer_document(
        document=virtual_file,
        caption=f"📄 <b>JSON Report:</b> {domain.domain_name}",
        parse_mode="HTML"
    )

    await callback.answer()

@router.callback_query(F.data.startswith("toggle_target_"))
async def process_target_status_change(callback: CallbackQuery):
    target_id = int(callback.data.split("_")[-1])

    async with async_session() as db:
        query = select(TargetModel).where(TargetModel.id == target_id).options(selectinload(TargetModel.domains))
        result = await db.execute(query)
        target = result.scalar_one_or_none()

        if not target:
            await callback.answer("Target not found!", show_alert=True)
            return

        if target.status == "paused":
            target.status = TargetStatus.ACTIVE
        elif target.status == "active":
            target.status = TargetStatus.PAUSED


        await db.commit()
        await db.refresh(target)

        status_msg = "✅ Target Activated." if target.status == TargetStatus.ACTIVE else "⏸ Target Paused."
        text = f"{status_msg}\n\nDomains for target <b>{target.name}</b>:"

        await callback.message.edit_text(
            text=text,
            reply_markup=get_domains_ikb(target_id, target.domains, target.status),
            parse_mode="HTML"
        )

    await callback.answer()



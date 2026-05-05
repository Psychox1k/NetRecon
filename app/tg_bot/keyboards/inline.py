from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from app.database.models import TargetModel, TargetStatus


def get_targets_ikb(targets: list):
    builder = InlineKeyboardBuilder()

    for target in targets:
        builder.add(InlineKeyboardButton(
            text=f"🎯 {target.name}",
            callback_data=f"show_target_{target.id}"
        ))


    builder.adjust(1)
    return builder.as_markup()


def get_domains_ikb(target_id: int, domains: list, target_status: TargetStatus):

    builder = InlineKeyboardBuilder()

    if target_status == TargetStatus.PAUSED:
        builder.row(
            InlineKeyboardButton(
                text="▶️ Activate Target",
                callback_data=f"toggle_target_{target_id}"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="⏸ Pause Target",
                callback_data=f"toggle_target_{target_id}"
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="➕ Scan new domain",
            callback_data=f"scan_new_domain_{target_id}"
        )
    )

    for domain in domains:
        builder.add(InlineKeyboardButton(
            text=f"🌐 {domain.domain_name}",
            callback_data=f"show_domain_{target_id}_{domain.id}"
        ))


    builder.adjust(1, 1, 2)

    builder.row(
        InlineKeyboardButton(
            text="🗑 Delete Target",
            callback_data=f"ask_delete_target_{target_id}"
        )
    )


    builder.row(
        InlineKeyboardButton(
            text="🔙 Back to targets",
            callback_data="back_to_targets_list"
        )
    )


    return builder.as_markup()

def get_domain_info_ikb(target_id: int, domain_id: int):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="📊 View Scan Results",
            callback_data=f"view_results_{domain_id}"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="🗑 Delete Domain",
            callback_data=f"ask_delete_domain_{target_id}_{domain_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Back to Domains",
            callback_data=f"show_target_{target_id}"
        )
    )

    return builder.as_markup()

def get_confirm_delete_ikb(item_type: str, item_id: int, target_id: int = None):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Yes, delete",
        callback_data=f"confirm_delete_{item_type}_{item_id}"
    )

    if item_type == "target":
        cancel_callback = f"show_target_{item_id}"
    else:
        cancel_callback = f"show_domain_{target_id}_{item_id}"

    builder.button(
        text="❌ No, cancel",
        callback_data=cancel_callback
    )

    builder.adjust(2)
    return builder.as_markup()


def get_results_ikb(target_id: int, domain_id: int):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🖥 Open in Swagger",
            url=f"http://0.0.0.0:8000/docs"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="📄 Download JSON",
            callback_data=f"download_json_{target_id}_{domain_id}"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="🔙 Back to Domain",
            callback_data=f"show_domain_{target_id}_{domain_id}"
        )
    )

    return builder.as_markup()


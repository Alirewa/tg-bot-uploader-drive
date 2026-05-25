from pyrogram import Client
from handlers.start import register as reg_start
from handlers.admin import register as reg_admin
from handlers.upload import register as reg_upload
from handlers.oauth import register as reg_oauth


def register_all(app: Client) -> None:
    reg_start(app)
    reg_admin(app)
    reg_upload(app)
    reg_oauth(app)

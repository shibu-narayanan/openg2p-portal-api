from typing import Annotated

from fastapi import Depends
from openg2p_fastapi_auth.controllers.auth_controller import AuthController
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError

from ..config import Settings
from ..dependencies import JwtBearerAuth
from ..models.credentials import AuthCredentials
from ..models.orm.partner_orm import (
    BankORM,
    PartnerBankORM,
    PartnerORM,
    PartnerPhoneNoORM,
)
from ..models.orm.reg_id_orm import RegIDORM, RegIDTypeORM
from ..models.profile import Profile

_config = Settings.get_config()


class AuthController(AuthController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_profile(
        self,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
        online: bool = True,
    ):
        # res = await super().get_profile(auth, online)

        if not auth.partner_id:
            raise UnauthorizedError(
                message="Unauthorized. Partner Not Found in Registry."
            )

        partner_data = await PartnerORM.get_partner_data(auth.partner_id)
        partner_ids_data = await RegIDORM.get_all_partner_ids(partner_data.id)
        partner_bank_data = await PartnerBankORM.get_partner_banks(partner_data.id)
        partner_phone_data = await PartnerPhoneNoORM.get_partner_phone_details(
            partner_data.id
        )

        partner_ids = []
        for reg_id in partner_ids_data:
            partner_id = {
                "id_type": None,
                "value": reg_id.value,
                "expiry_date": reg_id.expiry_date,
            }

            id_type_name = await RegIDTypeORM.get_id_type_name(reg_id.id_type)

            if id_type_name:
                partner_id["id_type"] = id_type_name.name

            partner_ids.append(partner_id)

        partner_bank_accounts = []
        for bank in partner_bank_data:
            partner_bank = {
                "bank_name": None,
                "acc_number": bank.acc_number,
            }

            bank = await BankORM.get_by_id(bank.bank_id)

            if bank:
                partner_bank["bank_name"] = bank.name

            partner_bank_accounts.append(partner_bank)

        partner_phone_numbers = []
        for phone in partner_phone_data:
            partner_phone_numbers.append(
                {
                    "phone_no": phone.phone_no,
                    "date_collected": phone.date_collected,
                }
            )

        return Profile(
            id=partner_data.id,
            ids=partner_ids,
            email=partner_data.email,
            gender=partner_data.gender,
            # address=partner_data.address,
            bank_ids=partner_bank_accounts,
            addl_name=partner_data.addl_name,
            given_name=partner_data.given_name,
            family_name=partner_data.family_name,
            birthdate=partner_data.birthdate,
            phone_numbers=partner_phone_numbers,
            birth_place=partner_data.birth_place,
            notification_preference=partner_data.notification_preference,
        )

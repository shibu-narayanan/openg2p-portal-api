from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.service import BaseService
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..config import Settings
from ..models.orm.partner_orm import PartnerORM
from ..models.orm.reg_id_orm import RegIDORM

_config = Settings.get_config(strict=False)


class PartnerService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def check_and_create_partner(self, userinfo_dict: dict):
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            partner = await RegIDORM.get_partner_by_reg_id(
                _config.auth_id_type_ids[userinfo_dict["iss"]], userinfo_dict["sub"]
            )

            # TODO: Check for the reg_id_type_id if not present throw the error

            if not partner:
                partner = PartnerORM(
                    name=userinfo_dict["name"],
                    given_name=userinfo_dict["given_name"],
                    family_name=userinfo_dict["family_name"],
                    email=userinfo_dict["email"],
                    active=True,
                )
                reg_id = RegIDORM(
                    partner=partner,
                    id_type=_config.auth_id_type_ids[userinfo_dict["iss"]],
                    value=userinfo_dict["sub"],
                )

                try:
                    session.add(partner)
                    session.add(reg_id)

                    await session.commit()
                except IntegrityError:
                    return "Could not create Partner"

        return "Partner created!!"

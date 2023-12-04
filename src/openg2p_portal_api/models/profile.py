from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RegistrantID(BaseModel):
    model_config = ConfigDict(extra="allow")

    id_type: Optional[str] = None
    value: Optional[str] = None
    expiry_date: Optional[date] = None


class BankDetails(BaseModel):
    model_config = ConfigDict(extra="allow")

    bank_name: Optional[str] = None
    acc_number: Optional[str] = None


class PhoneNumber(BaseModel):
    model_config = ConfigDict(extra="allow")

    phone_no: Optional[str] = None
    date_collected: Optional[date] = None


class Profile(BaseModel):
    model_config = ConfigDict()

    id: Optional[int] = None
    ids: List[RegistrantID] = []
    email: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[dict] = {}
    bank_ids: List[BankDetails] = []
    addl_name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    birthdate: Optional[date] = None
    phone_numbers: List[PhoneNumber] = []
    birth_place: Optional[str] = None
    notification_preference: Optional[str] = None

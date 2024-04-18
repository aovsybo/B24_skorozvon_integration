from pydantic import BaseModel, field_validator, Field, AliasPath

from .db import get_field_value_by_id


class SkorozvonCall(BaseModel):
    title: str = Field(default="Лид")
    call_id: str = Field(validation_alias=AliasPath("call_id"), default="")
    name: str = Field(validation_alias=AliasPath("lead_name"), default="")
    phone: str = Field(validation_alias=AliasPath("lead_phones"), default="")
    comment: str = Field(validation_alias=AliasPath("lead_comment"), default="")
    scenario_id: int = Field(validation_alias=AliasPath("call_scenario_id"), default="")
    result_name: str = Field(validation_alias=AliasPath("call_result_result_name"), default="")


class SkorozvonForm(BaseModel):
    title: str = Field(default="Анкетный")
    call_id: str = Field(validation_alias=AliasPath("call_id"), default="")
    name: str = Field(validation_alias=AliasPath("lead_name"), default="")
    phone: str = Field(validation_alias=AliasPath("lead_phones"), default="")
    comment: str = Field(validation_alias=AliasPath("lead_comment"), default="")
    scenario_id: int = Field(validation_alias=AliasPath("call_scenario_id"), default="")
    form: str = Field(validation_alias=AliasPath("form_response"), default="")
    result_id: str = Field(validation_alias=AliasPath("call_result_id"), default="")


class BitrixDeal(BaseModel):
    stage_id: str = Field(validation_alias=AliasPath("result", "STAGE_ID"), default="")
    lead_name: str = Field(validation_alias=AliasPath("result", "UF_CRM_1664819061161"), default="")
    phone: str = Field(validation_alias=AliasPath("result", "UF_CRM_1665719874029"), default="")
    lead_type: str = Field(validation_alias=AliasPath("result", "UF_CRM_1664819174514"), default="")
    lead_qualification: str = Field(validation_alias=AliasPath("result", "UF_CRM_1664819117290"), default="")
    lead_comment: str = Field(validation_alias=AliasPath("result", "UF_CRM_1664819040131"), default="")
    link_to_audio: str = Field(validation_alias=AliasPath("result", "UF_CRM_1664819217017"), default="")
    date: str = Field(validation_alias=AliasPath("result", "DATE_MODIFY"), default="")
    city: str = Field(validation_alias=AliasPath("result", "UF_CRM_1687464323171"), default="")
    country: str = Field(validation_alias=AliasPath("result", "UF_CRM_1688409961271"), default="")
    car_mark: str = Field(validation_alias=AliasPath("result", "UF_CRM_1694678311862"), default="")
    car_model: str = Field(validation_alias=AliasPath("result", "UF_CRM_1694678343732"), default="")

    # @field_validator("lead_type")
    # def lead_type_validator(cls, lead_type):
    #     return get_field_value_by_id("Тип лида", lead_type)
    #
    # @field_validator("lead_qualification")
    # def lead_qualification_validator(cls, lead_qualification):
    #     return get_field_value_by_id("Квалификация лида", lead_qualification)
    #
    # @field_validator("city")
    # def city_validator(cls, city):
    #     return get_field_value_by_id("Город", city)
    #
    # @field_validator("country")
    # def country_validator(cls, country):
    #     return get_field_value_by_id("Страна", country)
    #
    # @field_validator("phone")
    # def phone_validator(cls, phone):
    #     remove_symbols = "+_-() "
    #     for symbol in remove_symbols:
    #         phone = phone.replace(symbol, "")
    #     if phone:
    #         return f"7{phone[-10:]}"
    #     return phone
    #
    # # TODO: datetime.fromisoformat
    # @field_validator("date")
    # def data_validator(cls, date):
    #     return ".".join(date.split("T")[0].split("-")[::-1])


def flatten_data(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

class BitrixDealCreation(Exception):
    pass


class ScenarioNotFoundError(BitrixDealCreation):
    pass


class UnsuccessfulLeadCreationError(BitrixDealCreation):
    pass


class CategoryNotFoundError(BitrixDealCreation):
    pass

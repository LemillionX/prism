from actions.base import AddEntityBase


class AddAsset(AddEntityBase):
    def __init__(self):
        super().__init__(entity_type="Asset")


class AddShot(AddEntityBase):
    def __init__(self):
        super().__init__(entity_type="Shot")

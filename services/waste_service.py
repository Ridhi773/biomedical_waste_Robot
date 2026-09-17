from dao.waste_dao import WasteDAO


class WasteService:

    def __init__(self):
        self.waste_dao = WasteDAO()

    def list_waste_types(self):
        return self.waste_dao.get_all_waste_types()

    def get_waste_type(self, waste_type_id):
        return self.waste_dao.get_waste_type_by_id(waste_type_id)

    def list_locations(self):
        return self.waste_dao.get_all_locations()

    def get_location(self, location_id):
        return self.waste_dao.get_location_by_id(location_id)

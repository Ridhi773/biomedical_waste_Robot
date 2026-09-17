from dao.collection_dao import CollectionDAO
from models.collection import Collection
from services.compartment_service import CompartmentService
from utils.validators import is_positive_number


class CollectionService:

    def __init__(self):
        self.collection_dao = CollectionDAO()
        self.compartment_service = CompartmentService()

    def record_collection(self, robot_id, compartment_id, waste_type_id, weight_kg, location_id=None):
        """
        Records a waste collection event, then updates the target compartment's fill level.
        Returns (success: bool, message: str).
        """
        if not is_positive_number(weight_kg):
            return False, "Weight must be a positive number."

        ok, msg = self.compartment_service.add_waste(compartment_id, float(weight_kg))
        if not ok:
            return False, msg

        self.collection_dao.create(Collection(
            collection_id=None,
            robot_id=robot_id,
            compartment_id=compartment_id,
            waste_type_id=waste_type_id,
            weight_kg=float(weight_kg),
            location_id=location_id,
        ))
        return True, msg

    def list_all(self):
        return self.collection_dao.get_all()

    def list_for_robot(self, robot_id):
        return self.collection_dao.get_by_robot(robot_id)

    def list_with_details(self):
        return self.collection_dao.get_with_details()

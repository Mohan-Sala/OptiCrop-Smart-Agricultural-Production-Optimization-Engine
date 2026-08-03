from enum import Enum


class UserRole(str, Enum):
    FARMER = "Farmer"
    RESEARCHER = "Researcher"
    POLICY_MAKER = "PolicyMaker"
    ADMIN = "Admin"

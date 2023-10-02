"""Data classes for the entities returned by the API."""
import hashlib
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ListType(str, Enum):
    PEP = "pep"
    SANCTION = "sanction"


@dataclass(frozen=True)
class DateOfBirth:
    date: str


@dataclass(frozen=True)
class Reference:
    name: str
    id_in_list: Optional[str]


@dataclass(frozen=True)
class OtherName:
    name: str
    type: str


@dataclass(frozen=True)
class PoliticalParty:
    title: str


@dataclass(frozen=True)
class Role:
    title: str


@dataclass(frozen=True)
class PlaceOfBirth:
    location: str
    country: Optional[str]


@dataclass(frozen=True)
class Entity:
    name: str

    @property
    @abstractmethod
    def rationale(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def entity_summary(self) -> str:
        pass


COLUMN_NAME = "Name"
COLUMN_FIRST_NAME = "FirstName"
COLUMN_MIDDLE_NAME = "MiddleName"
COLUMN_LAST_NAME = "LastName"
COLUMN_GENDER = "Gender"
COLUMN_DOB = "DOB"
COLUMN_COUNTRY = "Country"

ALL_COLUMNS = [
    COLUMN_NAME,
    COLUMN_FIRST_NAME,
    COLUMN_MIDDLE_NAME,
    COLUMN_LAST_NAME,
    COLUMN_GENDER,
    COLUMN_DOB,
    COLUMN_COUNTRY,
]


@dataclass(frozen=True, eq=True)
class Person(Entity):  # pylint: disable=too-many-instance-attributes
    update_at: Optional[str]
    category: str
    name: str
    deceased: bool
    deceased_date: Optional[str]
    gender: Optional[Gender]
    original_script_name: Optional[str]
    dates_of_birth: list[DateOfBirth]
    places_of_birth: list[PlaceOfBirth]
    reference_type: str
    references: list[Reference]
    program: Optional[str]
    occupations: list[str]
    political_parties: list[PoliticalParty]
    roles: list[Role]
    nationality: str
    citizenship: str
    other_names: list[OtherName]
    summary: Optional[str]
    match_rate: float

    @property
    def rationale(self) -> Optional[str]:  # pylint: disable=too-many-return-statements
        if self.deceased:
            return f"Deceased {self.deceased_date}"

        if self.original_script_name:
            return f"Not an Indonesian name: {self.original_script_name}"

        if self.program and "syr" in self.program.lower():
            return "Suspect in Syrian conflict"

        if self.citizenship != "" and "indonesia" not in self.citizenship.lower():
            return f"Foreigner: {self.citizenship}"

        if "politician" in self.occupations:
            return self.politician_summary

        if self.roles:
            return f"Public figure: {self.roles[0].title}"

        return None

    @property
    def politician_summary(self):
        summary = self.entity_summary
        affiliation = (
            f" for {self.political_parties[0].title}" if self.political_parties else ""
        )
        return f"Politician, {summary}{affiliation}"

    @property
    def entity_summary(self):
        if self.summary:
            return self.summary

        name = (
            ", ".join([other.name for other in self.other_names])
            if self.other_names
            else self.name
        )
        origin = (
            f", in {self.places_of_birth[0].location}" if self.places_of_birth else ""
        )
        born = f", born {self.dates_of_birth[0].date}" if self.dates_of_birth else ""
        gender = f", {self.gender.value}" if self.gender else ""
        return f"{name}{gender}{born}{origin}"

    def __hash__(self):
        return hash(tuple(self.references))

    @staticmethod
    def from_json(person: dict):
        gender = person.get("gender", None)
        return Person(
            update_at=person.get("updateAt", None),
            category=person["category"],
            name=person["name"],
            deceased=person.get("deceased", False),
            deceased_date=person.get("deceasedDate"),
            gender=None if not gender else Gender(gender.strip().lower()),
            original_script_name=person.get("originalScriptName"),
            dates_of_birth=[
                DateOfBirth(date=dob["date"]) for dob in person.get("datesOfBirth", [])
            ],
            places_of_birth=[
                PlaceOfBirth(
                    location=pob.get("location", ""), country=pob.get("country")
                )
                for pob in person.get("placesOfBirth", [])
            ],
            reference_type=person["referenceType"],
            references=[
                Reference(name=ref["name"], id_in_list=ref.get("idInList"))
                for ref in person.get("references", [])
            ],
            program=person.get("program", None),
            occupations=person.get("occupations", []),
            political_parties=[
                PoliticalParty(title=party["title"])
                for party in person.get("politicalParties", [])
            ],
            roles=[Role(title=role["title"]) for role in person.get("roles", [])],
            nationality=person["nationality"],
            citizenship=person["citizenship"],
            other_names=[
                OtherName(name=other_name["name"], type=other_name["type"])
                for other_name in person.get("otherNames", [])
            ],
            summary=person.get("summary", None),
            match_rate=person["matchRate"],
        )


@dataclass
class OrganisationReference:
    name: str
    since: Optional[str]
    until: Optional[str]
    id_in_list: str


@dataclass
class Address:
    address1: str
    address2: str
    address3: str
    city: str
    region: str
    postal_code: str
    country: str
    text: str
    note: str


@dataclass
class Identity:
    number: str
    country: str
    note: str
    type: str


@dataclass
class Contact:
    value: str
    type: str


@dataclass
class Link:
    url: str
    type: str


@dataclass(frozen=True, eq=True)
class Organisation(Entity):  # pylint: disable=too-many-instance-attributes
    category: str
    original_script_name: str
    reference_type: Optional[str]
    references: list[OrganisationReference]
    program: Optional[str]
    addresses: list[Address]
    other_names: list[OtherName]
    identities: list[Identity]
    contacts: list[Contact]
    images: list[str]
    links: list[Link]
    sources: list[str]
    basis: Optional[str]
    summary: Optional[str]
    match_rate: int

    @property
    def entity_summary(self) -> str:
        return self.name

    @property
    def rationale(self) -> Optional[str]:
        return None


@dataclass(frozen=True, eq=True)
class ResultEntity:
    date: str
    scan_id: str
    number_of_matches: int
    entities: list[Entity]


@dataclass(frozen=True, eq=True)
class PersonScanResult(ResultEntity):
    number_of_pep_matches: int
    number_of_sip_matches: int

    @staticmethod
    def from_json(data: dict):
        return PersonScanResult(
            date=data["date"],
            scan_id=data["scanId"],
            number_of_matches=data["numberOfMatches"],
            number_of_pep_matches=data["numberOfPepMatches"],
            number_of_sip_matches=data["numberOfSipMatches"],
            entities=[Person.from_json(person) for person in data.get("persons", [])],
        )


@dataclass(frozen=True)
class EntityToScan:
    name: str
    country: str

    @property
    @abstractmethod
    def hash(self) -> str:
        pass


@dataclass(frozen=True)
class OrganizationToScan(EntityToScan):
    name: str
    country: str

    @property
    def hash(self) -> str:
        joined = "".join([self.name, self.country])
        return hashlib.md5(joined.encode("utf-8")).hexdigest()

    @staticmethod
    def from_dataframe(frame: dict):
        return OrganizationToScan(name=frame["Name"], country=frame["Country"])


@dataclass(frozen=True)
class PersonToScan(EntityToScan):  # pylint: disable=too-many-instance-attributes
    name: str
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[Gender]
    dob: Optional[str]
    country: str
    list_type: Optional[ListType]
    included_lists: Optional[str]
    excluded_lists: Optional[str]
    match_rate: int = 50

    @property
    def hash(self) -> str:
        fields = [
            self.name,
            self.dob or "",
            self.first_name or "",
            self.last_name or "",
            self.gender or "",
        ]
        joined = "".join(field.replace("-", "") for field in fields)
        return hashlib.md5(joined.encode("utf-8")).hexdigest()

    @staticmethod
    def to_namescan_dob_format(dob: Optional[str]):
        if dob is None:
            return ""
        try:
            dtm = datetime.fromisoformat(dob)
            return dtm.strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return dob

    @staticmethod
    def from_dataframe(frame_dict: dict):
        gender = frame_dict.get(COLUMN_GENDER, None)
        return PersonToScan(
            name=frame_dict[COLUMN_NAME],
            first_name=frame_dict.get(COLUMN_FIRST_NAME),
            middle_name=frame_dict.get(COLUMN_MIDDLE_NAME),
            last_name=frame_dict.get(COLUMN_LAST_NAME),
            gender=None if not gender else Gender(gender.strip().lower()),
            dob=PersonToScan.to_namescan_dob_format(frame_dict.get(COLUMN_DOB)),
            country=frame_dict.get(COLUMN_COUNTRY, "Indonesia"),
            list_type=None,
            included_lists=None,
            excluded_lists=None,
            match_rate=50,
        )


@dataclass(frozen=True, eq=True)
class OrganisationScanResult(ResultEntity):
    @staticmethod
    def from_json(data: dict):
        return OrganisationScanResult(
            date=data["date"],
            scan_id=data["scanId"],
            number_of_matches=data["numberOfMatches"],
            entities=[
                Organisation(
                    category=org["category"],
                    name=org["name"],
                    original_script_name=org["originalScriptName"],
                    reference_type=org["referenceType"],
                    references=[
                        OrganisationReference(
                            name=ref["name"],
                            since=ref.get("since"),
                            until=ref.get("to"),
                            id_in_list=ref["idInList"],
                        )
                        for ref in org.get("references", [])
                    ],
                    program=org.get("program"),
                    addresses=[
                        Address(
                            address1=addr.get("address1"),
                            address2=addr.get("address2"),
                            address3=addr.get("address3"),
                            city=addr.get("city"),
                            region=addr.get("region"),
                            postal_code=addr.get("postalCode"),
                            country=addr.get("country"),
                            text=addr.get("text"),
                            note=addr.get("note"),
                        )
                        for addr in org.get("addresses", [])
                    ],
                    other_names=[
                        OtherName(name=name["name"], type=name["type"])
                        for name in org.get("otherNames", [])
                    ],
                    identities=[
                        Identity(
                            number=identity["number"],
                            country=identity.get("country"),
                            note=identity.get("note"),
                            type=identity.get("type"),
                        )
                        for identity in org.get("identities", [])
                    ],
                    contacts=[
                        Contact(value=contact["value"], type=contact["type"])
                        for contact in org.get("contacts", [])
                    ],
                    images=org.get("images"),
                    links=[
                        Link(url=link["url"], type=link["type"])
                        for link in org.get("links", [])
                    ],
                    sources=org.get("sources"),
                    basis=org.get("basis"),
                    summary=org["summary"],
                    match_rate=org["matchRate"],
                )
                for org in data.get("organisations", [])
            ],
        )

import json
from enum import StrEnum
from typing import Self

from jsonschema import Draft202012Validator
from haystack.dataclasses import Document

__all__ = "Database",

class LocationType(StrEnum):
    FILE = "file"
    DIRECTORY = "directory"
    WEBSITE = "website"

# Description of a valid layout of information in the index json file. Used to validate while loading.
index_schema = {
    "type": "object",
    "patternProperties": {
        "^.*$": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "location": {
                        "type": "string"
                    },
                    "location_type": {
                        "enum": list(LocationType)
                    }
                },
                "required": [
                    "keywords",
                    "location",
                    "location_type"
                ],
                "additionalProperties": False
            }
        }
    },
    "additionalProperties": False
}
Draft202012Validator.check_schema(index_schema)
index_validator = Draft202012Validator(index_schema)

class Link:
    """
    Represents a link between a collection of keywords and a file containing some text.
    """

    __slots__ = "keywords", "location", "location_type"

    def __init__(self, keywords: list[str], location: str, location_type: LocationType) -> None:
        self.keywords: list[str] = keywords
        self.location: str = location
        self.location_type: LocationType = location_type

    def read_document(self) -> Document:
        match self.location_type:
            case LocationType.FILE:
                with open(self.location, "r") as file:
                    return Document(
                        id = self.location,
                        content = file.read()
                    )
            case LocationType.DIRECTORY:
                raise NotImplemented()
            case LocationType.WEBSITE:
                raise NotImplemented()
            case _:
                assert False, "Unreachable"

    def match_keywords(self, text: str) -> bool:
        return any(word in self.keywords for word in text.split())

class Subject:
    """
    Represents a subject that has links to relevant subject information.
    """

    __slots__ = "name", "links"

    def __init__(self, name: str, links: list[Link]) -> None:
        self.name: str = name
        self.links: list[Link] = links

    @classmethod
    def from_raw_links(cls, name: str, data: list[dict[str, str | list]]) -> Self:
        links: list[Link] = []
        for link in data:
            links.append(Link(link["keywords"], link["location"], LocationType(link["location_type"])))
        self = object.__new__(cls)
        self.__init__(name, links)
        return self

class Database:
    """
    Represents a simple database that can fetch documents for use with haystack.
    """

    __slots__ = "index_path", "subjects"

    def __init__(self, index_path: str) -> None:
        self.index_path: str = index_path
        self.subjects: list[Subject] = []
        self.update_data()

    def update_data(self) -> None:
        with open(self.index_path, "r") as file:
            index_data: dict[str, list] = json.load(file)

        index_validator.validate(index_data)

        self.subjects = [
            Subject.from_raw_links(subject_name, links)
            for subject_name, links in index_data.items()
        ]

    def fetch_relevant_documents(self, subject_name: str, text: str) -> list[Document]:
        for subject in self.subjects:
            if subject.name == subject_name:
                return [
                    link.read_document()
                    for link in subject.links
                    if link.match_keywords(text)
                ]
        else:
            raise ValueError(f"{subject_name} is not a valid subject name.")

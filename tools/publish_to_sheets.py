from __future__ import annotations

import os
from googleapiclient.discovery import build
from google.auth import default

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]

def update_tab(spreadsheets_resource, tab: str, values: list[list[str]]) -> None:
    spreadsheets_resource.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{tab}!A1",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()

def main() -> None:
    creds, _ = default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)

    spreadsheets = service.spreadsheets()

    elements = [
        ["id", "label", "type", "family"],
        ["faith", "Faith", "virtue", "theological"],
    ]
    connections = [
        ["from", "to", "type"],
        ["faith", "charity", "perfected_by"],
    ]

    update_tab(spreadsheets, "elements", elements)
    update_tab(spreadsheets, "connections", connections)

if __name__ == "__main__":
    main()


"""
from __future__ import annotations
import os
from googleapiclient.discovery import build
from google.auth import default

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]

def update_tab(service, tab: str, values: list[list[str]]) -> None:
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{tab}!A1",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()

def main() -> None:
    creds, _ = default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
    sheets = build("sheets", "v4", credentials=creds).spreadsheets()

    # Minimal smoke-test payload (replace later with real export)
    elements = [
        ["id", "label", "type", "family"],
        ["faith", "Faith", "virtue", "theological"],
    ]
    connections = [
        ["from", "to", "type"],
        ["faith", "charity", "perfected_by"],
    ]

    update_tab(sheets, "elements", elements)
    update_tab(sheets, "connections", connections)

if __name__ == "__main__":
    main()
"""
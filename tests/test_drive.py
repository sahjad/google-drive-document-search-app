from app.connectors.drive_connector import GoogleDriveConnector

def test_drive_listing():
    connector = GoogleDriveConnector()
    files = connector.list_supported_files()

    print(f"Found {len(files)} supported file(s):")
    for file in files:
        print(f"- {file['name']} ({file['mimeType']}) | ID: {file['id']}")

if __name__ == "__main__":
    test_drive_listing()
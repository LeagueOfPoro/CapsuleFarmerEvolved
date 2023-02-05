import requests as req


class VersionManager:

    @staticmethod
    def get_latest_tag():
        latest_tag_response = req.get("https://api.github.com/repos/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest")
        if 'application/json' in latest_tag_response.headers.get('Content-Type', ''):
            latest_tag_json = latest_tag_response.json()
            if "tag_name" in latest_tag_json:
                return float(latest_tag_json["tag_name"][1:])
        return 0.0

    @staticmethod
    def is_latest_version(current_version):
        return current_version >= VersionManager.get_latest_tag()

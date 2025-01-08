import io
import os

import qrcode
import requests

from dotenv import load_dotenv


# Load my .env file :)
load_dotenv()

def create_qr_code(url: str):
    qr = qrcode.QRCode(
        box_size=10,
        border=3,
    )
    qr.add_data(url)
    img = qr.make_image(fill_color="black", back_color="white")

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io # The PNG file to return :)


class CheckViruses:
    def __init__(self):
        self.google_api_key = os.environ['GOOGLE_SAFE_BROWSING_KEY']
        self.virustotal_api_key = os.environ['VIRUSTOTAL_KEY']



    def check_viruses(self, url: str):
        return self._check_google(url) or self._check_virustotal(url) #or self._check_phishtank(url)


    def _check_google(self, url: str):
        data = {
            "client": {
                "clientId": "felixgao",
                "clientVersion": "0.1.0dev"
            },
            "threatInfo": {
                "threatTypes": [
                    "THREAT_TYPE_UNSPECIFIED",
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION",
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }

        response = requests.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.google_api_key}",
            json=data
        )
        response.raise_for_status()
        return "matches" in response.json()


    def _check_virustotal(self, url: str):
        response = requests.get(
            "https://www.virustotal.com/vtapi/v2/url/report",
            params={
                'apikey': self.virustotal_api_key,
                'resource': url
            }
        )
        response.raise_for_status()
        return response.json().get('positives', 0) > 0


    """
    @staticmethod  # No API key so self isn't needed, thus staticmethod
    def _check_phishtank(url: str):
        response = requests.post(
            'https://checkurl.phishtank.com/checkurl/',
            headers={
                "User-Agent": 'phishtank/felixgao-url-shortener' # Assign a custom user agent to avoid extra ratelimits
            },
            data={
                'format': 'json',
                'url': url
            }
        )
        response.raise_for_status()
        return response.json().get('results', {}).get('in_database', False)
    """


    #def _check_phish_directory(self, url: str):
    #    response = requests.get(
    #        'https://api.phish.directory/domain/check',
    #        headers={
    #            "Authorization": f'Bearer {self.phishtank_api_key}'
    #        },
    #        params={
    #            "domain": urllib.parse.quote_plus(url)
    #        }
    #    )
    #    response.raise_for_status()
    #    return response.json()


if __name__ == "__main__":
    virus_checker = CheckViruses()
    print(virus_checker.check_viruses("https://auth-ext-coinbasehelp.webflow.io/"))

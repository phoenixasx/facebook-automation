#!/usr/bin/env python3
"""
Facebook Automation Post Generator
Replicates the n8n workflow logic for GitHub Actions
Handles: Persona selection, vibe assignment, news fetching, AI generation, image download, Facebook posting
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)


class PersonaAndVibeSelector:
    """Selects persona and vibe based on date and day of year"""

    PERSONAS = [
        {
            'gender': 'babae',
            'callouts': ['sis', 'girl', 'bestie', 'ate'],
            'flavor': 'OFW mom energy — sweet sa labas pero biblical ang wrath pag nagalit. Laging may iced coffee at receipts.'
        },
        {
            'gender': 'lalaki',
            'callouts': ['bro', 'pare', 'kuya', 'dude'],
            'flavor': 'Night shift worker vibes — tahimik pero sharp. Ang honest friend na masakit pag nagsalita pero totoo naman.'
        },
        {
            'gender': 'queer/LGBT',
            'callouts': ['bes', 'mare', 'beh', 'teh'],
            'flavor': 'Sabog energy, grounded values. Sass at grace sa iisang katawan. Living their truth habang exhausted sa buhay.'
        }
    ]

    PERSONA_NAMES = {
        'babae': 'Malditang Relihiyosa',
        'lalaki': 'Malditong Banal',
        'queer/LGBT': 'Marites Eme'
    }

    PERSONA_TAGLINES = {
        'babae': 'preach:',
        'lalaki': 'said:',
        'queer/LGBT': 'spills:'
    }

    VIBES = [
        {
            'type': 'BRIGHT_REAL_TALK',
            'label': 'Bright Real Talk',
            'weight': 2,
            'description': 'Sinasampal ang reader ng katotohanan tungkol sa generational gaslighting o toxic habits, pero may kasamang solusyon at pag-asa. May pagmamahal at paggabay.'
        },
        {
            'type': 'RELATABLE_JOY',
            'label': 'Relatable Joy',
            'weight': 2,
            'description': 'Nakikiramay sa pagod ng reader, validates ang feeling — PERO may malditang kurot sa dulo para magising sila at makahanap ng saya. Yakapin ka, tapos kurutin, tapos tawanan ang buhay.'
        },
        {
            'type': 'HOPE_AND_CELEBRATION',
            'label': 'Hope and Celebration',
            'weight': 4,
            'description': 'High-energy praise, hope, lighthearted family humor, at pure inspiration. Yung post na nagpapangiti kahit pagod ka, at nagbibigay lakas para lumaban.'
        }
    ]

    @staticmethod
    def get_day_of_year(date: datetime) -> int:
        """Get day of year (0-365)"""
        return (date - datetime(date.year, 1, 1)).days

    @staticmethod
    def get_week_number(date: datetime) -> int:
        """Get week number for persona cycling"""
        return int(date.timestamp() / (7 * 24 * 60 * 60))

    @classmethod
    def select_persona(cls, date: datetime) -> Dict:
        """Select persona based on week number"""
        week_num = cls.get_week_number(date)
        persona = cls.PERSONAS[week_num % 3]
        return persona

    @classmethod
    def select_vibe(cls, date: datetime) -> Dict:
        """Select vibe based on day of year"""
        day_of_year = cls.get_day_of_year(date)
        expanded_pool = []
        for vibe in cls.VIBES:
            expanded_pool.extend([vibe] * vibe['weight'])
        selected_vibe = expanded_pool[day_of_year % len(expanded_pool)]
        return selected_vibe

    @classmethod
    def get_callout(cls, date: datetime, persona: Dict) -> str:
        """Get a callout word for the persona"""
        day_of_year = cls.get_day_of_year(date)
        callouts = persona['callouts']
        return callouts[day_of_year % len(callouts)]


class DayConfigSelector:
    """Selects day-specific configuration based on day of week"""

    DAY_CONFIGS = {
        0: {
            'day': 'Sunday',
            'theme': 'Gratitude / God / Counting Blessings',
            'imageStyle': 'sunny, warm, colorful Filipino scene, vibrant market, children playing, family gathering, bright natural light',
            'imageMood': 'joyful and hopeful',
            'adSlogan': 'Nescafe: Sarap ng umaga',
            'topics': [
                'mga blessings na hindi napapansin kasi busy sa inggit sa iba',
                'pasasalamat kahit hindi pa kumpleto ang buhay',
                'rest as worship — hindi tamad ang magpahinga',
                'gratitude bilang giyera laban sa anxiety'
            ]
        },
        1: {
            'day': 'Monday',
            'theme': 'Work / Hustle / Toxic Workplace',
            'imageStyle': 'bright, dynamic Filipino workplace, collaborative team, natural light, vibrant colors, smiling faces, modern office with traditional Filipino elements',
            'imageMood': 'determined and thriving',
            'adSlogan': 'Nike: Just Do It',
            'topics': [
                'toxic hustle culture na sinasabi pang blessing ang pagod',
                'boss na hindi ka nire-respeto pero inaasahang loyal ka',
                'overtime na unpaid pero pag nag-late ka issues agad',
                'workplace favoritism na nakikita mo pero pinapaligtas ka ng HR',
                'burnout na pina-pray lang pero walang sinasabi sa manager'
            ]
        },
        2: {
            'day': 'Tuesday',
            'theme': 'Friendships / Fake Friends / Loneliness',
            'imageStyle': 'vibrant Filipino community gathering, friends laughing at a lively carinderia, warm street lights, group of people enjoying each other\'s company',
            'imageMood': 'connected and joyful',
            'adSlogan': 'Globe: Para sa isa\'t isa',
            'topics': [
                'kaibigan na nandoon lang pag kailangan nila ng bagay sa yo',
                'loneliness na mas masahol pa sa bad company',
                'friendship na one-sided na pero ikaw pa rin ang nagso-sorry',
                'barkada na lagi kang pinagtatawanan pero joke lang daw',
                'outgrowing friends na hindi mo kayang aminin sa sarili mo'
            ]
        },
        3: {
            'day': 'Wednesday',
            'theme': 'Body / Food / Diet Culture / Health',
            'imageStyle': 'bright and abundant Filipino market, colorful fresh produce, happy vendors and customers, natural light, lively atmosphere',
            'imageMood': 'nourished and vibrant',
            'adSlogan': 'L\'Oreal: Because you\'re worth it',
            'topics': [
                'diet culture na sinabing masama ang kumain ng masarap',
                'body shaming mula sa pamilya mo mismo',
                'health journey na puro aesthetics walang actual health',
                'pagkain bilang kaligayahan hindi kaaway',
                'mental health na di pa rin tinatrato as real health'
            ]
        },
        4: {
            'day': 'Thursday',
            'theme': 'Money / Utang / OFW Remittance / Financial Trauma',
            'imageStyle': 'bright and hopeful Filipino financial scene, hands counting Philippine peso bills with a smile, small business owner thriving, warm natural light, symbols of growth and prosperity',
            'imageMood': 'financially empowered and hopeful',
            'adSlogan': 'BDO: We find ways',
            'topics': [
                'utang na loob na ginagamit para kontrolin ka',
                'family financial trauma na dinala mo sa adulthood',
                'OFW remittance pressure — nagtatrabaho ka abroad pero ikaw mismo wala',
                'kakilala na laging humihingi pero hindi nagbabayad',
                'generational poverty na pino-pray lang walang systemic change'
            ]
        },
        5: {
            'day': 'Friday',
            'theme': 'Love / Relationships / Heartbreak',
            'imageStyle': 'vibrant Filipino celebration of love, couple laughing under string lights, warm glow of sunset, joyful gathering of friends and family',
            'imageMood': 'loved and thriving',
            'adSlogan': 'Jollibee: Joy sa bawat sandali',
            'topics': [
                'trauma bonding na inakala mong love',
                'minahal mo ng buong puso pero half-hearted lang ang binigay sa yo',
                'long distance — pag-ibig na binubuhay ng remittance at prayers',
                'red flags na inignore mo kasi mahal mo sila',
                'heartbreak na hindi mo kayang i-admit sa barkada'
            ]
        },
        6: {
            'day': 'Saturday',
            'theme': 'Family / Toxic Parents / Generational Trauma',
            'imageStyle': 'warm, multi-generational Filipino family gathering, laughter and togetherness, home-cooked meal, natural light, intimate family moments',
            'imageMood': 'warm and connected',
            'adSlogan': 'Sprite: Obey Your Thirst',
            'topics': [
                'toxic parents na ginagawa kang emotional support nila',
                'parental guilt-tripping na "lahat ginawa ko para sa inyo"',
                'siblings na mas favored pero mas irresponsible',
                'family secrets na everyone knows pero hindi nidiscuss',
                'generational trauma na ipinasa from parent to child'
            ]
        }
    }

    @classmethod
    def get_config(cls, date: datetime) -> Dict:
        """Get day configuration based on day of week"""
        day_of_week = date.weekday()
        # Convert Python weekday (0=Monday) to our config (0=Sunday)
        config_day = (day_of_week + 1) % 7
        return cls.DAY_CONFIGS.get(config_day, cls.DAY_CONFIGS[0])


class NewsAPI:
    """Fetch trending Philippine news"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"

    def fetch_trending_news(self, country: str = 'ph', limit: int = 5) -> List[Dict]:
        """Fetch top headlines from Philippines"""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'country': country,
                'apiKey': self.api_key,
                'pageSize': limit,
                'sortBy': 'publishedAt'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                logger.info(f"Fetched {len(articles)} news articles from Philippines")
                return articles
            else:
                logger.warning(f"NewsAPI error: {data.get('message')}")
                return []
        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            return []


class GeminiPostGenerator:
    """Generate Facebook posts using Google Gemini"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_post(self, context: Dict) -> str:
        """Generate a Facebook post based on context"""
        try:
            prompt = self._build_prompt(context)
            response = self.model.generate_content(prompt)
            post_text = response.text.strip()
            logger.info("Generated post successfully")
            return post_text
        except Exception as e:
            logger.error(f"Failed to generate post: {e}")
            return ""

    def _build_prompt(self, context: Dict) -> str:
        """Build the prompt for Gemini"""
        day_config = context.get('day_config', {})
        persona = context.get('persona', {})
        vibe = context.get('vibe', {})
        news = context.get('news', [])
        callout = context.get('callout', 'sis')

        news_text = "\n".join([f"- {article.get('title', '')}" for article in news[:3]])

        prompt = f"""
You are {persona.get('flavor', '')}.

Today is {day_config.get('day')}. The theme is: {day_config.get('theme')}.

Vibe: {vibe.get('description')}

Trending news in Philippines:
{news_text}

Write a Facebook post (150-250 words) that:
1. Addresses the reader as "{callout}"
2. Connects today's theme with the news or everyday Filipino life
3. Uses the {vibe.get('label')} vibe
4. Ends with a call-to-action or reflection
5. Feels authentic, not preachy
6. Uses Filipino-English code-switching naturally

Keep it conversational and real. No hashtags unless absolutely necessary.
"""
        return prompt


class PollinationsImageGenerator:
    """Generate images using Pollinations API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pollinations.ai/v1"

    def generate_image(self, prompt: str, style: str) -> Optional[str]:
        """Generate an image and return the URL"""
        try:
            full_prompt = f"{prompt}. Style: {style}. No text, no letters, no watermark."
            
            url = f"{self.base_url}/images"
            params = {
                'prompt': full_prompt,
                'model': 'flux-pro',
                'width': 1200,
                'height': 630,
                'seed': int(datetime.now().timestamp()) % 1000000
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            image_url = response.url
            logger.info(f"Generated image: {image_url}")
            return image_url
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            return None

    def download_image(self, url: str, filename: str) -> Optional[str]:
        """Download image to local file"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            filepath = f"images/{filename}"
            os.makedirs('images', exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None


class FacebookAPI:
    """Post to Facebook"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"

    def post_with_image(self, page_id: str, message: str, image_path: str) -> Optional[str]:
        """Post message with image to Facebook page"""
        try:
            url = f"{self.base_url}/{page_id}/photos"
            
            with open(image_path, 'rb') as f:
                files = {'source': f}
                data = {
                    'message': message,
                    'access_token': self.access_token
                }
                response = requests.post(url, files=files, data=data, timeout=30)
            
            response.raise_for_status()
            result = response.json()
            post_id = result.get('post_id') or result.get('id')
            logger.info(f"Posted to Facebook: {post_id}")
            return post_id
        except Exception as e:
            logger.error(f"Failed to post to Facebook: {e}")
            return None

    def post_first_comment(self, post_id: str, comment_text: str) -> bool:
        """Post a first comment on the Facebook post"""
        try:
            url = f"{self.base_url}/{post_id}/comments"
            data = {
                'message': comment_text,
                'access_token': self.access_token
            }
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            logger.info(f"Posted first comment to {post_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to post comment: {e}")
            return False


class GoogleSheetsLogger:
    """Log post metadata to Google Sheets"""

    def __init__(self, sheets_id: str, credentials_json: Optional[str] = None):
        self.sheets_id = sheets_id
        self.credentials = self._get_credentials(credentials_json)
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def _get_credentials(self, credentials_json: Optional[str]):
        """Get Google Sheets credentials"""
        try:
            if credentials_json and os.path.exists(credentials_json):
                return Credentials.from_service_account_file(
                    credentials_json,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            else:
                # Use Application Default Credentials
                return google.auth.default(
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )[0]
        except Exception as e:
            logger.error(f"Failed to get Google Sheets credentials: {e}")
            return None

    def log_post(self, post_data: Dict) -> bool:
        """Log post metadata to Google Sheets"""
        try:
            if not self.credentials:
                logger.warning("Google Sheets credentials not available, skipping log")
                return False

            values = [[
                post_data.get('timestamp', ''),
                post_data.get('day', ''),
                post_data.get('persona', ''),
                post_data.get('vibe', ''),
                post_data.get('post_text', '')[:100],
                post_data.get('image_url', ''),
                post_data.get('facebook_post_id', ''),
                post_data.get('bible_verse', ''),
                post_data.get('first_comment_url', '')
            ]]

            body = {'values': values}
            self.service.spreadsheets().values().append(
                spreadsheetId=self.sheets_id,
                range='Sheet1!A:I',
                valueInputOption='RAW',
                body=body
            ).execute()

            logger.info("Logged post to Google Sheets")
            return True
        except Exception as e:
            logger.error(f"Failed to log to Google Sheets: {e}")
            return False


def main():
    """Main automation workflow"""
    try:
        logger.info("Starting Facebook automation workflow")

        # Get current time in Manila timezone
        now = datetime.now()
        logger.info(f"Current time: {now}")

        # Initialize APIs
        gemini_key = os.getenv('GEMINI_API_KEY')
        facebook_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        newsapi_key = os.getenv('NEWSAPI_KEY')
        sheets_id = os.getenv('GOOGLE_SHEETS_ID')
        pollinations_key = os.getenv('POLLINATIONS_API_KEY')

        if not all([gemini_key, facebook_token, newsapi_key, sheets_id, pollinations_key]):
            logger.error("Missing required environment variables")
            sys.exit(1)

        # Select persona, vibe, and day config
        persona = PersonaAndVibeSelector.select_persona(now)
        vibe = PersonaAndVibeSelector.select_vibe(now)
        day_config = DayConfigSelector.get_config(now)
        callout = PersonaAndVibeSelector.get_callout(now, persona)

        logger.info(f"Selected persona: {persona['gender']}, vibe: {vibe['type']}, day: {day_config['day']}")

        # Fetch news
        news_api = NewsAPI(newsapi_key)
        news = news_api.fetch_trending_news()

        # Generate post
        context = {
            'persona': persona,
            'vibe': vibe,
            'day_config': day_config,
            'news': news,
            'callout': callout
        }

        gemini = GeminiPostGenerator(gemini_key)
        post_text = gemini.generate_post(context)

        if not post_text:
            logger.error("Failed to generate post")
            sys.exit(1)

        # Add persona header
        persona_name = PersonaAndVibeSelector.PERSONA_NAMES[persona['gender']]
        tagline = PersonaAndVibeSelector.PERSONA_TAGLINES[persona['gender']]
        full_post = f"🤨 {persona_name} {tagline}\n\n{post_text}"

        logger.info(f"Generated post:\n{full_post}")

        # Generate image
        pollinations = PollinationsImageGenerator(pollinations_key)
        image_prompt = day_config['imageStyle']
        image_url = pollinations.generate_image(image_prompt, day_config['imageMood'])

        if image_url:
            image_path = pollinations.download_image(image_url, f"post_{now.strftime('%Y%m%d_%H%M%S')}.jpg")
        else:
            logger.warning("Failed to generate image, continuing without image")
            image_path = None

        # Post to Facebook
        facebook = FacebookAPI(facebook_token)
        # You'll need to extract your page ID from your Facebook setup
        page_id = os.getenv('FACEBOOK_PAGE_ID', '')
        
        if page_id and image_path:
            post_id = facebook.post_with_image(page_id, full_post, image_path)
            if post_id:
                # Post first comment
                first_comment = "Basahin ang buong post para sa mas maraming insights! 💭"
                facebook.post_first_comment(post_id, first_comment)
        else:
            logger.warning("Skipping Facebook post: missing page ID or image")
            post_id = None

        # Log to Google Sheets
        sheets = GoogleSheetsLogger(sheets_id)
        log_data = {
            'timestamp': now.isoformat(),
            'day': day_config['day'],
            'persona': persona['gender'],
            'vibe': vibe['type'],
            'post_text': post_text,
            'image_url': image_url,
            'facebook_post_id': post_id or 'N/A',
            'bible_verse': '',
            'first_comment_url': ''
        }
        sheets.log_post(log_data)

        logger.info("Workflow completed successfully")

    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

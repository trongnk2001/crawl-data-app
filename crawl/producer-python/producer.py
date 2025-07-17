import os
import time
import json
import requests
from bs4 import BeautifulSoup
from confluent_kafka import Producer
import re

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC = os.getenv('INPUT_TOPIC', 'youtube-raw-data')

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'youtube-crawler-producer',
    'message.timeout.ms': 10000,
    'socket.timeout.ms': 10000,
    'socket.keepalive.enable': True,
    'log.connection.close': False
}


class YouTubeCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def crawl_youtube_search(self, search_query):
        """
        Crawl trang search của YouTube
        Lưu ý: Đây là cách crawl cơ bản, YouTube có thể block hoặc thay đổi cấu trúc
        """
        try:
            # URL search của YouTube
            search_url = f"https://www.youtube.com/results?search_query={search_query}"

            print(f"Crawling: {search_url}")
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Tìm script tag chứa dữ liệu JSON
            script_tags = soup.find_all('script')
            video_data = []

            for script in script_tags:
                if script.string and 'var ytInitialData' in script.string:
                    # Trích xuất JSON data từ script
                    script_content = script.string
                    # Tìm phần JSON
                    start = script_content.find(
                        'var ytInitialData = ') + len('var ytInitialData = ')
                    end = script_content.find(';</script>', start)
                    if end == -1:
                        end = script_content.find(';', start)

                    try:
                        json_str = script_content[start:end]
                        data = json.loads(json_str)
                        video_data = self.extract_video_info(data)
                        break
                    except:
                        continue

            # Nếu không tìm thấy dữ liệu từ JSON, thử parse HTML trực tiếp
            if not video_data:
                video_data = self.extract_video_info_html(soup)

            return {
                'search_query': search_query,
                'crawl_timestamp': int(time.time()),
                'total_videos': len(video_data),
                'videos': video_data,
                'url': search_url
            }

        except Exception as e:
            print(f"Error crawling YouTube: {e}")
            return {
                'search_query': search_query,
                'crawl_timestamp': int(time.time()),
                'error': str(e),
                'videos': [],
                'url': search_url
            }

    def extract_video_info(self, data):
        """Trích xuất thông tin video từ JSON data"""
        videos = []
        try:
            # Điều hướng qua cấu trúc JSON phức tạp của YouTube
            contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get(
                'primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])

            for content in contents:
                if 'itemSectionRenderer' in content:
                    items = content['itemSectionRenderer'].get('contents', [])
                    for item in items:
                        if 'videoRenderer' in item:
                            video_info = self.parse_video_renderer(
                                item['videoRenderer'])
                            if video_info:
                                videos.append(video_info)
        except Exception as e:
            print(f"Error extracting video info from JSON: {e}")

        return videos

    def parse_video_renderer(self, video_renderer):
        """Parse thông tin từ videoRenderer"""
        try:
            video_info = {
                'video_id': video_renderer.get('videoId', ''),
                'title': '',
                'channel': '',
                'views': '',
                'duration': '',
                'published_time': '',
                'description': ''
            }

            # Title
            title_runs = video_renderer.get('title', {}).get('runs', [])
            if title_runs:
                video_info['title'] = title_runs[0].get('text', '')

            # Channel
            owner_text = video_renderer.get('ownerText', {}).get('runs', [])
            if owner_text:
                video_info['channel'] = owner_text[0].get('text', '')

            # Views
            view_count = video_renderer.get('viewCountText', {})
            if 'simpleText' in view_count:
                video_info['views'] = view_count['simpleText']

            # Duration
            length_text = video_renderer.get('lengthText', {})
            if 'simpleText' in length_text:
                video_info['duration'] = length_text['simpleText']

            # Published time
            published_time = video_renderer.get('publishedTimeText', {})
            if 'simpleText' in published_time:
                video_info['published_time'] = published_time['simpleText']

            # Description
            description_snippet = video_renderer.get(
                'detailedMetadataSnippets', [])
            if description_snippet:
                desc_runs = description_snippet[0].get(
                    'snippetText', {}).get('runs', [])
                if desc_runs:
                    video_info['description'] = ''.join(
                        [run.get('text', '') for run in desc_runs])

            return video_info

        except Exception as e:
            print(f"Error parsing video renderer: {e}")
            return None

    def extract_video_info_html(self, soup):
        """Fallback: trích xuất thông tin từ HTML thuần"""
        videos = []
        try:
            # Tìm các thẻ video container (cấu trúc có thể thay đổi)
            video_containers = soup.find_all(
                'div', {'class': re.compile(r'ytd-video-renderer')})

            for container in video_containers[:10]:  # Giới hạn 10 video
                video_info = {
                    'video_id': '',
                    'title': '',
                    'channel': '',
                    'views': '',
                    'duration': '',
                    'published_time': '',
                    'description': ''
                }

                # Tìm title
                title_element = container.find('a', {'id': 'video-title'})
                if title_element:
                    video_info['title'] = title_element.get('title', '')
                    href = title_element.get('href', '')
                    if href and '/watch?v=' in href:
                        video_info['video_id'] = href.split(
                            '/watch?v=')[1].split('&')[0]

                # Tìm channel
                channel_element = container.find(
                    'a', {'class': re.compile(r'yt-simple-endpoint.*channel')})
                if channel_element:
                    video_info['channel'] = channel_element.get_text(
                        strip=True)

                # Tìm views và thời gian
                metadata = container.find_all(
                    'span', {'class': re.compile(r'style-scope.*metadata')})
                for meta in metadata:
                    text = meta.get_text(strip=True)
                    if 'views' in text.lower() or 'lượt xem' in text.lower():
                        video_info['views'] = text
                    elif 'ago' in text.lower() or 'trước' in text.lower():
                        video_info['published_time'] = text

                if video_info['title']:  # Chỉ thêm nếu có title
                    videos.append(video_info)

        except Exception as e:
            print(f"Error extracting from HTML: {e}")

        return videos


def delivery_report(err, msg):
    """Callback khi gửi message"""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(
            f'Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}')


def main():
    # Danh sách các từ khóa để crawl
    search_queries = [
        'python programming',
        'java tutorial',
        'kafka streams',
        'machine learning',
        'web development'
    ]

    crawler = YouTubeCrawler()
    producer = Producer(conf)

    try:
        for query in search_queries:
            print(f"\n--- Crawling for: {query} ---")

            # Crawl dữ liệu
            crawl_data = crawler.crawl_youtube_search(query)

            # Gửi dữ liệu đến Kafka
            message = {
                'id': f"{query}_{int(time.time())}",
                'timestamp': int(time.time()),
                'type': 'youtube_search',
                'data': crawl_data
            }

            try:
                producer.produce(
                    topic=TOPIC,
                    key=query,
                    value=json.dumps(message, ensure_ascii=False),
                    callback=delivery_report
                )
                producer.flush()
                print(f"✓ Sent data for query: {query}")
                print(f"  Found {len(crawl_data.get('videos', []))} videos")

            except Exception as e:
                print(f"✗ Error sending message: {e}")

            # Đợi giữa các request để tránh rate limiting
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nCrawler interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        producer.flush()
        print("Producer closed")


if __name__ == "__main__":
    print("Starting YouTube Crawler Producer...")
    main()

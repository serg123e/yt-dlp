import itertools

from .common import SearchInfoExtractor
from .yandexmusic import YandexMusicBaseIE, YandexMusicTrackIE
from ..utils import try_get


class YandexMusicSearchIE(YandexMusicBaseIE, SearchInfoExtractor):
    IE_NAME = 'yandexmusic:search'
    IE_DESC = 'Яндекс.Музыка - Поиск'
    _SEARCH_KEY = 'ymsearch'
    _TESTS = [{
        'url': 'ymsearch5:rain',
        'playlist_count': 5,
        'info_dict': {
            'id': 'rain',
            'title': 'rain',
        },
        # 'skip': 'Travis CI servers blocked by YandexMusic',
    }]

    _SEARCH_TYPES = 'track,wave,podcast,podcast_episode,clip,concert'

    def _search_results(self, query):
        for page in itertools.count(0):
            result = self._download_json(
                'https://api.music.yandex.ru/search/instant/mixed',
                query, f'Downloading page {page + 1}',
                query={
                    'text': query,
                    'type': self._SEARCH_TYPES,
                    'page': page,
                    'pageSize': 36,
                })['result']
            for item in result.get('results') or []:
                track = item.get('track') or {}
                track_id = track.get('id')
                album_id = try_get(track, lambda x: x['albums'][0]['id'])
                if not track_id or not album_id:
                    continue
                yield self.url_result(
                    f'https://music.yandex.ru/album/{album_id}/track/{track_id}',
                    ie=YandexMusicTrackIE.ie_key(), video_id=str(track_id))
            if result.get('lastPage'):
                break

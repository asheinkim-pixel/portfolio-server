"""
실시간 주가 데이터 서버
- 한국 주식 시세 조회
- CORS 문제 해결
- 간단한 REST API 제공
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import time
import os  # 환경변수 읽기 위해 추가

app = Flask(__name__)
CORS(app)  # CORS 문제 해결

# 주요 종목 코드 매핑 (빠른 검색용 + 폴백)
STOCK_CODES = {
    '삼성전자': '005930',
    'SK하이닉스': '000660',
    'LG에너지솔루션': '373220',
    '삼성바이오로직스': '207940',
    '현대차': '005380',
    '기아': '000270',
    'NAVER': '035420',
    '네이버': '035420',
    '카카오': '035720',
    'KB금융': '105560',
    '신한지주': '055550',
    '삼성물산': '028260',
    'POSCO홀딩스': '005490',
    '포스코홀딩스': '005490',
    'LG화학': '051910',
    '삼성SDI': '006400',
    '현대모비스': '012330',
    'LG전자': '066570',
    'SK이노베이션': '096770',
    '셀트리온': '068270',
    '삼성생명': '032830',
    'SK텔레콤': '017670',
    'KT&G': '033780',
    'LG생활건강': '051900',
    '한국전력': '015760',
    '삼성화재': '000810',
    'HD현대중공업': '329180',
    '기업은행': '024110',
    '우리금융지주': '316140',
    '하나금융지주': '086790',
    'SK': '034730',
    'LG': '003550',
    '에코프로비엠': '247540',
    '알테오젠': '196170',
    'HLB': '028300',
    '엘앤에프': '066970',
    '씨젠': '096530',
    '펄어비스': '263750',
    '크래프톤': '259960',
    '에코프로': '086520',
    '리노공업': '058470',
    '위메이드': '112040',
    '카카오게임즈': '293490',
    '셀트리온제약': '068760',
    '두산에너빌리티': '034020',
    '한화에어로스페이스': '012450',
    'SK스퀘어': '402340',
    '삼성전기': '009150',
    '고려아연': '010130',
    '한국항공우주': '047810',
    '포스코퓨처엠': '003670',
    # 추가 종목
    '효성중공업': '298040',
    'LS일렉트릭': '010120',
    'LS': '006260',
    '농협증권': '016420',
    'NH투자증권': '005940',
    'NH증권': '005940',
    '효성': '004800',
    '효성티앤씨': '298020',
    '효성첨단소재': '298050',
    '두산': '000150',
    '두산밥캣': '241560',
    'KT': '030200',
    '한화': '000880',
    '롯데케미칼': '011170',
    'GS': '078930',
    'SK바이오팜': '326030',
    # 주요 ETF
    'KODEX 200': '069500',
    '코덱스200': '069500',
    'KODEX레버리지': '122630',
    'KODEX 레버리지': '122630',
    'KODEX 인버스': '114800',
    'KODEX 금액티브': '0064K0',
    'TIGER 200': '102110',
    '타이거200': '102110',
    'KODEX 코스닥150': '229200',
    'TIGER 코스닥150': '251340',
    'KODEX 삼성그룹': '130680',
    'KODEX 반도체': '091160',
    'TIGER 2차전지테마': '305720',
    'KODEX 2차전지산업': '305540',
    'TIGER 미국S&P500': '360750',
    'TIGER 미국나스닥100': '133690',
    'KODEX 미국S&P500': '379800',
    'ACE 미국30년국채': '305080',
}

# 캐시 (API 호출 최소화)
price_cache = {}
search_cache = {}  # 검색 결과 캐시
cache_timeout = 10  # 10초 캐시


def search_stock_naver(query):
    """네이버 금융에서 종목 검색 - 검색 페이지 스크래핑 (주식 + ETF + 종목코드)"""
    try:
        # 캐시 확인
        cache_key = f"search_{query}"
        if cache_key in search_cache:
            cached_time, cached_result = search_cache[cache_key]
            if time.time() - cached_time < 300:  # 5분 캐시
                return cached_result
        
        # 종목코드로 직접 검색하는 경우
        # 6자리 숫자 또는 6자리 영숫자 조합 (예: 005930, 0064K0)
        if len(query) == 6 and (query.isdigit() or query.isalnum()):
            # 종목코드로 직접 조회
            try:
                url = f'https://finance.naver.com/item/main.naver?code={query}'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 종목명 추출 (여러 방법 시도)
                name = None
                
                # 방법 1: 일반 종목
                name_elem = soup.select_one('.wrap_company h2 a')
                if name_elem:
                    name = name_elem.text.strip()
                
                # 방법 2: ETF
                if not name:
                    name_elem = soup.select_one('.h_company h2')
                    if name_elem:
                        name = name_elem.text.strip()
                
                if name:
                    result = [{
                        'name': name,
                        'code': query.upper()  # 대문자로 통일
                    }]
                    search_cache[cache_key] = (time.time(), result)
                    return result
            except:
                pass  # 실패하면 일반 검색으로 진행
        
        # 네이버 금융 검색 페이지
        url = 'https://finance.naver.com/search/searchList.naver'
        params = {
            'query': query
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        
        # 검색 결과 테이블에서 종목 추출 (주식 + ETF)
        stock_items = soup.select('.tbl_search tbody tr')
        
        for item in stock_items[:20]:  # 상위 20개 (더 많이)
            try:
                # 종목명
                name_elem = item.select_one('td a.tltle')
                if not name_elem:
                    continue
                    
                name = name_elem.text.strip()
                
                # 종목코드 추출 (링크에서)
                link = name_elem.get('href', '')
                if 'code=' in link:
                    code = link.split('code=')[1].split('&')[0]
                    
                    # 6자리 코드 (숫자 또는 영숫자 조합)
                    if len(code) == 6:
                        results.append({
                            'name': name,
                            'code': code.upper()
                        })
            except Exception as e:
                continue
        
        # 중복 제거 (같은 코드가 여러 번 나올 수 있음)
        seen = set()
        unique_results = []
        for item in results:
            if item['code'] not in seen:
                seen.add(item['code'])
                unique_results.append(item)
        
        # 캐시 저장
        search_cache[cache_key] = (time.time(), unique_results)
        
        return unique_results
        
    except Exception as e:
        print(f"Search error for '{query}': {e}")
        import traceback
        traceback.print_exc()
        return []


def get_stock_price_naver(code):
    """네이버 금융에서 주가 정보 가져오기 (주식 + ETF 지원)"""
    try:
        url = f'https://finance.naver.com/item/main.naver?code={code}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 현재가 추출 (여러 방법 시도)
        price = None
        price_element = soup.select_one('.no_today .blind')
        if price_element:
            price = int(price_element.text.replace(',', '').strip())
        
        # 현재가를 못 찾으면 다른 방법 시도 (ETF용)
        if not price:
            price_element2 = soup.select_one('.rate_info .blind')
            if price_element2:
                price = int(price_element2.text.replace(',', '').strip())
        
        if not price:
            print(f"Price not found for {code}")
            return None
        
        # 등락 정보
        change = 0
        change_rate = 0
        
        try:
            # 방법 1: 일반 주식
            change_element = soup.select_one('.no_exday .blind')
            if change_element:
                change_text = change_element.text.replace(',', '').strip()
                exday_text = soup.select_one('.no_exday').text
                
                if '상승' in exday_text:
                    change = int(change_text)
                elif '하락' in exday_text:
                    change = -int(change_text)
                
                # 등락률
                rate_elements = soup.select('.no_exday .blind')
                if len(rate_elements) >= 2:
                    rate_text = rate_elements[1].text.replace('%', '').replace('+', '').replace('-', '').strip()
                    if rate_text:
                        change_rate = float(rate_text)
                        if '하락' in exday_text:
                            change_rate = -change_rate
            
            # 방법 2: ETF나 다른 구조
            if change == 0 and change_rate == 0:
                # 전일대비 찾기
                change_area = soup.select_one('.new_totalinfo .no_exday')
                if change_area:
                    spans = change_area.select('span')
                    for span in spans:
                        text = span.text.strip()
                        if text and text != '전일대비':
                            # 등락 금액
                            if ',' in text or text.replace('-', '').replace('+', '').replace(',', '').isdigit():
                                change_text = text.replace(',', '').replace('+', '').strip()
                                if change_text.startswith('-'):
                                    change = -int(change_text.replace('-', ''))
                                else:
                                    change = int(change_text)
                            # 등락률
                            elif '%' in text:
                                rate_text = text.replace('%', '').replace('+', '').replace('-', '').strip()
                                if rate_text:
                                    change_rate = float(rate_text)
                                    if text.startswith('-'):
                                        change_rate = -change_rate
        except Exception as e:
            print(f"Change rate extraction error for {code}: {e}")
            pass  # 등락 정보 없어도 계속 진행
        
        # 시가총액 추출 (실패해도 계속 진행)
        market_cap = price * 1000000  # 기본값
        
        try:
            # 방법 1: _market_sum
            market_cap_element = soup.select_one('#_market_sum')
            if market_cap_element:
                market_cap_text = market_cap_element.text.strip().replace(',', '').replace(' ', '')
                if '조' in market_cap_text:
                    num = market_cap_text.replace('조', '').strip()
                    market_cap = int(float(num) * 1000000000000)
                elif '억' in market_cap_text:
                    num = market_cap_text.replace('억', '').strip()
                    market_cap = int(float(num) * 100000000)
        except Exception as e:
            print(f"Market cap calculation error for {code}: {e}")
            pass
        
        return {
            'price': price,
            'change': change,
            'changeRate': round(change_rate, 2),
            'marketCap': market_cap
        }
        
    except Exception as e:
        print(f"Error fetching price for {code}: {e}")
        import traceback
        traceback.print_exc()
        return None


@app.route('/api/stock/<code>', methods=['GET'])
def get_stock(code):
    """특정 종목의 시세 조회"""
    
    # 캐시 확인
    cache_key = f"{code}_{int(time.time() / cache_timeout)}"
    if cache_key in price_cache:
        return jsonify(price_cache[cache_key])
    
    # 실시간 조회
    data = get_stock_price_naver(code)
    
    if data:
        result = {
            'success': True,
            'code': code,
            'price': f"{data['price']:,}",
            'change': data['change'],
            'changeRate': data['changeRate'],
            'marketCap': data['marketCap']
        }
        price_cache[cache_key] = result
        return jsonify(result)
    else:
        return jsonify({
            'success': False,
            'message': '시세 조회 실패'
        }), 404


@app.route('/api/search', methods=['GET'])
def search_stock():
    """종목 검색 - 네이버 금융 API 사용"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    # 네이버 API로 실시간 검색
    results = search_stock_naver(query)
    
    # 검색 결과가 없으면 로컬 STOCK_CODES에서도 검색
    if not results:
        for name, code in STOCK_CODES.items():
            if query.lower() in name.lower():
                results.append({
                    'name': name,
                    'code': code
                })
    
    return jsonify(results[:10])


@app.route('/api/stocks', methods=['GET'])
def get_all_stocks():
    """전체 종목 리스트"""
    stocks = [{'name': name, 'code': code} for name, code in STOCK_CODES.items()]
    return jsonify(stocks)


@app.route('/api/marketmap/<market>', methods=['GET'])
def get_marketmap(market):
    """마켓맵 데이터 조회 (코스피/코스닥)"""
    # 시장별 주요 종목 선정
    if market == 'kospi':
        target_stocks = [
            ('삼성전자', '005930'), ('SK하이닉스', '000660'),
            ('LG에너지솔루션', '373220'), ('삼성바이오로직스', '207940'),
            ('현대차', '005380'), ('기아', '000270'),
            ('NAVER', '035420'), ('카카오', '035720'),
            ('KB금융', '105560'), ('신한지주', '055550'),
            ('삼성물산', '028260'), ('POSCO홀딩스', '005490'),
            ('LG화학', '051910'), ('삼성SDI', '006400'),
            ('현대모비스', '012330'), ('LG전자', '066570'),
            ('SK이노베이션', '096770'), ('셀트리온', '068270'),
            ('삼성생명', '032830'), ('SK텔레콤', '017670'),
            ('KT&G', '033780'), ('LG생활건강', '051900'),
            ('한국전력', '015760'), ('삼성화재', '000810'),
            ('HD현대중공업', '329180'), ('기업은행', '024110'),
            ('우리금융지주', '316140'), ('하나금융지주', '086790'),
            ('SK', '034730'), ('LG', '003550'),
        ]
    else:  # kosdaq
        target_stocks = [
            ('에코프로비엠', '247540'), ('알테오젠', '196170'),
            ('HLB', '028300'), ('엘앤에프', '066970'),
            ('씨젠', '096530'), ('펄어비스', '263750'),
            ('크래프톤', '259960'), ('에코프로', '086520'),
            ('리노공업', '058470'), ('위메이드', '112040'),
            ('카카오게임즈', '293490'), ('셀트리온제약', '068760'),
            ('두산에너빌리티', '034020'), ('한화에어로스페이스', '012450'),
            ('SK스퀘어', '402340'), ('삼성전기', '009150'),
        ]
    
    results = []
    for name, code in target_stocks:
        data = get_stock_price_naver(code)
        if data:
            results.append({
                'name': name,
                'code': code,
                'price': data['price'],
                'change': data['change'],
                'changeRate': data['changeRate'],
                # 시가총액은 임시로 가격 기반으로 계산 (실제로는 별도 조회 필요)
                'marketCap': data['price'] * 1000000  # 임시값
            })
    
    return jsonify({
        'success': True,
        'market': market,
        'stocks': results
    })


@app.route('/health', methods=['GET'])
def health():
    """서버 상태 확인"""
    return jsonify({'status': 'ok', 'message': '서버가 정상 작동 중입니다'})


if __name__ == '__main__':
    # Render.com에서는 환경변수 PORT를 사용
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 50)
    print("🚀 실시간 주가 서버 시작!")
    print("=" * 50)
    print(f"\n서버 포트: {port}")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=False)

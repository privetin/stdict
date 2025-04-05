import json
import os
from pathlib import Path

import mcp.types as types
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stdict")

SEARCH_API_URL = "https://stdict.korean.go.kr/api/search.do"
VIEW_API_URL = "https://stdict.korean.go.kr/api/view.do"


def get_api_key():
    # First try environment variable
    api_key = os.environ.get("STDICT_API_KEY")
    if api_key:
        return api_key

    # Then try Claude desktop config
    config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
                if "mcpServers" in config and "stdict" in config["mcpServers"]:
                    env = config["mcpServers"]["stdict"].get("env", {})
                    if "STDICT_API_KEY" in env:
                        return env["STDICT_API_KEY"]
        except:
            pass

    raise ValueError(
        "API key not found. Please set the STDICT_API_KEY environment variable or configure it in Claude desktop config."
    )


API_KEY = get_api_key()


@mcp.tool()
def search(
    query: str,
    api_key: str = API_KEY,
    req_type: str = "json",
    start: int = 1,
    num: int = 10,
    advanced: bool = False,
    target: int = 1,
    method: str = "exact",
    type1: str = "all",
    type2: str = "all",
    pos: str = "0",
    cat: str = "0",
    multimedia: str = "0",
    letter_s: int = 1,
    letter_e: int = 1,
    update_s: str = None,
    update_e: str = None
) -> list[types.TextContent | types.ImageContent]:
    """
    Search the Dictionary

    Args:
        <table class="tbl_type01 mt_10 lh_28">
            <caption>검색요청 정보</caption>
            <colgroup>
                <col style="width:15%">
                <col style="width:20%">
                <col style="width:15%">
                <col style="width:15%">
                <col>
            </colgroup>
            <thead>
                <tr>
                    <th scope="col">요청 변수</th>
                    <th scope="col">타입</th>
                    <th scope="col">허용값</th>
                    <th scope="col">필수/선택</th>
                    <th scope="col">설명</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="brdnone">key</td>
                    <td>string</td>
                    <td>16진수 32자리</td>
                    <td>필수</td>
                    <td class="left">인증 키</td>
                </tr>
                <tr>
                    <td class="brdnone">q</td>
                    <td>string</td>
                    <td>-</td>
                    <td>필수</td>
                    <td class="left">검색어(UTF-8 인코딩)</td>
                </tr>
                <tr>
                    <td class="brdnone">req_type</td>
                    <td>string</td>
                    <td>xml<br>json</td>
                    <td>선택</td>
                    <td class="left">요청 타입(기본값 xml)</td>
                </tr>
                <tr>
                    <td class="center">start</td>
                    <td class="center">integer </td>
                    <td class="center">1~1000</td>
                    <td class="center">선택</td>
                    <td class="left">검색의 시작 번호(기본값 1)</td>
                </tr>
                <tr>
                    <td class="center">num</td>
                    <td class="center">integer </td>
                    <td class="center">10~100</td>
                    <td class="center">선택</td>
                    <td class="left">결과 출력 건수(기본값 10)</td>
                </tr>
                <tr>
                    <td class="center">advanced</td>
                    <td class="center">string</td>
                    <td class="center">
                        <p>n</p>
                        <p>y</p>
                    </td>
                    <td class="center">선택</td>
                    <td class="left">
                        <p>- 자세히 찾기 여부(기본값 n)</p>
                        <p>y: 자세히 찾기 사용</p>
                        <p>n: 자세히 찾기 미사용</p>
                    </td>
                </tr>
                <tr>
                    <td class="t_red" colspan="5"><br />※ 하단의 요청 변수들을 사용하시려면 자세히 찾기 여부(기본값
                        n)인 "advanced" 요청 변수를 'y'로 하셔야 합니다.</td>
                </tr>
                <tr>
                    <td class="center">target</td>
                    <td class="center">integer</td>
                    <td class="center">1 ~ 11</td>
                    <td class="center">선택</td>
                    <td class="left">
                        <p>- 찾을 대상(기본값 1)</p>
                        <p>1: 표제어</p>
                        <p>2: 원어</p>
                        <p>3: 어원</p>
                        <p>4: 발음</p>
                        <p>5: 활용</p>
                        <p>6: 문형</p>
                        <p>7: 문법</p>
                        <p>8: 뜻풀이</p>
                        <p>9: 용례</p>
                        <p>10: 용례 출전</p>
                        <p>11: 용례 번역</p>
                    </td>
                </tr>
                <tr>
                    <td class="center">method</td>
                    <td class="center">string</td>
                    <td class="center">
                        <p>exact</p>
                        <p>include</p>
                        <p>start</p>
                        <p>end</p>
                        <p>wildcard</p>
                    </td>
                    <td class="center">선택</td>
                    <td class="left">
                        <p>- 검색 방식(기본값: exact)</p>
                        <p>exact: 일치 검색</p>
                        <p>include: 포함 검색</p>
                        <p>start: 시작</p>
                        <p>end: 끝</p>
                        <p>wildcard: 와일드카드 검색</p>
                    </td>
                </tr>
                <tr>
                    <td class="center">type1</td>
                    <td class="center">array of string</td>
                    <td class="center">
                        <p>all</p>
                        <p>word</p>
                        <p>phrase</p>
                        <p>idiom</p>
                        <p>proverb</p>
                    </td>
                    <td class="center">선택</td>
                    <td class="left">
                        <p>- 구분 1(기본값 all)</p>
                        <p>all: 전체</p>
                        <p>- 아래 값을 다중 선택할 수 있도록 콤마(,)로 구분하여 나열한다.</p>
                        <p>word: 어휘</p>
                        <p>phrase: 구</p>
                        <p>idiom: 관용구</p>
                        <p>proverb: 속담</p>
                    </td>
                </tr>
                <tr>
                    <td class="center">type2</td>
                    <td class="center">array of string</td>
                    <td class="center">
                        <p>all</p>
                        <p>native</p>
                        <p>chinese</p>
                        <p>loanword</p>
                        <p>hybrid</p>
                    </td>
                    <td class="center">선택</td>
                    <td class="left">
                        <p>- 구분 2(기본값 all)</p>
                        <p>all: 전체</p>
                        <p>- 아래 값을 다중 선택할 수 있도록 콤마(,)로 구분하여 나열한다.</p>
                        <p>native: 고유어</p>
                        <p>chinese: 한자어</p>
                        <p>loanword: 외래어</p>
                        <p>hybrid: 혼종어</p>
                    </td>
                </tr>
                <!--  
        <tr>
            <td class="center">type3</td>
            <td class="center">array of string</td>
            <td class="center">
                <p>all</p>
                <p>dialect</p>
                <p>nkorean</p>
                <p>ancient</p>
            </td>
            <td class="center">선택</td>
            <td class="left">
                <p>- 구분 3(기본값 all)</p>
                <p>all: 전체</p>
                <p>- 아래 값을 다중 선택할 수 있도록 콤마(,)로 구분하여 나열한다.</p>
                <p>dialect: 방언</p>
                <p>nkorean: 북한어</p>
                <p>ancient: 옛말</p>
            </td>
        </tr>
        -->
                <tr>
                    <td class="center">pos</td>
                    <td class="center">array of integer</td>
                    <td class="center">0~15</td>
                    <td class="center">선택</td>
                    <td class="left">
                        <p>- 품사(기본값 0)</p>
                        <p>0: 전체</p>
                        <p>- 아래 값을 다중 선택할 수 있도록 콤마(,)로 구분하여 나열한다.</p>
                        <p>1: 명사</p>
                        <p>2: 대명사</p>
                        <p>3: 수사</p>
                        <p>4: 조사</p>
                        <p>5: 동사</p>
                        <p>6: 형용사</p>
                        <p>7: 관형사</p>
                        <p>8: 부사</p>
                        <p>9: 감탄사</p>
                        <p>10: 접사</p>
                        <p>11: 의존 명사</p>
                        <p>12: 보조 동사</p>
                        <p>13: 보조 형용사</p>
                        <p>14: 어미</p>
                        <p>15: 품사 없음</p>
                    </td>
                </tr>
                <tr>
                    <td class="center">cat</td>
                    <td class="center">array of integer</td>
                    <td class="center">0~67</td>
                    <td class="center">선택</td>
                    <td class="left">
                        <p>- 전문 분야(기본값 0)</p>
                        <p>0: 전체</p>
                        <p>- 아래 값을 다중 선택할 수 있도록 콤마(,)로 구분하여 나열한다.</p>
                        <p>1: 언어</p>
                        <p>2: 문학</p>
                        <p>3: 역사</p>
                        <p>4: 철학</p>
                        <p>5: 교육</p>
                        <p>6: 민속</p>
                        <p>7: 인문 일반</p>
                        <p>8: 법률</p>
                        <p>9: 군사</p>
                        <p>10: 경영</p>
                        <p>11: 경제</p>
                        <p>12: 복지</p>
                        <p>13: 정치</p>
                        <p>14: 매체</p>
                        <p>15: 행정</p>
                        <p>16: 심리</p>
                        <p>17: 사회 일반</p>
                        <p>18: 지구</p>
                        <p>19: 지리</p>
                        <p>20: 해양</p>
                        <p>21: 천문</p>
                        <p>22: 환경</p>
                        <p>23: 생명</p>
                        <p>24: 동물</p>
                        <p>25: 식물</p>
                        <p>26: 천연자원</p>
                        <p>27: 수학</p>
                        <p>28: 물리</p>
                        <p>29: 화학</p>
                        <p>30: 자연 일반</p>
                        <p>31: 농업</p>
                        <p>32: 수산업</p>
                        <p>33: 임업</p>
                        <p>34: 광업</p>
                        <p>35: 공업</p>
                        <p>36: 서비스업</p>
                        <p>37: 산업 일반</p>
                        <p>38: 의학</p>
                        <p>39: 약학</p>
                        <p>40: 한의</p>
                        <p>41: 수의</p>
                        <p>42: 식품</p>
                        <p>43: 보건 일반</p>
                        <p>44: 건설</p>
                        <p>45: 교통</p>
                        <p>46: 기계</p>
                        <p>47: 전기·전자</p>
                        <p>48: 재료</p>
                        <p>49: 정보·통신</p>
                        <p>50: 공학 일반</p>
                        <p>51: 체육</p>
                        <p>52: 연기</p>
                        <p>53: 영상</p>
                        <p>54: 무용</p>
                        <p>55: 음악</p>
                        <p>56: 미술</p>
                        <p>57: 복식</p>
                        <p>58: 공예</p>
                        <p>59: 예체능 일반</p>
                        <p>60: 가톨릭</p>
                        <p>61: 기독교</p>
                        <p>62: 불교</p>
                        <p>63: 종교 일반</p>
                        <p>64: 인명</p>
                        <p>65: 지명</p>
                        <p>66: 책명</p>
                        <p>67: 고유명 일반</p>
                    </td>
                </tr>
                <tr>
                    <td class="center">multimedia</td>
                    <td class="center">array of integer</td>
                    <td class="center">0~6</td>
                    <td class="center">선택</td>
                    <td class="left">
                        <p>- 멀티미디어(기본값 0)</p>
                        <p>0: 전체</p>
                        <p>- 아래 값을 다중 선택할 수 있도록 콤마(,)로 구분하여 나열한다.</p>
                        <p>1: 사진</p>
                        <p>2: 삽화</p>
                        <p>3: 동영상</p>
                        <p>4: 애니메이션</p>
                        <p>5: 소리</p>
                        <p>6: 없음</p>
                    </td>
                </tr>
                <tr>
                    <td class="center">letter_s</td>
                    <td class="center">integer</td>
                    <td class="center">1 ~ </td>
                    <td class="center">선택</td>
                    <td class="left">- 음절 수 시작(기본값 1)</td>
                </tr>
                <tr>
                    <td class="center">letter_e</td>
                    <td class="center">integer</td>
                    <td class="center">1 ~ </td>
                    <td class="center">선택</td>
                    <td class="left">- 음절 수 끝(기본값 1)</td>
                </tr>
                <tr>
                    <td class="center">update_s</td>
                    <td class="center">integer</td>
                    <td class="center">yyyymmdd</td>
                    <td class="center">선택</td>
                    <td class="left">- 고친 날짜 시작일</td>
                </tr>
                <tr>
                    <td class="center">update_e</td>
                    <td class="center">integer</td>
                    <td class="center">yyyymmdd</td>
                    <td class="center">선택</td>
                    <td class="left">- 고친 날짜 종료일</td>
                </tr>
            </tbody>
        </table>
    """
    params = {
        "key": api_key,
        "q": query,
        "req_type": req_type,
        "start": start,
        "num": num,
        "advanced": "y" if advanced else "n",
        "type_search": "search"
    }

    if advanced:
        advanced_params = {
            "target": target,
            "method": method,
            "type1": type1,
            "type2": type2,
            "pos": pos,
            "cat": cat,
            "multimedia": multimedia,
            "letter_s": letter_s,
            "letter_e": letter_e,
        }

        # Only add date parameters if they're provided
        if update_s:
            advanced_params["update_s"] = update_s
        if update_e:
            advanced_params["update_e"] = update_e

        params.update(advanced_params)

    try:
        response = requests.get(SEARCH_API_URL, params=params)
        response.raise_for_status()

        # Return the original XML response as text
        return [types.TextContent(type="text", text=response.text)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


def determine_method(query: str) -> str:
    """
    Determine the appropriate method based on query format

    Args:
        query: The search term or target code

    Returns:
        The appropriate method: "target_code" for numeric IDs, "word_info" for words
    """
    # Check if query contains only digits
    if query.isdigit():
        return "target_code"
    else:
        return "word_info"


@mcp.tool()
def detail(
    query: str,
    api_key: str = API_KEY,
    method: str = None,
    req_type: str = "json",
) -> list[types.TextContent | types.ImageContent]:
    """
    Get detailed information about a Dictionary entry

    Args:
        <table class="tbl_type01 mt_10 lh_28">
            <caption>검색 요청 설명</caption>
            <colgroup>
                <col style="width:15%;">
                <col style="width:15%;">
                <col style="width:15%;">
                <col style="width:15%;">
                <col>
            </colgroup>
            <thead>
                <tr>
                    <th scope="col">요청 변수</th>
                    <th scope="col">타입</th>
                    <th scope="col">허용값</th>
                    <th scope="col">필수/선택</th>
                    <th scope="col">설명</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="brdnone">key</td>
                    <td>string</td>
                    <td>16진수 32자리</td>
                    <td>필수</td>
                    <td class="left">인증 키</td>
                </tr>
                <tr>
                    <td class="brdnone">method</td>
                    <td>string</td>
                    <td>
                        word_info
                        <br />
                        target_code
                    </td>
                    <td>필수</td>
                    <td class="left">
                        -검색 방식(기본값 word_info)
                        <br />
                        word_info: 표제어 정보(표제어 + 어깨번호)
                        <br />
                        target_code: *대상 코드(target_code)
                    </td>
                </tr>
                <tr>
                    <td class="brdnone">req_type</td>
                    <td>string</td>
                    <td>xml<br>json</td>
                    <td>선택</td>
                    <td class="left">요청 타입(기본값 xml)</td>
                </tr>
                <tr>
                    <td class="brdnone">q</td>
                    <td>string</td>
                    <td>-</td>
                    <td>필수</td>
                    <td class="left">검색어(UTF-8 인코딩)</td>
                </tr>
            </tbody>
        </table>
    """
    # Auto-determine method if not specified
    if method is None:
        method = determine_method(query)

    # Validate method parameter
    if method not in ["word_info", "target_code"]:
        return [types.TextContent(type="text", text="Error: Invalid method value. Must be 'word_info' or 'target_code'")]

    # Validate req_type parameter
    if req_type not in ["json", "xml"]:
        return [types.TextContent(type="text", text="Error: Invalid req_type value. Must be 'json' or 'xml'")]

    params = {
        "key": api_key,
        "method": method,
        "req_type": req_type,
        "q": query,
        "type_search": "view"
    }

    try:
        response = requests.get(VIEW_API_URL, params=params)
        response.raise_for_status()

        # Return the original response as text
        return [types.TextContent(type="text", text=response.text)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

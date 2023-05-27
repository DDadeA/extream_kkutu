https://raw.githubusercontent.com/DDadeA/extream_kkutu/main/%5BSHANA%5D2023-05-27%2022-21-10.mp4

장난으로 만든 끝말잇기 서버. 정말 놀라운 점은, 한 사람이 단어를 입력하면, 그 사람을 제외한 모든 사람이 그 단어를 이어나가야 한다는 점이다. 

그 결과, 단어는 지수적으로 증가하고, 입력한 글자 수 만큼 점수를 얻어, 제한 시간 내에 점수가 가장 높은 사람이 이기는 게임이 탄생했다.
웹소켓으로만 작성했다. 

사실 대충 만들다가 말아서, 보안도 전혀 신경쓰지 않았다. 그래서 '어떤' 스토리 게임처럼 클라이언트 변조가 가능하다.

## 시작하는 법
- realServer.py를 실행시킨다.
- 웹서버를 연다. <code>python -m SimpleHTTPServer 8000</code> 명령어 등으로 열 수 있다.
- 참여자를 모두 접속시킨다.
- 사이트 채팅창에 <code>/start [normal, super]</code>를 통해 게임을 시작할 수 있다. normal은 그냥 끝말잇기, super는 위 설명의 룰이다.
- 즐기기
___

- 서버 주소는 index.html의 456 line에 있다. 수정해서 사용해야 한다.
- 닉네임은 겹치면 안 된다.
- <code>Tambourin.mp3</code>가 배경음악인데, 저작권 문제로 올리지 않았다.
- <code>_id_ko.csv</code>는 [끄투 db](https://github.com/JJoriping/KKuTu/blob/master/db.sql)에서 잘라온 것이다. 공개된 db가 오래전의 것이라 최신 단어들은 없다. GPL 3.0은 이것 때문에 적용했다.

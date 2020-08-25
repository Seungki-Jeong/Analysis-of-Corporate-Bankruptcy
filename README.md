# 08/21 주간 계획

1. 기업 선정
 - 건실 기업, 부도기업 분류
 - 기업 리스트 수집
 - 추후 기업 종목 선정
 현재: 부도 기업 리스트 확보했고 건실 기업 및 부도 기업 리스트 데이터화 해야 함 <br>
관련 링크: https://dev-kind.krx.co.kr/main.do?method=loadInitPage&scrnmode=1 <br>
(투자유의사항 -> 기타사항 -> 상장폐지현황)

2. 데이터 수집
 - 기업 납세 현황 파악
 - 데이터 수집 및 저장
 현재: 납세 현황을 파악하려 했으나 데이터 수집이 어려워 기업재무제표를 활용하기로 함. (부도기업 포함) <br>
기업과 데이터 선정을 하지 않았기 때문에 공시 시스템 api를 활용해서 언제든지 필요한 데이터를 가져올 수 있도록 임의의 데이터를 가져오는 코드만 만들어 놓는 것을 목표. <br>
관련 링크: 공시시스템(http://dart.fss.or.kr/), <br>
api 연결(https://datascienceschool.net/view-notebook/adead36729704e7b8660dda3be6a6524/) <br>

3. 텍스트 수집
 - 기업 뉴스 데이터 크롤링
 - 핵심 키워드 파악
 현재: 진행 x
 전체 참고자료(http://www.korfin.org/korfin_file/forum/17fall5-2.pdf)
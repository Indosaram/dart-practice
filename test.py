import dart_fss as dart

# Open DART API KEY 설정
API_KEY = "45cb594fcb8f1389f5b4e0c46c77b4f8e1d12d85"
dart.set_api_key(api_key=API_KEY)




corp_code = '00126380'

reports = dart.filings.search(
    corp_code=corp_code, bgn_de='20210101', pblntf_detail_ty='a001'
)
print(reports)


# 가장 최신 보고서 선택
report = reports[0]

# report에서 xbrl 파일 추출
xbrl = report.xbrl

cash_flow_report = xbrl.get_cash_flows()[0].to_DataFrame()
cash_flow_report.to_csv("cash_flow.csv")

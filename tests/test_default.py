import easy_athena

def test_query():
    result = easy_athena.EasyAthena(output_bucket_name='kmong-data-lake', output_prefix='97.trash/athena/query_output', region_name='ap-northeast-1').query(
        'SELECT * FROM "history"."kcp_ads_20201201" LIMIT 100;')
    print(result)
    assert len(result) == 100

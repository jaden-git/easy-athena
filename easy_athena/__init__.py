import uuid
import gzip
import time
import random
import os
import json
import datetime
import mimetypes
import boto3

class EasyAthena():

    def __init__(self, output_bucket_name, output_prefix, region_name='ap-northeast-2'):
        self._athena_client= boto3.client('athena', region_name=region_name)
        self._output_prefix = output_prefix
        self._output_bucket_name = output_bucket_name


    def query(self, sql, format_type="auto", request_limit=10000):
        def get_format_type(sql):
            if sql.lower().startswith('select'):
                return "select"
            else:
                return "raw"

        def get_varchar_value(row):
            result = []
            for piece in row["Data"]:
                result.append(piece.get('VarCharValue', None))

            return result
            # return [piece["VarCharValue"] for piece in row["Data"]]

        def merge_with_columns(columns, data):
            result = {}
            for index, piece in enumerate(data):
                result[columns[index]] = piece
            return result

        def get_var_char_values(d):
            return [obj.get('VarCharValue', None) for obj in d['Data']]

        def parse(header, rows):
            header = get_var_char_values(header)
            return [dict(zip(header, get_var_char_values(row))) for row in rows]


        if format_type == "auto":
            format_type = get_format_type(sql)

        result = []

        query_id = self._athena_client.start_query_execution(**{
            "QueryString": sql,
            "ResultConfiguration": {
                "OutputLocation": f"s3://{self._output_bucket_name}/{self._output_prefix[1:] if self._output_prefix.startswith('/') else self._output_prefix}"
            }
        })["QueryExecutionId"]

        while True:
            status = self._athena_client.get_query_execution(QueryExecutionId=query_id)[
                "QueryExecution"]["Status"]["State"]
            time.sleep(1)
            if status == "CANCELLED":
                raise ValueError(f"[{sql}] is cancelled.")

            elif status == "FAILED":
                raise ValueError(f"[{sql}] is failed.")

            elif status == "SUCCEEDED":
                break
            else:
                continue

        next_tokens = []
        header = []
        for index in range(request_limit):
            
            request_data = {
                "QueryExecutionId":query_id
            }

            if len(next_tokens):
                request_data["NextToken"] = next_tokens[-1]

            query_raw_result = self._athena_client.get_query_results(**request_data)

            if format_type == "raw":
                result.append(query_raw_result)
                break
            elif format_type == "select":
                if index == 0:
                    header, *rows = query_raw_result['ResultSet']['Rows']
                else:
                    rows = query_raw_result['ResultSet']['Rows']

                result.extend(parse(header, rows))
                
                if "NextToken" in query_raw_result:
                    new_next_token = query_raw_result["NextToken"]
                    if new_next_token not in next_tokens:
                        next_tokens.append(new_next_token)
                    else:
                        break
                else:
                    break

        return result

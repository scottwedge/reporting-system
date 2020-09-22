# -*- coding:utf-8 -*
#
import re
from eggit.flask_restful_response import ok
from flask_restful import Resource, reqparse, marshal
from reporting_api.utils.requests_utils import get_argument
from reporting_api.exceptions.service_error import ServiceError
from reporting_api.exceptions.service_exception import ServiceException
from reporting_api.models.sales_models.sales_analysis_report import OrdSourceAdfeeModel
from reporting_api.utils.response_utils import obj_to_dict


class EntrySourceFee(Resource):
    def get(self):
        start_time = get_argument("start_time", default="2020-8-01", required=True)
        end_time = get_argument("end_time", default="2020-10-01")
        results = OrdSourceAdfeeModel.query.filter(
            OrdSourceAdfeeModel.order_pay_time.between(start_time, end_time))
        day_list = []
        tmp_dic = {}
        for result in results:
            store_code = obj_to_dict(result, keys=[], display=False)
            ord_pay_time = "{}({})".format(re.match(r'(\d+-\d+-\d+)', store_code.get("order_pay_time"))[0],
                                           store_code.get("week"))
            if ord_pay_time not in day_list:
                day_list.append(ord_pay_time)
                tmp_dic[ord_pay_time] = {
                    "total_us_fee": 0,
                    "total_japan_fee": 0,
                    "total_europe_fee": 0,
                    "total_canada_fee": 0,
                    "total_loctek_fee": 0,
                    "total_google_fee": 0,
                    "total_india_fee": 0,
                    "TV mounts": 0,  # 电视架
                    "Monitor mounts": 0,  # 显示架
                    "Fitness": 0,  # 健身
                    "Spacemaster mounts": 0,  # 空间
                    "Desktop Riser": 0,  # 升降桌
                    "height adjustable desk": 0,  # 升降台
                    "Monitor Stand": 0,  # 增高台.
                    "healthcare": 0,  # 健康管理类
                    "offacc": 0,  # 办公周边
                }
            total_us_fee = store_code.get('total_us_fee')
            tmp_dic[ord_pay_time]["total_us_fee"] += float(total_us_fee) if total_us_fee else 0

            total_japan_fee = store_code.get('total_japan_fee')
            tmp_dic[ord_pay_time]["total_japan_fee"] += float(total_japan_fee) if total_japan_fee else 0

            total_europe_fee = store_code.get('total_europe_fee')
            tmp_dic[ord_pay_time]["total_europe_fee"] += float(total_europe_fee) if total_europe_fee else 0

            total_canada_fee = store_code.get('total_canada_fee')
            tmp_dic[ord_pay_time]["total_canada_fee"] += float(total_canada_fee) if total_canada_fee else 0

            total_loctek_fee = store_code.get('total_loctek_fee')
            tmp_dic[ord_pay_time]["total_loctek_fee"] += float(total_loctek_fee) if total_loctek_fee else 0

            total_google_fee = store_code.get('total_google_fee')
            tmp_dic[ord_pay_time]["total_google_fee"] += float(total_google_fee) if total_google_fee else 0

            total_india_fee = store_code.get('total_india_fee')
            tmp_dic[ord_pay_time]["total_india_fee"] += float(total_india_fee) if total_india_fee else 0

            ad_fee_pro_type = store_code.get('ad_fee_pro_type')
            total_ad_fee = store_code.get('total_ad_fee')
            if ad_fee_pro_type in ["TV mounts", "Monitor mounts", "Fitness", "Spacemaster mounts", "Desktop Riser",
                                   "height adjustable desk", "Monitor Stand", "healthcare", "offacc"]:
                tmp_dic[ord_pay_time][ad_fee_pro_type] += float(total_ad_fee) if total_ad_fee else 0

        res_list = []
        for tmp in tmp_dic:
            res_list.append({
                "data_time": tmp,
                "total_us_fee": round(tmp_dic[tmp]["total_us_fee"], 1),
                "total_japan_fee": round(tmp_dic[tmp]["total_japan_fee"], 1),
                "total_europe_fee": round(tmp_dic[tmp]["total_europe_fee"], 1),
                "total_canada_fee": round(tmp_dic[tmp]["total_canada_fee"], 1),
                "total_loctek_fee": round(tmp_dic[tmp]["total_loctek_fee"], 1),
                "total_google_fee": round(tmp_dic[tmp]["total_google_fee"], 1),
                "total_india_fee": round(tmp_dic[tmp]["total_india_fee"], 1),
                "tv_mounts": round(tmp_dic[tmp]["TV mounts"], 1),
                "monitor_mounts": round(tmp_dic[tmp]["Monitor mounts"], 1),
                "fitness": round(tmp_dic[tmp]["Fitness"], 1),
                "spacemaster_mounts": round(tmp_dic[tmp]["Spacemaster mounts"], 1),
                "desktop_riser": round(tmp_dic[tmp]["Desktop Riser"], 1),
                "height_adjustable_desk": round(tmp_dic[tmp]["height adjustable desk"], 1),
                "monitor_stand": round(tmp_dic[tmp]["Monitor Stand"], 1),
                "healthcare": round(tmp_dic[tmp]["healthcare"], 1),
                "offacc": round(tmp_dic[tmp]["offacc"], 1),
                "total_cost": round(sum([
                    tmp_dic[tmp]["TV mounts"], tmp_dic[tmp]["Monitor mounts"], tmp_dic[tmp]["Fitness"],
                    tmp_dic[tmp]["Spacemaster mounts"],
                    tmp_dic[tmp]["Desktop Riser"], tmp_dic[tmp]["height adjustable desk"],
                    tmp_dic[tmp]["Monitor Stand"], tmp_dic[tmp]["healthcare"], tmp_dic[tmp]["offacc"]
                ]), 1)
            })
        return ok({"data": res_list})

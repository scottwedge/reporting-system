# -*- coding:utf-8 -*
# 店铺费用录入
import re
import datetime
from eggit.flask_restful_response import ok
from flask_restful import Resource, reqparse, marshal
from reporting_api.utils.requests_utils import get_argument
from reporting_api.exceptions.service_error import ServiceError
from reporting_api.exceptions.service_exception import ServiceException
from reporting_api.models.sales_models.sales_analysis_report import SalesAnalysisReportModel, ProProductModel
from reporting_api.utils.response_utils import obj_to_dict


class GlobalSaleLog(Resource):
    def get(self):
        start_time = get_argument("start_time", default='2019-01-01')
        end_time = get_argument("end_time", default='2019-02-02')
        city = get_argument("city", default="Japan")
        city_code = {
            "Japan": {"ord_sitecode": "JP", "db_field": "all_feejp"},  # 日本
            "Canada": {"ord_sitecode": "CAN", "db_field": "all_feecanada"},  # 加拿大
            "European": {"ord_sitecode": "EU", "db_field": "all_feeeu"},  # 欧洲
            "India": {"ord_sitecode": "INEI", "db_field": "all_feeeu"},  # 印度
            "US": {"ord_sitecode": "US", "db_field": "all_feeus"},  # 美国
        }

        if start_time > end_time:
            raise ServiceException(ServiceError.INVALID_VALUE)

        results = SalesAnalysisReportModel.query.filter(
            SalesAnalysisReportModel.ord_pay_time.between(start_time, end_time),
            SalesAnalysisReportModel.ord_sitecode == city_code[city].get("ord_sitecode"))
        temp_list = []
        tmp_dic = {
            "tot_sanum": 0,  # 总销量
            "tot_samount": 0,  # 总销售额
            "tot_platfee": 0,  # 总销售额

            "ord_maoli": 0.0,  # 毛利
            "ord_fobfee": 0.0,  # FOB
            "ord_costfee": 0.0  # 成本费=fob仓对应的值
        }
        for result in results:
            obj_dict = obj_to_dict(result, keys=[], display=False)
            store_code = obj_dict.get('source_code', '')
            if store_code not in temp_list:
                temp_list.append(store_code)
                tmp_dic[store_code] = {
                    "model": [],  # 执享型号 and 乐歌型号
                    "model_dic": {},
                }
            model_key = "{}_{}".format(obj_dict.get('pro_fname'), obj_dict.get('pro_bsname'))
            if model_key not in tmp_dic[store_code]['model']:
                tmp_dic[store_code]['model'].append(model_key)
                tmp_dic[store_code]["model_dic"][model_key] = {
                    "ord_salenum": 0,  # 销量
                    "ord_sale_amount": 0,  # 销售额
                    "ord_platfee": 0,  # 平台
                }
            # 平台费用
            try:
                ord_platfee = float(obj_dict.get("ord_platfee"))
            except Exception as e:
                ord_platfee = 0
            tmp_dic[store_code]["model_dic"][model_key]["ord_platfee"] += ord_platfee
            tmp_dic["tot_platfee"] += ord_platfee
            # 销量
            ord_salenum = int(obj_dict.get("ord_salenum"))
            tmp_dic[store_code]["model_dic"][model_key]["ord_salenum"] += ord_salenum
            tmp_dic["tot_sanum"] += ord_salenum
            # 销售额
            ord_sale_amount = float(obj_dict.get("ord_sale_amount"))
            tmp_dic[store_code]["model_dic"][model_key]["ord_sale_amount"] += ord_sale_amount
            tmp_dic["tot_samount"] += ord_sale_amount

            for key in ['ord_maoli', 'ord_fobfee', 'ord_costfee']:
                try:
                    tmp_dic[key] += float(obj_dict.get(key))
                except Exception as e:
                    pass

        res_ls = []
        tot_samount = tmp_dic.pop("tot_samount")
        if not tot_samount:
            return ok({"data": []})
        tot_maoli = tmp_dic.pop("ord_maoli") / tot_samount if tot_samount else 0
        ret_dic = {
            'total_sale_num': round(tmp_dic.pop("tot_sanum"), 1),
            'total_sale_amount': round(tot_samount, 1),
            'total_ord_platfee': round(tmp_dic.pop("tot_platfee"), 1),
            "total_maoli": round(tot_maoli, 3),
            "total_fobfee": round(tmp_dic.pop("ord_fobfee"), 1),
            "total_costfee": round(tmp_dic.pop("ord_costfee"), 1),
            "data": []
        }
        ret_dic.update({
            "tot_average": round(tot_samount / ret_dic["total_sale_num"] if ret_dic["total_sale_amount"] else 0, 1),
        })
        num = 0
        for tmp_k in tmp_dic:
            for model_k in tmp_dic[tmp_k]['model_dic']:
                num += 1
                shop_name = tmp_k
                if tmp_k in res_ls:
                    shop_name = ''
                else:
                    res_ls.append(shop_name)
                mode_dic = {
                    "id": num,
                    "shop_name": shop_name,
                    "fname": model_k.split('_')[0],
                    "bsname": model_k.split('_')[1],
                    "sale_num": int(tmp_dic[tmp_k]["model_dic"][model_k]['ord_salenum']),
                    "sale_amount": round(tmp_dic[tmp_k]["model_dic"][model_k]['ord_sale_amount'], 1),
                    "ord_platfee": round(tmp_dic[tmp_k]["model_dic"][model_k]['ord_platfee'], 1),
                }

                user = ProProductModel.query.filter(ProProductModel.bsname == mode_dic['bsname']).first()
                product_dict = obj_to_dict(user, keys=[], display=False)
                mode_dic.update({
                    'img_url': product_dict.get("pro_image_path", ""),
                    'sale_avg': round(mode_dic.get("sale_amount", 0) / mode_dic.get("sale_num", 0), 1),
                })
                if mode_dic.get("shop_name"):
                    mode_dic['children'] = []
                    ret_dic['data'].append(mode_dic)
                else:
                    ret_dic['data'][-1]['children'].append(mode_dic)

        return ok(ret_dic)

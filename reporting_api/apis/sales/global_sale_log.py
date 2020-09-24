# -*- coding:utf-8 -*
# 店铺费用录入1
import re
import datetime
from eggit.flask_restful_response import ok
from reporting_api.extensions import db

from flask_restful import Resource, reqparse, marshal
from reporting_api.utils.requests_utils import get_argument
from reporting_api.exceptions.service_error import ServiceError
from reporting_api.exceptions.service_exception import ServiceException
from reporting_api.utils.response_utils import obj_to_dict
from reporting_api.models.sales_models.sales_analysis_report import (
    SalesAnalysisReportModel as SalesM,
    ProProductModel as ProductM
)


class GlobalSaleLog(Resource):

    def fob_maoli(self, factoryfee, fob):
        # 换汇 = 出厂价 / fob
        swap = factoryfee / fob
        # FOB毛利 = FOB金额 * (汇率 + 0.17 * 换汇 / 1.17 - 换汇)
        fob_maoli = fob * (swap + 0.17 * swap / 1.17 - swap)
        return "{}%".format(round(fob_maoli * 100), 2)

    def get(self):
        start_time = get_argument("start_time", default='2019-9-01')
        end_time = get_argument("end_time", default='2019-9-22')
        city = get_argument("city", default="Japan")
        city_code = {
            "Japan": {"ord_sitecode": "JP", "db_field": "all_feejp"},  # 日本
            "Canada": {"ord_sitecode": "CAN", "db_field": "all_feecanada"},  # 加拿大
            "European": {"ord_sitecode": "EU", "db_field": "all_feeeu"},  # 欧洲
            "India": {"ord_sitecode": "INEI", "db_field": "all_feeeu"},  # 印度
            "US": {"ord_sitecode": "US", "db_field": "all_feeus"},  # 美国
        }
        table = db.session.query(SalesM, ProductM).join(SalesM, SalesM.pro_fname == ProductM.bsname)

        results = table.filter(
            SalesM.ord_pay_time.between(start_time, end_time),
            SalesM.ord_sitecode == city_code[city].get("ord_sitecode"))
        tmp_list = []
        tmp_dic = {
        }
        sorts_list = ["ord_salenum", "ord_maoli", "ord_sale_amount", "ord_sale_price", "ord_platfee", "ord_factoryfee",
                      "ord_fobfee"]
        for i in sorts_list:
            tmp_dic[i] = 0
        for sales_table, product_table in results:
            obj_dict = obj_to_dict(sales_table, keys=[], display=False)
            obj_dict.update({
                'image': product_table.pro_image_path,
            })
            store_code = obj_dict.get('source_code', '')
            if store_code not in tmp_list:
                tmp_list.append(store_code)
                tmp_dic[store_code] = {
                    "model": [],  # 执享型号 and 乐歌型号
                    "model_dic": {},
                }
            model_key = "{}_{}".format(obj_dict.get('pro_fname'), obj_dict.get('pro_bsname'))
            if model_key not in tmp_dic[store_code]['model']:
                tmp_dic[store_code]['model'].append(model_key)
                tmp_dic[store_code]["model_dic"] = {
                    model_key: {"image": ''}
                }
                for i in ["ord_salenum", "ord_sale_amount", "ord_sale_price", "ord_platfee"]:
                    tmp_dic[store_code]["model_dic"][model_key][i] = 0
            for sort in sorts_list:
                try:
                    tmp_dic[sort] += float(obj_dict.get(sort)) if obj_dict.get(sort) else 0
                except Exception as e:
                    pass
            for sales in ["ord_salenum", "ord_sale_amount", "ord_sale_price", "ord_platfee"]:
                try:
                    print(obj_dict.get(sales))
                    tmp_dic[store_code]["model_dic"][model_key][sales] += float(obj_dict.get(sales)) if obj_dict.get(
                        sales) else 0
                except Exception as e:
                    pass
            if not tmp_dic[store_code]["model_dic"][model_key]['image']:
                tmp_dic[store_code]["model_dic"][model_key]['image'] = obj_dict.get("image")
        res_list = []
        shop_name_list = []
        num = 0
        if not tmp_dic['ord_sale_amount']:
            return ok({"title": '', "data": res_list})
        table_txt = "{}-{}{}销售{}美金, 毛利率{}%. FOB金额{}美金,, FOB毛利{}元, FOB毛利占比{}%."

        table_txt = table_txt.format(start_time.replace('-', '/'), end_time.replace('-', '/'), city,
                                     round(tmp_dic['ord_sale_amount'], 2),
                                     round((tmp_dic['ord_maoli'] / tmp_dic['ord_sale_amount']) * 100, 2),
                                     round(tmp_dic['ord_fobfee'], 2),
                                     self.fob_maoli(tmp_dic['ord_fobfee'], tmp_dic['ord_factoryfee']),
                                     round(tmp_dic['ord_factoryfee'] / tmp_dic['ord_sale_amount'] * 100, 2))

        for shop in tmp_dic:
            if shop in sorts_list:
                continue
            shop_name = shop
            if shop_name in shop_name_list:
                shop_name = ''
            for mede in tmp_dic[shop]["model_dic"]:
                num += 1
                arge = {
                    "id": num,
                    "shop_name": shop_name,
                    "fname": mede.split('_')[0],
                    "bsname": mede.split('_')[1],
                    "image": tmp_dic[shop]["model_dic"][mede]["image"],
                    "sale_num": int(tmp_dic[shop]["model_dic"][mede]["ord_salenum"]),
                    "sale_amount": round(tmp_dic[shop]["model_dic"][mede]["ord_sale_amount"], 2),
                    "sale_platfee": round(tmp_dic[shop]["model_dic"][mede]["ord_platfee"], 2),
                }
                arge.update({
                    "sale_average_plaftee": round(arge.get("sale_amount") / arge.get("sale_num"), 2)
                })
                res_list.append(arge)

        return ok({"title": table_txt, "data": res_list})
